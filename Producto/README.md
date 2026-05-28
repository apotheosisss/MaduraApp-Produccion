# MaduraApp — Producto

> Sistema de análisis de madurez agrícola mediante visión computacional.
> App Android nativa + API FastAPI + modelo YOLO26n entrenado.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)
![Android](https://img.shields.io/badge/Android-API_29+-3DDC84?logo=android&logoColor=white)
![mAP](https://img.shields.io/badge/mAP@50-0.9229-brightgreen)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)

---

## Descripción

MaduraApp clasifica el estado de madurez de **4 frutas climatéricas** en **3 categorías** usando visión computacional:

| Fruta | Estados |
|-------|---------|
| 🥑 Aguacate Hass | Inmaduro · Óptimo · Sobre maduro |
| 🍌 Plátano | Inmaduro · Óptimo · Sobre maduro |
| 🍅 Tomate Cherry | Inmaduro · Óptimo · Sobre maduro |
| 🥭 Mango | Inmaduro · Óptimo · Sobre maduro |

El usuario abre la app → selecciona la fruta → escanea con la cámara (o elige una foto de la galería) → recibe el diagnóstico de madurez + recomendación agronómica en menos de 2.5 segundos.

---

## Estructura del código

```
Producto/
├── backend/                        ← API REST FastAPI
│   ├── app/
│   │   ├── main.py                 ← Entry point (lifespan + routers)
│   │   ├── core/
│   │   │   ├── config.py           ← Settings (pydantic-settings)
│   │   │   ├── database.py         ← AsyncEngine + get_db
│   │   │   └── yolo_wrapper.py     ← Wrapper YOLO26n
│   │   ├── routers/
│   │   │   ├── predict.py          ← POST /v1/predict
│   │   │   └── history.py          ← GET /v1/history
│   │   ├── services/
│   │   │   ├── inference_service.py ← Lógica de inferencia + recomendaciones
│   │   │   └── history_service.py   ← CRUD historial
│   │   ├── models/
│   │   │   └── scan_entity.py      ← ORM SQLAlchemy
│   │   └── schemas/
│   │       └── scan_result.py      ← Pydantic response/request
│   ├── alembic/                    ← Migraciones de BD
│   ├── tests/                      ← 9/9 tests pytest
│   ├── weights/                    ← yolo26n_maduraapp.pt (5.2 MB)
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                       ← App Android (Kotlin)
│   └── app/src/main/java/cl/duoc/maduraapp/
│       ├── ui/
│       │   ├── selector/           ← FruitSelectorActivity (pantalla inicial)
│       │   ├── ScanViewModel.kt
│       │   └── history/
│       └── data/
│           ├── api/                ← Retrofit + OkHttp
│           ├── dto/                ← DTOs Kotlinx Serialization
│           ├── local/              ← Room (cache offline)
│           └── repository/         ← FruitRepository (Single Source of Truth)
│
├── scripts/                        ← Pipeline CRISP-DM (entrenamiento)
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── export_model.py
│
└── notebooks/
    └── train_yolo26n_colab.ipynb   ← Notebook Kaggle/Colab (GPU gratuito)
```

---

## Levantar el backend localmente

### Requisitos previos
- Python 3.12
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/apotheosisss/MaduraApp-Produccion.git
cd MaduraApp-Produccion/Producto/backend

# 2. Crear entorno virtual
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env si es necesario (los valores por defecto sirven para desarrollo)

# 5. Aplicar migraciones de base de datos
alembic upgrade head

# 6. Levantar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verificar

```bash
curl http://localhost:8000/v1/health
# {"status": "ok", "model_loaded": true}
```

Documentación interactiva Swagger: http://localhost:8000/docs

### Ejecutar tests

```bash
pytest tests/ -v
# 9/9 tests passing
```

---

## Configurar la app Android

### Requisitos previos
- Android Studio Hedgehog (2023.1) o posterior
- JDK 17

### Pasos

1. Abrir Android Studio → `File → Open` → seleccionar `Producto/frontend/`
2. Esperar sincronización de Gradle (~5 min la primera vez)
3. Editar `gradle.properties` para apuntar al backend:

```properties
# Emulador AVD (backend en el mismo PC):
maduraapp.api.baseUrl=http://10.0.2.2:8000/

# Dispositivo físico con cable USB + adb reverse tcp:8000 tcp:8000:
# maduraapp.api.baseUrl=http://localhost:8000/

# Producción:
# maduraapp.api.baseUrl=https://maduraapp-backend.onrender.com/
```

4. Ejecutar la app en emulador o dispositivo físico

---

## API Endpoints

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/v1/predict` | Analiza una imagen y retorna el diagnóstico de madurez | Opcional |
| `GET` | `/v1/history` | Retorna el historial de escaneos paginado | Opcional |
| `GET` | `/v1/health` | Estado del servicio y del modelo | No |

### Ejemplo de predicción

```bash
curl -X POST \
  -F "file=@imagen_aguacate.jpg" \
  -F "fruit_type=aguacate_hass" \
  http://localhost:8000/v1/predict
```

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

**`fruit_type` válidos:** `aguacate_hass` · `platano` · `tomate_usda` · `mango`

---

## Variables de entorno

| Variable | Dev (defecto) | Producción |
|----------|--------------|------------|
| `ENVIRONMENT` | `development` | `production` |
| `DB_URL` | `sqlite+aiosqlite:///./maduraapp_dev.db` | `postgresql+asyncpg://...` (Supabase) |
| `YOLO_MODEL_PATH` | `weights/yolo26n_maduraapp.pt` | `weights/yolo26n_maduraapp.pt` |
| `CONFIDENCE_THRESHOLD` | `0.55` | `0.55` |
| `AUTH_SECRET_KEY` | `dev_secret_key` | Auto-generado por Render |

---

## Modelo de IA

| Métrica | Valor |
|---------|-------|
| Arquitectura | YOLO26n (Ultralytics, Enero 2026) |
| Dataset | 31.940 imágenes · 12 clases · 4 frutas |
| Épocas | 80 |
| **mAP@50** | **0.9229** (KPI ≥ 0.75 ✅) |
| Precision | 0.945 |
| Recall | 0.873 |
| Tamaño del modelo | 5.2 MB |
| Inferencia CPU local | ~80-150 ms |
| Inferencia Render Free | ~200-400 ms |

El archivo del modelo (`weights/yolo26n_maduraapp.pt`) está incluido en el repositorio.

### Reentrenar el modelo

```bash
cd scripts/

# 1. Descargar dataset (requiere ROBOFLOW_API_KEY en .env)
python download_dataset.py

# 2. Preparar y normalizar
python prepare_dataset.py

# 3. Entrenar (recomendado en Kaggle/Colab con GPU)
python train_model.py

# 4. Evaluar
python evaluate_model.py

# 5. Exportar al backend
python export_model.py
```

---

## Despliegue con Docker

```bash
cd Producto/

# Levantar stack completo (backend + PostgreSQL local)
docker-compose up --build

# Solo el backend
cd backend/
docker build -t maduraapp-backend .
docker run -p 8000:8000 --env-file .env maduraapp-backend
```

---

## Despliegue en producción (Render)

El deploy es automático al hacer push a `main` — Render detecta el [`render.yaml`](../render.yaml) en la raíz del repositorio.

**Flujo:** `push main` → GitHub Actions CI (pytest) → Render build Docker → deploy automático

Para un deploy desde cero, ver [`Documentación/Evaluacion_2/08_Configuracion_Servidor_Produccion.md`](../Documentación/Evaluacion_2/08_Configuracion_Servidor_Produccion.md).

---

## Demo rápida en sala o computador ajeno

```powershell
# Ejecutar el script de configuración automática (Windows)
.\DEMO_INICIO.ps1
```

El script verifica Python, crea el venv, instala dependencias, migra la BD y levanta el servidor. Ver [`GUIA_DEMO_SALA.md`](../GUIA_DEMO_SALA.md) para instrucciones completas.
