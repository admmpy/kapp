# Script to recreate the Python virtual environment for Windows
# This fixes the issue where the venv was created on Mac with Mac-specific paths

$backendDir = "backend"
$venvDir = Join-Path $backendDir "venv"
$requirementsFile = Join-Path $backendDir "requirements.txt"

Write-Host "Setting up Python virtual environment for Windows..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "ERROR: Python not found. Please install Python 3.12 or activate your conda environment." -ForegroundColor Red
    Write-Host "If you're using conda, activate it first: conda activate base" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version
Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
Write-Host "Python path: $($pythonCmd.Source)" -ForegroundColor Gray
Write-Host ""

# Remove existing Mac-created venv if it exists
if (Test-Path $venvDir) {
    Write-Host "Removing existing virtual environment (created on Mac)..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $venvDir
    Write-Host "Removed old virtual environment" -ForegroundColor Green
}

# Create new Windows virtual environment
Write-Host "Creating new Windows virtual environment..." -ForegroundColor Cyan
Push-Location $backendDir

python -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Virtual environment created successfully!" -ForegroundColor Green
Write-Host ""

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
$activateScript = "venv\Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "ERROR: Virtual environment activation script not found" -ForegroundColor Red
    Pop-Location
    exit 1
}

& $activateScript

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install requirements
if (Test-Path $requirementsFile) {
    Write-Host "Installing requirements from requirements.txt..." -ForegroundColor Cyan
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Some packages may have failed to install. Check the output above." -ForegroundColor Yellow
    } else {
        Write-Host "All requirements installed successfully!" -ForegroundColor Green
    }
} else {
    Write-Host "WARNING: requirements.txt not found at $requirementsFile" -ForegroundColor Yellow
}

Pop-Location

Write-Host ""
Write-Host "Virtual environment setup complete!" -ForegroundColor Green
Write-Host "You can now run .\start-servers.ps1 to start the application." -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate the venv manually in the future, run:" -ForegroundColor Gray
Write-Host "  cd backend" -ForegroundColor Gray
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
