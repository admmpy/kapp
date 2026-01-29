# Start Kapp Backend, Frontend, and Ollama Servers for Windows (Monorepo)
#
# This script starts all three components needed for Kapp:
# 1. Ollama (Local LLM server)
# 2. Flask backend server
# 3. React frontend dev server

# Configuration
$backendDir = "backend"
$webDir = "packages\web"
$backendPort = 5001
$ollamaPort = 11434
$ErrorActionPreference = "SilentlyContinue"

Write-Host "Starting Kapp servers for Windows (Monorepo)..." -ForegroundColor Cyan

# ------------------------------------
# Check if backend port is in use
# ------------------------------------
Write-Host "Checking for existing backend process on port $backendPort..."
$existingProcess = Get-NetTCPConnection -LocalPort $backendPort -ErrorAction SilentlyContinue |
                  Select-Object -ExpandProperty OwningProcess -Unique

if ($existingProcess) {
    Write-Host "Found existing process (PID: $existingProcess), terminating..." -ForegroundColor Yellow
    Stop-Process -Id $existingProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Write-Host "Existing process terminated" -ForegroundColor Green
} else {
    Write-Host "No existing process found on port $backendPort" -ForegroundColor Gray
}

# ------------------------------------
# Start Ollama if not running
# ------------------------------------
Write-Host "Checking if Ollama is running on port $ollamaPort..."
$ollamaRunning = Get-NetTCPConnection -LocalPort $ollamaPort -ErrorAction SilentlyContinue

if (-not $ollamaRunning) {
    Write-Host "Starting Ollama..." -ForegroundColor Cyan

    # Check if Ollama is installed
    $ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue
    if ($ollamaPath) {
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Write-Host "Ollama server started" -ForegroundColor Green
    } else {
        Write-Host "Ollama not found. Please install Ollama from: https://ollama.com/download" -ForegroundColor Yellow
        Write-Host "Continuing without Ollama..." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Ollama is already running" -ForegroundColor Green
}

# ------------------------------------
# Start backend
# ------------------------------------
Write-Host "Starting backend on http://localhost:$backendPort..." -ForegroundColor Cyan

# Find Python executable (check for conda first, then venv, then system)
$pythonCmd = $null
$venvPython = Join-Path $backendDir "venv\Scripts\python.exe"

# Check if we're in a conda environment
if ($env:CONDA_DEFAULT_ENV) {
    Write-Host "Using Conda environment: $env:CONDA_DEFAULT_ENV" -ForegroundColor Green
    $pythonCmd = "python"
}
# Check for venv - but verify it's a Windows venv, not a Mac one
elseif (Test-Path $venvPython) {
    # Check if the venv was created on Mac by looking at pyvenv.cfg
    $pyvenvCfg = Join-Path $backendDir "venv\pyvenv.cfg"
    if (Test-Path $pyvenvCfg) {
        $cfgContent = Get-Content $pyvenvCfg -Raw
        if ($cfgContent -match "/Users/" -or $cfgContent -match "/usr/") {
            Write-Host "WARNING: Virtual environment was created on Mac and won't work on Windows." -ForegroundColor Yellow
            Write-Host "Please run .\setup-windows-venv.ps1 to recreate the venv for Windows." -ForegroundColor Yellow
            Write-Host "Falling back to system Python for now..." -ForegroundColor Yellow
            $pythonCmd = "python"
        } else {
            Write-Host "Using virtual environment" -ForegroundColor Green
            $pythonCmd = $venvPython
        }
    } else {
        Write-Host "Using virtual environment" -ForegroundColor Green
        $pythonCmd = $venvPython
    }
}
# Fall back to system Python
else {
    $pythonPath = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonPath) {
        Write-Host "Using system Python (no venv found)" -ForegroundColor Yellow
        $pythonCmd = "python"
    } else {
        Write-Host "Python not found. Please install Python or activate conda environment." -ForegroundColor Red
        Write-Host "If you have a venv, run .\setup-windows-venv.ps1 to recreate it for Windows." -ForegroundColor Yellow
        exit 1
    }
}

# Start backend in a new window so output is visible
$backendScript = Join-Path $backendDir "app.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; $pythonCmd app.py" -WindowStyle Normal

Write-Host "Backend started in new window" -ForegroundColor Green
Start-Sleep -Seconds 3

# ------------------------------------
# Start frontend using npm workspaces
# ------------------------------------
Write-Host "Starting frontend on http://localhost:5173..." -ForegroundColor Cyan

# Check for npm
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    Write-Host "npm not found. Please install Node.js from: https://nodejs.org/" -ForegroundColor Red
    Write-Host "After installing Node.js, RESTART YOUR TERMINAL or COMPUTER" -ForegroundColor Yellow
    Write-Host "Note: Backend is running in separate window - close that window manually" -ForegroundColor Yellow
    exit 1
}

# Ensure node_modules exists at root level
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies." -ForegroundColor Red
        Write-Host "Note: Backend is running in separate window - close that window manually" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Starting npm run web (press Ctrl+C to stop all services)..." -ForegroundColor Cyan
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Frontend starting..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C here to stop frontend" -ForegroundColor Yellow
Write-Host "Backend is running in separate window" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Run the dev command using workspace script
npm run web

Write-Host ""
Write-Host "Frontend stopped." -ForegroundColor Yellow
Write-Host "Note: Backend is still running in separate window - close that window manually to stop it." -ForegroundColor Yellow
Write-Host "Ollama may still be running in the background." -ForegroundColor Gray
