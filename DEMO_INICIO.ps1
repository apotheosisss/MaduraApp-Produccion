# =====================================================================
#  DEMO_INICIO.ps1 — MaduraApp · Script de arranque para la sala
#  Ejecutar en PowerShell como Administrador (o usuario normal si hay permisos)
#
#  Uso: click derecho → "Ejecutar con PowerShell"
#       o desde PowerShell: .\DEMO_INICIO.ps1
# =====================================================================

$ErrorActionPreference = "Continue"
$REPO_DIR   = $PSScriptRoot                     # La carpeta donde está este script
$BACKEND    = Join-Path $REPO_DIR "Producto\backend"
$VENV       = Join-Path $BACKEND ".venv"
$MODEL      = Join-Path $BACKEND "weights\yolo26n_maduraapp.pt"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   MaduraApp — Setup demo (sala)"           -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Verificar Python ──────────────────────────────────────────────
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow

$python = $null
foreach ($cmd in @("python", "python3", "python3.12", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(1[0-9]|[89])") {
            $python = $cmd
            Write-Host "      OK — $ver ($cmd)" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host ""
    Write-Host "  ERROR: No se encontro Python 3.10+ en este equipo." -ForegroundColor Red
    Write-Host ""
    Write-Host "  Opciones rapidas:" -ForegroundColor Yellow
    Write-Host "  A) Instalar Python 3.12 desde https://python.org/downloads"
    Write-Host "     (marcar 'Add to PATH' durante la instalacion, luego re-ejecutar este script)"
    Write-Host ""
    Write-Host "  B) Si Docker esta instalado, ejecutar:"
    Write-Host "     cd Producto"
    Write-Host "     docker-compose up --build"
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

# ── 2. Verificar que el modelo esta presente ─────────────────────────
Write-Host "[2/6] Verificando modelo YOLO..." -ForegroundColor Yellow

if (-not (Test-Path $MODEL)) {
    Write-Host "      ERROR: No se encontro el modelo en:" -ForegroundColor Red
    Write-Host "      $MODEL"
    Write-Host ""
    Write-Host "      Asegurate de que el archivo yolo26n_maduraapp.pt" -ForegroundColor Yellow
    Write-Host "      este en la carpeta Producto\backend\weights\"
    Read-Host "Presiona Enter para salir"
    exit 1
}

$modelSize = (Get-Item $MODEL).Length / 1MB
Write-Host "      OK — yolo26n_maduraapp.pt ($([math]::Round($modelSize,1)) MB)" -ForegroundColor Green

# ── 3. Crear entorno virtual si no existe ───────────────────────────
Write-Host "[3/6] Preparando entorno virtual..." -ForegroundColor Yellow

if (-not (Test-Path (Join-Path $VENV "Scripts\activate.ps1"))) {
    Write-Host "      Creando venv (primera vez, ~1 min)..." -ForegroundColor Gray
    & $python -m venv $VENV
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      ERROR al crear venv" -ForegroundColor Red
        exit 1
    }
    Write-Host "      Venv creado." -ForegroundColor Green
} else {
    Write-Host "      OK — venv ya existe" -ForegroundColor Green
}

# ── 4. Instalar dependencias ─────────────────────────────────────────
Write-Host "[4/6] Instalando dependencias..." -ForegroundColor Yellow
Write-Host "      (puede tardar 3-8 minutos la primera vez — PyTorch ~200 MB)" -ForegroundColor Gray

$pip = Join-Path $VENV "Scripts\pip.exe"
& $pip install --upgrade pip -q
& $pip install -r (Join-Path $BACKEND "requirements.txt") -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERROR al instalar dependencias." -ForegroundColor Red
    exit 1
}
Write-Host "      OK — dependencias instaladas" -ForegroundColor Green

# ── 5. Crear .env si no existe ───────────────────────────────────────
Write-Host "[5/6] Configurando variables de entorno..." -ForegroundColor Yellow

$envFile = Join-Path $BACKEND ".env"
if (-not (Test-Path $envFile)) {
    @"
API_PORT=8000
YOLO_MODEL_PATH=weights/yolo26n_maduraapp.pt
CONFIDENCE_THRESHOLD=0.55
DB_URL=sqlite+aiosqlite:///./maduraapp_dev.db
AUTH_SECRET_KEY=demo_key_sala
ENVIRONMENT=development
"@ | Out-File -Encoding utf8 $envFile
    Write-Host "      .env creado con configuracion de demo" -ForegroundColor Green
} else {
    Write-Host "      .env ya existe" -ForegroundColor Green
}

# Aplicar migraciones Alembic
$alembic = Join-Path $VENV "Scripts\alembic.exe"
Write-Host "      Aplicando migraciones de base de datos..." -ForegroundColor Gray
Push-Location $BACKEND
& $alembic upgrade head 2>&1 | Out-Null
Pop-Location
Write-Host "      OK — base de datos lista" -ForegroundColor Green

# ── 6. Arrancar el servidor ──────────────────────────────────────────
Write-Host "[6/6] Arrancando backend..." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Backend en: http://localhost:8000"         -ForegroundColor Cyan
Write-Host "  Swagger UI: http://localhost:8000/docs"    -ForegroundColor Cyan
Write-Host ""
Write-Host "  Para la demo desde el telefono:"           -ForegroundColor Cyan
Write-Host "  1. Conectar telefono por USB"
Write-Host "  2. Abrir otra PowerShell y ejecutar:"
Write-Host "     adb reverse tcp:8000 tcp:8000"
Write-Host "  3. Abrir MaduraApp en el telefono"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ctrl+C para detener el servidor"           -ForegroundColor Gray
Write-Host ""

$uvicorn = Join-Path $VENV "Scripts\uvicorn.exe"
Push-Location $BACKEND
& $uvicorn app.main:app --host 0.0.0.0 --port 8000
Pop-Location
