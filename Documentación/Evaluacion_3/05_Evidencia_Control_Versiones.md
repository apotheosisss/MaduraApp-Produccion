# Evidencia de Control de Versiones — MaduraApp

> **Estado de Avance 3 — TPY1101**
> Documenta la **gestión de control de versiones** (software adecuado) y la evidencia de las copias de configuración del proyecto.

---

## 1. Herramienta y repositorios

| Aspecto | Detalle |
|---------|---------|
| Software de control de versiones | **Git** |
| Hosting remoto | **GitHub** — https://github.com/apotheosisss/MaduraApp-Produccion |
| Estrategia de ramas | Git Flow simplificado (`main` estable + ramas `feature/*`) |
| Convención de commits | **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`) |
| Total de commits (a la fecha) | **40** |
| Integración continua | GitHub Actions — `backend_ci.yml` (suite pytest en cada push) |

---

## 2. Ramas del proyecto

| Rama | Propósito | Estado |
|------|-----------|--------|
| `main` | Código estable, entregado en Evaluación 2 | Protegida |
| `feature/auth-feedback` | Autenticación JWT + feedback + mejoras de seguridad y UI (Evaluación 3) | Activa |
| `backup/2026-05-26-pre-sync` | Respaldo previo a una sincronización mayor | Archivada |

---

## 3. Historial de commits relevantes (Evaluación 3)

Trabajo de la rama `feature/auth-feedback` que sustenta esta evaluación:

```text
88ffe74  feat(android): rediseño UI con design system Material 3 (ui-ux-pro-max)
db09e83  feat(android): cifrado en tránsito/reposo e indicador de seguridad (OWASP)
43cd16c  feat(backend): endurecer seguridad según OWASP
a8fc521  fix(android): alinear API y tests con AuthInterceptor tras merge
69b7293  fix(backend): dependencias de auth (email-validator, bcrypt 4.0.1) y tests JWT
8a7a495  Merge branch 'main' into feature/auth-feedback
263f76a  feat: autenticación JWT + feedback con rating 1-5 estrellas
```

Cada commit es atómico, descriptivo y trazable a una mejora del producto (ver [`04_Mejoras_Producto.md`](04_Mejoras_Producto.md)).

---

## 4. Copias de configuración (configuration items)

Archivos de configuración versionados que permiten reconstruir el ambiente:

| Ítem de configuración | Archivo | Propósito |
|-----------------------|---------|-----------|
| Variables de entorno (plantilla) | `Producto/backend/.env.example` | Documenta config sin exponer secretos |
| Dependencias backend | `Producto/backend/requirements.txt` | Reproducir entorno Python |
| Migraciones de BD | `Producto/backend/alembic/versions/` | Esquema versionado (Alembic) |
| Build Android | `Producto/frontend/app/build.gradle.kts` | Dependencias y configuración Gradle |
| Política de red Android | `app/src/main/res/xml/network_security_config.xml` | HTTPS forzado |
| Pipeline CI | `.github/workflows/backend_ci.yml` | Pruebas automáticas |
| Exclusiones | `.gitignore` | Evita versionar secretos, pesos del modelo, builds |

> **Seguridad de la configuración:** los secretos (claves JWT, credenciales de BD) **nunca** se versionan; solo se incluye la plantilla `.env.example`. Los pesos del modelo (`*.pt`) están en `.gitignore`.

---

## 5. Buenas prácticas aplicadas

- **Commits atómicos** con mensajes según Conventional Commits, legibles y trazables.
- **Ramas de feature** aisladas de `main`; integración mediante merge controlado (se resolvieron conflictos de `build.gradle.kts` y binarios documentadamente).
- **CI** que ejecuta la suite en cada push, impidiendo integrar código que rompa las pruebas.
- **Sin secretos en el repositorio** (verificado); `.gitignore` cubre `.env`, `weights/`, builds y artefactos.
- **Respaldo** (`backup/2026-05-26-pre-sync`) antes de operaciones de riesgo en el historial.

---

## 6. Cómo reproducir el proyecto desde cero

```bash
git clone https://github.com/apotheosisss/MaduraApp-Produccion
cd MaduraApp-Produccion

# Backend
cd Producto/backend
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env          # completar JWT_SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload

# Android
cd ../frontend
./gradlew assembleDebug
```
