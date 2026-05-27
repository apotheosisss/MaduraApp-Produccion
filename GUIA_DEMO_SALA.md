# Guía de Demo en Sala — MaduraApp
## Evaluación 2 · TPY1101

> **Tiempo estimado de setup:** 5 min (si Python ya instalado) — 15 min (primera vez + descargas)

---

## La noche antes — hacer OBLIGATORIAMENTE desde tu PC

### Paso 1 — Cambiar la URL del APK a `localhost`

Editar `Producto/frontend/gradle.properties`:

```properties
# Cambiar esta línea:
maduraapp.api.baseUrl=http://10.0.2.2:8000/

# Por esta:
maduraapp.api.baseUrl=http://localhost:8000/
```

### Paso 2 — Compilar el APK de demo

```bash
cd Producto/frontend
./gradlew assembleDebug
```

El APK queda en:
```
Producto/frontend/app/build/outputs/apk/debug/app-debug.apk
```

### Paso 3 — Instalar en el teléfono

Conectar el teléfono, habilitar **Depuración USB** y ejecutar:

```bash
adb install Producto/frontend/app/build/outputs/apk/debug/app-debug.apk
```

O simplemente copiar el APK al teléfono y abrirlo con "Instalar".

### Paso 4 — Verificar que la app funciona contra tu backend local

Con el backend corriendo en tu PC:
```bash
cd Producto/backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Abrir la app, escanear → debe funcionar.

### Paso 5 — Llevar preparado (en USB o carpeta sincronizada)

- [ ] El repositorio ya clonado (ZIP del repo o clone previo)
- [ ] `platform-tools` de Android (contiene `adb.exe`) — descargar de:
      https://developer.android.com/tools/releases/platform-tools
      → extraer en `C:\platform-tools\`
- [ ] El APK ya instalado en el teléfono

---

## En la sala — día de la evaluación

### 1. Clonar o copiar el repositorio

**Opción A — Git (si la PC tiene internet y Git):**
```bash
git clone https://github.com/apotheosisss/MaduraApp-Produccion.git
cd MaduraApp-Produccion
```

**Opción B — Desde USB:**
Copiar la carpeta `MaduraApp-Produccion` desde el pendrive directamente.

### 2. Arrancar el backend

Hacer doble click en **`DEMO_INICIO.ps1`** (o click derecho → Ejecutar con PowerShell).

El script hace automáticamente:
- Verifica Python
- Crea el entorno virtual
- Instala dependencias (solo la primera vez, ~5-8 min)
- Configura la BD
- Arranca el servidor en `localhost:8000`

**Si Python no está instalado en la PC de la sala:**
→ Ver sección "Plan B" al final de esta guía.

### 3. Verificar que el backend está activo

Abrir en el navegador: http://localhost:8000/v1/health

Debe mostrar: `{"status":"ok","model_loaded":true}`

### 4. Conectar el teléfono por USB

1. Conectar el cable USB al PC de la sala.
2. Si aparece "¿Permitir depuración USB?" en el teléfono → Aceptar.

### 5. Configurar el puente USB (ADB reverse)

**Opción A — Si ADB está disponible en la PC de la sala:**
```bash
adb reverse tcp:8000 tcp:8000
```

**Opción B — Usar el ADB que traes en el USB:**
```bash
C:\platform-tools\adb.exe reverse tcp:8000 tcp:8000
```

**Verificar que el teléfono se detecta:**
```bash
adb devices
# Debe mostrar: [serial]    device
```

### 6. Abrir la app en el teléfono

- Abrir **MaduraApp** (el APK instalado anoche).
- Seleccionar una fruta.
- Escanear → el resultado debe aparecer.

**Si funciona → ¡listo para la demo!**

---

## Flujo de demo recomendado (30 minutos)

| Minuto | Acción |
|--------|--------|
| 0-5 | Contexto: qué es MaduraApp, el problema que resuelve |
| 5-10 | Arquitectura 4+1 — mostrar los documentos clave |
| 10-15 | **Demo en vivo:** escanear aguacate → resultado → historial |
| 15-20 | Demo galería + cambiar fruta |
| 20-25 | Código: mostrar el modelo 4+1 implementado (predict.py, inference_service.py, FruitSelectorActivity) |
| 25-30 | Tests: ejecutar `pytest tests/ -v` en vivo; mostrar 9 passed |
| 30-40 | Preguntas del docente |

### Comandos para ejecutar en vivo durante la demo

```bash
# Mostrar que los tests pasan (abrir otra terminal)
cd Producto/backend
.venv\Scripts\activate
pytest tests/ -v

# Mostrar el health check
curl http://localhost:8000/v1/health

# Mostrar la inferencia directo por curl (sin app)
curl -X POST -F "file=@sample.jpg" -F "fruit_type=aguacate_hass" http://localhost:8000/v1/predict
```

---

## Plan B — Si Python NO está instalado en la PC de la sala

### Opción B1: Instalar Python 3.12 en ~5 minutos

1. Descargar: https://python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe (llevar en USB)
2. Ejecutar instalador → marcar **"Add Python to PATH"** → Install Now.
3. Cerrar y reabrir PowerShell.
4. Ejecutar `DEMO_INICIO.ps1`.

### Opción B2: Docker (si está instalado)

```bash
cd Producto
docker-compose up --build
```

El backend arranca en `localhost:8000`. Mismo ADB reverse del paso 5.

### Opción B3: Demo sin teléfono (última opción)

Si nada funciona, mostrar la demo usando:
- `http://localhost:8000/docs` — Swagger UI en el navegador.
- Subir una imagen de fruta desde la interfaz de Swagger.
- Mostrar el response JSON.
- Ejecutar los tests en vivo.

---

## Checklist pre-demo (hacer en casa la noche antes)

- [ ] `gradle.properties` cambiado a `localhost:8000`
- [ ] APK compilado con `./gradlew assembleDebug`
- [ ] APK instalado en el teléfono y probado
- [ ] Backend local probado (app escanea correctamente)
- [ ] Platform-tools en USB (`adb.exe` disponible)
- [ ] Python 3.12 installer en USB (por si acaso)
- [ ] Repositorio en USB (por si no hay internet en la sala)
- [ ] `pytest tests/ -v` corre y muestra 9 passed
- [ ] Documentos de la Evaluación 2 abiertos para mostrar

---

## Solución de problemas rápida

| Síntoma | Solución |
|---------|----------|
| `DEMO_INICIO.ps1` no se ejecuta | Click derecho → Propiedades → Desbloquear; o ejecutar `Set-ExecutionPolicy Bypass -Scope Process` |
| App dice "Error de conexión" | Verificar que `adb reverse tcp:8000 tcp:8000` estuvo ejecutado Y que el backend muestra `model_loaded:true` |
| `adb: device not found` | Conectar USB, aceptar el prompt del teléfono, esperar 5 seg, reintentar |
| Backend no arranca (falta modelo) | El archivo `.pt` debe estar en `Producto/backend/weights/`. Si falta, copiarlo desde el USB |
| Puerto 8000 ocupado | `netstat -ano \| findstr :8000` → `taskkill /PID <numero> /F` |
| App crashea al abrir | El APK instalado es el de producción (Render URL). Reinstalar el APK compilado con `localhost:8000` |
