# Pruebas de Rendimiento y Tiempos de Respuesta — MaduraApp

> **Estado de Avance 3 — TPY1101**
> Responde a las observaciones del docente: (2) tiempos de respuesta del servicio en un **ambiente controlado** y (3) **prueba de rendimiento con usuarios concurrentes**.

---

## 1. Ambiente controlado (dónde está montado el servicio y la red)

| Componente | Detalle |
|------------|---------|
| **Servicio (producción)** | API FastAPI dentro de un contenedor **Docker** en **AWS EC2 `t3.small`** (2 vCPU, 2 GB RAM, **sin GPU**), región **us-east-1 (Virginia, EE.UU.)**, expuesto por una **IP elástica fija** sobre el puerto 8000. Base de datos SQLite en la instancia. |
| **Modelo** | YOLO26n (5,2 MB), inferencia en **CPU**. |
| **Cliente de prueba** | PC del estudiante (Windows 11, Chile), conexión residencial. |
| **Red** | Internet pública. Entre el cliente (Chile) y el servidor (Virginia) hay un **RTT de red de ~150-200 ms** que se suma a cada petición en producción. |
| **Herramienta de medición** | Script propio en Python (`httpx` + `ThreadPoolExecutor`), `scripts_perf/medir_rendimiento.py`. Abre **una conexión nueva por petición** (simula clientes móviles independientes, sin keep-alive). |

> **Nota metodológica:** para **aislar el tiempo de procesamiento** del servicio (sin el ruido de la red pública), la corrida documentada aquí se ejecutó contra el **mismo binario desplegado, corriendo en local (`localhost`)**, con el modelo real cargado. El tiempo de red de producción (~150-200 ms RTT a AWS) debe **sumarse** a estas cifras para estimar la latencia extremo a extremo desde Chile. El mismo script puede ejecutarse contra la IP de AWS (`python medir_rendimiento.py http://3.215.43.61:8000`) para obtener las cifras con red incluida.

---

## 2. Tiempos de respuesta (peticiones secuenciales)

| Endpoint | n | Mín | Promedio | p95 | Máx | Errores |
|----------|---|-----|----------|-----|-----|---------|
| `GET /v1/health` | 30 | 238,7 ms | 251,7 ms | 267,2 ms | 270,0 ms | 0 |
| `POST /v1/predict` (inferencia) | 15 | 439,4 ms | 455,9 ms | 487,3 ms | 487,3 ms | 0 |

**Lectura:**
- El `/health` no ejecuta el modelo; su latencia (~250 ms) está dominada por el establecimiento de conexión del cliente en cada petición (overhead cliente + loopback en el equipo de prueba), no por el servidor.
- El `/predict` agrega sobre eso el **tiempo de inferencia real del modelo**: aprox. **200 ms** (455,9 − 251,7), consistente con el KPI de verificación (< 400 ms p95 de inferencia).
- En **producción (AWS desde Chile)** se suma el RTT de red (~150-200 ms): una predicción extremo a extremo ronda **~600-700 ms**, aceptable para una app de captura puntual.

---

## 3. Prueba de rendimiento con usuarios concurrentes

Se dispararon peticiones en paralelo con distintos niveles de concurrencia (usuarios simultáneos).

### 3.1 `GET /v1/health` (carga liviana)

| Usuarios concurrentes | n | Promedio | p95 | Throughput | Errores |
|----------------------|---|----------|-----|-----------|---------|
| 5 | 40 | 395,5 ms | 429,9 ms | 12,5 req/s | 0 |
| 10 | 40 | 484,9 ms | 515,6 ms | 20,3 req/s | 0 |
| 20 | 40 | 851,4 ms | 1.046 ms | 21,5 req/s | 0 |
| 50 | 40 | 1.604 ms | 1.706 ms | 21,8 req/s | 0 |

### 3.2 `POST /v1/predict` (carga real: inferencia)

| Usuarios concurrentes | n | Promedio | p95 | Throughput | Errores |
|----------------------|---|----------|-----|-----------|---------|
| 3 | 12 | 646,7 ms | 936,4 ms | 4,3 req/s | 0 |
| 6 | 12 | 1.168 ms | 1.646 ms | 4,3 req/s | 0 |

**Lectura:**
- **Cero errores** en todos los niveles, incluso con **50 usuarios concurrentes** → el servicio es **estable bajo carga** (no se cae ni se queda sin memoria).
- El throughput de `/health` se estabiliza en **~21-22 req/s** (límite del esquema de conexión nueva por petición en el equipo de prueba).
- El throughput de `/predict` se mantiene en **~4,3 req/s** y la latencia sube con la concurrencia: el cuello de botella es la **CPU** (la inferencia YOLO es intensiva en cómputo y se procesa por turnos). Es el comportamiento esperado de un modelo de IA en CPU sin GPU.

---

## 4. Conclusiones

1. **Tiempos de respuesta** adecuados para el caso de uso (captura puntual de una foto): ~200 ms de inferencia local; ~600-700 ms extremo a extremo desde Chile contra AWS.
2. **Estabilidad bajo concurrencia**: 0 errores hasta 50 usuarios simultáneos; el sistema degrada la latencia de forma controlada, sin caídas.
3. **Cuello de botella identificado**: la CPU durante la inferencia. Mejora futura para alta concurrencia: instancia con más vCPU o GPU, o una cola de inferencia.
4. La medición es **reproducible** con el script versionado; basta cambiar la URL para medir contra el entorno local o el de AWS.

---

## 5. Cómo reproducir

```bash
cd Producto/backend
# Contra el backend en AWS (incluye red):
./.venv/Scripts/python.exe scripts_perf/medir_rendimiento.py http://3.215.43.61:8000
# Contra un backend local (solo procesamiento):
./.venv/Scripts/python.exe scripts_perf/medir_rendimiento.py http://127.0.0.1:8000
```

Genera `perf_results.json` con los datos crudos. *(Datos de esta corrida: 25/06/2026, backend local con modelo real, equipo del estudiante.)*
