# Documentación — Evaluación 3 (TPY1101)

> Entregables del **Estado de Avance 3** de MaduraApp. Foco: plan de pruebas, aplicación de pruebas de validación y mejoras al producto.
>
> **Estudiante:** Claudio Vicente Aro Kath · RUT 22.022.498-8 · Sección 001D

---

## 📄 Documento maestro

**[`00_Informe_Tecnico_Evaluacion_3.md`](00_Informe_Tecnico_Evaluacion_3.md)** — Informe técnico consolidado (incluye resumen Eval 1 y 2). Versión Word: **`Informe_Tecnico_Evaluacion_3_MaduraApp.docx`**.

---

## 📋 Entregables del encargo

| # | Documento | Criterio rúbrica |
|---|-----------|------------------|
| 01 | [`01_Plan_de_Pruebas.md`](01_Plan_de_Pruebas.md) | 1 — Plan de pruebas (57 casos en tabla) |
| 02 | [`02_Base_Datos_Pruebas.md`](02_Base_Datos_Pruebas.md) | 1 — Base de datos de pruebas |
| 03 | [`03_Aplicacion_Pruebas_Resultados.md`](03_Aplicacion_Pruebas_Resultados.md) | 2 — Aplicación de pruebas de validación |
| 04 | [`04_Mejoras_Producto.md`](04_Mejoras_Producto.md) | 3 — Mejoras al producto (5 estándares) |
| 05 | [`05_Evidencia_Control_Versiones.md`](05_Evidencia_Control_Versiones.md) | 4 — Evidencias / control de versiones |
| 06 | [`06_Conclusion_Lecciones.md`](06_Conclusion_Lecciones.md) | 4 — Conclusión y lecciones |
| 08 | [`08_Deploy_AWS_LearnerLab.md`](08_Deploy_AWS_LearnerLab.md) | Guía operativa de despliegue (AWS Learner Lab) |
| 09 | [`09_Pruebas_Rendimiento.md`](09_Pruebas_Rendimiento.md) | Tiempos de respuesta y concurrencia (obs. docente) |
| 10 | [`10_Gestion_Proyecto.md`](10_Gestion_Proyecto.md) | Gestión: objetivos SMART, alcance, justificación cloud, atributos de calidad, certificación |
| 11 | [`11_Arquitectura_AWS.md`](11_Arquitectura_AWS.md) | Arquitectura AWS (EC2 + RDS), Docker, env, backup — **reemplaza la infra de EV2** |
| 12 | [`12_Anexos.md`](12_Anexos.md) | Contrato de API, DDL, variables de entorno, comandos, glosario, referencias |

> **Diagramas nuevos:** `../diagramas/Gantt_MaduraApp_v3.png` · diagrama de despliegue (Mermaid) en el doc 11.
> **Análisis de coherencia:** [`ANALISIS_BRECHAS_vs_Formato.md`](ANALISIS_BRECHAS_vs_Formato.md) — comparación con el formato institucional.

**Evidencia de pruebas:** **`Reporte_Pruebas_MaduraApp.html`** — reporte auto-contenido con las 57 pruebas.

---

## ✍️ Actas de avance (para firmar)

- **`Acta_Avance_EP1_MaduraApp.pdf`** · **`Acta_Avance_EP2_MaduraApp.pdf`** · **`Acta_Avance_EP3_MaduraApp.pdf`**
- Cada una con identificación, fecha, entregables y espacio para firma de **estudiante** y **docente**.

---

## 🎤 Presentación (defensa — 70%)

- **`MaduraApp_Presentacion_Evaluacion3.pptx`** — 9 slides con notas de orador.
- **`MaduraApp_Presentacion_Evaluacion3_GRABAR.pptx`** — versión con narración verbatim para grabar video.
- [`07_Guion_Defensa.md`](07_Guion_Defensa.md) — Preguntas probables del Q&A en detalle.
- **`Guion_Celular_Defensa.pdf`** — guion de bolsillo (Di / Clave / Si profundizan) para el celular.
- **`Guion_Narracion_Grabacion.md`** — narración verbatim (teleprompter).

---

## 🔧 Scripts de generación

- `_gen_informe.py` — genera el Word desde el contenido.
- `_gen_ppt.py` — genera el PPT.

Reproducibles con `python _gen_informe.py` / `python _gen_ppt.py` (requiere `python-docx` y `python-pptx`).

---

## ✅ Resumen de cumplimiento

- **57/57 pruebas** automatizadas en verde (38 backend + 19 Android).
- **15 mejoras** trazables a commits, por estándar de calidad.
- **Integración continua** (`backend_ci.yml`) ejecutando la suite en cada push.
- Pendiente honesto: despliegue en AWS Lab y aprobación del plan en la defensa.
