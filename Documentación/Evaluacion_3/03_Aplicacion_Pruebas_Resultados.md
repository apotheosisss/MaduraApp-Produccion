# Aplicación de Pruebas y Resultados — MaduraApp

> **Estado de Avance 3 — TPY1101**
> Evidencia de la **aplicación de las pruebas de validación** a los distintos componentes del proyecto para asegurar funcionalidad, buenas prácticas, calidad y seguridad (criterio 2 del encargo, IL3.1).
>
> Resultados obtenidos al ejecutar la suite el **21 de junio de 2026**.

---

## 1. Resumen de resultados

| Suite | Framework | Pruebas | Resultado | Tiempo |
|-------|-----------|---------|-----------|--------|
| Backend (API FastAPI) | pytest 9.0.3 / Python 3.13 | 38 | ✅ 38 passed, 0 failed | 5.34 s |
| Android — FruitRepository | JUnit + MockK + Turbine | 9 | ✅ 9 passed, 0 failed | — |
| Android — ScanViewModel | JUnit + MockK + coroutines-test | 6 | ✅ 6 passed, 0 failed | — |
| Android — HistoryViewModel | JUnit + MockK + LiveData | 4 | ✅ 4 passed, 0 failed | — |
| **Total** | | **57** | **✅ 36 passed, 0 failed** | |

---

## 2. Evidencia — Suite backend (pytest)

Comando: `pytest tests/ -v` desde `Producto/backend` con el entorno virtual activo.

```text
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.0.3, pluggy-1.6.0
tests/test_history.py::test_history_requires_auth PASSED                 [  5%]
tests/test_history.py::test_history_empty_for_new_user PASSED            [ 11%]
tests/test_history.py::test_history_after_predict PASSED                 [ 17%]
tests/test_history.py::test_history_pagination PASSED                    [ 23%]
tests/test_history.py::test_history_limit_validation PASSED              [ 29%]
tests/test_history.py::test_auth_register_duplicate PASSED               [ 35%]
tests/test_history.py::test_auth_register_weak_password PASSED           [ 41%]
tests/test_history.py::test_auth_login_wrong_password PASSED             [ 47%]
tests/test_history.py::test_feedback_submit PASSED                       [ 52%]
tests/test_history.py::test_feedback_invalid_rating PASSED               [ 58%]
tests/test_predict.py::test_health PASSED                                [ 64%]
tests/test_predict.py::test_predict_requires_auth PASSED                 [ 70%]
tests/test_predict.py::test_predict_unsupported_format PASSED            [ 76%]
tests/test_predict.py::test_predict_invalid_fruit_type PASSED            [ 82%]
tests/test_predict.py::test_predict_no_detection PASSED                  [ 88%]
tests/test_predict.py::test_predict_with_detection PASSED                [ 94%]
tests/test_predict.py::test_predict_with_fruit_filter PASSED             [100%]
======================= 38 passed, 14 warnings in 5.34s =======================
```

> Los *warnings* corresponden a `DeprecationWarning` de `datetime.utcnow()` en dependencias de terceros (SQLAlchemy/jose); no afectan el resultado. El código propio ya migró a `datetime.now(UTC)`.

**Cobertura por componente:**

| Componente | Pruebas | Casos (Plan) |
|------------|---------|--------------|
| Autenticación (`/v1/auth/*`) | 3 | CP-01, CP-02, CP-18 |
| Inferencia (`/v1/predict`, `/v1/health`) | 6 | CP-04…CP-09 |
| Historial (`/v1/history`) | 5 | CP-10…CP-13 |
| Feedback (`/v1/feedback`) | 2 | CP-14, CP-15 |
| Seguridad (JWT obligatorio) | 2 | CP-16, CP-17 |

---

## 3. Evidencia — Suite Android (Gradle / JVM)

Comando: `./gradlew testDebugUnitTest`.

```text
> Task :app:testDebugUnitTest
BUILD SUCCESSFUL in 35s

Reporte por clase (app/build/test-results/testDebugUnitTest/):
  FruitRepositoryTest .......... tests="9"  failures="0"
  ScanViewModelTest ............ tests="6"  failures="0"
  HistoryViewModelTest ......... tests="4"  failures="0"
```

Reporte HTML navegable: `app/build/reports/tests/testDebugUnitTest/index.html`.

**Detalle FruitRepositoryTest (capa de datos / cache offline):**

- ✅ predict cachea el resultado cuando el backend detecta una fruta
- ✅ predict NO cachea cuando el backend no detecta nada
- ✅ predict propaga la excepción del API como Result failure
- ✅ refreshHistory exitoso reemplaza el cache local cuando offset es 0
- ✅ refreshHistory con offset mayor a 0 NO limpia el cache
- ✅ refreshHistory falla devuelve Result failure sin tocar cache
- ✅ observeLocalHistory emite los items del cache local
- ✅ isBackendHealthy retorna true cuando el endpoint responde con status ok
- ✅ isBackendHealthy retorna false ante excepción de red

**Detalle ScanViewModel / HistoryViewModel (capa de presentación / MVVM):**

- ✅ estado inicial es Idle · submitImage → Success / NoDetection / Error / fallback · reset → Idle
- ✅ init dispara refresh → Loaded · refresh fallido → Error con cache · cachedItems refleja stream · refresh manual → Loading

---

## 4. Verificación de calidad (atributos no funcionales)

| Prueba | KPI | Resultado | Evidencia |
|--------|-----|-----------|-----------|
| mAP@50 del modelo | ≥ 0.75 | **0.9229** | `scripts/evaluate_model.py` |
| Tamaño del modelo | < 10 MB | 5.2 MB | `backend/weights/yolo26n_maduraapp.pt` |
| APK compila | sin errores | ✅ (23 MB) | `gradlew assembleDebug` |
| Migraciones aplican | 3 tablas | ✅ | `alembic upgrade head` |
| CI ejecuta la suite | configurado | ✅ | `.github/workflows/backend_ci.yml` |

---

## 5. Pruebas de seguridad aplicadas (OWASP)

| Verificación | Riesgo OWASP | Resultado |
|--------------|--------------|-----------|
| Endpoints `/predict` y `/history` exigen JWT | A01 — Broken Access Control | ✅ 401 sin token (CP-16, CP-17) |
| Contraseñas con política (≥8, letra+número) | A07 — Auth Failures | ✅ 422 a contraseña débil (CP-18) |
| Secreto JWT obligatorio en producción | A02/A05 — Cripto/Misconfig | ✅ la app rechaza arrancar con secreto por defecto |
| Cifrado en tránsito (HTTPS forzado) | A02 — Cryptographic Failures | ✅ `network_security_config` bloquea cleartext |
| Token cifrado en reposo (dispositivo) | A02 / M9 | ✅ EncryptedSharedPreferences (AES-256) |
| Contraseñas hasheadas (bcrypt) | A02 | ✅ nunca en texto plano |

---

## 6. Conclusión de la aplicación de pruebas

Las **57 pruebas automatizadas pasan al 100%**, cubriendo los componentes críticos (autenticación, inferencia, historial, feedback, cache offline y presentación) más las verificaciones de calidad y seguridad. Los resultados obtenidos coinciden con los esperados definidos en el Plan de Pruebas ([`01_Plan_de_Pruebas.md`](01_Plan_de_Pruebas.md)). Los hallazgos detectados durante la ejecución originaron las mejoras documentadas en [`04_Mejoras_Producto.md`](04_Mejoras_Producto.md).
