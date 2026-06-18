# Informe Técnico — Estado de Avance 2
## Proyecto MaduraApp

**Asignatura:** Taller Aplicado de Programación (TPY1101)
**Sección:** 001D
**Integrantes:** Claudio Vicente Aro Kath
**Docente:** José Ignacio Campos Árevalo
**Fecha de entrega:** Semana 11 — 2026

---

## Índice

1. [Introducción](#1-introducción)
2. [Resumen Evaluación 1](#2-resumen-evaluación-1)
3. [Modelado y Diseño — Modelo 4+1 de Kruchten](#3-modelado-y-diseño--modelo-41-de-kruchten)
   - 3.1 Marco conceptual del modelo
   - 3.2 Vista Lógica
   - 3.3 Vista de Procesos
   - 3.4 Vista de Desarrollo
   - 3.5 Vista Física
   - 3.6 Vista de Escenarios (+1)
4. [Mockups y Diseño de Interfaz](#4-mockups-y-diseño-de-interfaz)
5. [Configuración del Ambiente de Pruebas](#5-configuración-del-ambiente-de-pruebas)
6. [Configuración del Servidor de Producción](#6-configuración-del-servidor-de-producción)
7. [Gestión de Datos — Backup y Replicación](#7-gestión-de-datos--backup-y-replicación)
8. [Plan de Pruebas](#8-plan-de-pruebas)
9. [Desarrollo de Software — Estado y Avances](#9-desarrollo-de-software--estado-y-avances)
10. [Evidencias de Pruebas Ejecutadas](#10-evidencias-de-pruebas-ejecutadas)
11. [Conclusiones y Lecciones Aprendidas](#11-conclusiones-y-lecciones-aprendidas)
12. [Anexos](#12-anexos)

---

## 1. Introducción

El presente informe documenta el **Estado de Avance 2** del proyecto **MaduraApp**, sistema de análisis de madurez agrícola mediante visión computacional. El documento se construye sobre los entregables de la Evaluación 1 (caracterización del problema, requisitos, primer prototipo) y avanza hacia el **diseño arquitectónico formal**, la **configuración de ambientes** y la **demostración del producto funcional**.

### 1.1 Propósito del documento

Este informe responde a los Indicadores de Logro IL2.1, IL2.2 e IL2.3 de la asignatura TPY1101 y se estructura en torno a tres ejes:

1. **Diseño metodológico riguroso** — modelado arquitectónico bajo el estándar 4+1 de Philippe Kruchten, complementado con mockups y diagramas de soporte.
2. **Configuración reproducible de ambientes** — descripción detallada del servidor de producción (cloud) y del ambiente de pruebas local, con paridad de configuración garantizada.
3. **Evidencia del producto funcional** — desarrollo de software de calidad con buenas prácticas industriales, pruebas automatizadas y procedimientos de gestión de datos.

### 1.2 Alcance del entregable

El informe cubre:

- Documentación arquitectónica completa (5 vistas + escenarios).
- Procedimientos operativos de despliegue, prueba y backup.
- Plan de pruebas con cobertura operacional, de validación y verificación.
- Evidencia de la suite de pruebas automatizada (9/9 pytest backend, tests JVM en Android).
- Estado actualizado del software desarrollado, incluyendo nuevas funcionalidades incorporadas tras la Evaluación 1 (selector de fruta, selección desde galería, Test Time Augmentation).

---

## 2. Resumen Evaluación 1

> *Esta sección sintetiza los entregables aprobados en la Evaluación 1 y se incluye por requisito formal de continuidad del proyecto.*

### 2.1 Problema identificado

Las pérdidas post-cosecha en frutas climatéricas (aguacate, plátano, tomate, mango) representan en Chile entre un **20% y un 40%** de la producción según FAO/ODEPA. Una de las causas raíz, identificada en el diagrama de Ishikawa, es la **falta de criterios objetivos y accesibles** para determinar el punto óptimo de consumo o procesamiento de la fruta a nivel de consumidor final, pequeño productor y feria local.

### 2.2 Solución propuesta

**MaduraApp** es un sistema de visión computacional accesible desde dispositivos móviles que clasifica el estado de madurez de cuatro frutas climatéricas en **tres categorías** (Inmaduro / Óptimo / Sobre maduro) y entrega recomendaciones agronómicas contextualizadas en tiempo real.

### 2.3 Tecnologías seleccionadas

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| App móvil | Android nativo — Kotlin + CameraX + Room | API 29+ |
| Backend | Python + FastAPI + SQLAlchemy async | 3.12 / 0.135 |
| Modelo IA | YOLO26n (Ultralytics) | Enero 2026 |
| Base de datos | PostgreSQL (Supabase prod) / SQLite (dev) | 16 / — |
| Contenerización | Docker + Docker Compose | — |
| Cloud | Render — plan Free, región Oregon | — |
| CI/CD | GitHub Actions | — |
| Control de versiones | Git + GitHub (2 repos: testeo + producción) | — |

### 2.4 Estado al cierre de Evaluación 1

- Sprint 1 (Backend) completo: API REST con 3 endpoints, persistencia async, migraciones Alembic, suite 9/9 pytest.
- Sprint 2 (Android) completo: app con CameraX, MVVM, cache offline con Room, tests JVM.
- Pipeline de entrenamiento CRISP-DM listo (datasets de Kaggle/Mendeley, 31.940 imágenes, 12 clases).
- Modelo entrenado YOLO26n alcanzando **mAP@50 = 0.9229** (KPI ≥ 0.75 superado con holgura).

---

## 3. Modelado y Diseño — Modelo 4+1 de Kruchten

### 3.1 Marco conceptual del modelo

El **modelo de vistas arquitectónicas 4+1** propuesto por **Philippe Kruchten** (IEEE Software, noviembre 1995) describe la arquitectura de sistemas de software intensivos en computación mediante **cinco vistas concurrentes**, cada una orientada a un conjunto específico de stakeholders y construida con notaciones apropiadas:

| Vista | Audiencia principal | Preocupación |
|-------|--------------------|--------------|
| **Lógica** | Usuarios finales, analistas | Funcionalidad que provee el sistema |
| **Procesos** | Integradores de sistema | Performance, escalabilidad, concurrencia |
| **Desarrollo** | Programadores, gerentes | Organización del software, gestión |
| **Física** | Ingenieros de sistemas | Topología, comunicaciones, hardware |
| **+1 Escenarios** | Todos | Validación e integración de las 4 vistas |

La aplicación del modelo a MaduraApp se justifica por la **heterogeneidad de stakeholders** (consumidor final, pequeño productor agrícola, docente evaluador, equipo de desarrollo, administrador de infraestructura) y por la **complejidad inherente** del sistema, que combina visión computacional, comunicación cliente-servidor, persistencia distribuida y operación móvil offline-first.

A continuación se desarrollan las cinco vistas. Cada vista se documenta en un archivo separado dentro de `Documentación/Evaluacion_2/` para mantener legibilidad; aquí se sintetizan los aspectos más relevantes y se referencian los documentos detallados.

### 3.2 Vista Lógica

📄 *Documento detallado:* [`01_Vista_Logica.md`](01_Vista_Logica.md)

La vista lógica describe **qué hace el sistema** desde la perspectiva del usuario final. Se compone de un **diagrama de clases UML** que modela las entidades principales del dominio (ScanResult, FruitType, MaturityLabel, ScanEntity) y un **diagrama de componentes** que ilustra las responsabilidades de los módulos de alto nivel:

- **Capa de presentación móvil:** FruitSelectorActivity, MainActivity, HistoryActivity.
- **Capa de aplicación móvil:** ScanViewModel, HistoryViewModel (MVVM).
- **Capa de datos móvil:** FruitRepository, LocalScanDataSource, MaduraApiService.
- **Capa de API REST:** PredictRouter, HistoryRouter.
- **Capa de servicios backend:** InferenceService, HistoryService, YOLO26Wrapper.
- **Capa de persistencia backend:** ScanEntity (ORM SQLAlchemy), base de datos.

### 3.3 Vista de Procesos

📄 *Documento detallado:* [`02_Vista_Procesos.md`](02_Vista_Procesos.md)

La vista de procesos modela el **comportamiento en tiempo de ejecución** y la **concurrencia** del sistema. Sus elementos clave:

- **Diagrama de secuencia** del caso de uso principal "Escaneo de fruta", incluyendo intercambio asíncrono entre Android, FastAPI, YOLO y la base de datos.
- **Diagrama de actividades** que detalla las decisiones, ciclos y bifurcaciones del flujo (permisos de cámara, validación de fruit_type, manejo de errores de conectividad).
- **Modelo de concurrencia:**
  - Android: corrutinas de Kotlin (`viewModelScope.launch`) en hilo de UI no bloqueante.
  - Backend FastAPI: event loop async con `asyncio.to_thread` para liberar workers durante la inferencia YOLO (operación CPU-bound).
  - Hilo separado en CameraX para captura sin bloquear el preview.

### 3.4 Vista de Desarrollo

📄 *Documento detallado:* [`03_Vista_Desarrollo.md`](03_Vista_Desarrollo.md)

La vista de desarrollo describe la **organización estática del código** desde la perspectiva del programador. Se documenta:

- **Estructura de paquetes** del repositorio (`Producto/backend/app/{routers,services,models,schemas,core}` y `Producto/frontend/app/src/main/java/cl/duoc/maduraapp/{ui,data,...}`).
- **Arquitectura en capas:**
  - Backend: Hexagonal/Clean con flujo `routers → services → models/db`.
  - Frontend: MVVM con `Activity → ViewModel → Repository → (API | Cache local)`.
- **Gestión de dependencias:** `requirements.txt` (backend), `build.gradle.kts` (Android).
- **Estrategia de ramas Git:** flujo trunk-based con `develop` (testeo) y `main` (producción).
- **Convenciones de código:** PEP 8 + type hints (Python), KDoc + Conventional Commits.

### 3.5 Vista Física

📄 *Documento detallado:* [`04_Vista_Fisica.md`](04_Vista_Fisica.md)

La vista física documenta la **topología de despliegue**, los nodos hardware/software involucrados y los protocolos de comunicación:

- **Nodo cliente:** Dispositivo Android (≥ API 29) con APK instalada.
- **Nodo backend:** Contenedor Docker en Render (plan Free, región Oregon, 512 MB RAM, CPU compartido).
- **Nodo base de datos:** Supabase PostgreSQL gestionado (tier free, 500 MB).
- **Nodo CI/CD:** GitHub Actions runners (Ubuntu latest, ephemeral).
- **Comunicaciones:**
  - Android ↔ Render: HTTPS + multipart/form-data (POST `/v1/predict`).
  - Render ↔ Supabase: TLS sobre PostgreSQL wire protocol (asyncpg con SSL).
  - GitHub Actions ↔ Render: deploy hook HTTPS.

### 3.6 Vista de Escenarios (+1)

📄 *Documento detallado:* [`05_Vista_Escenarios.md`](05_Vista_Escenarios.md)

La quinta vista —**Escenarios**— actúa como **integradora** de las otras cuatro. Se identifican cinco casos de uso troncales del sistema:

1. **CU-01 — Escanear fruta con cámara** (escenario principal).
2. **CU-02 — Escanear fruta desde galería** (alternativa offline-to-online).
3. **CU-03 — Consultar historial de escaneos** (vista cacheada + refresh remoto).
4. **CU-04 — Cambiar fruta seleccionada** (navegación inversa al selector).
5. **CU-05 — Operar sin conexión** (visualización de historial cacheado).

Para cada escenario se documenta el flujo principal, flujos alternativos, precondiciones, postcondiciones y cómo el escenario **ejercita** las cuatro vistas previas (qué clases participan, qué procesos se activan, qué nodos físicos están involucrados, qué módulos de código se ejecutan).

---

## 4. Mockups y Diseño de Interfaz

📄 *Documento detallado:* [`06_Mockups_y_Wireframes.md`](06_Mockups_y_Wireframes.md)

Los mockups originales se encuentran en [`Documentación/WireFrame MaduraApp.pdf`](../WireFrame%20MaduraApp.pdf). En el avance actual se incorporaron **tres pantallas nuevas o actualizadas** que se documentan en el archivo de mockups:

| Pantalla | Estado | Descripción |
|----------|--------|-------------|
| **Selector de fruta** | Nueva | Grid 2×2 con cards (aguacate, plátano, tomate cherry, mango). Pantalla inicial. |
| **Pantalla principal con fruta** | Actualizada | Título dinámico con fruta seleccionada + botón galería. |
| **Resultado de escaneo** | Actualizada | Semáforo de madurez + recomendación agronómica detallada. |

El flujo de navegación está documentado mediante un diagrama de estados de la UI.

---

## 5. Configuración del Ambiente de Pruebas

📄 *Documento detallado:* [`07_Configuracion_Ambiente_Pruebas.md`](07_Configuracion_Ambiente_Pruebas.md)

El ambiente de pruebas replica fielmente el ambiente de producción manteniendo **paridad en versión de lenguaje, dependencias, esquema de base de datos y endpoints**. Las diferencias controladas son:

| Aspecto | Producción | Pruebas |
|---------|-----------|---------|
| Plataforma | Render (Docker Linux Oregon) | Localhost (Windows / Linux) |
| Base de datos | Supabase PostgreSQL 16 | SQLite (aiosqlite) o PostgreSQL local |
| Variable `ENVIRONMENT` | `production` | `development` |
| Warmup de modelo | Deshabilitado (ahorra RAM) | Habilitado (más rápido) |
| URL base API | `https://maduraapp-backend.onrender.com` | `http://localhost:8000` |

El documento detallado incluye:

- Instalación de herramientas (Python 3.12, Java/Android Studio, Docker, Git).
- Procedimiento de levantamiento del backend local paso a paso.
- Procedimiento de configuración del proyecto Android en Android Studio.
- Verificación funcional del ambiente (health check, smoke test).

---

## 6. Configuración del Servidor de Producción

📄 *Documento detallado:* [`08_Configuracion_Servidor_Produccion.md`](08_Configuracion_Servidor_Produccion.md)

El servidor de producción está desplegado en **Render** mediante el archivo `render.yaml` ubicado en la raíz del repositorio. La configuración se gestiona como código (IaC) para garantizar reproducibilidad.

**Especificaciones del servicio:**

```yaml
type: web
name: maduraapp-backend
env: docker
dockerfilePath: ./Producto/backend/Dockerfile
dockerContext: ./Producto/backend
plan: free
region: oregon
branch: main
healthCheckPath: /v1/health
```

**Variables de entorno gestionadas:**

| Variable | Valor / Origen | Sensibilidad |
|----------|---------------|--------------|
| `ENVIRONMENT` | `production` | Pública |
| `DB_URL` | Connection string Supabase | **Secreta** (sync: false) |
| `AUTH_SECRET_KEY` | Auto-generada por Render | **Secreta** |
| `YOLO_MODEL_PATH` | `weights/yolo26n_maduraapp.pt` | Pública |
| `CONFIDENCE_THRESHOLD` | `0.55` | Pública |

El documento detallado cubre: justificación de Render vs alternativas, configuración paso a paso desde cero, configuración de Supabase, despliegue continuo y procedimiento de rollback.

---

## 7. Gestión de Datos — Backup y Replicación

📄 *Documento detallado:* [`09_Procedimientos_Backup.md`](09_Procedimientos_Backup.md)

Se documentan tres procedimientos clave para satisfacer el indicador IL2.2 sobre gestión de datos:

### 7.1 Backup de BD de producción
Procedimiento `pg_dump` contra Supabase con autenticación SSL, frecuencia recomendada (diaria + pre-deploy), almacenamiento (volumen local + repositorio privado cifrado) y política de retención (30 días rotativos).

### 7.2 Restauración en ambiente de pruebas
Script reproducible que toma el dump de producción y lo carga en una base PostgreSQL local del ambiente de pruebas, manteniendo el mismo esquema (`scans` table con migraciones Alembic aplicadas).

### 7.3 Replicación de configuración del servidor
Procedimiento detallado para levantar el mismo stack (Python 3.12 + ultralytics + FastAPI + SQLAlchemy + asyncpg) en un nuevo servidor, garantizando paridad con producción.

---

## 8. Plan de Pruebas

📄 *Documento detallado:* [`10_Plan_de_Pruebas.md`](10_Plan_de_Pruebas.md)

El plan de pruebas adopta el modelo de **pirámide de pruebas** y clasifica los tests en tres niveles según el indicador de logro:

| Tipo | Cantidad | Cobertura |
|------|----------|-----------|
| **Operacionales** | Health check, smoke tests, monitoreo Render | 100% endpoints |
| **Validación** | Pruebas funcionales por endpoint, validación de inputs | 9/9 pytest backend + tests JVM Android |
| **Verificación** | Latencia de inferencia, uso de RAM, mAP del modelo | KPI ≥ 0.75 superado (0.9229) |

El documento incluye matriz completa de casos de prueba con su ID, descripción, precondición, pasos, resultado esperado y resultado observado.

---

## 9. Desarrollo de Software — Estado y Avances

📄 *Documento detallado:* [`11_Estado_Desarrollo.md`](11_Estado_Desarrollo.md)

### 9.1 Avances entre Evaluación 1 y Evaluación 2

| Avance | Impacto | Componentes afectados |
|--------|---------|----------------------|
| **Selector de fruta inicial** | Mejora precisión del modelo (filtra clases) | FruitSelectorActivity, ScanViewModel, predict.py |
| **Selección desde galería** | Permite analizar fotos ya tomadas | MainActivity, gallery launcher |
| **Test Time Augmentation (TTA)** | +2-3% precisión cuando hay filtro | yolo_wrapper.py, inference_service.py |
| **Umbral de confianza ajustado** | 0.45 → 0.55 (menos falsos positivos) | config.py, render.yaml |
| **Recomendaciones agronómicas detalladas** | Información útil al usuario | inference_service.py |
| **Optimización de RAM en producción** | Habilita free tier (512 MB) | yolo_wrapper.py (warmup condicional) |

### 9.2 Patrones de arquitectura aplicados

- **Backend:** Clean Architecture / Layered (routers → services → models).
- **Frontend:** MVVM con LiveData + Single Source of Truth en Repository.
- **Cache:** Single source of truth en Room + refresh remoto explícito.
- **DI manual:** Sin framework de inyección — singletons en `MaduraApp.kt` y dependencias por constructor.

### 9.3 Calidad del código

- **Python:** PEP 8, type hints obligatorios, docstrings en servicios.
- **Kotlin:** Convenciones oficiales, KDoc en clases públicas.
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, etc.).
- **CI:** GitHub Actions ejecuta `pytest tests/ -v` en cada PR (verde como gate).
- **Sin secrets en repo:** `.env`, modelos `.pt` (en testing) y dumps de BD excluidos por `.gitignore`.

### 9.4 Seguridad

- Validación estricta de inputs (`Content-Type`, tamaño máximo 10 MB, `fruit_type` enumerado).
- Header `Authorization: Bearer <token>` preparado para autenticación futura.
- HTTPS obligatorio en producción (Render gestiona TLS).
- CORS configurado para orígenes explícitos.
- Sin SQL crudo (SQLAlchemy ORM como única vía de acceso a BD).

---

## 10. Evidencias de Pruebas Ejecutadas

📄 *Documento detallado:* [`12_Evidencias_Pruebas.md`](12_Evidencias_Pruebas.md)

El archivo de evidencias incluye:

- Captura de la suite completa pytest: `9 passed in X.XXs`.
- Tabla de resultados del modelo entrenado: mAP@50 = 0.9229, P/R por clase.
- Captura del endpoint `/v1/health` retornando `{"status": "ok", "model_loaded": true}`.
- Resultado de un escaneo real desde la app Android con bbox + maturity_label.
- Logs del backend en local mostrando inferencia exitosa (~150 ms con TTA).
- Logs del CI verde en el repositorio `MaduraApp-Produccion`.

---

## 11. Conclusiones y Lecciones Aprendidas

### 11.1 Cumplimiento de objetivos

Al cierre de esta Evaluación 2, el proyecto MaduraApp cumple con:

- ✅ **IL2.1** — diseño documentado bajo el estándar industrial 4+1 de Kruchten, con cinco vistas formalmente desarrolladas.
- ✅ **IL2.2** — ambiente de producción operativo en Render, ambiente de pruebas reproducible localmente, procedimientos de backup documentados.
- ✅ **IL2.3** — software funcional desplegado, cumpliendo los requerimientos funcionales aprobados en la Evaluación 1 y agregando funcionalidades nuevas (selector de fruta, galería, TTA).

### 11.2 Decisiones técnicas relevantes

- **Render Free vs Standard:** Se eligió el tier Free para minimizar costos durante el proyecto académico, asumiendo la restricción de 512 MB RAM y el cold-start de 15 minutos. Se mitiga con: (a) warmup deshabilitado en producción, (b) liberación explícita de tensores tras inferencia, (c) `gc.collect()` post-inferencia, (d) workflow keepalive en GitHub Actions.
- **Supabase vs Neon.tech:** Inicialmente se evaluó Neon.tech; se eligió Supabase por mejor integración con el flujo de desarrollo del equipo y por su pooler de conexiones nativo.
- **YOLO26n vs YOLOv8/v11:** YOLO26n (Enero 2026) ofrece mejor compromiso tamaño/precisión (5.2 MB con mAP@50 = 0.92) que las generaciones anteriores, crítico para tiempo de descarga del modelo en el cold-start de Render.
- **Filtro de fruta opcional:** En vez de obligar al usuario a elegir fruta (UX más rígida), se mantiene el modo libre y se ofrece el selector como mejora opcional. El backend acepta `fruit_type` como Form opcional y degrada limpio cuando falta.

### 11.3 Lecciones aprendidas

- **Gestión de RAM en cloud free tiers es crítica.** Los modelos de ML basados en PyTorch consumen mucha memoria; medir antes de desplegar.
- **La paridad ambiente prueba/producción** es un trabajo continuo, no un check único.
- **Conventional Commits + Git flow** acelera la generación de notas de release y trazabilidad para evaluación académica.
- **Aprovechar el modelo 4+1** desde el diseño temprano evita decisiones arquitectónicas implícitas que luego son difíciles de revertir.

### 11.4 Trabajo futuro (Evaluación 3 y posterior)

- Implementación de autenticación real (Bearer JWT firmado).
- Migración a Render Standard si el proyecto se mantiene activo post-asignatura.
- Recolección de feedback de usuarios reales para re-entrenamiento del modelo.
- Expansión del catálogo de frutas soportadas (palta variedad Edranol, kiwi, paltón).

---

## 12. Anexos

📄 *Documento detallado:* [`13_Anexos.md`](13_Anexos.md)

Incluye:

- A.1 Comandos frecuentes (Git, Docker, pytest, Alembic).
- A.2 Glosario técnico (TTA, mAP, async/await, MVVM, etc.).
- A.3 Referencias bibliográficas.
- A.4 Tabla completa de endpoints REST.
- A.5 Esquema de la base de datos (DDL).

---

*Documento generado el 2026-05-26 — Versión 2.0 — Estado de Avance 2*
