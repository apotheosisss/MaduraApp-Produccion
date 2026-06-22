# Despliegue en AWS Academy Learner Lab — MaduraApp

> Guía paso a paso para desplegar el backend de MaduraApp en un **AWS Academy Learner Lab** (sandbox con ~$50 de presupuesto, sesiones temporales, sin GPU, solo `LabRole`).
>
> **Arquitectura elegida:** EC2 `t3.small` + Docker (Dockerfile existente) + SQLite + cloudflared para HTTPS.

---

## 0. Antes de empezar — entender el Learner Lab

| Hecho | Implicación |
|-------|-------------|
| La sesión dura ~4 h; al cerrar el lab la instancia se **detiene** | Reábrela y reinicia la instancia; **la IP pública y la URL del túnel cambian** |
| Presupuesto ~$50 | `t3.small` cuesta ~$0.02/h. **Apaga la instancia** (`stop`) cuando no la uses |
| Sin GPU | El modelo corre en CPU (~200 ms). Sin problema |
| Solo existe `LabRole` (no puedes crear IAM) | Usa la instancia tal cual; no intentes crear roles |
| Región | Normalmente `us-east-1`. No la cambies |

> **Regla de oro:** apaga (Stop, no Terminate) la instancia al terminar cada sesión para no gastar presupuesto. *Terminate* borra todo (incluida la BD SQLite).

---

## 1. Crear la instancia EC2

1. Abre el Learner Lab → **Start Lab** (espera el punto verde) → **AWS** (abre la consola).
2. Consola → **EC2** → **Launch instance**.
3. Configuración:
   - **Name:** `maduraapp-backend`
   - **AMI:** Amazon Linux 2023 (la que viene por defecto)
   - **Instance type:** `t3.small` (2 GB RAM)
   - **Key pair:** crea uno nuevo (`maduraapp-key`) y **descarga el `.pem`** (lo necesitas para SSH)
   - **Network settings → Edit → Security group:** crea uno con estas reglas de entrada:
     - SSH (22) desde **My IP**
     - Custom TCP (8000) desde **My IP** (opcional; con cloudflared no es estrictamente necesario, útil para probar)
   - **Storage:** 16 GB (suficiente; la imagen Docker + modelo pesan ~2 GB)
4. **Launch instance.**

> Si `t3.small` se queda corto de RAM al cargar el modelo, sube a `t3.medium` (4 GB). Apaga primero, cambia el tipo, reinicia.

---

## 2. Conectarse por SSH

Desde tu PC (Git Bash / PowerShell), en la carpeta donde está el `.pem`:

```bash
chmod 400 maduraapp-key.pem   # (Git Bash). En Windows nativo: usar icacls o conectar via consola EC2 Instance Connect
ssh -i maduraapp-key.pem ec2-user@<IP_PUBLICA_DE_LA_INSTANCIA>
```

> Alternativa sin `.pem`: en la consola EC2 selecciona la instancia → **Connect** → **EC2 Instance Connect** (SSH desde el navegador).

---

## 3. Instalar Docker y el código

Ya conectado a la instancia:

```bash
# Docker
sudo dnf update -y
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user      # para usar docker sin sudo
newgrp docker                          # aplica el grupo en la sesión actual

# Obtener el código (repo privado → usar token personal de GitHub)
git clone https://github.com/apotheosisss/MaduraApp-Produccion.git
# Si pide credenciales: usuario = tu usuario GitHub, password = un Personal Access Token (PAT)
cd MaduraApp-Produccion/Producto/backend
```

> **Repo privado:** crea un PAT en GitHub (Settings → Developer settings → Tokens, scope `repo`) y úsalo como contraseña. El modelo `weights/yolo26n_maduraapp.pt` viene incluido en el repo, así que no hay que subirlo aparte.

---

## 4. Configurar variables de entorno (seguras)

Genera un secreto JWT fuerte y crea el `.env`:

```bash
# Generar secreto (cópialo)
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# Crear .env (reemplaza el valor del secreto por el generado)
cat > .env <<'EOF'
ENVIRONMENT=production
JWT_SECRET_KEY=PEGA_AQUI_EL_SECRETO_GENERADO
JWT_EXPIRE_DAYS=30
DB_URL=sqlite+aiosqlite:///./maduraapp_prod.db
CORS_ORIGINS=https://maduraapp.cl
CONFIDENCE_THRESHOLD=0.55
EOF
```

> Notas:
> - `ENVIRONMENT=production` activa el endurecimiento (rechaza secreto por defecto y CORS `*`).
> - `CORS_ORIGINS` no puede ser `*` en producción. La app Android es nativa (no usa CORS), así que cualquier valor no-`*` sirve; dejamos un dominio placeholder.
> - SQLite escribe `maduraapp_prod.db` dentro del contenedor; para que **persista** entre reinicios del contenedor, lo montamos como volumen (paso 5).

---

## 5. Construir y levantar el backend (Docker)

```bash
# Construir la imagen (incluye el modelo y dependencias)
docker build -t maduraapp-backend .

# Levantar el contenedor con la BD persistida en el host
docker run -d \
  --name maduraapp \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  -v /home/ec2-user/maduraapp-data:/app/data \
  -e DB_URL=sqlite+aiosqlite:////app/data/maduraapp_prod.db \
  maduraapp-backend

# Aplicar migraciones dentro del contenedor
docker exec maduraapp alembic upgrade head

# Verificar
curl http://localhost:8000/v1/health
# → {"status":"ok","model_loaded":true,...}
```

> El volumen `/home/ec2-user/maduraapp-data` mantiene la BD aunque recrees el contenedor. El `-e DB_URL` sobreescribe la ruta para que apunte al volumen.

---

## 6. Exponer por HTTPS con cloudflared

La app Android **exige HTTPS**, así que no sirve la IP pública en HTTP directo. Usamos un túnel:

```bash
# Instalar cloudflared
curl -L --output cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Levantar el túnel (déjalo corriendo; o usa nohup/screen)
cloudflared tunnel --url http://localhost:8000
```

Verás una línea como:

```
https://algo-aleatorio.trycloudflare.com
```

Esa es tu **URL pública HTTPS**. Para que siga viva tras cerrar el SSH:

```bash
nohup cloudflared tunnel --url http://localhost:8000 > ~/cloudflared.log 2>&1 &
grep trycloudflare ~/cloudflared.log   # ver la URL
```

---

## 7. Apuntar la app Android al backend desplegado

En tu PC, edita `Producto/frontend/gradle.properties`:

```properties
maduraapp.api.baseUrl=https://algo-aleatorio.trycloudflare.com/
```

Recompila e instala el APK:

```bash
cd Producto/frontend
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

Prueba el flujo: registro → login → escaneo → rating → historial, ahora contra el backend en AWS.

---

## 8. Apagar para no gastar presupuesto

Al terminar cada sesión:

```
Consola EC2 → instancia → Instance state → Stop instance
```

Al volver: **Start instance** → reconecta por SSH → el contenedor arranca solo (`--restart unless-stopped`) → relanza cloudflared (paso 6) → actualiza la URL en la app (paso 7).

> **Nunca uses Terminate** salvo que quieras borrar todo. Stop conserva el disco y la BD.

---

## 9. Checklist de la demo (defensa)

- [ ] Start Lab + Start instance
- [ ] SSH a la instancia
- [ ] Contenedor corriendo: `docker ps` y `curl localhost:8000/v1/health`
- [ ] cloudflared corriendo → copiar URL HTTPS
- [ ] `gradle.properties` con la URL → recompilar APK → instalar
- [ ] Probar flujo completo en el teléfono
- [ ] (al terminar) Stop instance

---

## 10. Alternativa sin cloudflared (HTTP directo)

Si prefieres no usar túnel, puedes permitir HTTP en claro **solo hacia tu instancia**:

1. Asigna una **Elastic IP** a la instancia (IP fija entre reinicios; en Learner Lab está permitido, costo mínimo mientras esté asociada a una instancia encendida).
2. Añade esa IP a `network_security_config.xml`:
   ```xml
   <domain-config cleartextTrafficPermitted="true">
       <domain includeSubdomains="false">TU.ELASTIC.IP.AQUI</domain>
   </domain-config>
   ```
3. `gradle.properties`: `maduraapp.api.baseUrl=http://TU.ELASTIC.IP:8000/`
4. Abre el puerto 8000 en el security group desde tu IP.
5. Recompila el APK (una sola vez, porque la Elastic IP es estable).

> Ventaja: no recompilas cada sesión. Desventaja: tráfico en HTTP (aceptable solo para demo de clase en red controlada; menos seguro que cloudflared).

---

## Resumen de costos estimados (presupuesto $50)

| Recurso | Costo | Nota |
|---------|-------|------|
| EC2 t3.small | ~$0.02/h | Solo mientras esté **encendida** |
| Almacenamiento EBS 16 GB | ~$1.3/mes | Mientras exista la instancia |
| cloudflared | $0 | Gratis |
| SQLite | $0 | En la instancia |
| Transferencia de datos | mínima | Demo de baja escala |

Encendiendo la instancia solo para pruebas y la defensa, el gasto total es de **pocos dólares**, muy por debajo de los $50.
