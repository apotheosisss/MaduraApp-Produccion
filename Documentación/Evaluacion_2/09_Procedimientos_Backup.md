# Procedimientos de Backup y Replicación de Datos — MaduraApp

> Este documento describe los **procedimientos operativos** para mantener copias de seguridad de la base de datos de producción y para **replicarla** en el ambiente de pruebas. También cubre la replicación de la configuración del servidor de producción en otros entornos.
>
> Responde al **criterio 3 de la rúbrica** ("procedimientos detallados para realizar una copia de seguridad de la base de datos de producción en el entorno de pruebas") e indicador IL2.2.

---

## 1. Visión general de la estrategia

```mermaid
graph LR
    Prod[(Supabase Prod<br/>PostgreSQL 16)] -->|pg_dump diario| Local[/dumps/<br/>backup_prod_YYYY-MM-DD.sql/]
    Local -->|pg_restore / psql| Test[(Test DB Local<br/>PostgreSQL o SQLite)]
    Local -->|cifrado AES-256| Remote[Repositorio<br/>privado de backups]
    Supabase[Supabase autobackup] -.->|cada 24h gestionado| Prod
```

### 1.1 Objetivos del esquema de backup

| Objetivo | Cumplimiento |
|----------|-------------|
| **Recuperación ante desastres** | Backup diario + autobackup Supabase |
| **Replicación a ambiente de pruebas** | Procedimiento documentado con script reproducible |
| **Auditabilidad histórica** | Retención 30 días con rotación |
| **Privacidad** | Dumps cifrados antes de almacenarse en repo de backups |
| **Reproducibilidad** | Todo el procedimiento ejecutable por script, sin pasos manuales en producción |

### 1.2 Esquema de la base de datos

La BD de producción consta de **una sola tabla** (`scans`), creada por la migración Alembic `0001_create_scans_table`:

```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_token VARCHAR(255) NOT NULL,
    fruit_type VARCHAR(50) NOT NULL,
    maturity_label VARCHAR(50) NOT NULL,
    confidence REAL NOT NULL,
    image_hash VARCHAR(64)
);

CREATE INDEX ix_scans_user_token ON scans (user_token);
CREATE INDEX ix_scans_timestamp ON scans (timestamp DESC);
```

Por su simplicidad, los dumps son rápidos (~ KB a MB).

---

## 2. Procedimiento A — Backup completo de BD de producción

### 2.1 Herramientas requeridas

- `pg_dump` v16 (incluido en `postgresql-client-16`).
- Acceso a la cadena de conexión `DB_URL` de Supabase.
- Espacio libre en disco (~ 2× tamaño actual de la BD).

### 2.2 Instalación de `pg_dump` v16

#### Ubuntu / Debian
```bash
sudo sh -c 'echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
  > /etc/apt/sources.list.d/pgdg.list'
wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install postgresql-client-16
pg_dump --version  # Verificar: pg_dump (PostgreSQL) 16.x
```

#### macOS
```bash
brew install postgresql@16
brew link postgresql@16 --force
```

#### Windows (PowerShell)
1. Descargar el instalador interactivo desde [postgresql.org](https://www.postgresql.org/download/windows/).
2. Marcar solo "Command Line Tools" durante la instalación.
3. Agregar `C:\Program Files\PostgreSQL\16\bin` al PATH.

### 2.3 Script de backup (`scripts/backup_prod.sh`)

> Esta sección documenta el script. Si no existe físicamente en el repo, se crea siguiendo este patrón:

```bash
#!/usr/bin/env bash
# scripts/backup_prod.sh
# Uso: ./backup_prod.sh
# Pre-requisito: DB_URL_PROD en variable de entorno (NUNCA hardcoded aquí)

set -euo pipefail

DB_URL="${DB_URL_PROD:?Define DB_URL_PROD antes de ejecutar}"
TIMESTAMP=$(date +%Y-%m-%d_%H%M)
BACKUP_DIR="${BACKUP_DIR:-./dumps}"
mkdir -p "$BACKUP_DIR"

OUTFILE="$BACKUP_DIR/backup_prod_${TIMESTAMP}.sql.gz"

# Convertir el prefijo SQLAlchemy a formato libpq nativo
PG_URL="${DB_URL/postgresql+asyncpg/postgresql}"

echo "==> Dumping production DB to $OUTFILE"
pg_dump "$PG_URL" \
  --no-owner \
  --no-acl \
  --format=plain \
  --table=scans \
  --table=alembic_version \
  | gzip > "$OUTFILE"

echo "==> Backup completed: $(du -h "$OUTFILE" | cut -f1)"
echo "==> Files in $BACKUP_DIR:"
ls -lh "$BACKUP_DIR"

# Rotación: conservar solo los 30 más recientes
echo "==> Pruning backups older than 30 days"
find "$BACKUP_DIR" -name "backup_prod_*.sql.gz" -mtime +30 -delete
```

### 2.4 Equivalente para PowerShell (`scripts/backup_prod.ps1`)

```powershell
# scripts/backup_prod.ps1
$dbUrl = $env:DB_URL_PROD
if (-not $dbUrl) {
    Write-Error "Define `$env:DB_URL_PROD antes de ejecutar"
    exit 1
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$backupDir = ".\dumps"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$outfile = "$backupDir\backup_prod_$timestamp.sql"

# Convertir prefijo SQLAlchemy a libpq
$pgUrl = $dbUrl -replace 'postgresql\+asyncpg', 'postgresql'

Write-Output "==> Dumping production DB to $outfile"
& pg_dump $pgUrl --no-owner --no-acl --format=plain `
  --table=scans --table=alembic_version | Out-File -Encoding utf8 $outfile

# Compresión opcional
Compress-Archive -Path $outfile -DestinationPath "$outfile.zip" -Force
Remove-Item $outfile

Write-Output "==> Backup completado"
Get-ChildItem $backupDir -Filter "backup_prod_*.sql.zip" | Format-Table Name, Length, LastWriteTime
```

### 2.5 Ejecución manual

```bash
export DB_URL_PROD="postgresql+asyncpg://postgres.xxxxx:PASS@host:5432/postgres"
./scripts/backup_prod.sh
```

Salida esperada:

```
==> Dumping production DB to ./dumps/backup_prod_2026-05-26_2130.sql.gz
==> Backup completed: 12K
==> Files in ./dumps:
-rw-r--r-- 1 user user 12K may 26 21:30 backup_prod_2026-05-26_2130.sql.gz
==> Pruning backups older than 30 days
```

### 2.6 Frecuencia recomendada

| Trigger | Frecuencia |
|---------|-----------|
| Manual | Antes de cualquier change disruptivo en BD |
| Programado | Diario a las 03:00 (cron / Task Scheduler) |
| Pre-deploy | Recomendado ejecutar antes de cada migración Alembic en producción |
| Autobackup de Supabase | 1× por día (gestionado por proveedor) |

---

## 3. Procedimiento B — Restaurar el backup en el ambiente de pruebas

### 3.1 Opción B.1 — Restaurar en PostgreSQL local (paridad máxima)

#### Pre-requisitos
- PostgreSQL 16 corriendo en `localhost:5432`.
- Base de datos vacía `maduraapp_test` creada.

```bash
# Crear BD vacía
createdb -h localhost -U postgres maduraapp_test

# Restaurar el dump
gunzip -c dumps/backup_prod_2026-05-26_2130.sql.gz | \
  psql -h localhost -U postgres -d maduraapp_test

# Verificar
psql -h localhost -U postgres -d maduraapp_test -c "SELECT COUNT(*) FROM scans;"
```

#### Configurar el backend para apuntar a la BD restaurada

Editar `Producto/backend/.env`:

```dotenv
DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/maduraapp_test
ENVIRONMENT=development
```

Levantar el backend y probar que los datos están:

```bash
uvicorn app.main:app --reload
curl http://localhost:8000/v1/history?limit=10
# Debe retornar los registros restaurados desde producción
```

### 3.2 Opción B.2 — Restaurar en SQLite (más rápido, menos paridad)

Útil para tests rápidos. Requiere un paso de conversión porque PostgreSQL y SQLite tienen sintaxis ligeramente diferente.

```bash
# Convertir dump PostgreSQL → SQLite con `pgloader` (recomendado)
# o usar pg_dump --data-only y reinyectar via SQLAlchemy

# Alternativa pragmática: usar el script de seed_from_prod
python scripts/seed_test_db_from_prod.py \
  --source-url "$DB_URL_PROD" \
  --target-url "sqlite+aiosqlite:///./maduraapp_dev.db"
```

> Si el script no existe, se sigue la opción B.1 que es más estándar.

### 3.3 Opción B.3 — Restaurar a partir de autobackup Supabase

Para recuperación ante desastres (no para uso cotidiano):

1. Login en Supabase Dashboard.
2. Proyecto `maduraapp-prod` → **Database** → **Backups**.
3. Seleccionar fecha del autobackup.
4. Click `Restore` (Supabase ofrece restore in-place o a un nuevo proyecto).
5. Esperar restauración (~ 5-10 min).

---

## 4. Procedimiento C — Replicación de configuración del servidor

Para levantar un nuevo servidor con la **misma configuración exacta** de producción (por ejemplo: ambiente staging, ambiente de demo para evaluación, ambiente de un nuevo equipo de desarrollo).

### 4.1 Replicación 1:1 vía Render Blueprint

El método más rápido aprovecha que `render.yaml` es portable:

1. **Fork** del repositorio `MaduraApp-Produccion` (opcional, para no compartir credenciales del proyecto original).
2. Crear nuevo servicio en Render → `New → Blueprint`.
3. Conectar el fork → Render detecta `render.yaml`.
4. Configurar `DB_URL` con una nueva BD Supabase (procedimiento §6.2 del [`08_Configuracion_Servidor_Produccion.md`](08_Configuracion_Servidor_Produccion.md)).
5. Deploy.

**Resultado:** stack idéntico en una URL distinta. Útil para mostrar el sistema sin interferir con producción.

### 4.2 Replicación a otro proveedor

Si se quiere migrar a AWS App Runner, Railway, Fly.io u otro:

1. **Tomar el `Dockerfile`** existente — funciona en cualquier PaaS que soporte Docker.
2. **Replicar las variables de entorno** del `render.yaml` en el nuevo proveedor:
   - `ENVIRONMENT=production`
   - `DB_URL=...` (nueva cadena de conexión)
   - `AUTH_SECRET_KEY=...` (generar de nuevo)
   - `YOLO_MODEL_PATH=weights/yolo26n_maduraapp.pt`
   - `CONFIDENCE_THRESHOLD=0.55`
3. **Configurar el health check** apuntando a `/v1/health`.
4. **Verificar TLS** se gestiona automáticamente.
5. Si la BD permanece en Supabase, no requiere cambios adicionales.

### 4.3 Instalación de lenguajes y bibliotecas en un servidor manual (bare metal / VPS)

Si se prescinde de PaaS y se levanta en un VPS Ubuntu:

```bash
# 1. Sistema operativo base
sudo apt update && sudo apt upgrade -y

# 2. Python 3.12 + venv
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# 3. Librerías de sistema requeridas por PIL/torch
sudo apt install -y libgl1 libglib2.0-0 build-essential

# 4. Cliente PostgreSQL
sudo apt install -y postgresql-client-16

# 5. nginx como reverse proxy
sudo apt install -y nginx
# Configurar /etc/nginx/sites-available/maduraapp con proxy_pass http://localhost:8000

# 6. Let's Encrypt para TLS
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d maduraapp.example.com

# 7. systemd unit para uvicorn
sudo nano /etc/systemd/system/maduraapp.service
# Ver §4.4

# 8. Clonar y configurar el repo
cd /opt
sudo git clone https://github.com/apotheosisss/MaduraApp-Produccion.git
cd MaduraApp-Produccion/Producto/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 9. Configurar .env y aplicar migraciones
sudo nano .env  # Editar con credenciales prod
alembic upgrade head

# 10. Iniciar el servicio
sudo systemctl enable --now maduraapp
sudo systemctl status maduraapp
```

### 4.4 Unidad systemd `/etc/systemd/system/maduraapp.service`

```ini
[Unit]
Description=MaduraApp FastAPI backend
After=network.target

[Service]
Type=simple
User=maduraapp
WorkingDirectory=/opt/MaduraApp-Produccion/Producto/backend
EnvironmentFile=/opt/MaduraApp-Produccion/Producto/backend/.env
ExecStart=/opt/MaduraApp-Produccion/Producto/backend/.venv/bin/uvicorn \
          app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 5. Verificación de la integridad de los backups

### 5.1 Test 1 — Verificar que el dump no esté corrupto

```bash
gunzip -t dumps/backup_prod_2026-05-26_2130.sql.gz
# Exit 0 = OK; cualquier otra cosa = corrupto
```

### 5.2 Test 2 — Restaurar en BD efímera y validar conteo

```bash
# Crear BD temporal
docker run --rm -d --name pg_test \
  -e POSTGRES_PASSWORD=test \
  -p 5433:5432 \
  postgres:16

# Esperar arranque
sleep 5

# Restaurar
gunzip -c dumps/backup_prod_2026-05-26_2130.sql.gz | \
  psql -h localhost -p 5433 -U postgres -d postgres

# Verificar conteo vs original
psql -h localhost -p 5433 -U postgres -d postgres \
  -c "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM scans;"

# Limpiar
docker stop pg_test
```

### 5.3 Test 3 — Restaurar y arrancar el backend contra la copia

Tras restaurar, levantar el backend apuntando a la BD restaurada y ejecutar:

```bash
curl http://localhost:8000/v1/history?limit=5 \
  -H "Authorization: Bearer test-token"
```

Si retorna los registros con el mismo formato que producción, el backup está íntegro y la app es capaz de operar contra él.

---

## 6. Política de retención

| Tipo de backup | Retención | Lugar de almacenamiento |
|----------------|-----------|------------------------|
| Backups manuales locales | 30 días con rotación | `./dumps/` en máquina del responsable |
| Backups pre-deploy | 90 días | Repo privado de backups (cifrado) |
| Autobackup Supabase | 7 días (tier free) | Gestionado por Supabase |
| Snapshots evaluación académica | Permanente | Repo privado, cifrado, vinculado al RUT del responsable |

### 6.1 Almacenamiento cifrado

Para dumps que abandonan la máquina local:

```bash
# Cifrar con gpg simétrico
gpg --symmetric --cipher-algo AES256 dumps/backup_prod_2026-05-26_2130.sql.gz
# Genera: dumps/backup_prod_2026-05-26_2130.sql.gz.gpg

# Descifrar
gpg --decrypt backup_prod_2026-05-26_2130.sql.gz.gpg > restored.sql.gz
```

La contraseña se gestiona en un gestor de contraseñas (1Password / Bitwarden), nunca en el repo.

---

## 7. Tabla resumen de procedimientos

| Necesidad | Procedimiento | Documento |
|-----------|---------------|-----------|
| Backup diario de producción | `scripts/backup_prod.sh` | §2.3 |
| Restaurar en ambiente de pruebas (Postgres) | `psql` + dump | §3.1 |
| Restaurar en SQLite | script seed | §3.2 |
| Recuperación catastrófica | Supabase autobackup | §3.3 |
| Replicar servidor en Render | Blueprint apply | §4.1 |
| Replicar servidor en VPS | `apt install` + systemd | §4.3 |
| Verificar integridad de backup | gunzip -t + restore test | §5 |

---

## 8. Lecciones aprendidas y mejores prácticas

- **Nunca hacer `pg_dump --clean`** contra producción sin antes hacer un backup propio.
- **Las credenciales** (`DB_URL_PROD`) viven en gestor de contraseñas y se cargan como env var al ejecutar el script — nunca en el repo, jamás en el historial de shell.
- **Verificar** los backups periódicamente (Schrödinger's backup: si no lo restauraste alguna vez, no sabes si funciona).
- **Documentar la versión** del `pg_dump` usado — el dump debe restaurarse con una versión igual o mayor.
- **Probar el restore en CI** (no aplicado en este proyecto, pero recomendado para producción real).
