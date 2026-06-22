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
| 01 | [`01_Plan_de_Pruebas.md`](01_Plan_de_Pruebas.md) | 1 — Plan de pruebas (36 casos en tabla) |
| 02 | [`02_Base_Datos_Pruebas.md`](02_Base_Datos_Pruebas.md) | 1 — Base de datos de pruebas |
| 03 | [`03_Aplicacion_Pruebas_Resultados.md`](03_Aplicacion_Pruebas_Resultados.md) | 2 — Aplicación de pruebas de validación |
| 04 | [`04_Mejoras_Producto.md`](04_Mejoras_Producto.md) | 3 — Mejoras al producto (5 estándares) |
| 05 | [`05_Evidencia_Control_Versiones.md`](05_Evidencia_Control_Versiones.md) | 4 — Evidencias / control de versiones |
| 06 | [`06_Conclusion_Lecciones.md`](06_Conclusion_Lecciones.md) | 4 — Conclusión y lecciones |

---

## 🎤 Presentación (defensa — 70%)

- **`MaduraApp_Presentacion_Evaluacion3.pptx`** — 9 slides con notas de orador.
- [`07_Guion_Defensa.md`](07_Guion_Defensa.md) — Guion, distribución de tiempo y preguntas probables con respuestas.

---

## 🔧 Scripts de generación

- `_gen_informe.py` — genera el Word desde el contenido.
- `_gen_ppt.py` — genera el PPT.

Reproducibles con `python _gen_informe.py` / `python _gen_ppt.py` (requiere `python-docx` y `python-pptx`).

---

## ✅ Resumen de cumplimiento

- **36/36 pruebas** automatizadas en verde (17 backend + 19 Android).
- **15 mejoras** trazables a commits, por estándar de calidad.
- **Integración continua** (`backend_ci.yml`) ejecutando la suite en cada push.
- Pendiente honesto: despliegue en AWS Lab y aprobación del plan en la defensa.
