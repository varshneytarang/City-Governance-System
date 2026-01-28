# Professional Agent Architecture - Setup Guide

## 🎯 Overview

This document provides complete setup instructions for the Professional Water Department Agent architecture with all database tables, test suites, and dependencies.

---

## 📋 Prerequisites

1. **PostgreSQL 14+** installed and running
2. **Python 3.10+** installed
3. **Git** for version control
4. **Groq API Key** (for Llama 3.3 70B LLM)

---

## 🗄️ Database Setup

### Step 1: Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE city_mas;

-- Connect to database
\c city_mas

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Step 2: Run Migrations

```powershell
# Navigate to backend directory
cd backend

# Run migration script (applies all migrations in order)
python run_migration_v2.py
```

**Migrations Applied:**
- `001_water_fire_agents.sql` - Water/Fire agent tables
- `002_professional_agent_architecture.sql` - Agent decisions, budgets, projects, workers, etc.

### Step 3: Verify Tables

The migration script automatically verifies table creation. Expected tables:

**Professional Architecture:**
- `agent_decisions` - Audit trail for all agent decisions
- `department_budgets` - Monthly budget tracking
- `projects` - Project cost tracking
- `work_schedules` - Work scheduling and conflicts
- `workers` - Manpower availability
- `pipelines` - Pipeline health monitoring
- `reservoirs` - Emergency backup water supply
- `incidents` - Safety risk tracking

**Water/Fire Agents:**
- `water_infrastructure` - Water pipeline infrastructure
- `water_incidents` - Water-related incidents
- `water_resources` - Water resources (reservoirs, pumps)
- `fire_stations` - Fire station data
- `emergency_incidents` - Emergency incident tracking
- `agent_messages` - Inter-agent communication

---

## 🐍 Python Environment Setup

### Step 1: Create Virtual Environment

```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 2: Install Dependencies

```powershell
# Install all requirements
pip install -r requirements.txt
```

**Key Dependencies:**
- `langgraph==0.2.45` - Workflow orchestration
- `langchain-groq==0.2.0` - Groq LLM integration
- `sqlalchemy==2.0.35` - Database ORM
- `asyncpg==0.30.0` - Async PostgreSQL driver
- `fastapi==0.115.0` - API framework
- `pytest==8.3.3` - Testing framework

### Step 3: Configure Environment Variables

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost/city_mas

# Groq API (for Llama 3.3 70B)
GROQ_API_KEY=your_groq_api_key_here

# Optional
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Get Groq API Key:**
1. Visit https://console.groq.com
2. Sign up for free account
3. Generate API key
4. Copy to `.env` file

---

## 🧪 Testing

### Test Suite 1: Agent-to-Human Escalation

Tests scenarios where agent must escalate to human decision-makers.

```powershell
# Run agent-to-human tests
python -m pytest test_agent_to_human.py -v -s
```

**Test Scenarios:**
1. Low confidence escalation
2. Policy violation escalation
3. High risk escalation
4. All plans infeasible
5. Budget constraint violation
6. Emergency override request

### Test Suite 2: Agent-to-Agent Coordination

Tests scenarios where agents must collaborate.

```powershell
# Run agent-to-agent tests
python -m pytest test_agent_to_agent.py -v -s
```

**Test Scenarios:**
1. Water-Fire coordination
2. Water-Roads coordination
3. Water-Electric grid coordination
4. Multi-agent resource conflict
5. Sequential agent workflow
6. Cross-department data query
7. Complex multi-agent project

### Run All Tests

```powershell
# Run all tests
python -m pytest test_agent_to_human.py test_agent_to_agent.py -v

# Run with coverage
pip install pytest-cov
python -m pytest test_agent_to_human.py test_agent_to_agent.py --cov=app --cov-report=html
```

---

## 🏗️ Architecture Verification

### Verify Water Agent V2 Structure

```powershell
# Check all water_v2 files exist
ls backend/app/agents/water_v2/

# Expected files:
# __init__.py          - Module exports
# state.py             - DepartmentState definition
# tools.py             - 6 deterministic tools
# agent.py             - 14 workflow nodes (Phases 3-14)
# graph.py             - LangGraph workflow
# README.md            - Complete documentation
# LOOP_EXPLAINED.md    - Loop mechanism explanation
# FEASIBILITY_EXPLAINED.md - Constraint checking details
# BUDGET_CONSTRAINT_ADDED.md - Budget feature summary
```

### Verify Database Tables

```powershell
# Run verification script
python verify_setup.py
```

Expected output:
```
✅ Database connection successful
✅ All required tables exist
✅ Sample data loaded
✅ Indexes created
✅ Triggers configured
```

---

## 🚀 Running the Agent

### Manual Test (Python Script)

```python
# test_manual.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.agents.water_v2.graph import create_workflow
from app.agents.water_v2.state import InputEvent
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def test_agent():
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        input_event = InputEvent(
            event_type="maintenance_request",
            location="Downtown",
            priority="medium",
            description="Routine pipeline inspection needed",
            citizen_id="C12345",
            requested_shift_days=2,
        )
        
        result = await workflow.ainvoke({"input_event": input_event})
        
        print("\n📊 Result:")
        print(f"  Decision: {result['decision']}")
        print(f"  Feasible: {result['feasible']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Response: {result['response'][:200]}...")

asyncio.run(test_agent())
```

Run it:
```powershell
python test_manual.py
```

### Via FastAPI (Future Integration)

```powershell
# Start server (after API routes created)
uvicorn app.main:app --reload

# Test endpoint
curl -X POST http://localhost:8000/api/water-v2/request \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "maintenance_request",
    "location": "Downtown",
    "priority": "medium",
    "description": "Pipeline inspection",
    "citizen_id": "C12345",
    "requested_shift_days": 2
  }'
```

---

## 📊 Database Schema Overview

### Agent Decision Flow

```
1. Request arrives → InputEvent created
2. Agent processes → Uses 6 tools to gather facts
3. Evaluates feasibility → Checks 6 constraints
4. Makes decision → approve/deny/escalate
5. Stores audit → agent_decisions table
```

### Budget Tracking Flow

```
1. Tool estimates cost → days × ₹12,500
2. Queries department_budgets → Get monthly allocation
3. Queries projects → Get spent amount
4. Calculates available → total - spent
5. Checks constraints → sufficient + utilization ≤ 90%
6. Returns result → budget_available, estimated_cost, sufficient
```

### Manpower Allocation Flow

```
1. Query workers table → Get active workers
2. Query work_schedules → Get already scheduled workers
3. Calculate available → total - scheduled
4. Compare to required → min_manpower = 5
5. Returns result → sufficient = (available >= required)
```

---

## 🔧 Troubleshooting

### Database Connection Issues

```powershell
# Test connection
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://postgres:password@localhost/city_mas'))"
```

If fails:
1. Check PostgreSQL is running: `Get-Service postgresql*`
2. Verify credentials in `.env`
3. Ensure database exists: `psql -U postgres -l`

### Groq API Issues

```powershell
# Test Groq connection
python -c "from langchain_groq import ChatGroq; llm = ChatGroq(model='llama-3.3-70b-versatile'); print(llm.invoke('Hello').content)"
```

If fails:
1. Check API key in `.env`
2. Verify internet connection
3. Check Groq quota: https://console.groq.com

### Import Errors

```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Test Failures

```powershell
# Run with verbose output
python -m pytest test_agent_to_human.py::test_low_confidence_escalation -vvs
```

---

## 📚 Next Steps

1. **Create FastAPI Routes**
   - Add `/api/water-v2/request` endpoint
   - Implement request validation
   - Return structured responses

2. **Add Frontend Integration**
   - Create UI for submitting requests
   - Display agent decisions
   - Show confidence scores

3. **Implement Other Agents**
   - Fire Department Agent
   - Roads Department Agent
   - Electric Department Agent

4. **Add Monitoring**
   - Prometheus metrics
   - Decision analytics dashboard
   - Performance tracking

---

## 📖 Documentation

- **Architecture:** `backend/app/agents/water_v2/README.md`
- **Loop Mechanism:** `backend/app/agents/water_v2/LOOP_EXPLAINED.md`
- **Feasibility Logic:** `backend/app/agents/water_v2/FEASIBILITY_EXPLAINED.md`
- **Budget Feature:** `backend/app/agents/water_v2/BUDGET_CONSTRAINT_ADDED.md`

---

## ✅ Setup Checklist

- [ ] PostgreSQL installed and running
- [ ] Database `city_mas` created
- [ ] UUID extension enabled
- [ ] Migrations run successfully (`run_migration_v2.py`)
- [ ] All tables verified
- [ ] Virtual environment created
- [ ] Dependencies installed (`requirements.txt`)
- [ ] `.env` file configured with DATABASE_URL and GROQ_API_KEY
- [ ] Agent-to-human tests pass
- [ ] Agent-to-agent tests pass
- [ ] Manual agent test works

---

**You're all set! 🎉**

The Professional Water Department Agent architecture is ready for deployment!
