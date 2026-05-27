# Configuración del Ambiente de Pruebas — MaduraApp

> Documento que describe **paso a paso** cómo levantar localmente un ambiente de pruebas funcional para MaduraApp, garantizando paridad con el ambiente de producción y permitiendo ejecutar la suite completa de pruebas operacionales, de validación y de verificación.
>
> Este documento responde al indicador **IL2.2** y al criterio 2 de la rúbrica del encargo.

---

## 1. Especificaciones del diseño

### 1.1 Objetivo del ambiente de pruebas

El ambiente de pruebas debe:

1. **Replicar el comportamiento funcional** del ambiente de producción (mismos endpoints, mismas reglas de validación, mismo modelo).
2. **Ser reproducible** desde cero por cualquier integrante del equipo en menos de 30 minutos.
3. **No requerir conexión a Internet** para correr (excepto para la descarga inicial de dependencias).
4. **Ejecutar la misma suite de tests** que el CI de GitHub Actions, con resultados idénticos.
5. **Permitir debug interactivo** (breakpoints, hot reload) que no es posible en producción.

### 1.2 Matriz de paridad ambiente prueba / producción

| Aspecto | Producción | Pruebas | ¿Paridad? |
|---------|-----------|---------|-----------|
| Versión Python | 3.12 | 3.12 | ✅ Sí |
| Framework web | FastAPI 0.135 + Uvicorn | FastAPI 0.135 + Uvicorn (`--reload`) | ✅ Sí |
| Versión PyTorch | 2.x CPU | 2.x CPU | ✅ Sí |
| Modelo ML | `yolo26n_maduraapp.pt` (5.2 MB) | Mismo archivo | ✅ Sí |
| ORM | SQLAlchemy async 2.0 | SQLAlchemy async 2.0 | ✅ Sí |
| Driver BD | asyncpg (PostgreSQL) | aiosqlite (SQLite) | ⚠️ Driver diferente, **mismo dialecto SQL** vía SQLAlchemy |
| Esquema BD | Tabla `scans` (Alembic 0001) | Misma migración | ✅ Sí |
| Variable `ENVIRONMENT` | `production` | `development` | ⚠️ Controlado (gatilla warmup en dev) |
| Warmup del modelo | OFF (ahorra RAM) | ON (más rápido tras inicio) | ⚠️ Controlado |
| TLS / HTTPS | Sí (Let's Encrypt) | No (HTTP local) | ⚠️ Configurado en cliente |
| Pruebas pytest | Mismas | Mismas | ✅ Sí |
| Pruebas Android JVM | Mismas | Mismas | ✅ Sí |
| `CONFIDENCE_THRESHOLD` | 0.55 (env var) | 0.55 (config.py default) | ✅ Sí |

**Diferencias justificadas:** la única divergencia real es el driver de BD (asyncpg vs aiosqlite). Esto no afecta la lógica de negocio porque SQLAlchemy abstrae completamente el dialecto. Si se requiere paridad absoluta, se puede correr PostgreSQL local con Docker (documentado más abajo).

---

## 2. Requisitos previos del entorno host

### 2.1 Hardware mínimo

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| RAM | 4 GB libres | 8 GB libres |
| Disco | 5 GB libres | 15 GB libres (con Android emulator) |
| CPU | 4 núcleos x86_64 / ARM | 8 núcleos |
| Conexión a Internet | Para instalar dependencias (≥ 5 Mbps recomendado) | — |

### 2.2 Software de base

| Software | Versión | Verificación |
|----------|---------|--------------|
| Sistema operativo | Windows 10/11, macOS 12+, o Linux con kernel 5+ | — |
| Python | **3.12.x** | `python --version` |
| Git | 2.30+ | `git --version` |
| Java | 17 (LTS) | `java -version` |
| Android Studio | Hedgehog (2023.1) o posterior | Apertura sin errores |
| Docker (opcional) | 24+ | `docker --version` |

### 2.3 Cuentas necesarias

- **GitHub** — acceso al repositorio `MaduraApp-Produccion` (público, no requiere credenciales adicionales).
- *(Opcional)* **Render** — si se quiere desplegar a Render desde la cuenta personal.
- *(Opcional)* **Supabase** — si se quiere probar contra PostgreSQL real.

---

## 3. Instalación de herramientas (paso a paso)

### 3.1 Python 3.12

#### Windows (PowerShell)
```powershell
# Instalar desde python.org o vía Microsoft Store
# Verificar
python --version
# Salida esperada: Python 3.12.x
```

#### macOS
```bash
brew install python@3.12
python3.12 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
python3.12 --version
```

### 3.2 Git

#### Windows
Descargar de [git-scm.com](https://git-scm.com/download/win) e instalar con configuración por defecto.

#### macOS
```bash
brew install git
```

#### Linux
```bash
sudo apt install git
```

### 3.3 Java 17 + Android Studio

1. Descargar Android Studio desde [developer.android.com](https://developer.android.com/studio).
2. Ejecutar el instalador con configuración por defecto.
3. Al primer arranque, instalar el JDK embebido (17) y el SDK Android API 34.
4. Verificar: `Android Studio → Settings → Build, Execution → Build Tools → Gradle → Gradle JDK = 17`.

### 3.4 Docker (opcional — para containerización)

#### Windows / macOS
Instalar Docker Desktop desde [docker.com](https://www.docker.com/products/docker-desktop).

#### Linux
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Logout / login para aplicar el grupo
```

---

## 4. Clonar el repositorio

```bash
cd ~/Documents/Proyectos  # o tu carpeta preferida
git clone https://github.com/apotheosisss/MaduraApp-Produccion.git
cd MaduraApp-Produccion
```

Estructura post-clone:

```
MaduraApp-Produccion/
├── Documentación/
├── Gestión/
├── Producto/
│   ├── backend/
│   ├── frontend/
│   └── ...
└── render.yaml
```

---

## 5. Levantar el backend localmente

### 5.1 Crear entorno virtual e instalar dependencias

```bash
cd Producto/backend
python -m venv .venv

# Activar venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

**Tiempo esperado:** 3-8 minutos (incluye descarga de PyTorch ~ 200 MB).

### 5.2 Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env`:

```dotenv
API_PORT=8000
YOLO_MODEL_PATH=weights/yolo26n_maduraapp.pt
CONFIDENCE_THRESHOLD=0.55
DB_URL=sqlite+aiosqlite:///./maduraapp_dev.db
AUTH_SECRET_KEY=dev_secret_key
ENVIRONMENT=development
```

### 5.3 Verificar que el modelo está presente

```bash
ls weights/
# Debe mostrar: yolo26n_maduraapp.pt
```

Si no está (ej. clone fresco sin LFS), descargarlo del último commit:

```bash
git checkout HEAD -- weights/yolo26n_maduraapp.pt
```

### 5.4 Ejecutar migraciones Alembic

```bash
alembic upgrade head
# Salida esperada: INFO ... Running upgrade ... 0001_create_scans_table
```

### 5.5 Levantar Uvicorn

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Salida esperada:

```
INFO:     Will watch for changes in these directories: ['.../backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Loading YOLO model from weights/yolo26n_maduraapp.pt
INFO:     Model loaded successfully (warmup completed)
INFO:     Application startup complete.
```

### 5.6 Verificación operacional del backend

```bash
# Health check (debe retornar status ok y modelo cargado)
curl http://localhost:8000/v1/health
# Expected: {"status":"ok","model_loaded":true}

# Documentación Swagger interactiva
# Abrir en navegador: http://localhost:8000/docs

# Probar predicción con imagen de muestra
curl -X POST -F "file=@./tests/fixtures/sample_aguacate.jpg" -F "fruit_type=aguacate_hass" \
     http://localhost:8000/v1/predict
```

---

## 6. Configurar y levantar el cliente Android

### 6.1 Abrir el proyecto en Android Studio

1. `File → Open` → seleccionar `MaduraApp-Produccion/Producto/frontend/`.
2. Esperar la sincronización de Gradle (5-10 min la primera vez).
3. Si pide actualizar Gradle/Android Gradle Plugin, aceptar.

### 6.2 Configurar la URL del backend

Editar `Producto/frontend/gradle.properties`:

```properties
# Para emulador AVD apuntando al backend en host
API_BASE_URL=http://10.0.2.2:8000/

# Para dispositivo físico en la misma red WiFi
# API_BASE_URL=http://192.168.1.XXX:8000/

# Para apuntar a Render (producción)
# API_BASE_URL=https://maduraapp-backend.onrender.com/
```

**Nota:** `10.0.2.2` es la dirección especial del emulador Android para acceder al `localhost` del host.

Sincronizar Gradle tras editar (`File → Sync Project with Gradle Files`).

### 6.3 Levantar emulador o conectar dispositivo

#### Emulador
1. `Tools → Device Manager → Create Device`.
2. Elegir un perfil (ej. Pixel 6).
3. Seleccionar System Image API 29+ (recomendado API 34).
4. Lanzar el AVD.

#### Dispositivo físico
1. Activar **Opciones de desarrollador** + **Depuración USB**.
2. Conectar por USB.
3. Aceptar el prompt de autorización en el dispositivo.

### 6.4 Compilar y ejecutar la app

```
Run → Run 'app' (Shift+F10)
```

La app instala en el dispositivo y arranca en `FruitSelectorActivity`.

---

## 7. Pruebas operacionales del ambiente

### 7.1 Test 1 — Verificar instalación de Python y dependencias

```bash
cd Producto/backend
source .venv/bin/activate  # (o equivalente Windows)
python -c "import fastapi, sqlalchemy, ultralytics; print('OK')"
# Salida esperada: OK
```

### 7.2 Test 2 — Verificar conexión a la BD local

```bash
python -c "from app.core.database import engine; import asyncio; \
asyncio.run(engine.connect().__aenter__())"
# Sin salida = éxito; cualquier error indica problema
```

### 7.3 Test 3 — Ejecutar la suite de tests automatizada

```bash
pytest tests/ -v
```

Salida esperada:

```
tests/test_history.py::test_history_empty PASSED
tests/test_history.py::test_history_after_save PASSED
tests/test_history.py::test_history_pagination PASSED
tests/test_history.py::test_history_no_token PASSED
tests/test_predict.py::test_predict_invalid_content_type PASSED
tests/test_predict.py::test_predict_no_file PASSED
tests/test_predict.py::test_predict_invalid_fruit_type PASSED
tests/test_predict.py::test_predict_with_fruit_filter PASSED
tests/test_predict.py::test_predict_no_detection PASSED

=========================== 9 passed in 12.34s ===========================
```

### 7.4 Test 4 — Smoke test E2E manual

| # | Acción | Resultado esperado |
|---|--------|-------------------|
| 1 | Backend corriendo, app instalada en emulador | App muestra selector de fruta |
| 2 | Tap card "Aguacate Hass" | Navega a MainActivity, título "Escaneando Aguacate Hass" |
| 3 | Conceder permiso de cámara | Preview de cámara visible |
| 4 | Apuntar a una imagen de aguacate (papel/pantalla) | Botón "Escanear" disponible |
| 5 | Tap "Escanear" | Loading → resultado con semáforo y recomendación |
| 6 | Tap menu overflow → Historial | Lista del escaneo recién hecho |
| 7 | Pull-to-refresh en historial | Refresca desde backend |
| 8 | Cerrar app, abrir sin red | Historial sigue visible (cache Room) |

---

## 8. Variante: levantar con Docker Compose

Para máxima paridad con producción (Docker Linux), ejecutar:

```bash
cd Producto/
docker-compose up --build
```

Esto levanta:
- Backend FastAPI en `localhost:8000`.
- PostgreSQL 16 local en `localhost:5432`.
- BD pre-migrada con el esquema actual.

Útil para probar el flujo Docker antes de pushear a Render.

---

## 9. Solución de problemas frecuentes

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| `ModuleNotFoundError: ultralytics` | Venv no activado o requirements no instalados | `source .venv/bin/activate && pip install -r requirements.txt` |
| `cannot find model file` al arrancar | Falta `weights/yolo26n_maduraapp.pt` | Verificar con `ls weights/`; si falta, `git checkout HEAD -- weights/` |
| Android emulator no llega a backend | `API_BASE_URL` incorrecto | Usar `http://10.0.2.2:8000/` en emulador, no `localhost` |
| `SocketTimeoutException` desde la app | Backend en cold start o caído | `curl http://localhost:8000/v1/health` para validar |
| `MaximumRecursionDepth` durante carga del modelo | `torch` y `ultralytics` mal instalados | Reinstalar con `pip install --force-reinstall ultralytics` |
| Tests fallan localmente pero pasan en CI | Caché pytest stale | `rm -rf .pytest_cache __pycache__ && pytest` |

---

## 10. Buenas prácticas adicionales

- **Nunca pushear `.env`** — ya está en `.gitignore`.
- **Nunca commitear `maduraapp_dev.db`** — está en `.gitignore`.
- **Sí commitear** cambios en `weights/yolo26n_maduraapp.pt` cuando se re-entrene el modelo (versionado de modelo).
- Antes de cada PR a `main`, ejecutar localmente `pytest tests/ -v` y `./gradlew test` (Android).
- Mantener `.venv/` fuera del repo (en `.gitignore`).

---

## 11. Resumen — checklist de levantamiento

Para considerar el ambiente de pruebas correctamente configurado:

- [ ] Python 3.12 instalado y en PATH.
- [ ] Repositorio clonado en local.
- [ ] Venv creado y activado.
- [ ] `pip install -r requirements.txt` exitoso.
- [ ] `.env` copiado desde `.env.example` y editado.
- [ ] `alembic upgrade head` exitoso.
- [ ] `uvicorn app.main:app --reload` arranca sin errores.
- [ ] `curl localhost:8000/v1/health` retorna `{"status":"ok","model_loaded":true}`.
- [ ] `pytest tests/ -v` retorna 9/9 passing.
- [ ] Android Studio abre el proyecto sin errores de Gradle.
- [ ] `API_BASE_URL` configurada acorde al destino (emulador / dispositivo / Render).
- [ ] App compila y arranca en emulador / dispositivo.
- [ ] Smoke test E2E manual pasa los 8 pasos del §7.4.
