# City Governance System - Deployment Script
# This script automates the deployment process

param(
    [Parameter()]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'reset', 'build')]
    [string]$Action = 'start',
    
    [Parameter()]
    [switch]$Dev,
    
    [Parameter()]
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Success "✓ Docker found: $dockerVersion"
    } catch {
        Write-Error "✗ Docker not found. Please install Docker Desktop."
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-Success "✓ Docker Compose found: $composeVersion"
    } catch {
        Write-Error "✗ Docker Compose not found. Please install Docker Compose."
        exit 1
    }
    
    # Check if Docker is running
    try {
        docker ps | Out-Null
        Write-Success "✓ Docker daemon is running"
    } catch {
        Write-Error "✗ Docker daemon is not running. Please start Docker Desktop."
        exit 1
    }
    
    # Check .env file
    if (-not (Test-Path ".env")) {
        Write-Warning "⚠ .env file not found. Creating from .env.example..."
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Warning "⚠ Please edit .env and add your API keys before continuing."
            Write-Info "Press Enter when ready..."
            Read-Host
        } else {
            Write-Error "✗ .env.example not found. Cannot create .env file."
            exit 1
        }
    } else {
        Write-Success "✓ .env file exists"
    }
}

# Build services
function Build-Services {
    Write-Info "Building Docker images..."
    
    if ($Dev) {
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
    } else {
        docker-compose build
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Build completed successfully"
    } else {
        Write-Error "✗ Build failed"
        exit 1
    }
}

# Start services
function Start-Services {
    Write-Info "Starting City Governance System..."
    
    # Initialize database first
    Write-Info "Starting database..."
    docker-compose up -d postgres
    
    Write-Info "Waiting for database to be ready - 10 seconds..."
    Start-Sleep -Seconds 10
    
    # Check if database is healthy
    $dbHealth = docker-compose ps postgres --format json | ConvertFrom-Json | Select-Object -ExpandProperty Health
    if ($dbHealth -eq "healthy" -or $dbHealth -eq "") {
        Write-Success "✓ Database is ready"
    } else {
        Write-Warning "⚠ Database health check unclear, continuing anyway..."
    }
    
    # Start all services
    Write-Info "Starting all services..."
    if ($Dev) {
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    } else {
        docker-compose up -d
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ All services started successfully"
        Write-Info ""
        Write-Info "Access the application at:"
        Write-Success "  Frontend:  http://localhost"
        Write-Success "  Backend:   http://localhost:8000"
        Write-Success "  API Docs:  http://localhost:8000/docs"
        Write-Info ""
        Write-Info "View logs with: .\deploy.ps1 logs"
    } else {
        Write-Error "✗ Failed to start services"
        exit 1
    }
}

# Stop services
function Stop-Services {
    Write-Info "Stopping City Governance System..."
    docker-compose down
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Services stopped successfully"
    } else {
        Write-Error "✗ Failed to stop services"
        exit 1
    }
}

# Restart services
function Restart-Services {
    Stop-Services
    Start-Sleep -Seconds 2
    Start-Services
}

# Show logs
function Show-Logs {
    Write-Info "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f
}

# Show status
function Show-Status {
    Write-Info "Service Status:"
    docker-compose ps
    
    Write-Info ""
    Write-Info "Resource Usage:"
    docker stats --no-stream
    
    Write-Info ""
    Write-Info "Health Checks:"
    
    # Backend health
    try {
        $backend = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-Success "✓ Backend: Healthy"
    } catch {
        Write-Error "✗ Backend: Unhealthy or not responding"
    }
    
    # Frontend health
    try {
        $frontend = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 5 -UseBasicParsing
        if ($frontend.StatusCode -eq 200) {
            Write-Success "✓ Frontend: Healthy"
        }
    } catch {
        Write-Error "✗ Frontend: Unhealthy or not responding"
    }
    
    # Database health
    try {
        $db = docker-compose exec -T postgres pg_isready -U postgres
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✓ Database: Healthy"
        }
    } catch {
        Write-Error "✗ Database: Unhealthy or not responding"
    }
}

# Reset everything
function Reset-All {
    Write-Warning "⚠ This will delete ALL data including database contents!"
    $confirm = Read-Host "Are you sure? Type 'yes' to continue"
    
    if ($confirm -ne "yes") {
        Write-Info "Reset cancelled."
        return
    }
    
    Write-Info "Stopping and removing all containers and volumes..."
    docker-compose down -v
    
    Write-Info "Removing Docker images..."
    docker-compose down --rmi local
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Reset completed successfully"
        Write-Info "Run '.\deploy.ps1 start' to start fresh"
    } else {
        Write-Error "✗ Reset failed"
        exit 1
    }
}

# Main script
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " City Governance System Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

switch ($Action) {
    'start' {
        Test-Prerequisites
        if (-not $NoBuild) {
            Build-Services
        }
        Start-Services
    }
    'stop' {
        Stop-Services
    }
    'restart' {
        Restart-Services
    }
    'logs' {
        Show-Logs
    }
    'status' {
        Show-Status
    }
    'reset' {
        Reset-All
    }
    'build' {
        Test-Prerequisites
        Build-Services
    }
}
