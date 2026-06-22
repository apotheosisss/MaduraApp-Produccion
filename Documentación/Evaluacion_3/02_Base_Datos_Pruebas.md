# Base de Datos de Pruebas — MaduraApp

> **Estado de Avance 3 — TPY1101**
> Documenta el ambiente y la **base de datos de pruebas** usada para ejecutar las pruebas de software, según lo solicitado en la rúbrica del encargo.

---

## 1. Estrategia: base de datos efímera y aislada

MaduraApp **no usa la base de datos de producción ni de desarrollo para las pruebas**. Cada corrida de la suite construye una base de datos limpia, la puebla con datos controlados (*fixtures*) y la destruye al finalizar. Esto garantiza:

- **Aislamiento:** una prueba no contamina a otra (sin estado compartido).
- **Reproducibilidad:** mismo resultado en local y en CI.
- **Velocidad:** la BD vive en memoria, sin E/S de disco.
- **Seguridad:** no se exponen datos reales de usuarios en las pruebas.

| Capa | Motor en producción | Motor en pruebas | Aislamiento |
|------|--------------------|--------------------|-------------|
| Backend (API) | PostgreSQL 16 (AWS Lab — pendiente) | **SQLite in-memory** (`aiosqlite`) | Por módulo de test |
| Android (cache) | Room (SQLite en dispositivo) | **MockK** (doble de prueba del DAO) | Por test |

---

## 2. Backend — SQLite in-memory + fixtures

### 2.1 Configuración

Definida en `Producto/backend/tests/conftest.py`:

```python
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="module")
async def client():
    test_engine = create_async_engine(TEST_DB_URL)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)   # crea el esquema
    # ...override de get_db con la sesión de prueba...
    app.state.model = MagicMock()                       # YOLO simulado
```

Puntos clave:

- **`:memory:`** — la base existe solo en RAM durante la corrida del módulo.
- **`Base.metadata.create_all`** — recrea el esquema completo (mismas tablas ORM que producción: `users`, `scans`, `scan_feedback`) sin depender de migraciones.
- **`app.state.model = MagicMock()`** — el modelo YOLO real (5.2 MB) se reemplaza por un *mock*, de modo que las pruebas no requieren los pesos ni GPU/CPU pesada. La detección se simula con `patch("app.routers.predict.inference_svc.run", ...)`.
- **Override de `get_db`** — inyecta la sesión SQLite de prueba en lugar de la real.

### 2.2 Datos de prueba (fixtures)

| Fixture | Qué provee | Uso |
|---------|-----------|-----|
| `client` | Cliente HTTP async (`httpx.AsyncClient`) contra la app con BD in-memory | Todas las pruebas de endpoint |
| `auth_headers` | Registra `testuser` / `test@maduraapp.cl` y devuelve cabecera `Authorization: Bearer <jwt>` real | Pruebas que requieren autenticación |
| `make_jpeg_bytes()` | Genera una imagen JPEG sintética en memoria (PIL) | Pruebas de `/v1/predict` |

Usuario de prueba estándar:

| Campo | Valor |
|-------|-------|
| username | `testuser` |
| email | `test@maduraapp.cl` |
| password | `testpassword123` (cumple política: ≥8, letra + número) |

> Las contraseñas de prueba **también se hashean con bcrypt** (no se almacenan en claro), igual que en producción. El JWT emitido es real y se valida en cada request protegido.

### 2.3 Esquema bajo prueba

```
users(user_id PK, username UNIQUE, email UNIQUE, hashed_password, is_active, created_at)
scans(id PK, user_id FK, fruit_type, maturity_label, confidence, bbox, recommendation, color_code, created_at)
scan_feedback(id PK, scan_id FK, user_id, rating, created_at)
```

---

## 3. Android — dobles de prueba (MockK)

La suite JVM **no toca Room real ni la red**. Sustituye las dependencias por *mocks*:

```kotlin
api   = mockk(relaxed = true)               // MaduraApiService simulado
local = mockk(relaxed = true)               // LocalScanDataSource (Room) simulado
repository = FruitRepository(api, local)
```

| Herramienta | Rol |
|-------------|-----|
| **MockK** | Simula `MaduraApiService` y `LocalScanDataSource`; verifica interacciones (`coVerify`) |
| **kotlinx-coroutines-test** | `runTest` + `advanceUntilIdle` controlan el dispatcher para pruebas deterministas |
| **Turbine** | Verifica la emisión de *flows* (`observeLocalHistory`) |
| **InstantTaskExecutorRule** | Ejecuta LiveData de forma síncrona |

Datos de prueba típicos (`ScanResultDto` de muestra):

| Campo | Valor |
|-------|-------|
| fruitType | `mango` |
| maturityLabel | `OPTIMO` |
| confidence | `0.92` |
| colorCode | `yellow` |

---

## 4. Cómo regenerar la base de pruebas

No requiere pasos manuales: la base se crea y destruye automáticamente al correr la suite.

```bash
# Backend — crea SQLite in-memory, corre 17 tests, destruye
cd Producto/backend && pytest tests/ -v

# Verificar migraciones contra una BD SQLite real (opcional)
alembic upgrade head      # genera maduraapp_dev.db con las 3 tablas

# Android — mocks, sin BD física
cd Producto/frontend && ./gradlew testDebugUnitTest
```

---

## 5. Justificación frente a la rúbrica

- **Funcionalidad:** los datos de prueba ejercitan los caminos felices y de error de cada endpoint y de cada componente Android.
- **Buenas prácticas:** uso de *fixtures*, *mocks* y BD efímera = patrón estándar de la industria (aislamiento, reproducibilidad).
- **Calidad:** la suite corre en CI en cada commit, evitando regresiones.
- **Seguridad:** ningún dato real ni secreto se usa en pruebas; las contraseñas de prueba se hashean igual que en producción.
