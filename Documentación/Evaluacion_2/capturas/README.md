# Capturas — Evidencia visual para la defensa

Carpeta destinada a screenshots reales del sistema en funcionamiento, que respaldan la evidencia documental de [`../12_Evidencias_Pruebas.md`](../12_Evidencias_Pruebas.md).

---

## 📷 Capturas a tomar antes de la defensa

### Tests automatizados

- [ ] `pytest_9_passed.png` — Terminal mostrando `9 passed` en `pytest tests/ -v`.
- [ ] `gradle_test_passed.png` — Reporte HTML JVM en verde (`./gradlew test`).
- [ ] `github_actions_green.png` — Workflow más reciente verde en https://github.com/apotheosisss/MaduraApp-Produccion/actions

### Backend en producción

- [ ] `render_dashboard_logs.png` — Logs del backend en Render mostrando arranque exitoso.
- [ ] `render_dashboard_metrics.png` — Panel de métricas (CPU/RAM) del último día.
- [ ] `health_endpoint.png` — Browser/Postman mostrando `{"status":"ok","model_loaded":true}`.
- [ ] `predict_response.json` — Response real de POST `/v1/predict` (puede ser texto JSON o screenshot).

### Base de datos

- [ ] `supabase_dashboard.png` — Dashboard de Supabase mostrando la tabla `scans` con datos reales.

### App Android (flujo de demo)

- [ ] `01_selector.png` — Pantalla inicial del selector de fruta (grid 2×2).
- [ ] `02_camera_with_fruit_selected.png` — MainActivity con título dinámico "Escaneando Aguacate Hass" y preview de cámara.
- [ ] `03_loading.png` — ProgressBar durante el escaneo.
- [ ] `04_result_aguacate_optimo.png` — Resultado de aguacate óptimo con semáforo amarillo y recomendación.
- [ ] `05_gallery_picker.png` — Picker del sistema al elegir "🖼 Seleccionar de galería".
- [ ] `06_result_platano.png` — Resultado para plátano con semáforo correspondiente.
- [ ] `07_history.png` — Pantalla de historial con varios escaneos.
- [ ] `08_offline_history.png` — Historial visible con el modo avión activado (cache Room).

### Modelo IA

- [ ] `model_kpi.png` — Captura del archivo `results.txt` o `confusion_matrix.png` del entrenamiento mostrando mAP@50 = 0.9229.

---

## 📐 Formato recomendado

- **Resolución:** mínimo 1280px de ancho para legibilidad en proyector.
- **Formato:** PNG (no JPG — sin compresión con pérdida para texto).
- **Naming:** numeración + descripción en `snake_case`.
- **Marcas (opcional):** flechas/highlights en rojo para destacar partes clave en las screenshots largas.

---

## 🚀 Tips para tomar las capturas

### Android
- **Emulador:** `Ctrl+S` (Windows) captura la pantalla del AVD.
- **Dispositivo físico:** Volumen abajo + power; o vía Android Studio → Device File Explorer.

### Terminal
- **Windows Terminal:** click derecho → Mark → Copiar como imagen (o capturar con Snipping Tool).
- **macOS:** Cmd+Shift+4 + Espacio → click en ventana.
- **Linux:** `gnome-screenshot -w` o herramienta del WM.

### Browser (dashboards de Render/Supabase/GitHub Actions)
- Usar la herramienta de captura del navegador (Firefox: "Take screenshot" en menú contextual; Chrome: DevTools → Capture full-size screenshot).
- Si el dashboard muestra info confidencial (URLs internas, tokens parciales), **redactar con un rectángulo negro** antes de incluir en el informe.

---

## 🔒 Privacidad

**Antes de incluir cualquier captura en el informe entregable:**

- [ ] No contiene tokens de autenticación visibles.
- [ ] No contiene credenciales de Supabase o Render.
- [ ] No contiene direcciones IP privadas que no quieras compartir.
- [ ] Para screenshots de la app: ninguna información personal del dispositivo (nombres de contactos, fotos privadas en la galería).

---

*Tomar estas capturas cerca de la fecha de defensa para que reflejen el estado real del sistema en ese momento.*
