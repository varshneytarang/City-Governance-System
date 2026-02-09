# City Governance System - Deployment Guide

## Overview
This guide covers deploying the City Governance System using Docker containers for production.

## Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  PostgreSQL │
│  (Nginx)    │     │  (FastAPI)  │     │   Database  │
│   Port 80   │     │  Port 8000  │     │  Port 5432  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Prerequisites
- Docker 24.0+ and Docker Compose 2.20+
- Git
- API keys for LLM providers (Groq/OpenAI)
- 4GB+ RAM, 10GB+ disk space

## Quick Start

### 1. Clone and Configure
```bash
cd City-Governance-System

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
notepad .env  # Windows
# OR
nano .env     # Linux/Mac
```

### 2. Configure Environment Variables
Edit `.env` file:
```env
# Required
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
POSTGRES_PASSWORD=your_secure_database_password

# Optional
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 3. Initialize Database
```bash
# Start only the database first
docker-compose up -d postgres

# Wait for database to be ready (check health)
docker-compose ps

# Run migrations
docker-compose exec postgres psql -U postgres -d departments -f /docker-entrypoint-initdb.d/complete_schema.sql
docker-compose exec postgres psql -U postgres -d departments -f /docker-entrypoint-initdb.d/comprehensive_seed_data.sql
```

### 4. Start All Services
```bash
# Start backend and frontend
docker-compose up -d

# Check all services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Access the Application
- **Frontend**: http://localhost (or http://localhost:80)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## Development Mode

### Running Backend Locally
```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:GROQ_API_KEY="your_key"  # PowerShell
# export GROQ_API_KEY="your_key"  # Bash

# Run backend
python main.py
```

### Running Frontend Locally
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:5173
```

### Using Docker for Development
```bash
# Override with development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# This mounts local directories for live reloading
```

## Production Deployment

### Build Production Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Deployment to Cloud (AWS/GCP/Azure)

#### Option 1: Docker Compose on VM
```bash
# On cloud VM
git clone <your-repo>
cd City-Governance-System
cp .env.example .env
# Edit .env with production credentials

docker-compose up -d
```

#### Option 2: Kubernetes
```bash
# Convert to Kubernetes manifests
kompose convert -f docker-compose.yml

# Deploy to cluster
kubectl apply -f .
```

#### Option 3: AWS ECS/Fargate
```bash
# Create ECR repositories
aws ecr create-repository --repository-name city-governance-backend
aws ecr create-repository --repository-name city-governance-frontend

# Build and push images
docker-compose build
docker tag city-governance-backend:latest <ecr-url>/city-governance-backend:latest
docker push <ecr-url>/city-governance-backend:latest

# Deploy using ECS task definitions
```

## Database Management

### Backup Database
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres departments > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U postgres departments < backup_20240101.sql
```

### Database Migrations
```bash
# Apply new migration
docker-compose exec postgres psql -U postgres -d departments -f /docker-entrypoint-initdb.d/your_migration.sql

# Check database status
docker-compose exec postgres psql -U postgres -d departments -c "\dt"
```

### Reset Database
```bash
# WARNING: This deletes all data
docker-compose down -v
docker-compose up -d postgres
# Re-run initialization scripts
```

## Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Health Checks
```bash
# Check all service health
docker-compose ps

# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost/health

# Database health
docker-compose exec postgres pg_isready -U postgres
```

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df
```

## Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing API keys - check .env file
# 2. Database not ready - wait for postgres health check
# 3. Port conflict - check if 8000 is in use

# Restart backend
docker-compose restart backend
```

### Frontend Won't Build
```bash
# Check Node modules
cd frontend
npm install

# Rebuild Docker image
docker-compose build --no-cache frontend
```

### Database Connection Issues
```bash
# Check database is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U postgres -c "SELECT version();"

# Check environment variables
docker-compose exec backend env | grep DATABASE
```

### Import Errors in Backend
```bash
# Verify PYTHONPATH is set
docker-compose exec backend env | grep PYTHONPATH

# Should show: PYTHONPATH=/app

# Test imports manually
docker-compose exec backend python -c "from agents.coordination_agent.agent import CoordinationAgent"
```

### Port Conflicts
```bash
# Find process using port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Change ports in docker-compose.yml if needed
```

## Performance Tuning

### Backend Scaling
```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Requires load balancer configuration
```

### Database Optimization
```sql
-- Connect to database
docker-compose exec postgres psql -U postgres departments

-- Analyze tables
ANALYZE;

-- Create indexes for common queries
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_incidents_department ON incidents(department_id);
```

### Nginx Caching (Frontend)
Edit `frontend/nginx.conf` to add caching:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m;

location /api {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    # ... rest of proxy config
}
```

## Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Use strong API keys (never commit to git)
- [ ] Enable HTTPS with SSL certificates (use Nginx reverse proxy)
- [ ] Configure firewall rules (only expose necessary ports)
- [ ] Regular security updates: `docker-compose pull`
- [ ] Implement rate limiting on API endpoints
- [ ] Use environment-specific .env files (never commit .env)
- [ ] Enable Docker security scanning: `docker scan city-governance-backend`
- [ ] Set up log aggregation (ELK stack, Grafana)
- [ ] Configure backup automation

## Updating the Application

### Pull Latest Changes
```bash
# Stop services
docker-compose down

# Pull updates
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run new migrations if any
docker-compose exec postgres psql -U postgres -d departments -f /docker-entrypoint-initdb.d/new_migration.sql
```

### Rolling Updates (Zero Downtime)
```bash
# Update backend
docker-compose build backend
docker-compose up -d --no-deps backend

# Update frontend
docker-compose build frontend
docker-compose up -d --no-deps frontend
```

## Cleanup

### Remove All Containers
```bash
# Stop and remove containers
docker-compose down

# Remove with volumes (WARNING: deletes data)
docker-compose down -v
```

### Clean Docker System
```bash
# Remove unused images
docker image prune

# Remove all unused resources
docker system prune -a
```

## Support

For issues and questions:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure all health checks pass: `docker-compose ps`
4. Review database migrations are applied
5. Check API documentation: http://localhost:8000/docs

## Architecture Details

### Services
- **Frontend**: React + Vite → Nginx (production build)
- **Backend**: FastAPI + LangGraph multi-agent system
- **Database**: PostgreSQL 17 with full schema

### Volumes
- `postgres_data`: Persistent database storage

### Networks
- `city-governance-network`: Bridge network for inter-service communication

### Environment Variables
See `.env.example` for complete list of configuration options.
