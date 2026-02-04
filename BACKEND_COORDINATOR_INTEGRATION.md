# Backend → Coordinator → Agent Integration

## Overview

The backend now routes **ALL** requests through the **Coordination Agent**, which dispatches them to the appropriate department agent.

## Architecture

```
┌──────────────┐
│    Client    │
│  (Frontend/  │
│   API Call)  │
└──────┬───────┘
       │
       │ POST /api/v1/query
       │ {type, location, ...}
       ↓
┌──────────────────────────────┐
│    Backend (FastAPI)         │
│  - Receives request          │
│  - Determines agent type     │
│  - Creates job record        │
└──────┬───────────────────────┘
       │
       │ coordinator.query_agent(agent_type, request)
       ↓
┌──────────────────────────────┐
│  Coordination Agent          │
│  - Routes to agent           │
│  - Handles conflicts         │
│  - Caches agent instances    │
└──────┬───────────────────────┘
       │
       │ agent.decide(request)
       ↓
┌──────────────────────────────┐
│  Department Agent            │
│  (Water/Engineering/Fire/    │
│   Sanitation/Health/Finance) │
│  - Runs LangGraph workflow   │
│  - Makes LLM calls           │
│  - Returns decision          │
└──────┬───────────────────────┘
       │
       │ Response
       ↓
┌──────────────────────────────┐
│    Backend                   │
│  - Stores result             │
│  - Client polls for result   │
└──────────────────────────────┘
```

## API Endpoints

### 1. Submit Query (NEW)

**POST** `/api/v1/query`

Submit a query that will be routed through the Coordination Agent.

**Request Body:**
```json
{
  "type": "capacity_query",
  "location": "Downtown",
  "reason": "Need water pressure info",
  "from": "Client"
}
```

**Response:**
```json
{
  "job_id": "uuid-here",
  "status": "queued",
  "agent_type": "water"
}
```

**Agent Type Routing:**
- `capacity_query`, `schedule_shift_request`, `maintenance_request` → **water**
- `project_planning`, `infrastructure_assessment`, `road_repair` → **engineering**
- `fire_emergency`, `fire_inspection`, `fire_safety_assessment` → **fire**
- `waste_collection`, `street_cleaning`, `sanitation_inspection` → **sanitation**
- `health_inspection`, `disease_outbreak`, `vaccination_campaign` → **health**
- `budget_approval`, `cost_estimation`, `financial_audit` → **finance**

### 2. Get Query Result

**GET** `/api/v1/query/{job_id}`

Fetch the complete job status and result.

**Response:**
```json
{
  "id": "uuid",
  "agent_id": "water",
  "status": "succeeded",
  "created_at": "2026-02-04T...",
  "finished_at": "2026-02-04T...",
  "result": {
    "decision": "escalate",
    "reason": "Policy violation detected",
    "requires_human_review": true,
    "details": {
      "feasible": true,
      "policy_compliant": false,
      "confidence": 0.62,
      "plan": {...}
    }
  }
}
```

### 3. Get Decision Only

**GET** `/api/v1/query/{job_id}/result`

Convenience endpoint that returns only status and result.

**Response:**
```json
{
  "status": "succeeded",
  "result": {
    "decision": "recommend",
    "confidence": 0.85,
    ...
  }
}
```

### 4. Health Check

**GET** `/api/v1/health`

Check backend and coordinator status.

**Response:**
```json
{
  "status": "ok",
  "coordinator": "initialized",
  "version": "0.2"
}
```

## Request Types by Department

### Water Department
- `capacity_query` - Check water capacity/pressure
- `schedule_shift_request` - Request schedule change
- `emergency_response` - Emergency water issue
- `maintenance_request` - Routine maintenance
- `pipeline_repair` - Pipeline repair work
- `water_quality_check` - Water quality assessment

### Engineering Department
- `project_planning` - Plan infrastructure project
- `infrastructure_assessment` - Assess infrastructure
- `road_repair` - Road repair work
- `bridge_inspection` - Bridge inspection
- `construction_approval` - Construction approval

### Fire Department
- `fire_emergency` - Fire emergency response
- `fire_inspection` - Fire safety inspection
- `fire_safety_assessment` - Safety assessment
- `hazmat_response` - Hazardous materials
- `rescue_operation` - Rescue operation

### Sanitation Department
- `waste_collection` - Waste collection
- `street_cleaning` - Street cleaning
- `sanitation_inspection` - Sanitation inspection
- `recycling_request` - Recycling request
- `hazardous_waste_disposal` - Hazardous waste

### Health Department
- `health_inspection` - Health inspection
- `disease_outbreak` - Disease outbreak response
- `vaccination_campaign` - Vaccination campaign
- `restaurant_inspection` - Restaurant inspection
- `public_health_assessment` - Public health assessment

### Finance Department
- `budget_approval` - Budget approval
- `cost_estimation` - Cost estimation
- `financial_audit` - Financial audit
- `revenue_forecast` - Revenue forecast
- `expenditure_review` - Expenditure review

## Running the Backend

### 1. Start Backend Server

```bash
# From project root
uvicorn backend.app.server:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Integration

```bash
# Run integration test
python test_backend_coordinator.py
```

### 3. Make API Calls

```bash
# Submit query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "type": "capacity_query",
    "location": "Downtown",
    "reason": "Test query"
  }'

# Get result (replace JOB_ID)
curl http://localhost:8000/api/v1/query/{JOB_ID}
```

## Example: Full Workflow

```python
import requests
import time

# 1. Submit query
response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "type": "capacity_query",
        "location": "Downtown",
        "reason": "Need water info"
    }
)
job = response.json()
job_id = job["job_id"]

# 2. Poll for result
while True:
    response = requests.get(f"http://localhost:8000/api/v1/query/{job_id}")
    job = response.json()
    
    if job["status"] == "succeeded":
        print("Decision:", job["result"]["decision"])
        break
    elif job["status"] == "failed":
        print("Error:", job["error"])
        break
    
    time.sleep(2)  # Wait 2 seconds
```

## Benefits

✅ **Unified Entry Point** - All requests go through coordinator  
✅ **Automatic Routing** - Request type determines agent  
✅ **Conflict Detection** - Coordinator checks for conflicts  
✅ **Agent Caching** - Agent instances reused for performance  
✅ **Async Processing** - Background job execution  
✅ **Full LLM Integration** - All 6 LLM nodes execute  
✅ **Backward Compatible** - Legacy endpoints still work  

## Migration from Legacy Endpoints

### Old Way (Deprecated)
```python
POST /api/v1/agents/water/query
```

### New Way (Recommended)
```python
POST /api/v1/query
```

The old endpoints still work but route through the coordinator internally.

## What Changed

### Before
```
Client → Backend → Direct LLM Call → Response
```

### After
```
Client → Backend → Coordinator → Agent (13 nodes) → Response
                                   ↓
                              6 LLM calls
```

Now you get the **full agentic workflow** with:
- Context loading
- Intent analysis
- Goal setting
- Planning
- Tool execution
- Policy validation
- Confidence estimation
- And more!

## Troubleshooting

### "Coordination Agent not initialized"
- Backend failed to start coordinator
- Check logs for initialization errors
- Verify database connection

### Long Response Times
- First request: ~8-10 seconds (agent instantiation + LLM calls)
- Subsequent requests: ~2-3 seconds (cached agent + LLM calls)
- This is normal for full agentic workflow

### "Unknown request type"
- Request type not in routing table
- Defaults to water agent
- Add your type to `_determine_agent_type()` in server.py

## Next Steps

1. **Frontend Integration** - Update frontend to use new `/api/v1/query` endpoint
2. **Monitoring** - Add logging/metrics for coordinator queries
3. **Caching** - Consider result caching for identical queries
4. **Rate Limiting** - Add rate limiting for production use

---

**Status:** ✅ **IMPLEMENTED AND READY**  
**Version:** 0.2  
**Date:** February 4, 2026
