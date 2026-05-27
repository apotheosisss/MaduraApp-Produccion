# Anexos — MaduraApp Evaluación 2

> Referencia rápida de comandos, glosario técnico, endpoints, esquema de BD y bibliografía.

---

## A.1 Comandos frecuentes

### A.1.1 Backend — desarrollo local

```bash
cd Producto/backend

# Crear y activar venv
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows PowerShell
source .venv/bin/activate       # macOS / Linux

# Instalar dependencias
pip install -r requirements.txt

# Levantar servidor con hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Documentación Swagger
# http://localhost:8000/docs

# Tests
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing

# Migraciones
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "descripción"
```

### A.1.2 Frontend Android

```bash
cd Producto/frontend

# Compilar APK debug
./gradlew assembleDebug

# Ejecutar tests JVM
./gradlew test

# Limpiar build
./gradlew clean

# Instalar en dispositivo conectado
./gradlew installDebug
```

### A.1.3 Docker

```bash
cd Producto/

# Levantar stack completo (backend + Postgres)
docker-compose up --build

# Solo backend
cd Producto/backend
docker build -t maduraapp-backend .
docker run -p 8000:8000 --env-file .env maduraapp-backend

# Limpiar
docker-compose down -v
```

### A.1.4 Git — flujo correcto

```bash
# Crear feature branch desde develop (en repo testing)
git checkout develop
git pull origin develop
git checkout -b feature/nombre-descriptivo

# Trabajar, agregar y commitear con Conventional Commits
git add archivo1 archivo2
git commit -m "feat(scope): descripción concisa"

# Pushear y abrir PR
git push origin feature/nombre-descriptivo
# → Abrir PR en GitHub apuntando a develop

# Backup antes de refactor mayor (en cualquier repo)
git tag backup-pre-{descripción}
git push origin backup-pre-{descripción}
```

### A.1.5 Pipeline de entrenamiento (CRISP-DM)

```bash
cd Producto/scripts

# Pull del dataset desde Roboflow
python download_dataset.py

# Preparar dataset (normalizar Kaggle → formato YOLO)
python prepare_dataset.py
python organize_avocado.py

# Entrenar
python train_model.py

# Evaluar
python evaluate_model.py

# Exportar el mejor checkpoint a backend/weights/
python export_model.py
```

### A.1.6 Backup y restore

```bash
# Crear backup de producción
export DB_URL_PROD="postgresql+asyncpg://..."
./scripts/backup_prod.sh

# Verificar integridad
gunzip -t dumps/backup_prod_*.sql.gz

# Restaurar a BD local
gunzip -c dumps/backup_prod_2026-05-26_2130.sql.gz | \
  psql -h localhost -U postgres -d maduraapp_test
```

### A.1.7 Curl — pruebas rápidas

```bash
# Health check
curl http://localhost:8000/v1/health
curl https://maduraapp-backend.onrender.com/v1/health

# Predicción
curl -X POST \
     -F "file=@./sample.jpg" \
     -F "fruit_type=aguacate_hass" \
     http://localhost:8000/v1/predict

# Historial
curl http://localhost:8000/v1/history?limit=10 \
     -H "Authorization: Bearer test-token"
```

### A.1.8 Generación de secretos

```bash
# AUTH_SECRET_KEY para producción
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## A.2 Glosario técnico

| Término | Definición |
|---------|------------|
| **API REST** | Application Programming Interface basada en el estilo arquitectónico REST (Representational State Transfer). |
| **APK** | Android Package Kit — archivo de distribución de apps Android. |
| **async/await** | Sintaxis de Python/Kotlin para programación asíncrona basada en corutinas. |
| **bbox** | Bounding box — caja delimitadora de un objeto detectado por el modelo (formato xyxy: x1, y1, x2, y2). |
| **CameraX** | API moderna de cámara para Android, parte de Jetpack. |
| **Cold start** | Tiempo de arranque desde estado suspendido — penalización típica en serverless/Render Free. |
| **Conventional Commits** | Convención de mensajes de commit estructurada (`feat:`, `fix:`, `docs:`, etc.). |
| **CRISP-DM** | Cross-Industry Standard Process for Data Mining — metodología de 6 fases para proyectos de ML. |
| **DTO** | Data Transfer Object — estructura para transportar datos entre capas (vs Entity, que es del dominio persistente). |
| **DI** | Dependency Injection — patrón de inyección de dependencias para desacoplar componentes. |
| **Hexagonal Architecture** | Variante de Clean Architecture donde el core de negocio está aislado del I/O. |
| **HTTPS / TLS** | HTTP sobre TLS (Transport Layer Security) — comunicaciones cifradas en tránsito. |
| **IaC** | Infrastructure as Code — configuración de infraestructura versionada (ej. `render.yaml`). |
| **JWT** | JSON Web Token — formato compacto para tokens de autenticación firmados. |
| **Kruchten 4+1** | Modelo de vistas arquitectónicas (Lógica, Procesos, Desarrollo, Física + Escenarios). |
| **LiveData** | Componente de AndroidX para datos observables conscientes del ciclo de vida. |
| **mAP@50** | Mean Average Precision con IoU threshold = 0.5 — métrica estándar en detección de objetos. |
| **MVVM** | Model-View-ViewModel — patrón arquitectónico de UI. |
| **OOM** | Out of Memory — error de agotamiento de memoria. |
| **ORM** | Object-Relational Mapping — abstracción de BD relacional como objetos. |
| **PaaS** | Platform as a Service — Render, Heroku, AWS App Runner, etc. |
| **PEP 8** | Python Enhancement Proposal 8 — guía de estilo oficial de Python. |
| **PostgreSQL** | Motor de base de datos relacional open source. |
| **PyTorch** | Framework de deep learning desarrollado por Meta. |
| **Retrofit** | Cliente HTTP type-safe para Android desarrollado por Square. |
| **Room** | API de Android para SQLite con verificación de queries en tiempo de compilación. |
| **SQLAlchemy** | ORM de Python con soporte async desde versión 1.4+. |
| **Supabase** | Plataforma DBaaS construida sobre PostgreSQL. |
| **TTA** | Test Time Augmentation — técnica de inferencia que augmenta la imagen de entrada (rotaciones, flips) y promedia resultados. |
| **uvicorn** | ASGI server de Python para aplicaciones FastAPI. |
| **ViewModel** | Componente AndroidX que sobrevive a recreaciones de Activity. |
| **YOLO** | You Only Look Once — familia de modelos de detección de objetos en tiempo real. |

---

## A.3 Tabla completa de endpoints REST

| Método | Path | Request | Response | Códigos | Auth |
|--------|------|---------|----------|---------|------|
| POST | `/v1/predict` | `multipart/form-data`<br/>· `file`: imagen JPEG/PNG/WebP<br/>· `fruit_type` (opcional): str | `PredictResponse` con `success`, `data`, `error` | 200, 400, 503 | Bearer token opcional |
| GET | `/v1/history?limit={1-100}&offset={int}` | Query params | `HistoryResponse` con `items: List<ScanResult>`, `total`, `limit`, `offset` | 200, 401 | Bearer token opcional (default "anonymous") |
| GET | `/v1/health` | — | `{"status": "ok"\|"degraded", "model_loaded": bool}` | 200 | No |

### A.3.1 Schemas Pydantic (response)

```python
class ScanResult(BaseModel):
    fruit_type: str       # "aguacate_hass" | "platano" | "tomate_usda" | "mango"
    maturity_label: str   # "INMADURO" | "OPTIMO" | "SOBRE_MADURO"
    confidence: float     # 0.0 - 1.0
    bbox: List[float]     # [x1, y1, x2, y2]
    recommendation: str   # texto agronómico
    color_code: str       # "green" | "yellow" | "red"


class PredictResponse(BaseModel):
    success: bool
    data: ScanResult | None = None
    error: str | None = None


class HistoryResponse(BaseModel):
    items: List[ScanResult]
    total: int
    limit: int
    offset: int
```

---

## A.4 Esquema completo de la base de datos (DDL)

```sql
-- Migración 0001_create_scans_table

CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_token VARCHAR(255) NOT NULL DEFAULT 'anonymous',
    fruit_type VARCHAR(50) NOT NULL,
    maturity_label VARCHAR(50) NOT NULL,
    confidence REAL NOT NULL,
    image_hash VARCHAR(64)
);

-- Índices para soportar las queries más comunes
CREATE INDEX ix_scans_user_token ON scans (user_token);
CREATE INDEX ix_scans_timestamp ON scans (timestamp DESC);

-- Constraint para evitar valores fuera de rango (validación adicional a la del backend)
ALTER TABLE scans
  ADD CONSTRAINT chk_confidence_range
  CHECK (confidence >= 0.0 AND confidence <= 1.0);

ALTER TABLE scans
  ADD CONSTRAINT chk_fruit_type_enum
  CHECK (fruit_type IN ('aguacate_hass', 'platano', 'tomate_usda', 'mango'));

ALTER TABLE scans
  ADD CONSTRAINT chk_maturity_enum
  CHECK (maturity_label IN ('INMADURO', 'OPTIMO', 'SOBRE_MADURO'));
```

Para la equivalencia PostgreSQL, reemplazar `INTEGER PRIMARY KEY AUTOINCREMENT` por `SERIAL PRIMARY KEY` o `GENERATED ALWAYS AS IDENTITY`.

---

## A.5 Variables de entorno completas

### A.5.1 Producción (Render)

```dotenv
ENVIRONMENT=production
DB_URL=postgresql+asyncpg://postgres.xxxxx:PASS@host:5432/postgres
AUTH_SECRET_KEY=<auto-generado por Render>
YOLO_MODEL_PATH=weights/yolo26n_maduraapp.pt
CONFIDENCE_THRESHOLD=0.55
```

### A.5.2 Pruebas locales

```dotenv
API_PORT=8000
YOLO_MODEL_PATH=weights/yolo26n_maduraapp.pt
CONFIDENCE_THRESHOLD=0.55
DB_URL=sqlite+aiosqlite:///./maduraapp_dev.db
AUTH_SECRET_KEY=dev_secret_key
ENVIRONMENT=development
```

### A.5.3 Android Gradle properties

```properties
# Para emulador AVD
API_BASE_URL=http://10.0.2.2:8000/

# Para dispositivo físico en LAN
# API_BASE_URL=http://192.168.1.XXX:8000/

# Para producción (Render)
# API_BASE_URL=https://maduraapp-backend.onrender.com/
```

---

## A.6 Referencias bibliográficas y fuentes

### A.6.1 Estándares y modelos

1. Kruchten, P. (1995). "Architectural Blueprints — The 4+1 View Model of Software Architecture". *IEEE Software*, 12(6), 42–50.
2. Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS Inc.
3. ISO/IEC/IEEE 42010:2011 — Systems and software engineering — Architecture description.

### A.6.2 Tecnologías y frameworks

4. FastAPI documentation — https://fastapi.tiangolo.com
5. SQLAlchemy 2.0 asyncio — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
6. Ultralytics YOLO documentation — https://docs.ultralytics.com
7. Android CameraX guide — https://developer.android.com/training/camerax
8. AndroidX Room documentation — https://developer.android.com/training/data-storage/room
9. Material Design 3 — https://m3.material.io
10. Render Blueprint Spec — https://render.com/docs/blueprint-spec
11. Supabase Connection Pooler — https://supabase.com/docs/guides/database/connecting-to-postgres

### A.6.3 Datasets

12. Kaggle — Banana Ripeness Classification Dataset
13. Mendeley Data — Hass Avocado Ripeness Dataset
14. Laboro Tomato Dataset — github.com/laboroai/LaboroTomato
15. Kaggle — Mango Ripening Stages Dataset

### A.6.4 Convenciones

16. PEP 8 — Style Guide for Python Code (https://peps.python.org/pep-0008/)
17. Conventional Commits — https://www.conventionalcommits.org
18. Kotlin Coding Conventions — https://kotlinlang.org/docs/coding-conventions.html

### A.6.5 Material agronómico (recomendaciones del modelo)

19. ODEPA — Oficina de Estudios y Políticas Agrarias de Chile. "Pérdidas post-cosecha en cadenas hortofrutícolas". Informes técnicos 2023-2025.
20. FAO. (2019). *The State of Food and Agriculture 2019: Moving forward on food loss and waste reduction*. Rome: Food and Agriculture Organization.

---

## A.7 Estructura completa del repositorio

```
MaduraApp-Produccion/
├── .github/
│   └── workflows/
│       └── keepalive.yml
├── .gitignore
├── Documentación/
│   ├── ERS_MaduraApp_v2.pdf
│   ├── Gantt_MaduraApp_v2.png
│   ├── Informe Evaluación 1 - MaduraApp.pdf
│   ├── Ishikawa.png
│   ├── MaduraApp_DiagramaCasosDeUso.png
│   ├── MaduraApp_DiagramaClases_v2.png
│   ├── MaduraApp_MER_v2.png
│   ├── Presentación MaduraApp Evaluación 1 (1).pptx
│   ├── WireFrame MaduraApp.pdf
│   └── Evaluacion_2/                            ← Esta evaluación
│       ├── 00_Informe_Tecnico_Evaluacion_2.md   ← Informe maestro
│       ├── 01_Vista_Logica.md
│       ├── 02_Vista_Procesos.md
│       ├── 03_Vista_Desarrollo.md
│       ├── 04_Vista_Fisica.md
│       ├── 05_Vista_Escenarios.md
│       ├── 06_Mockups_y_Wireframes.md
│       ├── 07_Configuracion_Ambiente_Pruebas.md
│       ├── 08_Configuracion_Servidor_Produccion.md
│       ├── 09_Procedimientos_Backup.md
│       ├── 10_Plan_de_Pruebas.md
│       ├── 11_Estado_Desarrollo.md
│       ├── 12_Evidencias_Pruebas.md
│       ├── 13_Anexos.md
│       ├── diagramas/                           ← Fuentes Mermaid si se exportan a PNG
│       └── capturas/                            ← Screenshots para evidencias
├── Gestión/
│   └── .gitkeep
├── Producto/
│   ├── backend/
│   ├── frontend/
│   ├── scripts/
│   ├── notebooks/
│   ├── docker-compose.yml
│   ├── CLAUDE.md
│   └── README.md
├── README.md
└── render.yaml
```

---

## A.8 Convenciones del proyecto — resumen ejecutivo

| Tipo | Convención |
|------|-----------|
| **Mensajes de commit** | Conventional Commits, imperativo presente, español |
| **Branches** | `feature/`, `fix/`, `docs/`, `refactor/` desde `develop` (testing) o `main` (producción) |
| **PRs** | Apuntan a `develop`/`main`, requieren CI verde |
| **Naming Python** | snake_case funciones/variables, PascalCase clases, UPPER_SNAKE_CASE constantes |
| **Naming Kotlin** | camelCase funciones/variables, PascalCase clases, UPPER_SNAKE_CASE constantes |
| **Documentación de código** | Docstrings Python en services/schemas, KDoc Kotlin en clases públicas |
| **Líneas de código** | Max 100 caracteres (Python y Kotlin) |
| **Backups antes de cambio mayor** | Tag `backup-pre-{descripción}` empujado a remoto |
| **Sin secretos en repo** | `.env`, dumps de BD, keystores — todo en `.gitignore` |
| **Modelo `.pt`** | Versionado en Git (público, no es secreto) |

---

*Fin de los anexos.*
