# Arranque rápido para la defensa — MaduraApp (jueves 25)

> El AWS Learner Lab es **efímero**: al cerrar la sesión la instancia se detiene y el túnel muere. El jueves la instancia tendrá **IP nueva** y cloudflared dará una **URL nueva**. Esta guía hace ese arranque mecánico (~10 min).
>
> El backend YA quedó construido y configurado el 21/06; el jueves solo hay que **encender, levantar túnel y recompilar el APK**.

---

## Datos fijos

- **Key SSH:** `C:\Users\molte\Downloads\TallerAplicadoProgramacion\maduraapp-key.pem`
- **Usuario SSH:** `ec2-user`
- **Instancia EC2:** `maduraapp-backend` (t3.small, us-east-1)
- **Contenedor:** `maduraapp` (arranca solo con la instancia gracias a `--restart unless-stopped`)

---

## Pasos (día de la defensa)

### 1. Encender el lab y la instancia
1. Canvas → módulo Learner Lab → **Start Lab** → espera el punto **verde** 🟢.
2. Clic en **AWS** → consola → **EC2 → Instancias**.
3. Selecciona `maduraapp-backend` → **Estado de instancia → Iniciar instancia (Start)**.
4. Espera a "En ejecución" + 2/2 checks. **Copia la nueva IPv4 pública.**

### 2. Conectar y verificar el backend (Git Bash en tu PC)
```bash
KEY="/c/Users/molte/Downloads/TallerAplicadoProgramacion/maduraapp-key.pem"
IP=NUEVA_IP_PUBLICA_AQUI

# El contenedor debería arrancar solo; verificar:
ssh -i "$KEY" ec2-user@$IP "sudo docker ps && curl -s http://localhost:8000/v1/health"
# Si NO está corriendo: ssh ... "sudo docker start maduraapp"
```
Debe responder: `{"status":"ok",...,"model_loaded":true}`

### 3. Levantar el túnel HTTPS y obtener la URL
```bash
ssh -i "$KEY" ec2-user@$IP 'pkill cloudflared 2>/dev/null; nohup cloudflared tunnel --url http://localhost:8000 > ~/cloudflared.log 2>&1 & sleep 12; grep -oE "https://[a-z0-9.-]+trycloudflare.com" ~/cloudflared.log | head -1'
```
Copia la URL `https://....trycloudflare.com`.

### 4. Apuntar la app y recompilar el APK (en tu PC)
Edita `Producto/frontend/gradle.properties`:
```properties
maduraapp.api.baseUrl=https://LA_URL_NUEVA.trycloudflare.com/
```
Luego:
```bash
cd Producto/frontend
export JAVA_HOME="/c/Program Files/Android/Android Studio/jbr"
export ANDROID_HOME="$LOCALAPPDATA/Android/Sdk"
./gradlew.bat assembleDebug
# Instalar en el teléfono (USB con depuración activada):
/c/Users/molte/AppData/Local/Android/Sdk/platform-tools/adb.exe install -r app/build/outputs/apk/debug/app-debug.apk
```

### 5. Probar antes de presentar
Abre la app → registro/login → escanear una fruta → ver diagnóstico → historial. Si responde, estás listo.

### 6. Al terminar la defensa
Consola EC2 → instancia → **Detener (Stop)** para no gastar presupuesto. (NUNCA "Terminar".)

---

## Plan B si algo falla el jueves
- **Sin internet del lab / túnel caído:** usa el backend **local** (uvicorn en tu PC + `adb reverse tcp:8000 tcp:8000`, baseUrl `http://localhost:8000/`). La demo igual funciona; explicas que en producción va en AWS.
- **SSH rechazado:** tu IP pública cambió → en el security group de la instancia, edita la regla SSH y pon "Mi IP" de nuevo. O usa **EC2 Instance Connect** (botón Connect en la consola).
- **RAM al límite:** apaga la instancia, cambia el tipo a `t3.medium`, reinicia.

---

## Verificación rápida (checklist)
- [ ] Lab verde + instancia "En ejecución"
- [ ] `docker ps` muestra `maduraapp` Up
- [ ] `/v1/health` → `model_loaded:true`
- [ ] Túnel HTTPS responde
- [ ] APK recompilado con la URL nueva e instalado
- [ ] Escaneo de prueba OK
