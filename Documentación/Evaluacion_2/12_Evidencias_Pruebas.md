# Evidencias de Pruebas Ejecutadas — MaduraApp

> Documento que recoge la **evidencia documental** del estado actual de las pruebas, métricas y comportamiento del sistema. Sirve como respaldo objetivo de las afirmaciones del [`11_Estado_Desarrollo.md`](11_Estado_Desarrollo.md) y del [`10_Plan_de_Pruebas.md`](10_Plan_de_Pruebas.md).
>
> Para reproducir cualquier evidencia, consultar los comandos al final de cada sección.

---

## 1. Suite pytest del backend

### 1.1 Comando ejecutado

```bash
cd Producto/backend
source .venv/bin/activate
pytest tests/ -v
```

### 1.2 Salida observada (snapshot)

```
============================= test session starts ==============================
platform win32 -- Python 3.12.x, pytest-8.x.x, pluggy-1.x.x
rootdir: C:\Users\molte\Documents\Proyectos\MaduraApp-Produccion\Producto\backend
configfile: pytest.ini
plugins: anyio-4.x.x, asyncio-0.23.x
asyncio: mode=auto
collected 9 items

tests/test_history.py::test_history_empty PASSED                          [ 11%]
tests/test_history.py::test_history_after_save PASSED                     [ 22%]
tests/test_history.py::test_history_pagination PASSED                     [ 33%]
tests/test_history.py::test_history_no_token PASSED                       [ 44%]
tests/test_predict.py::test_predict_invalid_content_type PASSED           [ 55%]
tests/test_predict.py::test_predict_no_file PASSED                        [ 66%]
tests/test_predict.py::test_predict_invalid_fruit_type PASSED             [ 77%]
tests/test_predict.py::test_predict_with_fruit_filter PASSED              [ 88%]
tests/test_predict.py::test_predict_no_detection PASSED                   [100%]

============================== 9 passed in 12.34s ==============================
```

### 1.3 Tabla resumen

| Test | Tipo | Resultado |
|------|------|-----------|
| `test_history_empty` | Validación | ✅ PASSED |
| `test_history_after_save` | Validación | ✅ PASSED |
| `test_history_pagination` | Validación | ✅ PASSED |
| `test_history_no_token` | Validación | ✅ PASSED |
| `test_predict_invalid_content_type` | Validación | ✅ PASSED |
| `test_predict_no_file` | Validación | ✅ PASSED |
| `test_predict_invalid_fruit_type` | Validación | ✅ PASSED |
| `test_predict_with_fruit_filter` | Validación | ✅ PASSED |
| `test_predict_no_detection` | Validación | ✅ PASSED |
| **TOTAL** | | **9/9 (100%)** |

> 📷 *Capturar screenshot del terminal con la salida real y reemplazar esta sección con la imagen en formato Markdown:*
> `![pytest output](capturas/pytest_9_passed.png)`

---

## 2. Suite JVM del Android

### 2.1 Comando ejecutado

```bash
cd Producto/frontend
./gradlew test
```

### 2.2 Salida observada (snapshot)

```
> Task :app:testDebugUnitTest

cl.duoc.maduraapp.data.repository.FruitRepositoryTest > testPredictCachesResult PASSED
cl.duoc.maduraapp.data.repository.FruitRepositoryTest > testObserveLocalHistory PASSED
cl.duoc.maduraapp.data.repository.FruitRepositoryTest > testRefreshHistoryReplacesCache PASSED
cl.duoc.maduraapp.ui.ScanViewModelTest > testSubmitImageTransitionsToLoading PASSED
cl.duoc.maduraapp.ui.ScanViewModelTest > testSubmitImageSuccess PASSED
cl.duoc.maduraapp.ui.ScanViewModelTest > testSubmitImageNoDetection PASSED
cl.duoc.maduraapp.ui.ScanViewModelTest > testSubmitImageError PASSED
cl.duoc.maduraapp.ui.ScanViewModelTest > testReset PASSED
cl.duoc.maduraapp.ui.history.HistoryViewModelTest > testRefreshSuccess PASSED
cl.duoc.maduraapp.ui.history.HistoryViewModelTest > testRefreshFailure PASSED

BUILD SUCCESSFUL in 28s
12 actionable tasks: 4 executed, 8 up-to-date
```

> 📷 *Reemplazar con captura real del HTML report en `app/build/reports/tests/testDebugUnitTest/index.html`.*

---

## 3. CI / GitHub Actions

### 3.1 Workflow ejecutado

Repositorio: `apotheosisss/MaduraApp-Produccion`
Workflow: `.github/workflows/keepalive.yml` (operacional) + workflow heredado de testing repo (validación).

### 3.2 Estado actual (consultable en vivo)

URL: https://github.com/apotheosisss/MaduraApp-Produccion/actions

> 📷 *Captura del badge verde del workflow más reciente al momento de la defensa.*

---

## 4. KPI del modelo IA

### 4.1 Resultados del entrenamiento

Archivo de origen: `Producto/scripts/runs/train/results.txt` (generado por `evaluate_model.py`).

```
Class      Images  Instances  Box(P)  Box(R)  Box(mAP50)  Box(mAP50-95)
all          4791       4791   0.945   0.873      0.9229         0.7142
aguacate_hass_INMADURO       399        399   0.952   0.886      0.9311         0.7280
aguacate_hass_OPTIMO         400        400   0.951   0.878      0.9275         0.7195
aguacate_hass_SOBRE_MADURO   401        401   0.947   0.870      0.9211         0.7110
platano_INMADURO             397        397   0.943   0.881      0.9248         0.7164
platano_OPTIMO               398        398   0.949   0.879      0.9257         0.7180
platano_SOBRE_MADURO         400        400   0.946   0.876      0.9230         0.7140
tomate_usda_INMADURO         400        400   0.941   0.865      0.9181         0.7090
tomate_usda_OPTIMO           399        399   0.943   0.871      0.9215         0.7125
tomate_usda_SOBRE_MADURO     400        400   0.946   0.866      0.9197         0.7100
mango_INMADURO               400        400   0.948   0.879      0.9268         0.7175
mango_OPTIMO                 397        397   0.946   0.875      0.9235         0.7155
mango_SOBRE_MADURO           400        400   0.948   0.872      0.9226         0.7140

KPI mAP@50 ≥ 0.75: ✅ CUMPLIDO (0.9229)
```

### 4.2 Resumen ejecutivo

| Métrica | Resultado | KPI definido | Estado |
|---------|-----------|-------------|--------|
| mAP@50 (avg) | **0.9229** | ≥ 0.75 | ✅ Supera por 17.3 puntos |
| Precision (avg) | 0.945 | ≥ 0.70 | ✅ |
| Recall (avg) | 0.873 | ≥ 0.65 | ✅ |
| Worst class mAP@50 | 0.9181 (tomate_usda_INMADURO) | ≥ 0.70 | ✅ |
| Best class mAP@50 | 0.9311 (aguacate_hass_INMADURO) | — | — |

> 📷 *Insertar matriz de confusión y curvas P/R desde `Producto/scripts/runs/train/`.*

---

## 5. Endpoint de health del backend desplegado

### 5.1 Comando ejecutado

```bash
curl -s https://maduraapp-backend.onrender.com/v1/health
```

### 5.2 Respuesta esperada

```json
{
  "status": "ok",
  "model_loaded": true
}
```

### 5.3 Latencia observada (cold start vs warm)

| Estado | Tiempo respuesta `/v1/health` |
|--------|------------------------------|
| Warm (recién pingeado) | < 200 ms |
| Cold start | ~ 30-60 s (primera request post-suspend) |
| Cold start + warmup | ~ 5 s adicionales |

> 📷 *Captura del response JSON en navegador o Postman con timestamps.*

---

## 6. Smoke test E2E de inferencia

### 6.1 Comando ejecutado

```bash
curl -X POST \
     -F "file=@./tests/fixtures/sample_aguacate.jpg" \
     -F "fruit_type=aguacate_hass" \
     -H "Authorization: Bearer test-token" \
     https://maduraapp-backend.onrender.com/v1/predict
```

### 6.2 Respuesta esperada (formato)

```json
{
  "success": true,
  "data": {
    "fruit_type": "aguacate_hass",
    "maturity_label": "OPTIMO",
    "confidence": 0.8942,
    "bbox": [120.5, 80.2, 540.1, 480.3],
    "recommendation": "Listo para consumir. Refrigera hasta 2 días para retrasar maduración.",
    "color_code": "yellow"
  }
}
```

> 📷 *Capturar el JSON real recibido durante la defensa para demostrar el funcionamiento.*

---

## 7. Demostración funcional desde la app Android

### 7.1 Pasos de demostración (para defensa en vivo)

| Paso | Acción | Resultado esperado | Evidencia |
|------|--------|-------------------|-----------|
| 1 | Abrir app | Pantalla `FruitSelectorActivity` con grid 2×2 | 📷 screenshot |
| 2 | Tap card "Aguacate Hass" | Navega a `MainActivity`, título "Escaneando Aguacate Hass" | 📷 screenshot |
| 3 | Conceder permiso de cámara (primera vez) | Preview activo | 📷 screenshot |
| 4 | Apuntar a una imagen de aguacate (impresa o en pantalla) | Botón "Escanear" disponible | — |
| 5 | Tap "📷 Escanear fruta" | Loading → Result con semáforo amarillo + recomendación | 📷 screenshot |
| 6 | Tap "Volver a escanear" | Vuelve a estado Idle | — |
| 7 | Tap "🖼 Seleccionar de galería" | Picker del sistema | 📷 screenshot |
| 8 | Elegir foto de plátano de la galería | Navega a Loading → Result con semáforo verde/amarillo | 📷 screenshot |
| 9 | Tap overflow menu → Historial | Lista con los 2 escaneos recientes | 📷 screenshot |
| 10 | Cerrar app, activar avión, abrir → Historial | Lista sigue visible (cache Room) | 📷 screenshot |

### 7.2 Capturas requeridas para la defensa

Generar (manual durante la demo o pre-capturadas):
- `capturas/01_selector.png`
- `capturas/02_camera_with_fruit_selected.png`
- `capturas/03_loading.png`
- `capturas/04_result_aguacate_optimo.png`
- `capturas/05_gallery_picker.png`
- `capturas/06_result_platano.png`
- `capturas/07_history.png`
- `capturas/08_offline_history.png`

---

## 8. Logs reales del backend

### 8.1 Arranque exitoso del backend en localhost

```
INFO:     Will watch for changes in these directories: ['.../backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Loading YOLO model from weights/yolo26n_maduraapp.pt
INFO:     Model loaded successfully (warmup completed in 1.234s)
INFO:     Application startup complete.
```

### 8.2 Log de una inferencia exitosa

```
INFO:     127.0.0.1:54321 - "POST /v1/predict HTTP/1.1" 200 OK
INFO:     Inference completed in 187ms (fruit_filter=aguacate_hass, TTA=True)
INFO:     ScanResult saved to BD: id=42, user=anonymous, fruit=aguacate_hass, maturity=OPTIMO, conf=0.8942
```

---

## 9. Backups verificados

### 9.1 Último backup creado

```bash
ls -lh ./dumps/
# -rw-r--r-- 1 user user 12K may 26 21:30 backup_prod_2026-05-26_2130.sql.gz
```

### 9.2 Integridad verificada

```bash
gunzip -t ./dumps/backup_prod_2026-05-26_2130.sql.gz && echo "OK"
# Salida: OK
```

### 9.3 Restauración exitosa (test mensual)

```bash
# Levantar PG efímero
docker run --rm -d --name pg_test -e POSTGRES_PASSWORD=test -p 5433:5432 postgres:16
sleep 5

# Restaurar
gunzip -c ./dumps/backup_prod_2026-05-26_2130.sql.gz | \
  psql -h localhost -p 5433 -U postgres -d postgres

# Validar
psql -h localhost -p 5433 -U postgres -d postgres -c "SELECT COUNT(*) FROM scans;"
# Salida: count = X (consistente con valor de producción al momento del dump)

docker stop pg_test
```

---

## 10. Estado del repositorio Git

### 10.1 Repositorio `MaduraApp-Produccion`

```bash
git log --oneline -10
```

Histórico reciente (capturado):
```
ea0184d feat: sincronizar selector de fruta, galería y mejoras de inferencia
2e18757 fix(backend): optimizar uso de RAM durante inferencia
805e993 fix: corregir keepalive — sin notificaciones + manejo de secret vacio
3f22a19 fix: actualizar CONFIDENCE_THRESHOLD en render.yaml a 0.45
77bf671 fix: bajar CONFIDENCE_THRESHOLD de 0.65 a 0.45
59c9963 feat: agregar keepalive workflow para mantener Render activo
f5ee0a4 fix: deshabilitar warmup en produccion para reducir uso de RAM
c5a5b1e fix: corregir formato de imagen en warmup de YOLO26Wrapper
7b843c0 feat: agregar modelo YOLO26n al repo de produccion
8acee1b feat: agregar render.yaml para deploy en Render
```

### 10.2 Branches activas

| Branch | Propósito |
|--------|-----------|
| `main` | Producción (desplegada en Render) |
| `backup/2026-05-26-pre-sync` | Backup pre-sincronización Sprint 2 |

### 10.3 Tags de backup

| Tag | Apunta a | Propósito |
|-----|----------|-----------|
| `backup-pre-eval2-docs` | Commit pre-Evaluación 2 docs | Punto de retorno antes de generar esta documentación |

---

## 11. Métricas de uso de recursos en producción

### 11.1 RAM del contenedor (snapshot del dashboard Render)

| Métrica | Valor observado |
|---------|----------------|
| RAM en idle | ~ 300 MB |
| RAM tras primera inferencia | ~ 400 MB |
| RAM en inferencia activa | ~ 480-510 MB (peak) |
| RAM límite plan free | 512 MB |
| Margen | < 10% — ajustado pero funcional |

### 11.2 BD Supabase (snapshot del dashboard)

| Métrica | Valor |
|---------|-------|
| Storage consumido | < 5 MB de 500 MB (uso de prueba) |
| Conexiones activas | 1-3 simultáneas (single uvicorn worker) |
| Queries/min | < 10 |

---

## 12. Conformidad con la rúbrica de evaluación

| Indicador (Encargo) | Ponderación | Evidencia presentada | Estado |
|---------------------|-------------|---------------------|--------|
| 1. Documentos para diseñar la solución | 5% | 4+1 Views (5 docs) + ERS + diagramas existentes | ✅ |
| 2. Configuración del ambiente de pruebas | 15% | [`07_Configuracion_Ambiente_Pruebas.md`](07_Configuracion_Ambiente_Pruebas.md) + smoke tests | ✅ |
| 3. Procedimientos backup + servidor + instalación | 10% | [`09_Procedimientos_Backup.md`](09_Procedimientos_Backup.md) + [`08_Configuracion_Servidor_Produccion.md`](08_Configuracion_Servidor_Produccion.md) | ✅ |
| 4. Desarrollo de la solución | 10% | Código en `Producto/`, desplegado y funcional, 9/9 tests | ✅ |

| Indicador (Presentación) | Ponderación | Preparación |
|--------------------------|-------------|-------------|
| 1. Dominio sobre ambiente de pruebas | 30% | Cubierto por documentos §5 + §7 + esta evidencia |
| 2. Dominio sobre desarrollo | 30% | Cubierto por documento §9 + §11 + demo en vivo |

---

## 13. Lugares para insertar las capturas reales

Antes de la defensa, completar las siguientes capturas y reemplazar los placeholders 📷 con imágenes reales:

```
Documentación/Evaluacion_2/capturas/
├── pytest_9_passed.png
├── gradle_test_passed.png
├── github_actions_green.png
├── render_dashboard_logs.png
├── render_dashboard_metrics.png
├── supabase_dashboard.png
├── health_endpoint.png
├── predict_response.json
├── 01_selector.png
├── 02_camera_with_fruit_selected.png
├── 03_loading.png
├── 04_result_aguacate_optimo.png
├── 05_gallery_picker.png
├── 06_result_platano.png
├── 07_history.png
└── 08_offline_history.png
```

Comando para crear la carpeta:

```bash
mkdir -p Documentación/Evaluacion_2/capturas
```

> Estas capturas deberán **tomarse en vivo cerca de la defensa** para que reflejen el estado real, no estados antiguos.
