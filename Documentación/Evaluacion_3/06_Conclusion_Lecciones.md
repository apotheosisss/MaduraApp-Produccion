# Conclusión y Lecciones Aprendidas — MaduraApp

> **Estado de Avance 3 — TPY1101**

---

## 1. Conclusión

MaduraApp alcanzó el estado de **producto funcional, probado y endurecido** en seguridad. Partiendo de la problemática de las pérdidas post-cosecha de frutas climatéricas (20–40% según FAO/ODEPA), se construyó un sistema cliente-servidor que clasifica la madurez de 4 frutas en 3 estados con un modelo YOLO26n de **mAP@50 = 0.9229**, superando el KPI (≥0.75) por más de 17 puntos.

En esta tercera evaluación el foco fue el **aseguramiento de calidad**:

- Se formalizó un **plan de pruebas** de 57 casos automatizados (38 backend + 19 Android) más verificaciones de calidad y operacionales, todos en verde.
- Se aplicaron **pruebas de validación** a cada componente (autenticación, inferencia, historial, feedback, cache offline, presentación), confirmando que el sistema cumple sus requisitos funcionales.
- Los hallazgos de las pruebas y de una **auditoría OWASP** originaron **15 mejoras** trazables a commits, abarcando los estándares de *seguridad, usabilidad, completitud, corrección y pertinencia*.
- Se incorporó **integración continua** para sostener la calidad en el tiempo.

El resultado es un producto que no solo funciona, sino que **protege los datos personales del usuario** (cifrado en tránsito y en reposo, contraseñas hasheadas, autenticación JWT) y ofrece una **experiencia de uso coherente** (rediseño Material 3 con modo oscuro e íconos vectoriales).

---

## 2. Objetivos cumplidos

| Objetivo | Estado |
|----------|--------|
| Plan de pruebas alineado a la problemática | ✅ 57 casos documentados |
| Aplicación de pruebas de validación a todos los componentes | ✅ 57/57 en verde |
| Mejoras según resultados de pruebas (calidad/ética/seguridad) | ✅ 15 mejoras trazables |
| Base de datos de pruebas documentada | ✅ SQLite in-memory + mocks |
| Control de versiones con evidencia | ✅ Git + CI + 40 commits |
| Informe con evidencias | ✅ Este conjunto documental |

---

## 3. Trabajo pendiente (honesto)

| Pendiente | Plan |
|-----------|------|
| Despliegue del backend en el AWS Laboratory del docente | Desplegar y reapuntar las pruebas operacionales (OP-05) a la URL pública |
| Pruebas E2E automatizadas (Espresso/UI Automator) | Reemplazar la demo manual de RF-01/02 por pruebas automáticas |
| Aprobación formal del plan por el docente guía | Se presenta para aprobación en la defensa |
| Merge de `feature/auth-feedback` → `main` | Tras validación end-to-end en dispositivo físico |

---

## 4. Lecciones aprendidas

1. **Integrar temprano evita deuda.** La rama `feature/auth-feedback` se separó de `main` antes de varios fixes de build; al integrarla aparecieron conflictos y pruebas rotas. Lección: integrar con frecuencia y mantener `main` como fuente de verdad reduce el costo de los merges.

2. **Las pruebas son una red de seguridad real.** Al añadir autenticación JWT, la suite detectó de inmediato que los endpoints ahora exigían token y que los tests viejos fallaban (401 vs 403). Sin las pruebas, esas regresiones habrían llegado al usuario.

3. **La seguridad se diseña, no se improvisa.** La auditoría OWASP reveló problemas no evidentes (secreto JWT por defecto, tráfico en claro, token sin cifrar). Aplicar un marco de referencia (OWASP) hace la revisión sistemática en lugar de intuitiva.

4. **Honestidad técnica frente al usuario.** Se descartó etiquetar la app como "cifrado de extremo a extremo" (como WhatsApp) porque la arquitectura no lo permite; se optó por un mensaje veraz ("cifrado en tránsito"). Comunicar la seguridad de forma honesta es parte de la ética del producto.

5. **Compatibilidad de dependencias importa.** `bcrypt 5.x` rompía `passlib 1.7.4`, y `email-validator`/`pydantic[email]` faltaban. Fijar versiones (`bcrypt==4.0.1`) y documentarlas en `requirements.txt` evita fallos no reproducibles.

6. **El diseño se apoya en un sistema, no en pantallas sueltas.** Centralizar color, tipografía y espaciado en tokens (Material 3) hizo que el modo oscuro y la consistencia surgieran "gratis" al cambiar las pantallas.

7. **La documentación es parte del producto.** Tener la suite real y los commits permitió construir este informe sobre hechos verificables, no sobre afirmaciones; cada caso de prueba y cada mejora es trazable.

---

## 5. Aprendizajes técnicos en profundidad (EP3)

8. **La infraestructura real rara vez coincide con el plan, y eso debe documentarse.** El diseño inicial apuntaba a Render + Supabase; la realidad fue hostear desde el PC (EP2) y luego AWS EC2 (EP3). La lección no es "planificar mejor", sino **mantener la documentación sincronizada con la implementación**: un diagrama que contradice el `Dockerfile` o las pruebas es un defecto de calidad. Por eso se reescribió la vista de despliegue y se marcaron los documentos obsoletos.

9. **Las restricciones del entorno definen la arquitectura tanto como los requisitos.** El AWS Academy Learner Lab —efímero, sin GPU y con un rol IAM restringido— obligó a usar EC2 (IaaS) en vez de un PaaS más "puro". Aprendí a **justificar la decisión con honestidad** en lugar de presentar una arquitectura ideal que no se implementó.

10. **Una métrica sin número no es un objetivo.** Reformular metas vagas ("que sea rápido y de calidad") como objetivos SMART (inferencia < 400 ms, cobertura ≥ 75%, 0 errores @ 50 concurrentes) cambió la forma de evaluar el producto: pasé de opiniones a evidencia medible. La cobertura del 76% reveló además **dónde faltaban pruebas** (wrapper del modelo, ramas de error), guiando el trabajo futuro.

11. **Probar el rendimiento aísla los cuellos de botella reales.** La prueba de concurrencia mostró que el límite no es la red ni la base de datos, sino la **CPU durante la inferencia** (modelo sin GPU). Esto orienta una mejora concreta (GPU o cola de inferencia) en vez de optimizar a ciegas.

12. **La separación dev/prod por configuración paga dividendos.** Que la base de datos se elija por `DB_URL` permitió usar SQLite en pruebas (rápido, aislado) y PostgreSQL en producción **sin cambiar código**, cumpliendo la paridad de ambientes que exige el estándar.
