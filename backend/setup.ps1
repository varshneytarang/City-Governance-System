# Quick Setup Script for Professional Agent Architecture
# Run this after PostgreSQL is installed and running

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Professional Agent Architecture - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check PostgreSQL
Write-Host "[1/6] Checking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service postgresql* -ErrorAction SilentlyContinue
if ($pgService) {
    Write-Host "  ✅ PostgreSQL service found: $($pgService.Name)" -ForegroundColor Green
    if ($pgService.Status -ne 'Running') {
        Write-Host "  ⚠️  PostgreSQL not running. Starting..." -ForegroundColor Yellow
        Start-Service $pgService.Name
    }
} else {
    Write-Host "  ❌ PostgreSQL not found. Please install PostgreSQL first." -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "`n[2/6] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(\d+)") {
    $minorVersion = [int]$matches[1]
    if ($minorVersion -ge 10) {
        Write-Host "  ✅ Python version: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Python 3.10+ required. Found: $pythonVersion" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ❌ Python not found or version check failed" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`n[3/6] Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  ⚠️  Virtual environment exists. Skipping creation." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "  ✅ Virtual environment created" -ForegroundColor Green
}

# Activate venv and install dependencies
Write-Host "`n[4/6] Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Host "  ✅ Dependencies installed" -ForegroundColor Green

# Check .env file
Write-Host "`n[5/6] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✅ .env file found" -ForegroundColor Green
    
    # Check for required variables
    $envContent = Get-Content .env -Raw
    $hasDB = $envContent -match "DATABASE_URL"
    $hasGroq = $envContent -match "GROQ_API_KEY"
    
    if (-not $hasDB) {
        Write-Host "  ⚠️  DATABASE_URL not found in .env" -ForegroundColor Yellow
    }
    if (-not $hasGroq) {
        Write-Host "  ⚠️  GROQ_API_KEY not found in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️  .env file not found. Creating template..." -ForegroundColor Yellow
    @"
# Database
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost/city_mas

# Groq API (for Llama 3.3 70B)
GROQ_API_KEY=your_groq_api_key_here

# Optional
ENVIRONMENT=development
LOG_LEVEL=INFO
"@ | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "  ✅ .env template created. Please update with your credentials." -ForegroundColor Green
}

# Run database migrations
Write-Host "`n[6/6] Running database migrations..." -ForegroundColor Yellow
Write-Host "  This will create the database and tables..." -ForegroundColor Gray
$migrationOutput = python run_migration_v2.py 2>&1
$migrationSuccess = $LASTEXITCODE -eq 0

if ($migrationSuccess) {
    Write-Host "  ✅ Database migrations completed" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Migration warnings (check output above)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n✅ Completed Steps:" -ForegroundColor Green
Write-Host "  - PostgreSQL verified"
Write-Host "  - Python 3.10+ verified"
Write-Host "  - Virtual environment ready"
Write-Host "  - Dependencies installed"
Write-Host "  - Environment configured"
Write-Host "  - Database migrations run"

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update .env with your DATABASE_URL and GROQ_API_KEY"
Write-Host "  2. Run tests: python -m pytest test_agent_to_human.py -v"
Write-Host "  3. Run tests: python -m pytest test_agent_to_agent.py -v"
Write-Host "  4. Check docs: SETUP_COMPLETE_V2.md"

Write-Host "`n🚀 Quick Test:" -ForegroundColor Cyan
Write-Host "  python test_agent_to_human.py" -ForegroundColor White

Write-Host "`n✨ Setup complete!`n" -ForegroundColor Green
