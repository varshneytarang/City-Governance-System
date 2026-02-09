# Quick Start Guide

Get the City Governance System running in under 5 minutes! 🚀

## Prerequisites

- **Docker Desktop**: [Download here](https://www.docker.com/products/docker-desktop/)
- **API Key**: Get a free key from [Groq](https://console.groq.com/) or [OpenAI](https://platform.openai.com/)

## Installation (3 Steps)

### Step 1: Get the Code
```bash
git clone <your-repo-url>
cd City-Governance-System
```

### Step 2: Configure API Key
```bash
# Copy the environment template
copy .env.example .env

# Open .env and add your API key
notepad .env
```

Edit this line:
```env
GROQ_API_KEY=your_actual_api_key_here
```

### Step 3: Deploy
```powershell
# Run the deployment script
.\deploy.ps1 start
```

That's it! 🎉

## Access Your Application

Wait about 30 seconds for all services to start, then visit:

- **🌐 Frontend**: http://localhost
- **🔌 Backend API**: http://localhost:8000
- **📖 API Docs**: http://localhost:8000/docs

## First Test

Try asking the Water Agent a question:

```bash
curl -X POST http://localhost:8000/api/agent/water \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is the current water quality?\"}"
```

Or visit the frontend at http://localhost and interact through the UI!

## Common Commands

```powershell
# View live logs
.\deploy.ps1 logs

# Check service status
.\deploy.ps1 status

# Stop everything
.\deploy.ps1 stop

# Restart services
.\deploy.ps1 restart

# Complete reset (WARNING: deletes all data)
.\deploy.ps1 reset
```

## Development Mode

Want to make code changes with live reload?

```powershell
.\deploy.ps1 start -Dev
```

This enables:
- ✅ Hot module replacement (frontend)
- ✅ Auto-reload on code changes (backend)
- ✅ Debug ports exposed
- ✅ Direct database access

## Troubleshooting

### "Port already in use"
```powershell
# Stop conflicting services
docker ps  # Find the conflicting container
docker stop <container-id>

# Or change ports in docker-compose.yml
```

### "API key not found"
```powershell
# Check your .env file
cat .env | grep GROQ_API_KEY

# Make sure there are no quotes around the key
# ✅ CORRECT: GROQ_API_KEY=gsk_abc123
# ❌ WRONG: GROQ_API_KEY="gsk_abc123"
```

### "Database connection failed"
```powershell
# Wait for database to be ready
.\deploy.ps1 status

# Check if postgres is healthy
docker-compose ps postgres
```

### Services won't start
```powershell
# Check Docker is running
docker ps

# If Docker isn't running, start Docker Desktop
# Then try again:
.\deploy.ps1 start
```

## What's Running?

When you start the system, 3 Docker containers are created:

1. **Frontend** (Nginx serving React app)
   - Port 80
   - Handles UI and routing
   - Proxies API requests to backend

2. **Backend** (Python FastAPI + AI Agents)
   - Port 8000
   - 7 AI agents (coordination, water, fire, engineering, health, finance, sanitation)
   - LangGraph workflows
   - Database connections

3. **Database** (PostgreSQL 17)
   - Port 5432
   - 31 tables across 6 departments
   - Pre-loaded with sample data

## Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for advanced deployment options
- Check [README.md](README.md) for full documentation
- Explore the API at http://localhost:8000/docs
- Review [STRUCTURE_UPDATE.md](STRUCTURE_UPDATE.md) to understand the architecture

## Getting Help

1. Check the [Troubleshooting](#troubleshooting) section above
2. View logs: `.\deploy.ps1 logs`
3. Check service status: `.\deploy.ps1 status`
4. Read the [DEPLOYMENT.md](DEPLOYMENT.md) guide

## Stopping the System

When you're done:

```powershell
.\deploy.ps1 stop
```

This stops all containers but preserves your data. Next time you run `.\deploy.ps1 start`, everything will be back where you left it!

---

**Enjoy building with the City Governance System! 🏛️**
