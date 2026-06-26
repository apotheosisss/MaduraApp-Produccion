# Anexos Técnicos — MaduraApp (EP3)

> Material de soporte: contrato de la API, esquema de base de datos, variables de entorno, comandos y referencias.

---

## A. Contrato de la API REST (Request / Response)

Base: `/v1`. Autenticación: `Authorization: Bearer <JWT>` (salvo `/health` y registro/login).

| Método | Ruta | Cuerpo / Query | Respuesta (200/201) | Errores |
|--------|------|----------------|---------------------|---------|
| POST | `/auth/register` | `{username, email, password}` | `201 {access_token, token_type, user_id, username}` | 409 duplicado · 422 inválido |
| POST | `/auth/login` | `{email, password}` | `200 {access_token, …}` | 401 credenciales |
| GET | `/auth/me` | — (Bearer) | `200 {user_id, username, email}` | 401 token |
| POST | `/predict` | multipart `file` + `fruit_type?` (Bearer) | `200 {success, data:{fruit_type, maturity_label, confidence, bbox, recommendation, color_code, scan_id}}` | 400 formato/fruta · 401 |
| GET | `/history` | `?limit&offset` (Bearer) | `200 {items[], total, limit, offset}` | 401 · 422 límite |
| POST | `/feedback` | `{scan_id, rating(1-5)}` (Bearer) | `201` | 401 · 422 rating |
| GET | `/health` | — | `200 {status, model, version, model_loaded}` | — |

**Ejemplo `/predict` (respuesta):**
```json
{
  "success": true,
  "data": {
    "fruit_type": "platano", "maturity_label": "OPTIMO",
    "confidence": 0.92, "bbox": [10.0, 20.0, 300.0, 400.0],
    "recommendation": "Punto ideal de consumo. Refrigera para extender 2-3 días más.",
    "color_code": "yellow", "scan_id": "a1b2c3…"
  }
}
```

---

## B. Esquema de base de datos (DDL — PostgreSQL)

```sql
CREATE TABLE users (
    user_id         VARCHAR(36) PRIMARY KEY,
    username        VARCHAR(50)  UNIQUE NOT NULL,
    email           VARCHAR(254) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE scans (
    id             SERIAL PRIMARY KEY,
    user_id        VARCHAR(36) REFERENCES users(user_id),
    fruit_type     VARCHAR(32),
    maturity_label VARCHAR(16),
    confidence     DOUBLE PRECISION,
    bbox           JSON,
    recommendation TEXT,
    color_code     VARCHAR(8),
    created_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE scan_feedback (
    id         SERIAL PRIMARY KEY,
    scan_id    INTEGER REFERENCES scans(id),
    user_id    VARCHAR(36),
    rating     SMALLINT CHECK (rating BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT now()
);
```
> El esquema se gestiona con migraciones **Alembic** (`alembic upgrade head`). En dev el motor es SQLite; en prod, AWS RDS PostgreSQL.

---

## C. Variables de entorno

| Variable | Dev | Producción |
|----------|-----|------------|
| `ENVIRONMENT` | `development` | `production` |
| `JWT_SECRET_KEY` | dev | secreto fuerte (≥32, por entorno) |
| `DB_URL` | `sqlite+aiosqlite:///./maduraapp_dev.db` | `postgresql+asyncpg://…rds.amazonaws.com:5432/maduraapp` |
| `CORS_ORIGINS` | `*` | dominios acotados |
| `CONFIDENCE_THRESHOLD` | `0.55` | `0.55` |

---

## D. Comandos frecuentes

```bash
# Backend
cd Producto/backend && pytest tests/ -v                 # 38 tests
pytest tests/ --cov=app --cov-report=term-missing       # cobertura 76%
alembic upgrade head                                    # migraciones
uvicorn app.main:app --reload

# Android
cd Producto/frontend && ./gradlew testDebugUnitTest     # 19 tests
./gradlew assembleDebug                                 # APK

# Rendimiento
python scripts_perf/medir_rendimiento.py http://<host>:8000

# Despliegue (EC2 + RDS) — ver 11_Arquitectura_AWS.md
```

---

## E. Glosario técnico

YOLO26n · mAP@50 · FastAPI · JWT · bcrypt · AES-256 · OWASP (A01/A02/A07) · MVVM · Room · CameraX · Alembic · CI · IaaS/DBaaS/SaaS · cobertura de código · fixture · mock.

---

## F. Referencias

- FAO / ODEPA — Estadísticas de pérdidas post-cosecha en frutas (Chile).
- OWASP Foundation — *OWASP Top 10* (2021).
- Ultralytics — *YOLO* documentation.
- Google — *Material Design 3* guidelines.
- Microsoft / OpenAPI — convenciones de contrato REST.
- AWS — *RDS PostgreSQL* y *EC2* documentation.
