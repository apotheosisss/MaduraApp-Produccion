# Análisis de Brechas — Documentación MaduraApp vs Formato Exigido (EVP3)

> Comparación de toda la documentación EVP2 + EVP3 contra: (a) el documento de referencia del docente *"Servicio Micro-Firma Hash (FirmaGob)"*, (b) las instrucciones del docente (correo) y (c) el estándar Duoc *aspectos-formales-de-un-informe*.
> Fecha del análisis: 25/06/2026.

---

## A. Veredicto general

El material de EVP3 sobre **pruebas, mejoras y rendimiento es sólido y excede lo pedido**. Sin embargo, frente al **formato de informe** que exige el docente (estructura del PDF de referencia), faltan secciones de **gestión de proyecto** y hay **discrepancias de consistencia arquitectónica** que el propio docente marcó como punto clave. Hay que **consolidar un único informe** con la estructura de referencia y **reconciliar el despliegue (Render→AWS)**.

---

## B. Mapa: estructura de referencia → ¿lo tenemos?

### Parte 1 — Descripción y Gestión de Proyecto

| # | Sección del formato | Estado | Dónde está / Brecha |
|---|---------------------|--------|---------------------|
| 1 | Contexto e impacto en el proceso de negocio | ⚠️ Parcial | Hay contexto (pérdidas post-cosecha) pero **falta el impacto cuantificado** en el proceso de negocio |
| 2 | Descripción del problema (Ishikawa) | ✅ | EV1 + `Ishikawa.png` |
| 3 | Diagnóstico (árbol de problemas) | ⚠️ Parcial | Ishikawa sí; árbol de problemas formal, no |
| 4 | **Objetivos SMART cuantificables (OE-01…)** | ❌ **FALTA** | No existen objetivos con métricas (ms, %, KB, cobertura). **Crítico** |
| 5 | Alcance (técnico, entregables, **supuestos**, **restricciones**) | ⚠️ Parcial | Alcance sí; **supuestos y restricciones no están explícitos** |
| 5b | Planificación (Carta Gantt por fases) | ✅ | `Gantt_MaduraApp_v2.png` |
| 6 | **Arquitectura cloud + justificación PaaS/SaaS/IaaS** | ❌ **FALTA** | No se justifica el modelo de servicio cloud; además el modelo real cambió (ver discrepancias) |
| 7 | **Conceptualización y Atributos de Calidad** | ❌ **FALTA** | No hay sección que liste Integridad / Confiabilidad-Seguridad / Precisión-Oportunidad |
| 8 | **Estrategia de certificación y revisiones parciales** | ❌ **FALTA** | No hay criterios de aceptación mandatorios documentados |

### Parte 2 — Diseño de Arquitectura, Ambientes y Plan de Pruebas

| # | Sección del formato | Estado | Dónde está / Brecha |
|---|---------------------|--------|---------------------|
| 1 | Modelo 4+1 de Kruchten (5 vistas) | ✅ | EV2 `01`–`05` (con diagramas Mermaid) |
| 2 | Config. de servidores (Prod/Pruebas) — Dockerfile + `.env` | ⚠️ | Existe (EV2 `07`,`08`) pero **describe Render/Supabase, no AWS** |
| 3 | Backup & Restore | ⚠️ | EV2 `09` usa `pg_dump`/Supabase; el deploy real es **SQLite** |

### Ítems de autoría del alumno (correo del docente)

| Ítem | Sección | Estado |
|------|---------|--------|
| 6 | **Aprendizajes** (en profundidad) | ⚠️ Hay lecciones (EV3 `06`) pero hay que desarrollarlas más |
| 7 | **Anexos** (en profundidad) | ⚠️ Hay anexos EV2 `13`; actualizar y profundizar |

---

## C. Los 4 puntos clave del docente

| Punto del docente | Estado | Acción requerida |
|-------------------|--------|------------------|
| **Delimitación del alcance (matemática/técnica)** | ❌ | Cuantificar el impacto: % de pérdidas evitables, tamaño de payload, latencia objetivo, etc. |
| **Métricas SMART** (ms, tasas, % cobertura) | ❌ | Crear objetivos OE-01/02/03 con números. **Tenemos los datos** (mAP 0,92; ~200 ms; 0 errores @50) pero falta **cobertura de código** (nunca medida) |
| **Consistencia arquitectónica** (diagramas ↔ Docker ↔ pruebas) | ❌ | Los diagramas dicen **Render/Supabase**; el Docker y el deploy real son **AWS/SQLite**. **Reconciliar** |
| **Aprendizajes y Anexos (ítems 6 y 7)** | ⚠️ | Profundizar ambas secciones |

---

## D. Discrepancias críticas (información que NO coincide entre documentos)

1. **Despliegue: Render vs AWS** — EV2 (`04_Vista_Fisica`, `08_Config_Servidor`, `09_Backup`) describe **Render Free + Supabase PostgreSQL** (`https://maduraapp-backend.onrender.com`). EV3 desplegó en **AWS EC2 t3.small + Docker + cloudflared/Elastic IP**. *Toda la Parte de infraestructura está desactualizada.*
2. **Base de datos: PostgreSQL vs SQLite** — EV2/diagramas/backup asumen **Supabase PostgreSQL**; el deploy real en AWS usa **SQLite** en la instancia. Los procedimientos de backup (`pg_dump`/`pg_restore`) **no aplican** a SQLite.
3. **Conteo de pruebas** — EV2 `10_Plan_de_Pruebas` habla de **9 tests backend**; EV3 son **57** (38 backend + 19 Android). El plan de EV2 está obsoleto (esperable, pero el informe consolidado debe usar 57).
4. **Modelo de servicio cloud** — La referencia valora **PaaS** (App Runner/Container Apps). Nosotros usamos **EC2 = IaaS** (más mantenimiento). Hay que **justificar honestamente** por qué EC2 (restricción del AWS Academy Learner Lab) en vez de presentarlo como PaaS.
5. **URL/keepalive** — Existe `keepalive.yml` apuntando a Render (servicio abandonado). Inconsistente con el deploy actual.

> ✅ **Sí coinciden** (sin discrepancia): mAP@50 = 0,9229 · 4 frutas × 3 estados · stack Kotlin/FastAPI/YOLO26n · las 57 pruebas y mejoras (EV3 internamente consistente tras la última corrección).

---

## E. Brechas faltantes — priorizadas

| Prioridad | Falta | Esfuerzo | Nota |
|-----------|-------|----------|------|
| 🔴 Alta | **Objetivos SMART (OE-01/02/03)** con métricas | Bajo | Tenemos casi todos los datos |
| 🔴 Alta | **Cobertura de código** (medir y reportar %) | Bajo | Instalar `pytest-cov`, correr, documentar |
| 🔴 Alta | **Reconciliar arquitectura** (diagramas/config → AWS+SQLite) | Medio | Actualizar Vista Física, Config Servidor, Backup |
| 🔴 Alta | **Justificación cloud (PaaS/SaaS/IaaS)** honesta | Bajo | Explicar EC2 (IaaS) por restricción del Learner Lab |
| 🟡 Media | **Atributos de Calidad** (sección dedicada) | Bajo | Reusar seguridad/rendimiento ya hechos |
| 🟡 Media | **Estrategia de certificación / criterios de aceptación** | Bajo | Formalizar (KPI ≥0,75; 57/57; <X ms; cobertura ≥Y%) |
| 🟡 Media | **Supuestos y restricciones** del proyecto | Bajo | Redactar (Learner Lab temporal, sin GPU, plazo) |
| 🟡 Media | **Delimitación del alcance cuantificada** | Bajo | % pérdidas, payload, latencia |
| 🟢 Baja | **Aprendizajes y Anexos** en profundidad | Medio | Ampliar EV3 `06` y EV2 `13` |
| 🟢 Baja | **Informe consolidado único** con formato Duoc | Medio | Portada, índice, intro, desarrollo, conclusión, referencias APA |

---

## F. Recomendación (plan de acción para el jueves)

1. **Crear el documento de "Gestión de Proyecto"** (Parte 1 del formato): contexto+impacto cuantificado, objetivos SMART, alcance/supuestos/restricciones, justificación cloud, atributos de calidad, estrategia de certificación.
2. **Medir y reportar cobertura de código** (pytest-cov) → cierra OE-03 y el punto SMART del docente.
3. **Reconciliar la arquitectura**: actualizar Vista Física, Config de Servidor y Backup a **AWS EC2 + Docker + SQLite**, o declarar claramente "diseño objetivo (PostgreSQL/PaaS) vs implementación de laboratorio (SQLite/EC2)".
4. **Profundizar Aprendizajes y Anexos**.
5. **Consolidar todo** en un único informe con el formato formal Duoc.

> El trabajo técnico está hecho; lo que falta es **encuadrarlo en el formato de gestión de proyecto** que exige el docente y **eliminar las contradicciones Render↔AWS**.
