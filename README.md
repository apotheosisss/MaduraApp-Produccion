# MaduraApp — Repositorio de Producción

> **Proyecto de Título — Taller Aplicado de Programación (TPY1101) · DuocUC**
>
> Sistema de análisis de madurez agrícola mediante visión computacional: app Android + API REST + modelo YOLO26n entrenado.

---

## Descripción

MaduraApp permite a consumidores finales y pequeños productores diagnosticar el estado de madurez de frutas climatéricas en tiempo real, usando la cámara de su teléfono Android. El diagnóstico (Inmaduro / Óptimo / Sobre maduro) lo realiza un modelo YOLO26n desplegado en la nube, con recomendaciones agronómicas contextualizadas por fruta.

**Frutas soportadas:** Aguacate Hass · Plátano · Tomate Cherry · Mango

**Resultado del modelo:** mAP@50 = **0.9229** — KPI ≥ 0.75 superado por +17.3 puntos

---

## Estructura del repositorio

```
MaduraApp-Produccion/
├── Documentación/          ← Informes, diagramas, PPT, informe Word
│   ├── Evaluacion_2/       ← Documentación técnica completa (4+1 Kruchten, configs, tests)
│   ├── ERS_MaduraApp_v2.pdf
│   ├── MaduraApp_DiagramaClases_v2.png
│   ├── MaduraApp_MER_v2.png
│   └── ...
├── Gestión/                ← Actas y documentos de gestión del proyecto
├── Producto/               ← Código fuente del sistema
│   ├── backend/            ← API FastAPI + modelo YOLO26n
│   ├── frontend/           ← App Android (Kotlin)
│   ├── scripts/            ← Pipeline de entrenamiento CRISP-DM
│   └── notebooks/          ← Notebook Kaggle/Colab para entrenar
├── render.yaml             ← Blueprint de despliegue en Render
└── README.md               ← Este archivo
```

---

## Tecnologías principales

| Capa | Tecnología | Versión |
|------|-----------|---------|
| App móvil | Android — Kotlin + CameraX + Room | API 29+ |
| Backend | Python + FastAPI + SQLAlchemy async | 3.12 / 0.135 |
| Modelo IA | YOLO26n (Ultralytics) | Enero 2026 |
| Base de datos | PostgreSQL (Supabase) / SQLite (dev) | 16 / — |
| Cloud | Render — Docker, región Oregon | Free tier |
| CI/CD | GitHub Actions | — |

---

## Documentación técnica

Toda la documentación de la Evaluación 2 se encuentra en [`Documentación/Evaluacion_2/`](Documentación/Evaluacion_2/):

| Documento | Descripción |
|-----------|-------------|
| [`00_Informe_Tecnico_Evaluacion_2.md`](Documentación/Evaluacion_2/00_Informe_Tecnico_Evaluacion_2.md) | Informe técnico completo |
| [`01_Vista_Logica.md`](Documentación/Evaluacion_2/01_Vista_Logica.md) → [`05_Vista_Escenarios.md`](Documentación/Evaluacion_2/05_Vista_Escenarios.md) | Modelo 4+1 de Kruchten |
| [`07_Configuracion_Ambiente_Pruebas.md`](Documentación/Evaluacion_2/07_Configuracion_Ambiente_Pruebas.md) | Setup del ambiente de desarrollo |
| [`10_Plan_de_Pruebas.md`](Documentación/Evaluacion_2/10_Plan_de_Pruebas.md) | Plan de pruebas completo |
| [`Informe_Evaluacion_2_MaduraApp.docx`](Documentación/Evaluacion_2/Informe_Evaluacion_2_MaduraApp.docx) | Informe Word para entrega |
| [`MaduraApp_Presentacion_Evaluacion2.pptx`](Documentación/Evaluacion_2/MaduraApp_Presentacion_Evaluacion2.pptx) | Presentación de defensa |

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

El backend se despliega automáticamente en **Render** al hacer push a `main`, usando la configuración de [`render.yaml`](render.yaml).

La base de datos de producción es **Supabase** (PostgreSQL 16, tier gratuito).

---

*Proyecto académico — DuocUC · Taller Aplicado de Programación (TPY1101) · 2026*
