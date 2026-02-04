# API Test Console - Quick Start Guide

## Overview

A comprehensive frontend testing page to test the complete backend integration:
**Frontend → Backend → Coordinator → Agents**

## Access the Test Console

### Option 1: Direct URL
```
http://localhost:5173/#test
```

### Option 2: Click Button
1. Open the frontend: `http://localhost:5173`
2. Click the "🧪 API Test Console" button in the top-right corner

## Starting the Services

### 1. Start Backend (Terminal 1)
```bash
cd City-Governance-System
python start_backend.py

# OR manually
uvicorn backend.app.server:app --reload --port 8000
```

**Backend will be available at:** `http://localhost:8000`

### 2. Start Frontend (Terminal 2)
```bash
cd City-Governance-System/frontend
npm run dev
```

**Frontend will be available at:** `http://localhost:5173`

## Using the Test Console

### Features

#### 1. **Endpoint Configuration**
- Set backend URL (default: `http://localhost:8000`)
- Click "🏥 Check Health" to verify backend is running

#### 2. **Request Builder**
- **Request Type**: Choose from 30+ request types across 6 departments
  - Water: capacity_query, schedule_shift_request, etc.
  - Engineering: project_planning, road_repair, etc.
  - Fire: fire_inspection, fire_emergency, etc.
  - Sanitation: waste_collection, street_cleaning, etc.
  - Health: health_inspection, disease_outbreak, etc.
  - Finance: budget_approval, cost_estimation, etc.
  
- **Location**: Enter location (Downtown, Main Street, etc.)
- **Reason**: Purpose of the request
- **Estimated Cost**: Optional cost field
- **Custom Fields**: Add custom JSON fields

#### 3. **Submit Query**
- Click "🚀 Submit Query" to send request
- Backend will automatically route to correct agent
- Job ID will be displayed
- Polling starts automatically

#### 4. **View Results**
- **Status**: queued → running → succeeded/failed
- **Decision**: Agent's decision (escalate/recommend)
- **Details**: Feasibility, policy compliance, confidence
- **Full JSON**: Complete response for debugging

#### 5. **Activity Logs**
- Real-time logs of all API calls
- Color-coded by type (info/success/error/warning)
- Timestamps for each action
- Clear logs button

### Quick Test Scenarios

Three preset buttons for quick testing:

1. **💧 Water Query**
   - Type: capacity_query
   - Location: Downtown
   - Tests water department routing

2. **🏗️ Engineering Query**
   - Type: project_planning
   - Location: Main Street
   - Cost: 50,000
   - Tests engineering department routing

3. **🚒 Fire Query**
   - Type: fire_inspection
   - Location: Industrial Zone
   - Tests fire department routing

## Testing Workflow

### Step-by-Step Test

1. **Health Check**
   ```
   Click "🏥 Check Health"
   Expected: ✅ Backend healthy, Coordinator: initialized
   ```

2. **Submit Query**
   ```
   Select request type: capacity_query
   Enter location: Downtown
   Click "🚀 Submit Query"
   ```

3. **Observe Logs**
   ```
   [Time] Submitting query to backend...
   [Time] Query submitted successfully!
   [Time] Job ID: xxx-xxx-xxx
   [Time] Routed to: water agent
   [Time] Starting to poll for results...
   [Time] Polling attempt 1/30...
   [Time] Status: running
   [Time] Polling attempt 2/30...
   [Time] Status: running
   ...
   [Time] ✅ Job completed successfully!
   ```

4. **View Results**
   ```
   Status: SUCCEEDED
   Decision: escalate (or recommend)
   Feasible: Yes
   Policy Compliant: No (or Yes)
   Confidence: 62%
   ```

## What Happens Behind the Scenes

```
Frontend Test Page
    ↓ POST /api/v1/query
Backend (FastAPI)
    ↓ coordinator.query_agent()
Coordination Agent
    ↓ AgentDispatcher
Department Agent
    ↓ 13-node LangGraph workflow
    ↓ 6 LLM API calls
    ↓ Coordination checkpoint
Agent Decision
    ↓ Response
Backend stores result
    ↓ Frontend polls
GET /api/v1/query/{job_id}
    ↓ Display result
```

## Troubleshooting

### Backend Not Responding
**Error:** Health check failed: Failed to fetch

**Solutions:**
1. Verify backend is running: `http://localhost:8000/docs`
2. Check backend terminal for errors
3. Verify GROQ_API_KEY is set (for LLM calls)
4. Check database is accessible

### CORS Errors
**Error:** Cross-Origin Request Blocked

**Solution:** Backend should have CORS enabled. If not, add to `server.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Polling Timeout
**Error:** Polling timeout (60 seconds)

**Causes:**
1. Agent workflow taking too long (first request ~10s, warm ~3s)
2. LLM API timeout
3. Database connection issues

**Solutions:**
1. Check backend logs for errors
2. Verify GROQ_API_KEY is valid
3. Try again (second request should be faster)

### Unknown Request Type
**Warning:** Unknown request type 'xxx', defaulting to water agent

**Solution:** Use one of the predefined request types from the dropdown

## Testing Different Scenarios

### Test 1: Simple Query (No Conflicts)
```json
{
  "type": "capacity_query",
  "location": "Downtown",
  "reason": "Check water pressure"
}
```
**Expected:** Agent processes, returns decision

### Test 2: Query with Cost
```json
{
  "type": "project_planning",
  "location": "Main Street",
  "estimated_cost": 50000,
  "reason": "Road repair"
}
```
**Expected:** Routes to engineering, checks budget

### Test 3: Emergency Query
```json
{
  "type": "fire_emergency",
  "location": "Industrial Zone",
  "reason": "Fire outbreak"
}
```
**Expected:** Routes to fire department, high priority

### Test 4: Multiple Requests (Conflict Detection)
1. Submit first query with location "Downtown"
2. While first is processing, submit second query with same location
3. Second query should detect conflict with first

## Response Interpretation

### Decision: "escalate"
- Requires human review
- Reasons: Policy violation, budget exceeded, high-risk, conflicts detected
- Details show: feasibility, policy compliance, confidence

### Decision: "recommend"
- Agent approved the plan
- Can proceed without human review
- High confidence score
- All criteria met

### Status: "failed"
- Agent execution error
- Check error field for details
- Check backend logs

## Advanced Features

### Custom Fields
Add any custom JSON fields:
```json
{
  "priority": "high",
  "deadline": "2026-02-10",
  "requester": "City Manager"
}
```

### Testing Specific Agents
Use request types to target specific departments:
- `capacity_query` → Water
- `project_planning` → Engineering
- `fire_inspection` → Fire
- `waste_collection` → Sanitation
- `health_inspection` → Health
- `budget_approval` → Finance

## Performance Metrics

### First Request (Cold Start)
- Backend initialization: ~2s
- Agent loading: ~1s
- Workflow execution: ~8s
- **Total: ~10-12 seconds**

### Subsequent Requests (Warm)
- Agent cached: ~0s
- Workflow execution: ~3s
- **Total: ~3-5 seconds**

### Polling
- Interval: 2 seconds
- Max attempts: 30 (60 seconds total)
- Auto-start after submit

## Tips

1. **Keep Logs Open** - Provides real-time feedback
2. **Use Quick Scenarios** - Fast way to test different departments
3. **Check Full JSON** - Useful for debugging
4. **Test Health First** - Verify backend is ready
5. **Try Multiple Requests** - Test conflict detection
6. **Monitor Backend Logs** - See LLM calls and agent workflow

## Next Steps

After testing the API:
1. Integrate with main frontend UI
2. Add real-time status updates (WebSocket)
3. Create dashboard for monitoring
4. Add result history/cache
5. Build workflow visualization

---

**Test Console Location:** `http://localhost:5173/#test`  
**Backend API Docs:** `http://localhost:8000/docs`  
**Status:** ✅ Ready for testing
