# MaduraApp — Repositorio de Producción

> **Proyecto de Título — Taller Aplicado de Programación (TPY1101) · DuocUC**
>
> Sistema de análisis de madurez agrícola mediante visión computacional: app Android + API REST + modelo YOLO26n entrenado.

---

## Descripción

MaduraApp permite a consumidores finales y pequeños productores diagnosticar el estado de madurez de frutas climatéricas en tiempo real, usando la cámara de su teléfono Android. El diagnóstico (Inmaduro / Óptimo / Sobre maduro) lo realiza un modelo YOLO26n desplegado en la nube, con recomendaciones agronómicas contextualizadas por fruta. La app cuenta con autenticación de usuario (JWT), historial de escaneos con cache offline y feedback sobre los diagnósticos.

**Frutas soportadas:** Aguacate Hass · Plátano · Tomate Cherry · Mango

**Resultado del modelo:** mAP@50 = **0.9229** — KPI ≥ 0.75 superado por +17.3 puntos

**Calidad:** 57/57 pruebas automatizadas en verde (38 backend + 19 Android) · 76% de cobertura backend

---

## Estructura del repositorio

```
MaduraApp-Produccion/
├── Documentación/
│   ├── Evaluacion_2/       ← Arquitectura 4+1 (Kruchten), configuración, plan de pruebas inicial
│   ├── Evaluacion_3/       ← Documentación vigente: plan de pruebas, resultados, mejoras,
│   │                          gestión (SMART), arquitectura AWS, actas de avance firmadas
│   ├── diagramas/          ← Gantt, Ishikawa, casos de uso, clases, MER
│   └── ...
├── Gestión/                ← Documentos de registro y gestión del proyecto
├── Producto/                ← Código fuente del sistema
│   ├── backend/            ← API FastAPI (auth, predict, history, feedback) + modelo YOLO26n
│   ├── frontend/           ← App Android (Kotlin, CameraX, Room, MVVM)
│   ├── scripts/            ← Pipeline de entrenamiento CRISP-DM
│   └── notebooks/          ← Notebook Kaggle/Colab para entrenar
└── README.md               ← Este archivo
```

---

## Tecnologías principales

| Capa | Tecnología | Versión |
|------|-----------|---------|
| App móvil | Android — Kotlin + CameraX + Room | API 29+ |
| Backend | Python + FastAPI + SQLAlchemy async | 3.12 / 0.135 |
| Modelo IA | YOLO26n (Ultralytics) | Enero 2026 |
| Base de datos | AWS RDS PostgreSQL 16 (prod) / SQLite (dev-test) | — |
| Cloud | AWS EC2 (Docker) + AWS RDS — AWS Academy Learner Lab | — |
| CI/CD | GitHub Actions (`backend_ci.yml`) | — |

---

## Documentación técnica

La documentación **vigente** del proyecto está en [`Documentación/Evaluacion_3/`](Documentación/Evaluacion_3/):

| Documento | Descripción |
|-----------|-------------|
| [`00_Informe_Tecnico_Evaluacion_3.md`](Documentación/Evaluacion_3/00_Informe_Tecnico_Evaluacion_3.md) | Informe técnico consolidado (versión Word: `Informe_Tecnico_Evaluacion_3_MaduraApp.docx`) |
| [`01_Plan_de_Pruebas.md`](Documentación/Evaluacion_3/01_Plan_de_Pruebas.md) → [`06_Conclusion_Lecciones.md`](Documentación/Evaluacion_3/06_Conclusion_Lecciones.md) | Plan de pruebas, base de datos de pruebas, resultados, mejoras, control de versiones, conclusión |
| [`08_Deploy_AWS_LearnerLab.md`](Documentación/Evaluacion_3/08_Deploy_AWS_LearnerLab.md) | Guía operativa de despliegue en AWS Learner Lab |
| [`09_Pruebas_Rendimiento.md`](Documentación/Evaluacion_3/09_Pruebas_Rendimiento.md) | Tiempos de respuesta y pruebas de concurrencia |
| [`10_Gestion_Proyecto.md`](Documentación/Evaluacion_3/10_Gestion_Proyecto.md) | Objetivos SMART, alcance, justificación cloud, atributos de calidad, certificación |
| [`11_Arquitectura_AWS.md`](Documentación/Evaluacion_3/11_Arquitectura_AWS.md) | Arquitectura AWS (EC2 + RDS), Docker, variables de entorno, backup |
| [`12_Anexos.md`](Documentación/Evaluacion_3/12_Anexos.md) | Contrato de API, DDL, variables de entorno, comandos, glosario |
| `Reporte_Pruebas_MaduraApp.html` | Reporte auto-contenido con las 57 pruebas |
| `Acta_Avance_EP1/EP2/EP3_MaduraApp.pdf` | Actas de avance firmadas (estudiante y docente) |

La documentación de la **Evaluación 2** (`Documentación/Evaluacion_2/`) se conserva como referencia histórica del diseño de arquitectura 4+1; la infraestructura descrita ahí (Render/Supabase) fue **reemplazada por AWS** — ver [`11_Arquitectura_AWS.md`](Documentación/Evaluacion_3/11_Arquitectura_AWS.md) para la versión vigente.

---

## Inicio rápido

Ver instrucciones detalladas en [`Producto/README.md`](Producto/README.md).

```bash
# Clonar y levantar el backend
git clone https://github.com/apotheosisss/MaduraApp-Produccion.git
cd MaduraApp-Produccion/Producto/backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

---

## Despliegue en producción

El backend corre en una instancia **AWS EC2 (`t3.small`)** dentro de un contenedor Docker, conectado a una base de datos **AWS RDS PostgreSQL** (`db.t3.micro`), ambos en el AWS Academy Learner Lab. La selección de base de datos es config-driven (`DB_URL`), por lo que el mismo código corre en SQLite (dev/test) o PostgreSQL (producción) sin cambios.

Detalles completos de la arquitectura, configuración de servidores y procedimientos de backup en [`Documentación/Evaluacion_3/11_Arquitectura_AWS.md`](Documentación/Evaluacion_3/11_Arquitectura_AWS.md).

---

*Proyecto académico — DuocUC · Taller Aplicado de Programación (TPY1101) · 2026*
