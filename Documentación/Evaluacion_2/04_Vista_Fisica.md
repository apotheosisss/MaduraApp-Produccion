# Vista Física — MaduraApp

> ⚠️ **Actualizado en EP3:** la arquitectura migró a **AWS EC2 + RDS PostgreSQL** (en EP2 el backend se hosteó desde el PC del estudiante de forma remota). La descripción basada en Render/Supabase de este documento corresponde al diseño de la Evaluación 2 y fue **reemplazada** por [`../Evaluacion_3/11_Arquitectura_AWS.md`](../Evaluacion_3/11_Arquitectura_AWS.md) y [`../Evaluacion_3/10_Gestion_Proyecto.md`](../Evaluacion_3/10_Gestion_Proyecto.md).
## Modelo 4+1 de Kruchten · Vista 4 de 5

> La **Vista Física** (también llamada Vista de Despliegue) documenta la **topología hardware/software** sobre la cual se ejecuta el sistema. Describe los **nodos físicos**, los **artefactos desplegados** en cada nodo y las **comunicaciones** entre ellos. Responde a la pregunta **¿dónde corre cada cosa y cómo se conecta?**

---

## 1. Propósito y audiencia

| Aspecto | Detalle |
|---------|---------|
| **Audiencia primaria** | Ingenieros de infraestructura, DevOps, equipo de operaciones |
| **Preocupación** | Topología de despliegue, performance, disponibilidad, costo, seguridad de red |
| **Notación principal** | UML — diagrama de despliegue |

---

## 2. Topología general del sistema

MaduraApp se despliega como un **sistema distribuido de tres niveles** + cliente móvil:

```mermaid
graph TB
    subgraph "Cliente — Smartphone Android"
        APK[APK MaduraApp<br/>Material 3 UI<br/>CameraX<br/>Room SQLite local]
    end

    subgraph "Internet"
        NET[HTTPS<br/>TLS 1.3]
    end

    subgraph "Cloud — Render Free Tier (Oregon, US-West)"
        CONT[Docker Container<br/>Python 3.12 + FastAPI<br/>YOLO26n + PyTorch CPU<br/>512 MB RAM · 0.1 CPU]
        VOL[Volume layer<br/>weights/yolo26n_maduraapp.pt]
    end

    subgraph "DBaaS — Supabase (AWS US-East)"
        PG[(PostgreSQL 16<br/>Tier Free 500 MB<br/>tabla scans)]
        POOL[Session pooler<br/>asyncpg compatible]
    end

    subgraph "CI/CD — GitHub Actions"
        GHA[Runner Ubuntu<br/>pytest backend<br/>keepalive workflow]
    end

    subgraph "Source Control — GitHub"
        REPO[(MaduraApp-Produccion<br/>repo público)]
    end

    APK <-->|HTTPS multipart<br/>POST /v1/predict<br/>GET /v1/history| NET
    NET <--> CONT
    CONT <-->|TLS<br/>PostgreSQL wire| POOL
    POOL --> PG
    CONT --- VOL
    REPO -->|push main| GHA
    GHA -->|deploy hook| CONT
    GHA -->|keepalive ping<br/>cada 14 min| CONT

    style APK fill:#e1f5ff
    style CONT fill:#fff4e1
    style PG fill:#ffe1e1
    style GHA fill:#e1ffe1
```

---

## 3. Nodos del sistema

### 3.1 Nodo cliente — Dispositivo Android

| Atributo | Valor |
|----------|-------|
| **Tipo** | Dispositivo móvil físico |
| **OS** | Android 10+ (API 29+) |
| **Hardware mínimo** | 2 GB RAM, cámara con autoenfoque, 50 MB libres |
| **Conectividad requerida** | Datos móviles / WiFi (HTTPS outbound) para escaneo<br/>Offline para visualización de historial cacheado |
| **Artefactos desplegados** | `maduraapp-1.0.apk` (~ 8-12 MB) |
| **Almacenamiento local** | Room database (~ 500 KB en uso típico de 50 escaneos) |
| **Permisos solicitados** | CAMERA, INTERNET, ACCESS_NETWORK_STATE |

**Distribución del APK:** durante el ciclo académico, instalación manual desde APK firmado debug. Para futuro: Google Play (requiere release signing key).

### 3.2 Nodo backend — Render Container

| Atributo | Valor |
|----------|-------|
| **Tipo** | Contenedor Docker administrado |
| **Plataforma** | Render — `plan: free` |
| **Región** | Oregon, US-West |
| **CPU** | 0.1 vCPU compartido |
| **RAM** | 512 MB |
| **Almacenamiento ephemeral** | Capa de imagen Docker (incluye `weights/yolo26n_maduraapp.pt`) |
| **Base de la imagen** | `python:3.12-slim` |
| **Puerto expuesto** | 8000 (mapeado a 443 externo HTTPS por Render) |
| **Health check** | `GET /v1/health` cada 30 s |
| **Sleep policy** | Suspende tras 15 min sin tráfico → cold start ~30-60 s |
| **URL pública** | `https://maduraapp-backend.onrender.com` (placeholder, depende del nombre asignado) |
| **TLS** | Gestionado automáticamente por Render (Let's Encrypt) |

**Artefactos desplegados:**

```
/app/
├── app/                    # Código FastAPI
├── alembic/                # Migraciones
├── weights/
│   └── yolo26n_maduraapp.pt    # Modelo de inferencia (5.2 MB)
├── requirements.txt
└── Dockerfile (entrypoint)
```

**Comando de entrada (Dockerfile):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 3.3 Nodo base de datos — Supabase PostgreSQL

| Atributo | Valor |
|----------|-------|
| **Tipo** | Base de datos relacional gestionada |
| **Plataforma** | Supabase (DBaaS) |
| **Motor** | PostgreSQL 16 |
| **Plan** | Free tier (500 MB almacenamiento, 5 GB transferencia mes) |
| **Hospedaje** | AWS US-East |
| **Conexión** | TLS sobre PostgreSQL wire protocol |
| **Connection pooling** | Session pooler nativo (PgBouncer) |
| **Backups** | Backup automático diario (gestionado por Supabase) |
| **Esquema desplegado** | Tabla `scans` (ver MER en [`MaduraApp_MER_v2.png`](../MaduraApp_MER_v2.png)) |
| **Cadena de conexión** | `postgresql+asyncpg://user:pass@host:5432/postgres` |

### 3.4 Nodo CI/CD — GitHub Actions

| Atributo | Valor |
|----------|-------|
| **Tipo** | Runners efímeros administrados |
| **OS** | Ubuntu Latest |
| **Disparadores** | `push` a cualquier rama, `pull_request` a main, schedule cron (keepalive) |
| **Workflows desplegados** | `backend_ci.yml`, `keepalive.yml` |
| **Secrets utilizados** | (Ninguno — el proyecto no requiere credenciales privadas en CI actualmente) |

---

## 4. Diagrama de despliegue UML detallado

```mermaid
graph LR
    subgraph mob[" «device» Smartphone Android "]
        direction TB
        mob_apk["«artifact»<br/>maduraapp.apk<br/>━━━━━━━━━━━<br/>FruitSelectorActivity<br/>MainActivity<br/>HistoryActivity<br/>+ Room SQLite"]
    end

    subgraph render[" «cloud node» Render Web Service "]
        direction TB
        render_dock["«container»<br/>Docker container<br/>━━━━━━━━━━━<br/>uvicorn + FastAPI<br/>YOLO26 + PyTorch CPU"]
        render_pt["«artifact»<br/>yolo26n_maduraapp.pt<br/>5.2 MB"]
        render_dock --- render_pt
    end

    subgraph sb[" «cloud node» Supabase PostgreSQL "]
        sb_db["«database»<br/>scans table"]
    end

    subgraph gh[" «cloud node» GitHub "]
        gh_repo["«repository»<br/>MaduraApp-Produccion"]
        gh_act["«workflow»<br/>backend_ci.yml<br/>keepalive.yml"]
    end

    mob_apk -.->|"«protocol»<br/>HTTPS/TLS 1.3<br/>multipart/form-data"| render_dock
    render_dock -.->|"«protocol»<br/>TLS<br/>PostgreSQL wire"| sb_db
    gh_repo -.->|"«deploy hook»"| render_dock
    gh_act -.->|"«HTTPS GET»"| render_dock

    style mob_apk fill:#e1f5ff
    style render_dock fill:#fff4e1
    style sb_db fill:#ffe1e1
    style gh_repo fill:#e1ffe1
    style gh_act fill:#e1ffe1
```

---

## 5. Protocolos de comunicación

### 5.1 Android ↔ Backend

| Endpoint | Método | Protocolo | Content-Type | Auth | Timeout cliente |
|----------|--------|-----------|--------------|------|-----------------|
| `/v1/predict` | POST | HTTPS | `multipart/form-data` (file JPEG/PNG/WebP + fruit_type opcional) | `Authorization: Bearer <token>` opcional | 30 s |
| `/v1/history` | GET | HTTPS | `application/json` | Idem | 30 s |
| `/v1/health` | GET | HTTPS | `application/json` | No requiere | 15 s |

**Tamaño máximo del request:** 10 MB (limitado en `inference_service.MAX_IMAGE_BYTES`).

### 5.2 Backend ↔ PostgreSQL

| Aspecto | Detalle |
|---------|---------|
| Driver | `asyncpg` 0.29+ |
| Pool | gestionado por SQLAlchemy AsyncEngine |
| SSL | obligatorio en producción (`sslmode=require`) |
| Connection string | desde env var `DB_URL`, jamás hardcodeado |

### 5.3 GitHub Actions ↔ Render

| Aspecto | Detalle |
|---------|---------|
| Deploy automático | Webhook nativo de Render escucha push a `main` |
| Keepalive | GitHub Actions ejecuta `curl https://.../v1/health` cada 14 min (cron `*/14 * * * *`) |
| Notificaciones | Email de Render en fallos de deploy |

---

## 6. Consideraciones de seguridad de red

| Riesgo | Mitigación implementada |
|--------|-------------------------|
| **Interceptación de tráfico** | HTTPS obligatorio extremo-a-extremo (Android → Render → Supabase) |
| **Exfiltración de credenciales en repo** | Variables sensibles en `render.yaml` con `sync: false`; `.env` en `.gitignore` |
| **DoS por imágenes gigantes** | Validación de tamaño 10 MB y Content-Type allowlist en `predict.py` |
| **SQL injection** | Acceso a BD exclusivamente vía ORM (SQLAlchemy parametrizado) |
| **Cleartext traffic dev** | `android:usesCleartextTraffic="true"` solo para builds debug contra localhost; release builds requerirán HTTPS estricto |
| **CORS** | Configurado para orígenes explícitos en `main.py` (no `*` en producción) |

---

## 7. Estrategia de monitoreo y observabilidad

| Capa | Herramienta actual | Tipo de visibilidad |
|------|--------------------|---------------------|
| Backend logs | Render dashboard (stdout/stderr stream) | Logs runtime, errores, latencias |
| Backend health | Endpoint `/v1/health` polled por keepalive | Up/down + model loaded |
| BD | Supabase dashboard | Storage usage, conexiones activas, slow queries |
| Cliente Android | Logcat local en debug; `Log.e(TAG, ...)` en cada error | Errores cliente |
| CI | GitHub Actions logs | Build status, tests passing |

**Trabajo futuro (no parte de Evaluación 2):** Sentry para errores Android, Render metrics avanzadas, Grafana sobre Supabase.

---

## 8. Plan de contingencia

| Evento | Severidad | Acción |
|--------|-----------|--------|
| Render Free duerme post-15 min idle | Baja | Keepalive workflow lo mantiene activo durante horario académico |
| Render Free agota cuota mensual | Media | Cambiar `plan: standard` en `render.yaml` ($25/mo) |
| Supabase BD llena (500 MB) | Baja | Cleanup script: borrar scans con > 90 días de antigüedad |
| OOM al cargar modelo en cold start | Alta | Warmup deshabilitado en producción (ya mitigado); plan B: quantizar a INT8 |
| GitHub Actions agota minutos free | Muy baja | Reducir frecuencia keepalive a cada 30 min |

---

## 9. Justificación de decisiones de infraestructura

### 9.1 ¿Por qué Render?

- **Docker nativo** sin configuración compleja.
- **Free tier funcional** para proyecto académico (a diferencia de Heroku que eliminó el suyo en 2022).
- **Auto-deploy desde Git** sin pipelines manuales.
- **TLS gestionado** sin trabajo manual de certificados.

### 9.2 ¿Por qué no AWS / GCP / Azure?

- Curva de configuración alta para proyecto de tiempo limitado.
- Free tiers requieren tarjeta de crédito.
- Justificación académica: el foco del ramo es el **desarrollo del producto**, no la administración de infraestructura cloud avanzada.

### 9.3 ¿Por qué Supabase y no Render PostgreSQL?

- Render solo ofrece PostgreSQL en plan Standard ($7/mo mínimo).
- Supabase free tier (500 MB) es suficiente para el volumen del proyecto.
- Supabase ofrece dashboard de consultas y backups automáticos.

### 9.4 ¿Por qué CPU y no GPU?

- YOLO26n (nano) está optimizado para CPU, alcanza latencias aceptables (~ 300 ms).
- GPUs en cloud son significativamente más caras (mínimo ~$30/mo).
- Proyecto académico no requiere throughput de producción real.

---

## 10. Relación con otras vistas

- **Vista Lógica** ([`01_Vista_Logica.md`](01_Vista_Logica.md)) — esta vista ubica físicamente los componentes lógicos.
- **Vista de Procesos** ([`02_Vista_Procesos.md`](02_Vista_Procesos.md)) — los procesos definidos en runtime corren en los nodos físicos descritos aquí.
- **Vista de Desarrollo** ([`03_Vista_Desarrollo.md`](03_Vista_Desarrollo.md)) — los artefactos del repo se empaquetan y despliegan en los nodos físicos.
