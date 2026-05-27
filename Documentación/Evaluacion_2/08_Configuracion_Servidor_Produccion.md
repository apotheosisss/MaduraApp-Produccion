# Configuración del Servidor de Producción — MaduraApp

> Documento que describe la **infraestructura cloud de producción** de MaduraApp, incluyendo el procedimiento para desplegar desde cero, las variables de entorno, la base de datos gestionada y la estrategia de despliegue continuo.
>
> Este documento responde al indicador **IL2.2** y al criterio 3 de la rúbrica del encargo (gestión de servidor de producción).

---

## 1. Visión general

MaduraApp se despliega como un servicio web containerizado en **Render** (plataforma PaaS), conectándose a una base de datos PostgreSQL gestionada en **Supabase**. La configuración se gestiona como código (IaC) mediante el archivo `render.yaml` versionado en el repositorio, asegurando reproducibilidad total.

```mermaid
graph LR
    GH[GitHub<br/>MaduraApp-Produccion] -->|push main| RD[Render Web Service<br/>Docker Linux Oregon]
    RD -->|asyncpg TLS| SB[(Supabase<br/>PostgreSQL 16)]
    RD -->|model file in image| MOD[weights/<br/>yolo26n_maduraapp.pt]
    KA[GitHub Actions<br/>keepalive cron] -->|HTTPS /v1/health| RD
```

---

## 2. Plataforma de hosting: Render

### 2.1 Justificación de la elección

| Criterio | Render | Heroku | AWS App Runner | Railway |
|----------|--------|--------|----------------|---------|
| Free tier funcional | ✅ Sí (512 MB) | ❌ Eliminado 2022 | ❌ Requiere card | ⚠️ Trial limitado |
| Docker nativo | ✅ Sí | ⚠️ Buildpacks | ✅ Sí | ✅ Sí |
| Auto-deploy Git | ✅ Sí | ✅ Sí | ✅ Sí | ✅ Sí |
| TLS auto | ✅ Let's Encrypt | ✅ Sí | ✅ Sí | ✅ Sí |
| Blueprint as code | ✅ `render.yaml` | ✅ `app.json` | ⚠️ CDK/CFN | ⚠️ Limited |
| Costo plan upgrade | $7-25/mo | $7+/mo | Pay-as-go | $5+/mo |

**Conclusión:** Render ofrece el mejor balance para un proyecto académico con presupuesto cero, manteniendo opcionalidad de upgrade si el proyecto crece post-asignatura.

### 2.2 Plan seleccionado

| Parámetro | Valor |
|-----------|-------|
| Plan | `free` |
| Región | Oregon (US-West) |
| RAM | 512 MB |
| CPU | 0.1 vCPU compartido |
| Sleep policy | Suspende tras 15 min sin tráfico |
| Cold start | ~ 30-60 s tras suspensión |
| Cuota mensual | 750 horas (suficiente para 24/7 si se mitiga sleep) |
| TLS | Incluido (Let's Encrypt auto-renovado) |
| Dominio | `*.onrender.com` (placeholder personalizable a custom domain) |

---

## 3. El archivo `render.yaml` (Blueprint)

Ubicación: **raíz** del repositorio `MaduraApp-Produccion`.

```yaml
# Render Blueprint — MaduraApp
# Documentacion: https://render.com/docs/blueprint-spec

services:
  - type: web
    name: maduraapp-backend
    env: docker
    dockerfilePath: ./Producto/backend/Dockerfile
    dockerContext: ./Producto/backend
    plan: free
    region: oregon
    branch: main
    healthCheckPath: /v1/health

    envVars:
      - key: ENVIRONMENT
        value: production

      - key: DB_URL
        sync: false           # Configurado manualmente en dashboard

      - key: AUTH_SECRET_KEY
        generateValue: true   # Render genera valor seguro

      - key: YOLO_MODEL_PATH
        value: weights/yolo26n_maduraapp.pt

      - key: CONFIDENCE_THRESHOLD
        value: "0.55"
```

### 3.1 Explicación campo por campo

| Campo | Valor | Significado |
|-------|-------|-------------|
| `type` | `web` | Servicio web HTTP (no worker, no static site) |
| `name` | `maduraapp-backend` | Nombre del servicio (define el subdominio asignado) |
| `env` | `docker` | Build via Dockerfile (alternativa: `python` con buildpack) |
| `dockerfilePath` | `./Producto/backend/Dockerfile` | Path relativo al Dockerfile |
| `dockerContext` | `./Producto/backend` | Carpeta base para `COPY` instrucciones |
| `plan` | `free` | Tier gratuito |
| `region` | `oregon` | Región AWS US-West-2 (menor latencia para Chile que us-east) |
| `branch` | `main` | Rama monitoreada para auto-deploy |
| `healthCheckPath` | `/v1/health` | Endpoint de liveness; Render reinicia si falla 3 veces seguidas |
| `sync: false` | (en DB_URL) | No sincronizar el valor — se carga manual desde dashboard (sensible) |
| `generateValue: true` | (en AUTH_SECRET_KEY) | Render genera valor aleatorio seguro al primer deploy |

---

## 4. Variables de entorno detalladas

| Variable | Tipo | Valor | Origen / Manejo |
|----------|------|-------|-----------------|
| `ENVIRONMENT` | string | `production` | Hardcoded en blueprint (no sensible) |
| `DB_URL` | secret | `postgresql+asyncpg://user:pass@host:5432/postgres` | Manual en Render Dashboard — viene de Supabase |
| `AUTH_SECRET_KEY` | secret | Auto-generado por Render | Generado al primer deploy; visible solo al usuario admin |
| `YOLO_MODEL_PATH` | string | `weights/yolo26n_maduraapp.pt` | Hardcoded (relativo al workdir del contenedor) |
| `CONFIDENCE_THRESHOLD` | string | `"0.55"` | Hardcoded; convertido a float por Pydantic |

**Importante:** `DB_URL` debe llevar el prefijo `postgresql+asyncpg://` (no `postgresql://`) para que SQLAlchemy use el driver asíncrono. Es la causa más común de fallos en el primer deploy.

---

## 5. El `Dockerfile` del backend

Ubicación: `Producto/backend/Dockerfile`.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema (libgl para PIL/opencv)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Capa de dependencias (caché eficiente)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código de la app
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY weights/ ./weights/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.1 Decisiones del Dockerfile

- **Base slim** (no `alpine`) — `alpine` rompe wheels compilados de PyTorch/numpy.
- **Capa de dependencias separada** del código — caché efectivo cuando solo cambia código (no requirements).
- **`weights/` se copia en la imagen** — el modelo viaja con el deploy. Trade-off: imagen más grande (~ 800 MB) pero deploy atómico sin descargas externas en runtime.
- **`--no-cache-dir`** en pip — reduce tamaño de imagen.

---

## 6. Procedimiento de despliegue desde cero

### 6.1 Pre-requisitos

- Cuenta gratuita en [render.com](https://render.com).
- Cuenta gratuita en [supabase.com](https://supabase.com).
- Acceso de admin al repositorio GitHub `MaduraApp-Produccion`.

### 6.2 Paso 1 — Crear la base de datos en Supabase

1. Login en Supabase → `New Project`.
2. Llenar:
   - **Name:** `maduraapp-prod`
   - **Database Password:** (generar y guardar en gestor de contraseñas — irreversible).
   - **Region:** la más cercana (ej. `South America (São Paulo)`).
   - **Pricing Plan:** Free.
3. Esperar provisioning (~ 2 min).
4. Ir a **Project Settings → Database → Connection string → URI (Session pooler)**.
5. Copiar la cadena tipo:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-sa-east-1.pooler.supabase.com:5432/postgres
   ```
6. **Cambiar el prefijo a `postgresql+asyncpg://`** para que funcione con SQLAlchemy async.
7. Guardar esta cadena — se usará en el paso 4.

### 6.3 Paso 2 — Aplicar migraciones a Supabase

Antes del primer deploy, aplicar las migraciones para crear la tabla `scans`:

```bash
cd Producto/backend
source .venv/bin/activate

# Configurar la cadena de producción temporalmente
export DB_URL="postgresql+asyncpg://postgres.xxxxx:PASS@host:5432/postgres"

# Aplicar migraciones
alembic upgrade head

# Verificar
psql "$DB_URL" -c "\dt"
# Debe mostrar tabla 'scans'
```

### 6.4 Paso 3 — Conectar el repo en Render

1. Login en Render → `New → Blueprint`.
2. Connect GitHub → autorizar acceso al repo `MaduraApp-Produccion`.
3. Render detecta automáticamente `render.yaml` en la raíz.
4. Review: confirmar que detecta el servicio `maduraapp-backend`.
5. Click `Apply`.

### 6.5 Paso 4 — Configurar la variable secreta `DB_URL`

1. En Render Dashboard → servicio `maduraapp-backend` → `Environment`.
2. Variable `DB_URL` aparece como **needs to be set**.
3. Pegar la cadena de Supabase del paso 1.6.
4. Save → Render reinicia el deploy automáticamente.

### 6.6 Paso 5 — Verificar el deploy

1. En Dashboard → `Logs` (live stream).
2. Esperar a ver:
   ```
   INFO: Loading YOLO model from weights/yolo26n_maduraapp.pt
   INFO: Model loaded successfully
   INFO: Application startup complete.
   INFO: Uvicorn running on http://0.0.0.0:8000
   ```
3. Acceder a la URL pública (visible en el dashboard, ej. `https://maduraapp-backend.onrender.com`).
4. Probar:
   ```bash
   curl https://maduraapp-backend.onrender.com/v1/health
   # Esperado: {"status":"ok","model_loaded":true}
   ```

### 6.7 Paso 6 — Actualizar la URL en el cliente Android

Editar `Producto/frontend/gradle.properties`:

```properties
API_BASE_URL=https://maduraapp-backend.onrender.com/
```

Sincronizar Gradle, recompilar APK y distribuir.

---

## 7. Despliegue continuo (Continuous Deployment)

### 7.1 Flujo automático

```mermaid
sequenceDiagram
    actor Dev as Desarrollador
    participant Local as Local
    participant GH as GitHub
    participant CI as GitHub Actions
    participant Render as Render

    Dev->>Local: git add ./ git commit
    Dev->>GH: git push origin main
    GH->>CI: trigger backend_ci.yml
    CI->>CI: pip install + pytest
    alt tests passing
        CI-->>GH: ✅ CI verde
        GH->>Render: webhook deploy
        Render->>Render: docker build
        Render->>Render: deploy nueva versión
        Render-->>Dev: notificación (email)
    else tests failing
        CI-->>GH: ❌ CI rojo
        Note over Render: NO se hace deploy
        CI-->>Dev: notificación de fallo
    end
```

### 7.2 Tiempos típicos

| Etapa | Duración |
|-------|----------|
| GitHub Actions CI (pytest) | 2-4 min |
| Render docker build | 4-8 min |
| Render swap atomic | < 30 s |
| **Total push → en vivo** | **~ 7-12 min** |

### 7.3 Rollback

Si un deploy falla en runtime:

1. Render Dashboard → servicio → `Deploys` tab.
2. Encontrar el deploy verde anterior.
3. Click `Rollback to this deploy`.
4. Render restaura la imagen Docker previa (sin necesidad de rebuild).

---

## 8. Mitigación del cold start (Free tier)

Render Free **suspende el contenedor tras 15 minutos sin tráfico**, generando un cold start de ~30-60 s en la siguiente request. Para minimizar el impacto durante horario académico:

### 8.1 Workflow `keepalive.yml`

Ubicación: `.github/workflows/keepalive.yml`.

```yaml
name: Keepalive Render

on:
  schedule:
    - cron: "*/14 * * * *"  # cada 14 minutos
  workflow_dispatch:        # manual trigger

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping backend health endpoint
        run: |
          curl -fSs https://maduraapp-backend.onrender.com/v1/health \
            -H "User-Agent: keepalive-github-actions" \
            --max-time 60 || exit 0
```

**Notas:**
- Cron `*/14` queda dentro del límite de 15 min de Render Free.
- `|| exit 0` evita que un cold start ocasional marque el workflow como rojo.
- No requiere secrets.

---

## 9. Monitoreo en producción

### 9.1 Dashboard de Render

- **Logs:** stream en vivo de stdout/stderr (búsqueda full-text).
- **Metrics:** uso de CPU/RAM, throughput de requests, tiempos de respuesta.
- **Events:** historial de deploys, restarts, scaling events.

### 9.2 Dashboard de Supabase

- **Database health:** conexiones activas, tamaño de la BD.
- **Logs:** queries lentos, errores.
- **Storage:** porcentaje del free tier consumido (500 MB).

### 9.3 Endpoints de health check

```bash
# Liveness (¿está vivo?)
curl https://maduraapp-backend.onrender.com/v1/health
# {"status":"ok","model_loaded":true}

# Readiness (¿puede atender requests?) — implícito en /v1/health
# si retorna model_loaded:false, el servicio está vivo pero no listo
```

---

## 10. Seguridad operacional

| Riesgo | Mitigación implementada |
|--------|-------------------------|
| **Credenciales en repo** | `DB_URL` y `AUTH_SECRET_KEY` solo en Render env, jamás commiteadas |
| **Acceso no autorizado a BD** | Supabase con SSL obligatorio + connection pooler con auth |
| **Modificación no autorizada del deploy** | Solo push a `main` desde miembros con permiso GitHub puede generar deploys |
| **Pérdida de datos por crash** | Supabase tiene backup automático diario (gestionado por proveedor) |
| **Modelo `.pt` siendo extraído** | El modelo es público de todos modos (entrenado con datasets públicos), no hay riesgo de IP leak |

---

## 11. Procedimiento de migración a otro servidor

Si se requiere migrar de Render a otro PaaS:

1. **Adaptar el formato del archivo de blueprint** (ej. AWS App Runner → `apprunner.yaml`, Railway → `railway.json`).
2. **Recrear las variables de entorno** (`DB_URL`, `AUTH_SECRET_KEY`, etc.) en el nuevo proveedor.
3. **Verificar que el nuevo proveedor soporta**:
   - Docker build (todos los principales lo soportan).
   - HTTPS automático.
   - Health check endpoint.
4. **Re-apuntar el DNS** si se usa custom domain.
5. **Actualizar `API_BASE_URL` en el cliente Android** y redistribuir APK.

La portabilidad es alta porque el código no depende de APIs propietarias de Render.

---

## 12. Documentación de referencia

- Render Blueprint Spec: https://render.com/docs/blueprint-spec
- Supabase asyncpg connection: https://supabase.com/docs/guides/database/connecting-to-postgres
- FastAPI deployment: https://fastapi.tiangolo.com/deployment/
- SQLAlchemy 2.0 async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
