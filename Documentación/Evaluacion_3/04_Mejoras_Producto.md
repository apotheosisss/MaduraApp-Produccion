# Mejoras al Producto según Resultados de las Pruebas — MaduraApp

> **Estado de Avance 3 — TPY1101**
> Documenta las **mejoras aplicadas al producto** siguiendo los resultados de las pruebas ejecutadas, representadas en tabla específica y mapeadas a los **estándares de calidad de la industria**: *usabilidad, seguridad, completitud, corrección y pertinencia* (criterio 3 del encargo, IL3.2).

---

## 1. Cómo surgieron las mejoras

Durante la Evaluación 3 se ejecutó la suite de pruebas y se realizó una auditoría de seguridad basada en **OWASP**. Tanto las pruebas como la auditoría revelaron hallazgos que originaron mejoras concretas. Cada mejora:

1. Parte de un **hallazgo** (resultado de prueba o auditoría).
2. Se implementa con un **cambio versionado** (commit identificable).
3. Se **re-prueba** para confirmar que el hallazgo quedó resuelto.

---

## 2. Tabla de mejoras (por estándar de calidad)

| # | Hallazgo (resultado de prueba/auditoría) | Mejora aplicada | Estándar de calidad | Commit | Verificación post-mejora |
|---|------------------------------------------|-----------------|---------------------|--------|--------------------------|
| M-01 | Auditoría OWASP A02/A05: `JWT_SECRET_KEY` hardcodeado permitiría falsificar tokens | El backend exige secreto fuerte por variable de entorno y **rechaza arrancar** con el valor por defecto en producción | **Seguridad** | `43cd16c` | Test manual: `ENVIRONMENT=production` lanza error de validación |
| M-02 | OWASP A05: CORS `allow_origins=["*"]` demasiado permisivo | CORS acotado por configuración; métodos y cabeceras explícitos | **Seguridad** | `43cd16c` | Config valida orígenes; `*` prohibido en producción |
| M-03 | OWASP A07: política de contraseña débil (mínimo 6, sin complejidad) | Mínimo 8 caracteres + letra + número, validado en cliente y servidor | **Seguridad** | `43cd16c` | CP-18 (`test_auth_register_weak_password`) → 422 ✅ |
| M-04 | OWASP A02: tráfico HTTP en claro (`usesCleartextTraffic=true`) expone email/contraseña | HTTPS forzado vía `network_security_config`; cleartext solo en localhost de desarrollo | **Seguridad** | `db09e83` | APK compila; cleartext bloqueado salvo dev |
| M-05 | OWASP A02/M9: token JWT guardado sin cifrar en el dispositivo | Token cifrado en reposo con **EncryptedSharedPreferences (AES-256)** y clave en Android Keystore | **Seguridad** | `db09e83` | APK compila; suite Android 19/19 ✅ |
| M-06 | Heurística de seguridad: el usuario no percibe la protección de sus datos | Indicador visible (candado + "datos cifrados") en login y registro, con mensaje honesto (cifrado en tránsito, no E2E) | **Usabilidad / Seguridad** | `db09e83` | Revisión visual en login/registro |
| M-07 | Revisión UX (skill ui-ux-pro-max): emojis usados como íconos (inconsistentes entre dispositivos) | Reemplazo por **íconos vectoriales** de fruta; sistema de color Material 3 completo | **Usabilidad** | `88ffe74` | APK compila; render consistente |
| M-08 | Revisión UX: modo oscuro inconsistente (tema DayNight sin paleta nocturna) | **Modo oscuro real** (`values-night`) emparejado con el claro; tokens semánticos | **Usabilidad** | `88ffe74` | Contraste verificado en ambos temas |
| M-09 | Revisión UX: tarjetas sin feedback táctil; tipografía y espaciado inconsistentes | `MaterialCardView` con ripple; roles tipográficos M3; ritmo de espaciado 4/8dp | **Usabilidad** | `88ffe74` | APK compila; 19/19 tests ✅ |
| M-10 | Pruebas en rojo tras integrar auth: endpoints exigían JWT pero los tests no lo enviaban | Tests actualizados con fixture `auth_headers` (token real); códigos 401 corregidos | **Corrección** | `69b7293` | Suite backend 38/38 ✅ |
| M-11 | Build de Android roto tras merge: `AuthRequestDto`/`bearerToken` inexistentes | Eliminado código muerto; firmas alineadas con `AuthInterceptor`; tests JVM corregidos | **Corrección** | `a8fc521` | APK compila; 19/19 tests ✅ |
| M-12 | Dependencias de auth ausentes/incompatibles (`email-validator`, `bcrypt 5.x` rompe `passlib`) | `pydantic[email]` añadido; `bcrypt` fijado a 4.0.1 | **Corrección / Completitud** | `69b7293` | Suite backend 38/38 ✅ |
| M-13 | Funcionalidades de auth y feedback codeadas pero sin integrar/probar | Integración end-to-end: registro→login→escaneo→rating→historial por usuario | **Completitud** | `43cd16c`, `a8fc521` | CP-01…CP-18, CP-14 ✅ |
| M-14 | Las recomendaciones de madurez deben ser pertinentes al dominio agrícola | Mensajes por estado (Inmaduro/Óptimo/Sobremaduro) y por fruta; filtro de fruta mejora precisión | **Pertinencia** | (base eval 2) | CP-05, CP-06 ✅ |
| M-15 | Sin integración continua: las pruebas solo corrían localmente, arriesgando regresiones | Workflow `backend_ci.yml` que ejecuta la suite pytest en cada push/PR a las ramas principales | **Corrección / Completitud** | (Eval 3) | Suite se ejecuta automáticamente en GitHub Actions |

---

## 3. Resumen por estándar de calidad

| Estándar | Mejoras | Síntesis |
|----------|---------|----------|
| **Seguridad** | M-01…M-06 | Endurecimiento OWASP: secreto JWT, CORS, política de contraseña, HTTPS forzado, cifrado en reposo, transparencia al usuario |
| **Usabilidad** | M-06…M-09 | Rediseño Material 3: íconos vectoriales, modo oscuro, feedback táctil, tipografía/espaciado consistentes |
| **Corrección** | M-10…M-12, M-15 | Suite de pruebas y build restaurados a verde; integración continua en CI |
| **Completitud** | M-12, M-13 | Autenticación + feedback integrados y probados end-to-end |
| **Pertinencia** | M-14 | Diagnóstico y recomendaciones ajustados al dominio (4 frutas × 3 estados) |

---

## 4. Trazabilidad pruebas → mejoras → re-prueba

```
Pruebas/Auditoría  ──►  Hallazgo  ──►  Mejora (commit)  ──►  Re-prueba (verde)
   pytest/JUnit          M-01..M-14      43cd16c/db09e83/      57/57 tests ✅
   + OWASP audit                         88ffe74/69b7293/      APK compila ✅
                                         a8fc521
```

Todas las mejoras quedaron **verificadas**: la suite completa (57 pruebas) está en verde y el APK compila e instala, confirmando que los hallazgos fueron resueltos sin introducir regresiones.
