# Documentación — Evaluación 2 (TPY1101)

> Carpeta de entregables del Estado de Avance 2 de MaduraApp. Lee este archivo primero para navegar el conjunto.

---

## 📄 Documento maestro

**[`00_Informe_Tecnico_Evaluacion_2.md`](00_Informe_Tecnico_Evaluacion_2.md)** — Informe técnico completo. Lee este primero. Incluye índice, resumen, decisiones técnicas y referencias cruzadas a todos los documentos de soporte.

---

## 🏛️ Modelo 4+1 de Kruchten (5 vistas)

| # | Vista | Documento | Audiencia |
|---|-------|-----------|-----------|
| 1 | **Lógica** | [`01_Vista_Logica.md`](01_Vista_Logica.md) | Usuarios finales, analistas |
| 2 | **Procesos** | [`02_Vista_Procesos.md`](02_Vista_Procesos.md) | Integradores de sistemas |
| 3 | **Desarrollo** | [`03_Vista_Desarrollo.md`](03_Vista_Desarrollo.md) | Programadores |
| 4 | **Física** | [`04_Vista_Fisica.md`](04_Vista_Fisica.md) | Ingenieros de infraestructura |
| 5 | **Escenarios (+1)** | [`05_Vista_Escenarios.md`](05_Vista_Escenarios.md) | Todos — integra las 4 anteriores |

Cada vista incluye al menos un diagrama Mermaid renderizable directamente en GitHub/VSCode.

---

## 🎨 Diseño de UI

**[`06_Mockups_y_Wireframes.md`](06_Mockups_y_Wireframes.md)** — Pantallas actualizadas Sprint 2 (selector de fruta, galería), sistema de diseño, flujo de navegación.

---

## ⚙️ Configuración de ambientes (IL2.2)

| Documento | Cubre |
|-----------|-------|
| [`07_Configuracion_Ambiente_Pruebas.md`](07_Configuracion_Ambiente_Pruebas.md) | Ambiente de pruebas local — instalación, levantamiento, smoke tests |
| [`08_Configuracion_Servidor_Produccion.md`](08_Configuracion_Servidor_Produccion.md) | Render + Supabase, render.yaml, despliegue continuo, rollback |
| [`09_Procedimientos_Backup.md`](09_Procedimientos_Backup.md) | Backup BD producción, restauración, replicación de configuración |

---

## ✅ Aseguramiento de calidad (IL2.3)

| Documento | Cubre |
|-----------|-------|
| [`10_Plan_de_Pruebas.md`](10_Plan_de_Pruebas.md) | Pruebas operacionales + validación + verificación; matriz de casos |
| [`11_Estado_Desarrollo.md`](11_Estado_Desarrollo.md) | Avances Sprint 2, patrones, calidad de código, seguridad |
| [`12_Evidencias_Pruebas.md`](12_Evidencias_Pruebas.md) | Logs, métricas, screenshots, KPIs del modelo |

---

## 📚 Anexos

**[`13_Anexos.md`](13_Anexos.md)** — Comandos frecuentes, glosario, endpoints REST, DDL de BD, variables de entorno, bibliografía.

---

## 📂 Carpetas auxiliares

- [`diagramas/`](diagramas/) — Fuentes Mermaid de los diagramas si se desea exportar a PNG/SVG.
- [`capturas/`](capturas/) — Screenshots reales de las evidencias (a tomar pre-defensa).

---

## 🎯 Orden de lectura sugerido

### Para el docente evaluador

1. [`00_Informe_Tecnico_Evaluacion_2.md`](00_Informe_Tecnico_Evaluacion_2.md) — visión general
2. [`05_Vista_Escenarios.md`](05_Vista_Escenarios.md) — casos de uso (ejercita todas las otras vistas)
3. Vistas 4+1 según interés: 01 a 04
4. [`12_Evidencias_Pruebas.md`](12_Evidencias_Pruebas.md) — verificación objetiva del estado

### Para nuevo miembro del equipo

1. [`07_Configuracion_Ambiente_Pruebas.md`](07_Configuracion_Ambiente_Pruebas.md) — levantar el ambiente
2. [`03_Vista_Desarrollo.md`](03_Vista_Desarrollo.md) — entender la organización del código
3. [`11_Estado_Desarrollo.md`](11_Estado_Desarrollo.md) — saber qué hay hecho y por hacer
4. [`13_Anexos.md`](13_Anexos.md) — comandos del día a día

### Para administrador de infraestructura

1. [`04_Vista_Fisica.md`](04_Vista_Fisica.md) — topología
2. [`08_Configuracion_Servidor_Produccion.md`](08_Configuracion_Servidor_Produccion.md) — Render + Supabase
3. [`09_Procedimientos_Backup.md`](09_Procedimientos_Backup.md) — backup / restore

---

## ✏️ Cómo se rinde esta evaluación

| Componente | Ponderación | Cómo se cubre |
|------------|------------|---------------|
| **Encargo (informe)** | 40% del total | Esta carpeta + `Documentación/` ascendente (ERS, diagramas heredados) |
| **Presentación oral** | 60% del total | PowerPoint de apoyo + demo en vivo + Q&A (30 min + 10 min) |

### Conformidad con la rúbrica

| Indicador | Documento principal | Evidencia |
|-----------|-------------------|-----------|
| 1. Diseño con diagramas y documentos | Vistas 01-05 + Mockups + ERS heredado | ✅ |
| 2. Configuración ambiente de pruebas | `07_...` | ✅ |
| 3. Backup BD + servidor + instalación | `08_...` + `09_...` | ✅ |
| 4. Desarrollo de software | `11_...` + código en `Producto/` | ✅ |

---

## 🛠️ Cómo regenerar / actualizar esta documentación

Los documentos son Markdown estándar con diagramas Mermaid. Para:

- **Visualizarlos:** abrir en GitHub web, VSCode con extensión "Markdown Preview Mermaid Support", o cualquier editor compatible.
- **Exportar a PDF:** usar `pandoc` o la función "Print to PDF" del navegador.
- **Exportar a Word:** `pandoc archivo.md -o archivo.docx`.

```bash
# Ejemplo: convertir todo el set a PDF
cd Documentación/Evaluacion_2
for f in *.md; do
  pandoc "$f" -o "${f%.md}.pdf" --pdf-engine=xelatex
done
```

---

*Versión 1.0 — Generado 2026-05-26 — Última edición [fecha de tu defensa].*
