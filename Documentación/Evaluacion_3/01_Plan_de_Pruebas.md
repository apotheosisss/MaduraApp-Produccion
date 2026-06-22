# Plan de Pruebas de Software — MaduraApp

> **Estado de Avance 3 — TPY1101 Taller Aplicado de Programación**
> Documento que define el **plan de pruebas** del proyecto MaduraApp alineado a la problemática planteada, identificando las pruebas del desarrollo del producto y representándolas en tablas claras y precisas con la funcionalidad a comprobar y el resultado esperado/obtenido.
>
> Responde al criterio 1 de la dimensión *Encargo* (IL3.1) y al criterio 1 de la dimensión *Presentación*.
>
> **Estudiante:** Claudio Vicente Aro Kath — RUT 22.022.498-8 — Sección 001D
> **Estado de aprobación:** presentado para aprobación del docente guía en la defensa de la Evaluación 3.

---

## 1. Alineación con la problemática

MaduraApp ataca las **pérdidas post-cosecha de frutas climatéricas** (20–40% según FAO/ODEPA) por falta de criterios objetivos de madurez. El producto es un sistema cliente-servidor:

- **App Android** (Kotlin + CameraX + Room + MVVM) que captura/sube imágenes y muestra el diagnóstico.
- **API FastAPI** que ejecuta inferencia YOLO26n, autentica usuarios (JWT) y persiste historial y feedback.
- **Modelo YOLO26n** (mAP@50 = 0.9229) que clasifica 4 frutas en 3 estados de madurez.

Por tanto, el plan de pruebas debe asegurar que **cada componente** (autenticación, inferencia, persistencia, cache offline, capa de presentación) **funciona, es correcto y es seguro**. Las pruebas se clasifican en cuatro tipos:

| Tipo | Pregunta que responde | Foco |
|------|----------------------|------|
| **Validación** | ¿Construimos el sistema correcto? | Cumplimiento de requisitos funcionales (RF) |
| **Verificación** | ¿Lo construimos correctamente? | Atributos de calidad no funcionales (RNF) |
| **Seguridad** | ¿Está protegido? | Autenticación, autorización, datos personales (OWASP) |
| **Operacional** | ¿Funciona en su entorno? | Disponibilidad y operación del sistema |

---

## 2. Ambiente y base de datos de pruebas

El detalle completo está en **[`02_Base_Datos_Pruebas.md`](02_Base_Datos_Pruebas.md)**. En resumen:

- **Backend:** suite `pytest` con **SQLite in-memory** (`sqlite+aiosqlite:///:memory:`) creada y destruida por test-module, aislando cada corrida. Modelo YOLO reemplazado por un `MagicMock` para no depender de pesos en CI. Datos de prueba generados por *fixtures* (`conftest.py`): usuario `testuser`, imágenes JPEG sintéticas, tokens JWT reales.
- **Android:** suite JVM con **mocks** (MockK) de la API y del `LocalScanDataSource` (Room), `kotlinx-coroutines-test` para controlar el dispatcher y Turbine para verificar *flows*.
- **Total de pruebas automatizadas: 36** (17 backend + 19 Android), todas en verde y ejecutadas en cada commit por CI (GitHub Actions).

---

## 3. Tabla maestra del Plan de Pruebas

Formato: **ID · Componente · Funcionalidad a comprobar · Pre-condición · Acción / datos de entrada · Resultado esperado · Resultado obtenido · Estado**.

### 3.1 Pruebas de validación funcional — Autenticación (Backend)

| ID | Componente | Funcionalidad a comprobar | Pre-condición | Acción / datos | Resultado esperado | Resultado obtenido | Estado |
|----|-----------|---------------------------|---------------|----------------|--------------------|--------------------|--------|
| CP-01 | `auth` | Registro rechaza email duplicado | Usuario `dup@maduraapp.cl` ya existe | POST `/v1/auth/register` con mismo email | HTTP 409 "correo ya registrado" | HTTP 409 | ✅ |
| CP-02 | `auth` | Login rechaza contraseña incorrecta | Usuario registrado | POST `/v1/auth/login` con password errónea | HTTP 401 "credenciales incorrectas" | HTTP 401 | ✅ |
| CP-03 | `auth` | Registro exitoso emite JWT | Email libre, password válida | POST `/v1/auth/register` válido | HTTP 201 + `access_token` | HTTP 201 + token | ✅ |

### 3.2 Pruebas de validación funcional — Inferencia (Backend)

| ID | Componente | Funcionalidad a comprobar | Pre-condición | Acción / datos | Resultado esperado | Resultado obtenido | Estado |
|----|-----------|---------------------------|---------------|----------------|--------------------|--------------------|--------|
| CP-04 | `health` | Health check público | Backend arriba | GET `/v1/health` | HTTP 200, `status:ok`, `model_loaded` presente | HTTP 200 | ✅ |
| CP-05 | `predict` | Predicción exitosa con fruta detectada | Token válido, modelo mock | POST `/v1/predict` (JPEG + JWT) | HTTP 200, `success:true`, `scan_id` no nulo, `color_code` | HTTP 200 + scan_id | ✅ |
| CP-06 | `predict` | Predicción con filtro de fruta | Token válido | POST `/v1/predict` con `fruit_type=mango` | HTTP 200, `success:true` | HTTP 200 | ✅ |
| CP-07 | `predict` | Imagen sin fruta detectable | Token válido | POST `/v1/predict` (mock sin detección) | HTTP 200, `success:false`, campo `error` | HTTP 200, success:false | ✅ |
| CP-08 | `predict` | Formato de imagen no soportado | Token válido | POST `/v1/predict` con archivo `.gif` | HTTP 400 "no soportado" | HTTP 400 | ✅ |
| CP-09 | `predict` | Tipo de fruta inválido | Token válido | POST `/v1/predict` con `fruit_type=manzana` | HTTP 400 | HTTP 400 | ✅ |

### 3.3 Pruebas de validación funcional — Historial y Feedback (Backend)

| ID | Componente | Funcionalidad a comprobar | Pre-condición | Acción / datos | Resultado esperado | Resultado obtenido | Estado |
|----|-----------|---------------------------|---------------|----------------|--------------------|--------------------|--------|
| CP-10 | `history` | Historial vacío para usuario nuevo | Token de usuario sin escaneos | GET `/v1/history` | HTTP 200, lista vacía | HTTP 200, `[]` | ✅ |
| CP-11 | `history` | Historial refleja escaneo previo | Tras un predict exitoso | GET `/v1/history` | HTTP 200, contiene el registro | HTTP 200 con registro | ✅ |
| CP-12 | `history` | Paginación por limit/offset | Token válido | GET `/v1/history?limit=5&offset=0` | HTTP 200, `limit=5`, ≤5 ítems | HTTP 200 paginado | ✅ |
| CP-13 | `history` | Validación de límite máximo | Token válido | GET `/v1/history?limit=200` | HTTP 422 (excede máximo) | HTTP 422 | ✅ |
| CP-14 | `feedback` | Registrar calificación 1–5 | Token + scan_id válido | POST `/v1/feedback` (rating 4) | HTTP 201 | HTTP 201 | ✅ |
| CP-15 | `feedback` | Rechazar rating fuera de rango | Token válido | POST `/v1/feedback` (rating inválido) | HTTP 422 | HTTP 422 | ✅ |

### 3.4 Pruebas de seguridad (Backend — OWASP)

| ID | Componente | Funcionalidad a comprobar | Pre-condición | Acción / datos | Resultado esperado | Resultado obtenido | Estado |
|----|-----------|---------------------------|---------------|----------------|--------------------|--------------------|--------|
| CP-16 | `predict` | Endpoint protegido exige JWT (A01) | Sin cabecera Authorization | POST `/v1/predict` sin token | HTTP 401 | HTTP 401 | ✅ |
| CP-17 | `history` | Endpoint protegido exige JWT (A01) | Sin cabecera Authorization | GET `/v1/history` sin token | HTTP 401 | HTTP 401 | ✅ |
| CP-18 | `auth` | Política de contraseña robusta (A07) | — | POST `/v1/auth/register` con `ab1` (corta) y `onlyletters` (sin número) | HTTP 422 en ambos | HTTP 422 | ✅ |

### 3.5 Pruebas de validación funcional — App Android (capa de datos)

| ID | Componente | Funcionalidad a comprobar | Pre-condición | Acción / datos | Resultado esperado | Resultado obtenido | Estado |
|----|-----------|---------------------------|---------------|----------------|--------------------|--------------------|--------|
| CP-19 | `FruitRepository` | Cachea resultado cuando hay detección | API mock con detección | `repository.predict(bytes)` | Cachea en Room, `Result.success` | Cacheado | ✅ |
| CP-20 | `FruitRepository` | NO cachea cuando no hay detección | API mock sin detección | `repository.predict(bytes)` | No invoca cache | No cacheado | ✅ |
| CP-21 | `FruitRepository` | Propaga excepción de red como failure | API mock lanza excepción | `repository.predict(bytes)` | `Result.failure`, sin cache | Failure | ✅ |
| CP-22 | `FruitRepository` | Refresh reemplaza cache (offset 0) | API mock con historial | `refreshHistory(offset=0)` | Limpia y recachea | Recacheado | ✅ |
| CP-23 | `FruitRepository` | Refresh con offset>0 no limpia cache | API mock | `refreshHistory(offset=50)` | No limpia cache | Sin limpiar | ✅ |
| CP-24 | `FruitRepository` | Refresh fallido no toca cache | API mock lanza excepción | `refreshHistory()` | `Result.failure`, cache intacto | Failure | ✅ |
| CP-25 | `FruitRepository` | Observa historial local (offline) | Cache con datos | `observeLocalHistory()` | Emite ítems cacheados | Emite datos | ✅ |
| CP-26 | `FruitRepository` | Health: backend sano | API mock `status:ok` | `isBackendHealthy()` | `true` | `true` | ✅ |
| CP-27 | `FruitRepository` | Health: backend caído | API mock excepción | `isBackendHealthy()` | `false` | `false` | ✅ |

### 3.6 Pruebas de validación funcional — App Android (capa de presentación)

| ID | Componente | Funcionalidad a comprobar | Pre-condición | Acción / datos | Resultado esperado | Resultado obtenido | Estado |
|----|-----------|---------------------------|---------------|----------------|--------------------|--------------------|--------|
| CP-28 | `ScanViewModel` | Estado inicial es Idle | ViewModel recién creado | Leer `state` | `ScanState.Idle` | Idle | ✅ |
| CP-29 | `ScanViewModel` | Detección → estado Success | Repo mock con detección | `submitImage(bytes)` | `ScanState.Success` | Success | ✅ |
| CP-30 | `ScanViewModel` | Sin detección → NoDetection | Repo mock sin detección | `submitImage(bytes)` | `ScanState.NoDetection` | NoDetection | ✅ |
| CP-31 | `ScanViewModel` | success:false sin mensaje → fallback | Repo mock | `submitImage(bytes)` | Mensaje de error por defecto | Fallback usado | ✅ |
| CP-32 | `ScanViewModel` | Fallo del repo → Error | Repo mock falla | `submitImage(bytes)` | `ScanState.Error` | Error | ✅ |
| CP-33 | `ScanViewModel` | Reset vuelve a Idle | Estado distinto de Idle | `reset()` | `ScanState.Idle` | Idle | ✅ |
| CP-34 | `HistoryViewModel` | Init dispara refresh → Loaded | Repo mock OK | crear ViewModel | termina en `Loaded` | Loaded | ✅ |
| CP-35 | `HistoryViewModel` | Refresh fallido → Error con cache | Repo mock falla | refresh | `Error` con ítems locales | Error+cache | ✅ |
| CP-36 | `HistoryViewModel` | cachedItems refleja el stream local | Repo mock con flujo | observar `cachedItems` | Emite los ítems del cache | Refleja stream | ✅ |
| CP-37 | `HistoryViewModel` | Refresh manual pasa por Loading | ViewModel inicializado | `refresh()` | `Loading` antes del resultado | Loading | ✅ |

> **Nota:** CP-01…CP-37 corresponden a las **36 pruebas automatizadas** reales (CP-18 agrupa dos aserciones de contraseña débil). Todas se ejecutan con `pytest tests/ -v` y `gradlew testDebugUnitTest` y están en verde.

### 3.7 Pruebas de verificación (atributos de calidad)

| ID | Atributo | Funcionalidad a comprobar | KPI | Resultado obtenido | Estado |
|----|----------|---------------------------|-----|--------------------|--------|
| VER-01 | Precisión (modelo) | mAP@50 del modelo en test set | ≥ 0.75 | **0.9229** | ✅ |
| VER-02 | Cobertura (modelo) | Recall por clase | ≥ 0.65 | > 0.80 todas | ✅ |
| VER-03 | Eficiencia | Tamaño del modelo en disco | < 10 MB | 5.2 MB | ✅ |
| VER-04 | Performance | Latencia de inferencia (CPU local) | < 400 ms p95 | ~160–300 ms | ✅ |
| VER-05 | Mantenibilidad | CI ejecuta la suite backend en cada push | suite verde | ✅ workflow `backend_ci.yml` configurado | ✅ |
| VER-06 | Seguridad | Sin secretos hardcodeados en repo | 0 hallazgos | ✅ (JWT por entorno) | ✅ |

### 3.8 Pruebas operacionales

> El backend **aún no está desplegado** en el AWS Laboratory del docente (pendiente). Las pruebas operacionales se documentan contra el **entorno local** usado en la demo (uvicorn + `adb reverse` / túnel cloudflared). Se replicarán contra la URL de AWS una vez desplegado.

| ID | Funcionalidad a comprobar | Acción | Resultado esperado | Resultado obtenido | Estado |
|----|---------------------------|--------|--------------------|--------------------|--------|
| OP-01 | Backend responde local | `curl http://localhost:8000/v1/health` | HTTP 200, `model_loaded:true` | HTTP 200 | ✅ |
| OP-02 | Migraciones aplican (Alembic) | `alembic upgrade head` | Crea tablas `users`, `scans`, `scan_feedback` | 3 tablas creadas | ✅ |
| OP-03 | APK compila e instala | `gradlew assembleDebug` + `adb install` | APK instalable | APK 23 MB OK | ✅ |
| OP-04 | App alcanza el backend | Login desde dispositivo físico | Sesión iniciada | (demo defensa) | ⏳ demo |
| OP-05 | Despliegue en AWS Lab | Deploy backend + URL pública | `/v1/health` 200 desde Internet | — | 🔲 pendiente |

---

## 4. Matriz de cobertura RF ↔ Casos de prueba

| RF | Descripción | Caso(s) que lo cubren |
|----|-------------|----------------------|
| RF-01 | Capturar imagen con cámara | Demo (OP-04) |
| RF-02 | Seleccionar imagen desde galería | Demo (OP-04) |
| RF-03 | Pre-seleccionar fruta | CP-06 |
| RF-04 | Enviar imagen al backend | CP-05, CP-06, CP-29 |
| RF-05 | Clasificar madurez con IA | CP-05, VER-01..02 |
| RF-06 | Recomendación contextualizada | CP-05 (campo `recommendation`) |
| RF-07 | Persistir cada escaneo | CP-11 |
| RF-08 | Consultar historial paginado | CP-10..13 |
| RF-09 | Historial offline (cache) | CP-19, CP-22, CP-25, CP-36 |
| RF-10 | Semáforo visual de madurez | CP-05 (`color_code`), demo |
| RF-11 | Validar formato de imagen | CP-08, CP-09 |
| RF-12 | Health check del servicio | CP-04, OP-01 |
| RF-13 | Autenticación de usuarios (JWT) | CP-01..03, CP-16..17 |
| RF-14 | Feedback con rating | CP-14, CP-15 |

---

## 5. Ejecución de las pruebas

```bash
# Backend — 17 tests
cd Producto/backend
source .venv/Scripts/activate
pytest tests/ -v            # → 17 passed

# Android — 19 tests JVM
cd Producto/frontend
./gradlew testDebugUnitTest # → 19 passed
# Reporte: app/build/reports/tests/testDebugUnitTest/index.html

# CI (GitHub Actions, workflow backend_ci.yml) corre la suite backend en cada push/PR.
```

Evidencia de ejecución (logs, capturas, métricas) en **[`03_Aplicacion_Pruebas_Resultados.md`](03_Aplicacion_Pruebas_Resultados.md)**.

---

## 6. Resumen de cumplimiento

| Categoría | Casos | Estado |
|-----------|-------|--------|
| Validación funcional (backend) | 15 | ✅ 15/15 |
| Seguridad (OWASP) | 3 | ✅ 3/3 |
| Validación funcional (Android) | 19 | ✅ 19/19 |
| Verificación (calidad) | 6 | ✅ 6/6 |
| Operacional | 5 | ✅ 3 · ⏳ 1 demo · 🔲 1 pendiente (deploy) |
| **Total automatizado** | **36** | **✅ 36/36 en verde** |
