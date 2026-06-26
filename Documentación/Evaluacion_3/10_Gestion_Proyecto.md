# Gestión de Proyecto — MaduraApp

> Documento de **descripción y gestión del proyecto** (Parte 1 del formato institucional). Integra contexto, problema, objetivos cuantificables, alcance, arquitectura cloud, atributos de calidad y estrategia de certificación.
>
> **Estudiante:** Claudio Vicente Aro Kath · RUT 22.022.498-8 · Sección 001D · TPY1101

---

## 1. Contexto del proyecto e impacto en el proceso de negocio

**Cliente objetivo:** consumidores finales, ferias libres y pequeños productores de frutas climatéricas en Chile.

**Proceso de negocio afectado — "Decisión de consumo/procesamiento de la fruta":** hoy la decisión de cuándo consumir, vender o procesar una fruta se toma de forma **subjetiva** (vista y tacto), sin criterio objetivo. Esto provoca que la fruta se deseche por considerarla "pasada" cuando aún es apta, o que se consuma fuera de su punto óptimo.

**Impacto de la solución:** MaduraApp transforma ese proceso entregando, en **~1 segundo desde un smartphone**, un diagnóstico objetivo del estado de madurez (precisión **92%**) con una recomendación de acción. Al objetivar la decisión, la solución ataca directamente la causa de una fracción del **20–40% de pérdidas post-cosecha** que reporta FAO/ODEPA para frutas climatéricas, sin requerir equipamiento especializado ni conocimiento agronómico del usuario.

---

## 2. Descripción del problema u oportunidad

Las pérdidas post-cosecha en frutas climatéricas (aguacate, plátano, tomate, mango) alcanzan en Chile entre **20% y 40%** de la producción (FAO/ODEPA). Una **causa raíz** es la ausencia de un criterio **objetivo y accesible** para determinar el punto óptimo de consumo o procesamiento.

### Análisis de causas y efectos (Ishikawa)

- **Método / Personas:** evaluación subjetiva por vista y tacto; falta de conocimiento agronómico del consumidor.
- **Tecnología:** inexistencia de herramientas accesibles (apps) que clasifiquen madurez de forma objetiva.
- **Información:** ausencia de recomendaciones contextualizadas por fruta y estado.
- **Efecto central:** decisiones erróneas de consumo/descarte → **desperdicio de fruta apta** y consumo fuera del punto óptimo.

> Diagrama: `Documentación/Ishikawa.png`.

**Oportunidad de mejora:** diseñar una aplicación móvil con **visión computacional** que clasifique la madurez en tiempo real y entregue recomendaciones, democratizando un criterio objetivo antes reservado a expertos.

---

## 3. Objetivos del proyecto

### Objetivo general
Desarrollar y validar un sistema de visión computacional (app Android + API + modelo de IA) que clasifique el estado de madurez de cuatro frutas climatéricas en tres categorías, entregando un diagnóstico y una recomendación en tiempo real, con calidad y seguridad de nivel productivo.

### Objetivos específicos (cuantificables — SMART)

| ID | Objetivo | Métrica / meta | Resultado obtenido | Estado |
|----|----------|----------------|--------------------|--------|
| **OE-01** | **Precisión del modelo** de clasificación de madurez | mAP@50 **≥ 0,75** en el set de test | **0,9229** | ✅ Superado |
| **OE-02** | **Rendimiento temporal** del servicio | Inferencia **< 400 ms** p95 (CPU); extremo a extremo **< 1 s** | ~200 ms inferencia · ~600–700 ms E2E | ✅ |
| **OE-03** | **Calidad y cobertura** de pruebas | **≥ 57** casos automatizados y **cobertura ≥ 75%** del código | 57/57 en verde · **76%** total (núcleo 90–100%) | ✅ |
| **OE-04** | **Estabilidad bajo carga** | **0 errores** con ≥ 50 usuarios concurrentes | 0 errores @ 50 concurrentes | ✅ |
| **OE-05** | **Eficiencia del modelo** (despliegue ligero) | Tamaño del modelo **< 10 MB** | **5,2 MB** | ✅ |
| **OE-06** | **Seguridad de datos personales** | 0 hallazgos críticos OWASP; cifrado en tránsito y reposo | Cumplido (bcrypt, JWT, HTTPS, AES-256) | ✅ |

---

## 4. Situación inicial y alcance del proyecto

### Alcance técnico
Diseño, desarrollo, pruebas y despliegue de:
- **App Android nativa** (Kotlin + CameraX): captura/galería, selector de fruta, semáforo de madurez, historial offline, autenticación y feedback.
- **API REST** (FastAPI async): inferencia con YOLO26n, autenticación JWT, historial y feedback.
- **Modelo YOLO26n** entrenado para 4 frutas × 3 estados de madurez.

### Entregables del proyecto
1. Código fuente (app Android + backend) versionado en Git.
2. Modelo entrenado (`yolo26n_maduraapp.pt`, mAP@50 = 0,92).
3. Suite de pruebas automatizadas (57 casos) + reporte de cobertura.
4. Documentación: arquitectura 4+1, plan de pruebas, configuración de ambientes, backup, informe técnico.
5. Pipeline CI (GitHub Actions) y despliegue en AWS.

### Supuestos
1. Disponibilidad de la **capa gratuita / créditos del AWS Academy Learner Lab** para el despliegue de pruebas.
2. El usuario final dispone de un smartphone Android (API 29+) con cámara y conexión a internet.
3. Las imágenes de entrada corresponden a una de las cuatro frutas soportadas en condiciones de iluminación razonables.

### Restricciones
1. **Temporal:** desarrollo acotado al calendario de la asignatura (3 evaluaciones parciales).
2. **Tecnológica / infraestructura:** el AWS Academy Learner Lab es un entorno **efímero** (sesiones ~4 h), **sin GPU** y con un rol IAM restringido (`LabRole`); esto condiciona el modelo de servicio cloud (ver §6).
3. **Alcance del modelo:** limitado a 4 frutas climatéricas y 3 estados; otras frutas quedan fuera.

---

## 5. Planificación del proyecto (Carta Gantt)

El proyecto se ejecutó en tres iteraciones alineadas a las evaluaciones parciales. Diagrama actualizado: `Documentación/diagramas/Gantt_MaduraApp_v3.*`.

| Iteración | Hito | Foco |
|-----------|------|------|
| **EP1** (hasta 08/04/2026) | Definición | Problema, ERS, objetivos, requisitos, diseño inicial |
| **EP2** (hasta 28/05/2026) | Producto | Arquitectura 4+1, backend + modelo, app Android, primera suite de pruebas |
| **EP3** (hasta 25/06/2026) | Aseguramiento de calidad | Plan de pruebas (57), seguridad OWASP, rendimiento, mejoras, despliegue AWS |

---

## 6. Arquitectura tecnológica y justificación de servicios cloud

**Stack:** Android nativo (Kotlin + CameraX + Room + MVVM) · FastAPI (Python 3.12 async) · YOLO26n (Ultralytics) · SQLAlchemy + Alembic · **PostgreSQL (producción) / SQLite (desarrollo)** · Docker · GitHub Actions.

### Modelos de servicio cloud (AWS)

| Modelo | Servicio | Justificación |
|--------|----------|---------------|
| **IaaS** (Infraestructura) | **AWS EC2** (`t3.small`, Docker) — cómputo del backend | Elegido por **restricción del AWS Academy Learner Lab**, que no habilita servicios PaaS con roles personalizados (App Runner/ECS requieren IAM que el lab no permite). EC2 da control total sobre el contenedor Docker y es el cómputo fiable del laboratorio. |
| **DBaaS / PaaS de datos** | **AWS RDS — PostgreSQL** (base de datos de producción) | Base de datos **gestionada**: AWS administra parches, respaldos automáticos y disponibilidad. Habilita los procedimientos `pg_dump`/`pg_restore` (ver doc de backup). En desarrollo/pruebas se usa SQLite por simplicidad y velocidad. |
| **SaaS** | **GitHub Actions** (CI) | Software listo para usar que ejecuta la suite de pruebas en cada push, sin administrar infraestructura de CI. |
| **Contenedores** | **Docker** | Garantiza **paridad de ambientes** (dev/prod): la misma imagen corre en local y en EC2. |

> **Nota de honestidad técnica:** el formato de referencia valora PaaS (p. ej. App Runner). En este proyecto se usó **EC2 (IaaS)** porque el AWS Academy Learner Lab **no permite** desplegar en PaaS con los roles disponibles. Se documenta tal cual, priorizando la veracidad sobre la "pureza" del modelo.

### Factibilidad de cumplimiento
El uso de contenedores Docker permite migrar la solución a un entorno PaaS (App Runner/ECS) o escalar horizontalmente sin cambios de código si el proyecto saliera del laboratorio académico. La app es **config-driven** (la base de datos se selecciona por `DB_URL`), por lo que el salto SQLite → RDS PostgreSQL es un cambio de configuración, no de código.

---

## 7. Conceptualización y atributos de calidad

El propósito de la solución es entregar un **diagnóstico de madurez objetivo, rápido, seguro y accesible**. La viabilidad técnica se soporta en los siguientes atributos de calidad:

- **Integridad:** validación de formato y tamaño de imagen; firma criptográfica de los tokens (JWT); esquema de base de datos versionado con migraciones Alembic. Una imagen corrupta o un token alterado se rechazan.
- **Confiabilidad y seguridad:** endurecimiento OWASP — autenticación JWT, contraseñas con hash bcrypt, **cifrado en tránsito** (HTTPS) y **en reposo** (AES-256 en el dispositivo). Estabilidad verificada: **0 errores** bajo 50 usuarios concurrentes.
- **Precisión y oportunidad:** el modelo alcanza **92%** de precisión (mAP@50) y responde en **~200 ms** de inferencia; las recomendaciones son específicas por fruta y estado.
- **Mantenibilidad:** arquitectura documentada (4+1 de Kruchten), **57 pruebas** automatizadas, integración continua y commits con convención (Conventional Commits).
- **Usabilidad:** interfaz Material Design 3 con modo oscuro y semáforo de madurez; mensajes de seguridad honestos al usuario.

---

## 8. Estrategia de certificación y revisiones parciales

### Criterios de aceptación mandatorios
El producto se considera certificado al cumplir simultáneamente:

| Criterio | Meta | Resultado |
|----------|------|-----------|
| Precisión del modelo | mAP@50 ≥ 0,75 | 0,9229 ✅ |
| Suite de pruebas | 100% en verde | 57/57 ✅ |
| Cobertura de código | ≥ 75% (núcleo) | 76% total ✅ |
| Estabilidad bajo carga | 0 errores @ 50 concurrentes | 0 errores ✅ |
| Build de la app | APK compila e instala | ✅ |
| Seguridad | 0 secretos en el repo · OWASP aplicado | ✅ |

### Revisiones parciales
- **EP1:** validación del problema, requisitos (ERS) y diseño.
- **EP2:** validación de la arquitectura (4+1) y del producto funcional (backend + modelo + app).
- **EP3:** validación del aseguramiento de calidad — plan de pruebas, cobertura, rendimiento, seguridad y mejoras, con evidencia ejecutable en el repositorio y CI.
