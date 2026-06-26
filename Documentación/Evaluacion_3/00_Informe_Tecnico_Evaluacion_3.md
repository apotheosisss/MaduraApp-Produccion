# Informe Técnico — Estado de Avance 3

**MaduraApp: Sistema de Análisis de Madurez Agrícola mediante Visión Computacional**

| | |
|---|---|
| **Asignatura** | Taller Aplicado de Programación (TPY1101) |
| **Sección** | 001D |
| **Estudiante** | Claudio Vicente Aro Kath — RUT 22.022.498-8 |
| **Docente guía** | José Ignacio Campos Arévalo |
| **Fecha** | Junio 2026 |
| **Repositorio** | https://github.com/apotheosisss/MaduraApp-Produccion |

---

## Índice

1. Introducción
2. Resumen Evaluación 1 — Problema y requisitos
3. Resumen Evaluación 2 — Arquitectura y producto
4. Evaluación 3 — Pruebas y mejoras
   - 4.1 Plan de pruebas
   - 4.2 Base de datos de pruebas
   - 4.3 Aplicación de pruebas y resultados
   - 4.4 Mejoras al producto
   - 4.5 Control de versiones
5. Conclusión y lecciones aprendidas
6. Anexos

---

## 1. Introducción

Las pérdidas post-cosecha en frutas climatéricas (aguacate, plátano, tomate, mango) representan en Chile entre un **20% y un 40%** de la producción según FAO/ODEPA. Una causa raíz es la **falta de criterios objetivos y accesibles** para determinar el punto óptimo de consumo.

**MaduraApp** es un sistema de visión computacional accesible desde el móvil que clasifica el estado de madurez de cuatro frutas climatéricas en tres categorías (Inmaduro / Óptimo / Sobre maduro) y entrega recomendaciones agronómicas en tiempo real.

Este informe corresponde al **Estado de Avance 3**, cuyo foco es el aseguramiento de calidad: el plan de pruebas, su aplicación a los componentes del proyecto y las mejoras derivadas de los resultados.

---

## 2. Resumen Evaluación 1 — Problema y requisitos

- **Problemática:** pérdidas post-cosecha por falta de criterios objetivos de madurez (diagrama de Ishikawa).
- **Solución propuesta:** app móvil + IA que clasifica madurez y recomienda acción.
- **Requisitos funcionales (RF-01…RF-14):** captura/galería, selección de fruta, inferencia, recomendación, persistencia, historial paginado, historial offline, semáforo visual, validación de formato, health check, autenticación JWT y feedback.
- **KPI principal:** precisión del modelo mAP@50 ≥ 0.75.

---

## 3. Resumen Evaluación 2 — Arquitectura y producto

- **Stack:** Android nativo (Kotlin + CameraX + Room + MVVM) · FastAPI (Python 3.12, async) · YOLO26n (Ultralytics) · SQLAlchemy + Alembic · PostgreSQL/SQLite.
- **Arquitectura 4+1 (Kruchten):** vistas lógica, de procesos, de desarrollo, física y de escenarios (documentadas en Evaluación 2).
- **Producto entregado:** app con selector de fruta, cámara y galería, semáforo de madurez, historial offline; backend con `/v1/predict`, `/v1/history`, `/v1/health`.
- **Modelo:** YOLO26n entrenado 80 épocas, **mAP@50 = 0.9229**, 5.2 MB.

Sobre esa base, la Evaluación 3 incorporó **autenticación JWT**, **feedback con rating**, **endurecimiento de seguridad (OWASP)** y un **rediseño de UI (Material 3)**, todos sometidos a pruebas.

---

## 4. Evaluación 3 — Pruebas y mejoras

### 4.1 Plan de pruebas

Se confeccionó un plan de pruebas alineado a la problemática, con **57 casos automatizados** clasificados en validación, verificación, seguridad y operacionales. Detalle completo (37 filas de casos paso a paso) en [`01_Plan_de_Pruebas.md`](01_Plan_de_Pruebas.md).

| Categoría | Casos | Estado |
|-----------|-------|--------|
| Verificación del estado de madurez (backend) | 21 | ✅ |
| Validación funcional y seguridad (backend) | 17 | ✅ |
| Validación funcional (Android) | 19 | ✅ |
| **Subtotal automatizado** | **57** | **✅ 57/57** |
| Verificación de calidad / KPI | 6 | ✅ |
| Operacional | 5 | ✅ 3 · ⏳ 1 demo · 🔲 1 deploy pendiente |
| Rendimiento y concurrencia | — | ✅ (ver doc 09) |

### 4.2 Base de datos de pruebas

Las pruebas usan una base **efímera y aislada**: SQLite in-memory para el backend (con *fixtures* que crean usuario, JWT real e imágenes JPEG sintéticas) y *mocks* (MockK) de la API y Room para Android. Ningún dato real ni secreto se usa en pruebas. Detalle en [`02_Base_Datos_Pruebas.md`](02_Base_Datos_Pruebas.md).

### 4.3 Aplicación de pruebas y resultados

Ejecutadas el 21/06/2026: **backend 38/38** (`pytest`, 5.34 s) y **Android 19/19** (`gradlew testDebugUnitTest`). Verificaciones de calidad: mAP@50 = 0.9229, modelo 5.2 MB, APK compila, migraciones aplican. Evidencia y logs en [`03_Aplicacion_Pruebas_Resultados.md`](03_Aplicacion_Pruebas_Resultados.md).

### 4.4 Mejoras al producto

Los hallazgos de las pruebas y de una auditoría OWASP originaron **15 mejoras** trazables a commits, mapeadas a estándares de calidad de la industria:

| Estándar | Mejoras destacadas |
|----------|--------------------|
| **Seguridad** | Secreto JWT obligatorio en prod, CORS acotado, política de contraseña, HTTPS forzado, token cifrado en reposo (AES-256), transparencia al usuario |
| **Usabilidad** | Rediseño Material 3: íconos vectoriales, modo oscuro real, feedback táctil, tipografía/espaciado consistentes |
| **Corrección** | Suite y build restaurados a verde; integración continua (CI) |
| **Completitud** | Autenticación + feedback integrados y probados end-to-end |
| **Pertinencia** | Diagnóstico y recomendaciones ajustados al dominio agrícola |

Tabla completa con hallazgo → mejora → commit → verificación en [`04_Mejoras_Producto.md`](04_Mejoras_Producto.md).

### 4.5 Control de versiones

Git + GitHub, **40 commits**, Conventional Commits, ramas de feature, CI (`backend_ci.yml`) que corre la suite en cada push, y copias de configuración versionadas (sin secretos). Detalle en [`05_Evidencia_Control_Versiones.md`](05_Evidencia_Control_Versiones.md).

---

## 5. Conclusión y lecciones aprendidas

MaduraApp es hoy un producto **funcional, probado y endurecido en seguridad**. Las 57 pruebas pasan al 100%, las mejoras derivadas de los resultados cubren los cinco estándares de calidad, y la protección de datos personales (cifrado en tránsito/reposo, hashing, JWT) es real y verificable. Lecciones clave: integrar temprano, tratar las pruebas como red de seguridad, diseñar la seguridad con un marco (OWASP), comunicarla con honestidad, y apoyar el diseño en un sistema de tokens. Detalle en [`06_Conclusion_Lecciones.md`](06_Conclusion_Lecciones.md).

Pendiente honesto: desplegar el backend en el AWS Laboratory del docente, automatizar pruebas E2E y obtener la aprobación formal del plan en la defensa.

---

## 6. Anexos

| Documento | Contenido |
|-----------|-----------|
| [`01_Plan_de_Pruebas.md`](01_Plan_de_Pruebas.md) | Plan de pruebas completo (37 casos) |
| [`02_Base_Datos_Pruebas.md`](02_Base_Datos_Pruebas.md) | Ambiente y base de datos de pruebas |
| [`03_Aplicacion_Pruebas_Resultados.md`](03_Aplicacion_Pruebas_Resultados.md) | Evidencia de ejecución |
| [`04_Mejoras_Producto.md`](04_Mejoras_Producto.md) | Tabla de mejoras por estándar |
| [`05_Evidencia_Control_Versiones.md`](05_Evidencia_Control_Versiones.md) | Git, CI y configuración |
| [`06_Conclusion_Lecciones.md`](06_Conclusion_Lecciones.md) | Conclusión y lecciones |

Documentación de Evaluaciones 1 y 2 en `Documentación/` y `Documentación/Evaluacion_2/`.
