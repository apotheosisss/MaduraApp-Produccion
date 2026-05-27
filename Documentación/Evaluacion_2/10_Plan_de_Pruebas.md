# Plan de Pruebas — MaduraApp

> Documento que define la **estrategia de pruebas** del proyecto MaduraApp, clasificando los casos de prueba en pruebas **operacionales**, **de validación** y **de verificación**, según el modelo solicitado en la rúbrica. Cubre tanto el backend FastAPI como la app Android.
>
> Responde al criterio 2 de la rúbrica del encargo y a los indicadores IL2.2 e IL2.3.

---

## 1. Estrategia general

### 1.1 Pirámide de pruebas aplicada

MaduraApp adopta la pirámide clásica de Mike Cohn, priorizando tests unitarios rápidos y reservando los end-to-end para validaciones manuales en la defensa:

```
        ▲
       ╱ ╲
      ╱   ╲     E2E (manual durante demo) — 8 casos
     ╱─────╲
    ╱       ╲   Integración (pytest backend) — 9 tests
   ╱─────────╲
  ╱           ╲ Unitarios (Android JVM + pytest)
 ╱─────────────╲   ~ 14 unidades de prueba
```

### 1.2 Distribución actual

| Nivel | Cantidad | Framework | Frecuencia |
|-------|----------|-----------|------------|
| Unitarios | 9 backend (pytest) + 5 Android (JVM) | pytest + MockK + JUnit | Cada commit en CI |
| Integración | Implícita en pytest con SQLite in-memory + TestClient | FastAPI TestClient | Cada commit en CI |
| Operacionales | 8 manuales documentados | curl + UI inspection | Antes de demo |
| E2E | 8 casos manuales en defensa | App física + backend | 1× por evaluación |

---

## 2. Clasificación según rúbrica

### 2.1 Pruebas operacionales (`Operational tests`)

Verifican que el sistema **funciona en su entorno** y está disponible para el uso normal. Foco en infraestructura y operación.

| ID | Test | Objetivo | Frecuencia |
|----|------|----------|-----------|
| OP-01 | Health check del backend | `/v1/health` retorna 200 con `model_loaded:true` | Continuo (keepalive cada 14 min) |
| OP-02 | Backend acepta conexiones HTTPS | TLS válido, certificado Let's Encrypt vigente | Mensual |
| OP-03 | BD Supabase responde | Conexión exitosa via pooler | Diario (vía health check del backend) |
| OP-04 | App Android instala correctamente | APK debug se instala en emulador y dispositivo | Cada release manual |
| OP-05 | Cliente alcanza al backend | Smoke test `curl https://maduraapp-backend.onrender.com/v1/health` | Pre-demo |
| OP-06 | Cold start dentro de límite aceptable | Render despierta en < 60 s | Mensual |
| OP-07 | Backups recuperables | Restaurar último dump en BD efímera y validar conteo | Mensual |
| OP-08 | Espacio de Supabase no excede free tier | Storage < 450 MB (90% de 500 MB) | Semanal |

### 2.2 Pruebas de validación (`Validation tests`)

Verifican que el sistema **cumple los requisitos funcionales aprobados** (los RF de la ERS). Responden a "¿estamos construyendo el sistema correcto?".

| ID | Test | RF cubierto | Implementación |
|----|------|-------------|----------------|
| VAL-01 | POST `/v1/predict` con imagen válida + fruit_type retorna ScanResult | RF-04, RF-05 | `tests/test_predict.py::test_predict_with_fruit_filter` |
| VAL-02 | POST `/v1/predict` sin fruit_type funciona (modo libre) | RF-04, RF-05 | (manual + similar al anterior) |
| VAL-03 | POST `/v1/predict` con content_type inválido → 400 | RF-11 | `tests/test_predict.py::test_predict_invalid_content_type` |
| VAL-04 | POST `/v1/predict` sin archivo → 422 | RF-11 | `tests/test_predict.py::test_predict_no_file` |
| VAL-05 | POST `/v1/predict` con fruit_type inválido → 400 | RF-11 | `tests/test_predict.py::test_predict_invalid_fruit_type` |
| VAL-06 | POST `/v1/predict` con imagen sin fruta detectable → success:false | RF-04, RF-05 | `tests/test_predict.py::test_predict_no_detection` |
| VAL-07 | GET `/v1/history` historial vacío → lista vacía | RF-08 | `tests/test_history.py::test_history_empty` |
| VAL-08 | GET `/v1/history` tras un save → contiene el registro | RF-07, RF-08 | `tests/test_history.py::test_history_after_save` |
| VAL-09 | GET `/v1/history` con paginación (limit/offset) | RF-08 | `tests/test_history.py::test_history_pagination` |
| VAL-10 | GET `/v1/history` sin token retorna lista del usuario "anonymous" | RF-08 | `tests/test_history.py::test_history_no_token` |
| VAL-11 | Submit image desde Android dispara Loading → Success | RF-04, RF-10 | `ScanViewModelTest.testSubmitImageSuccess` |
| VAL-12 | NoDetection del backend → estado `NoDetection` en ViewModel | RF-04 | `ScanViewModelTest.testSubmitImageNoDetection` |
| VAL-13 | Cache local refleja último response | RF-09 | `FruitRepositoryTest.testPredictCachesResult` |
| VAL-14 | observeLocalHistory emite datos cacheados | RF-09 | `FruitRepositoryTest.testObserveLocalHistory` |

### 2.3 Pruebas de verificación (`Verification tests`)

Verifican que el sistema cumple **propiedades no funcionales y atributos de calidad** (performance, robustez, mantenibilidad). Responden a "¿estamos construyendo el sistema correctamente?".

| ID | Test | Atributo de calidad | KPI | Estado actual |
|----|------|---------------------|-----|---------------|
| VER-01 | Latencia de inferencia sin TTA en CPU local | Performance | < 200 ms p95 | ~ 80-150 ms (✅) |
| VER-02 | Latencia de inferencia con TTA en CPU local | Performance | < 400 ms p95 | ~ 160-300 ms (✅) |
| VER-03 | Latencia end-to-end Android → resultado (LAN local) | Performance | < 500 ms p95 | ~ 250-500 ms (✅) |
| VER-04 | Latencia end-to-end Android → resultado (Render Free) | Performance | < 3 s p95 sin cold start | ~ 1.5-2.5 s (✅) |
| VER-05 | mAP@50 del modelo en test set | Precisión | ≥ 0.75 | **0.9229** (✅) |
| VER-06 | Precision por clase | Precisión | ≥ 0.70 cada clase | Todas > 0.85 (✅) |
| VER-07 | Recall por clase | Cobertura | ≥ 0.65 cada clase | Todas > 0.80 (✅) |
| VER-08 | RAM consumida por backend en runtime | Eficiencia | < 500 MB en free tier | ~ 400-500 MB (✅ marginal) |
| VER-09 | RAM peak durante inferencia | Eficiencia | < 512 MB | Mitigado con `del + gc.collect()` (✅) |
| VER-10 | Tamaño del modelo en disco | Eficiencia | < 10 MB | 5.2 MB (✅) |
| VER-11 | CI verde en cada commit a `main` | Mantenibilidad | 100% gates pasados | ✅ (vigente) |
| VER-12 | Sin secretos en repo | Seguridad | 0 hallazgos | ✅ (verificado manualmente) |

---

## 3. Casos de prueba — detalle paso a paso

A continuación se documentan los casos de prueba clave con el formato estándar de la industria.

### 3.1 Caso CP-001 — Predicción exitosa con filtro de fruta

| Campo | Valor |
|-------|-------|
| **ID** | CP-001 |
| **Tipo** | Validación |
| **Pre-condición** | Backend corriendo, modelo cargado, BD vacía o operativa |
| **Datos de entrada** | imagen JPEG de aguacate maduro (640×480), `fruit_type=aguacate_hass` |
| **Pasos** | 1. POST a `/v1/predict` con multipart (file + fruit_type)<br/>2. Recibir respuesta JSON |
| **Resultado esperado** | HTTP 200<br/>`{"success":true, "data":{"fruit_type":"aguacate_hass", "maturity_label":"OPTIMO", "confidence": >=0.55, ...}}`<br/>BD: nuevo registro en `scans` con esos valores |
| **Resultado observado** | ✅ Pasa (verificado en pytest `test_predict_with_fruit_filter`) |

### 3.2 Caso CP-002 — Content-Type rechazado

| Campo | Valor |
|-------|-------|
| **ID** | CP-002 |
| **Tipo** | Validación |
| **Pre-condición** | Backend corriendo |
| **Datos de entrada** | archivo `.txt` con header `Content-Type: text/plain` |
| **Pasos** | 1. POST a `/v1/predict` con archivo txt |
| **Resultado esperado** | HTTP 400 con `{"detail":"Formato de imagen no soportado"}` |
| **Resultado observado** | ✅ Pasa |

### 3.3 Caso CP-003 — fruit_type inválido

| Campo | Valor |
|-------|-------|
| **ID** | CP-003 |
| **Tipo** | Validación |
| **Pre-condición** | Backend corriendo |
| **Datos de entrada** | imagen válida + `fruit_type=manzana` (no soportada) |
| **Pasos** | 1. POST a `/v1/predict` con esos parámetros |
| **Resultado esperado** | HTTP 400 con `detail` listando frutas válidas |
| **Resultado observado** | ✅ Pasa |

### 3.4 Caso CP-004 — Sin detección en imagen sin frutas

| Campo | Valor |
|-------|-------|
| **ID** | CP-004 |
| **Tipo** | Validación |
| **Pre-condición** | Backend corriendo, modelo cargado |
| **Datos de entrada** | imagen JPEG de paisaje (sin frutas) |
| **Pasos** | 1. POST a `/v1/predict` |
| **Resultado esperado** | HTTP 200 con `{"success":false, "error":"No se detectó..."}`<br/>BD: sin inserción |
| **Resultado observado** | ✅ Pasa |

### 3.5 Caso CP-005 — Paginación de historial

| Campo | Valor |
|-------|-------|
| **ID** | CP-005 |
| **Tipo** | Validación |
| **Pre-condición** | BD con > 25 registros de un usuario |
| **Datos de entrada** | GET `/v1/history?limit=10&offset=10` con `Authorization: Bearer user1` |
| **Resultado esperado** | HTTP 200 con `items` array de máx 10 elementos, los siguientes después del offset 10 |
| **Resultado observado** | ✅ Pasa |

### 3.6 Caso CP-006 — Estado Loading desde Android

| Campo | Valor |
|-------|-------|
| **ID** | CP-006 |
| **Tipo** | Validación |
| **Pre-condición** | `ScanViewModel` instanciado con `FakeRepository` |
| **Pasos** | 1. Llamar `viewModel.submitImage(bytes)`<br/>2. Observar `state.value` inmediatamente después |
| **Resultado esperado** | `state.value == ScanState.Loading` antes de que la corrutina complete |
| **Resultado observado** | ✅ Pasa (`ScanViewModelTest.testSubmitImageTransitionsToLoading`) |

### 3.7 Caso CP-007 — Cache local actualizado tras predict exitoso

| Campo | Valor |
|-------|-------|
| **ID** | CP-007 |
| **Tipo** | Validación |
| **Pre-condición** | `LocalScanDataSource` con BD Room en memoria |
| **Pasos** | 1. Mock `MaduraApiService.predict` retorna response exitosa<br/>2. Llamar `repository.predict(bytes, "platano")`<br/>3. Consultar `local.observeRecent(50)` |
| **Resultado esperado** | El nuevo ScanResultDto aparece en la lista observada |
| **Resultado observado** | ✅ Pasa (`FruitRepositoryTest`) |

### 3.8 Caso CP-008 — Latencia inferencia + TTA

| Campo | Valor |
|-------|-------|
| **ID** | CP-008 |
| **Tipo** | Verificación |
| **Pre-condición** | Backend local con modelo cargado, CPU > 4 cores |
| **Pasos** | 1. Ejecutar 50 predicts secuenciales con TTA habilitado<br/>2. Medir p95 |
| **Resultado esperado** | p95 < 400 ms |
| **Resultado observado** | ~ 220-300 ms p95 (✅) |

### 3.9 Caso CP-009 — mAP@50 del modelo

| Campo | Valor |
|-------|-------|
| **ID** | CP-009 |
| **Tipo** | Verificación |
| **Pre-condición** | Modelo entrenado, dataset de test (15% del total = ~4790 imágenes) |
| **Pasos** | 1. Ejecutar `python scripts/evaluate_model.py`<br/>2. Inspeccionar `results.txt` |
| **Resultado esperado** | mAP@50 ≥ 0.75 (KPI definido en ERS) |
| **Resultado observado** | mAP@50 = **0.9229** — supera el KPI por 17.3 puntos (✅) |

### 3.10 Caso CP-010 — RAM en runtime durante inferencia

| Campo | Valor |
|-------|-------|
| **ID** | CP-010 |
| **Tipo** | Verificación |
| **Pre-condición** | Backend corriendo, container con límite 512 MB |
| **Pasos** | 1. Iniciar backend (warmup deshabilitado).<br/>2. Hacer 10 predicts seguidos.<br/>3. Medir RSS del proceso uvicorn vía `/proc/PID/status` o Render metrics. |
| **Resultado esperado** | RSS < 500 MB sin OOM kill |
| **Resultado observado** | ~ 400-490 MB (✅ marginal pero funcional) |

---

## 4. Matriz de cobertura RF ↔ Tests

| RF | Descripción | Test(s) que lo cubren |
|----|-------------|----------------------|
| RF-01 | Capturar imagen con cámara | (Demo manual) |
| RF-02 | Seleccionar imagen desde galería | (Demo manual) |
| RF-03 | Pre-seleccionar fruta a escanear | (Demo manual) |
| RF-04 | Enviar imagen al backend | VAL-01, VAL-11 |
| RF-05 | Clasificar madurez con IA | VAL-01, VER-05 a VER-07 |
| RF-06 | Devolver recomendación contextualizada | VAL-01 (validar campo `recommendation` en response) |
| RF-07 | Persistir cada escaneo | VAL-08 (verifica insert en BD) |
| RF-08 | Consultar historial paginado | VAL-07, VAL-08, VAL-09, VAL-10 |
| RF-09 | Visualizar historial offline | VAL-13, VAL-14 |
| RF-10 | Semáforo visual de madurez | VAL-11 (verifica color_code), demo manual |
| RF-11 | Validar formato de imagen | VAL-03, VAL-04, VAL-05 |
| RF-12 | Health check del servicio | OP-01 |

---

## 5. Ejecución de las pruebas

### 5.1 Suite pytest del backend

```bash
cd Producto/backend
source .venv/bin/activate
pytest tests/ -v

# Con coverage
pip install pytest-cov
pytest tests/ --cov=app --cov-report=term-missing
```

Resultado esperado: 9 passed.

### 5.2 Suite JVM del Android

```bash
cd Producto/frontend
./gradlew test

# Reporte HTML
# app/build/reports/tests/testDebugUnitTest/index.html
```

### 5.3 Suite del CI (GitHub Actions)

El workflow `backend_ci.yml` se ejecuta automáticamente en cada PR a `develop`/`main`. Status accesible en https://github.com/apotheosisss/MaduraApp-Produccion/actions.

### 5.4 Tests operacionales manuales

Listado en sección §2.1; ejecutar antes de cada defensa:

```bash
# OP-01
curl https://maduraapp-backend.onrender.com/v1/health

# OP-05 (smoke E2E desde host con la app emulando un cliente)
curl -X POST -F "file=@./fixtures/sample_aguacate.jpg" \
     -F "fruit_type=aguacate_hass" \
     https://maduraapp-backend.onrender.com/v1/predict
```

---

## 6. Criterios de aceptación del Sprint 2

Para considerar el Sprint 2 cerrado, todos los siguientes deben ser verdaderos:

- [x] Suite pytest backend: 9/9 passing.
- [x] Suite JVM Android: todos los tests passing (FruitRepositoryTest, ScanViewModelTest, HistoryViewModelTest).
- [x] CI verde en última versión de `main` de `MaduraApp-Produccion`.
- [x] KPI mAP@50 ≥ 0.75 cumplido (actual: 0.9229).
- [x] Backend desplegado en Render y responde a `/v1/health`.
- [x] APK construible sin errores (`./gradlew assembleDebug`).
- [x] Sin secretos en el repo público.
- [x] Documentación 4+1 completa (5 vistas).

---

## 7. Roadmap de pruebas (post-Evaluación 2)

| Mejora futura | Justificación |
|---------------|---------------|
| Tests E2E automatizados con Espresso / UI Automator | Eliminar la dependencia de demo manual para RF-01, RF-02, RF-03 |
| Tests de carga (`locust`, `k6`) contra backend en Render | Validar capacidad real bajo concurrencia |
| Pruebas de mutación (`mutmut`) | Verificar que los tests detectan regresiones reales |
| Coverage gate ≥ 80% en CI | Prevenir regresión de cobertura |
| Pruebas de seguridad automatizadas (`bandit`, `safety`) | Detectar dependencias con CVEs |
| Pruebas de A11y en Android (`Accessibility Scanner`) | Cumplimiento WCAG AA |
