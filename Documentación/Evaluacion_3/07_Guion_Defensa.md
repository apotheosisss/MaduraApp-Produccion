# Guion de Defensa y Preguntas Probables — MaduraApp (Eval 3)

> Material de preparación para la **defensa oral** (15 min presentación + 5 min preguntas). La presentación vale el **70%** de la nota; la rúbrica premia "argumentos coherentes y propios de la disciplina". **No leer las slides: explicar con tus palabras.**

---

## 1. Distribución de tiempo (15 min)

| Min | Slide | Qué decir |
|-----|-------|-----------|
| 0–1 | 1 Portada | Presentarte y enunciar el objetivo |
| 1–2 | 2 Agenda | Ruta de la presentación |
| 2–4 | 3 Contexto | Problema (pérdidas post-cosecha) + solución + KPI |
| 4–7 | 4 Plan de pruebas | Los 4 tipos de prueba y por qué (clave) |
| 7–10 | 5 Aplicación | 57/57 verde, CI, cómo se ejecutan |
| 10–12 | 6 Mejoras | 15 mejoras por estándar, derivadas de las pruebas |
| 12–13 | 7 Seguridad | OWASP + mensaje honesto al usuario |
| 13–15 | 8 Conclusión | Logros + pendientes honestos |

---

## 2. Conceptos que DEBES dominar (para responder con propiedad)

### Tipos de prueba
- **Validación** = "¿construyo el sistema correcto?" → cumple los requisitos funcionales (RF). Ej.: que `/predict` devuelva el diagnóstico correcto.
- **Verificación** = "¿lo construyo correctamente?" → atributos de calidad (performance, precisión, tamaño). Ej.: mAP@50 ≥ 0.75.
- **Prueba unitaria**: prueba una unidad aislada (una función/clase) con sus dependencias simuladas.
- **Prueba de integración**: prueba que varios componentes funcionen juntos (ej.: endpoint + base de datos).

### Base de datos de pruebas
- **SQLite in-memory**: base que vive en RAM, se crea y destruye en cada corrida → aislamiento, velocidad, no toca datos reales.
- **Fixture**: función que prepara datos/estado antes de un test (ej.: crear usuario + token).
- **Mock**: objeto que simula una dependencia (ej.: el modelo YOLO o la API) para no depender de recursos reales.

### Seguridad (OWASP)
- **OWASP Top 10**: lista estándar de los 10 riesgos de seguridad más críticos en aplicaciones web.
- **A01 Broken Access Control**: acceder a algo sin permiso → lo mitigamos exigiendo JWT.
- **A02 Cryptographic Failures**: datos sin cifrar → HTTPS (tránsito) + AES-256 (reposo).
- **A07 Auth Failures**: contraseñas débiles → política de 8+ con letra y número.
- **JWT**: token firmado que prueba la identidad del usuario en cada request.
- **bcrypt / hashing**: la contraseña NO se guarda; se guarda un hash irreversible.

---

## 3. Preguntas probables y respuestas

**P: ¿Por qué SQLite en memoria para las pruebas y no la base real?**
R: Para aislar cada prueba (que una no contamine a otra), por velocidad (sin disco) y por seguridad (no exponer datos reales). El esquema es el mismo que producción, así que la prueba es representativa.

**P: ¿Por qué "mockean" el modelo YOLO en los tests?**
R: Porque la prueba del endpoint valida la *lógica de la API* (validación de entrada, persistencia, respuesta), no la red neuronal. Mockear el modelo hace los tests rápidos y deterministas, sin depender de los pesos ni de GPU. La precisión del modelo se valida aparte con la métrica mAP.

**P: ¿Cómo aseguran que las pruebas se ejecutan siempre?**
R: Con integración continua (GitHub Actions, `backend_ci.yml`): la suite corre automáticamente en cada push. Si algo rompe una prueba, se detecta antes de integrar.

**P: ¿Las mejoras de dónde salieron?**
R: De dos fuentes: los resultados de las pruebas (ej.: tests rojos al añadir JWT → corregí los tests) y una auditoría de seguridad con OWASP (ej.: encontré el secreto JWT hardcodeado → lo moví a variable de entorno). Cada mejora tiene un commit que la respalda.

**P: ¿Por qué no es "cifrado de extremo a extremo" como WhatsApp?**
R: Porque en E2E real ni el servidor puede leer el contenido. Aquí el servidor *necesita* leer la imagen para correr la inferencia y guardar el historial. Sería deshonesto llamarlo E2E; por eso uso el término correcto: "cifrado en tránsito" (HTTPS) más "cifrado en reposo". Protege igual los datos personales, pero se llama distinto.

**P: ¿Qué pasa si alguien intercepta la red?**
R: No ve nada útil: el tráfico va por HTTPS/TLS. Y la contraseña nunca viaja ni se guarda en claro: se hashea con bcrypt.

**P: ¿Cómo guardan la sesión en el teléfono de forma segura?**
R: El token JWT se cifra en reposo con EncryptedSharedPreferences (AES-256), con la clave en el Android Keystore. Si alguien extrae el archivo del dispositivo, no puede leer el token.

**P: ¿Qué cobertura tienen las pruebas?**
R: 57 casos cubren los componentes críticos: autenticación, inferencia, historial, feedback, cache offline y la capa de presentación (MVVM). La matriz RF↔casos del plan muestra qué requisito cubre cada prueba.

**P: ¿Qué falta / qué mejorarían?**
R: Desplegar el backend en el laboratorio AWS, automatizar las pruebas end-to-end (hoy la cámara se prueba manualmente) y subir la cobertura. Lo tengo documentado como pendiente honesto.

**P: ¿Por qué Android nativo y no multiplataforma?**
R: Para aprovechar CameraX y el control fino de cámara/rendimiento; el alcance del proyecto es Android.

**P: ¿Qué es mAP@50?**
R: Mean Average Precision con umbral de solapamiento (IoU) 0.5; mide qué tan bien el modelo detecta y clasifica. 0.9229 significa muy alta precisión, sobre el KPI de 0.75.

---

## 4. Consejos de defensa

- Habla de **decisiones y porqués**, no de "hice esto y esto". La rúbrica premia el dominio.
- Si no sabes algo: reconócelo y explica **cómo lo averiguarías**. Es mejor que inventar.
- Ten a mano el **reporte de tests** (`app/build/reports/.../index.html`) y el repo por si piden evidencia.
- Usa el vocabulario técnico (validación/verificación, fixture, mock, OWASP, JWT, hashing) con naturalidad.
- Mantén el ritmo: no te detengas demasiado en el contexto; el peso está en pruebas y mejoras.
