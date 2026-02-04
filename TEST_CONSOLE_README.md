# 🧪 API Test Console - Complete Testing Suite

## Quick Start

### 1. Start Everything (Easiest)

**Windows:**
```bash
start_full_stack.bat
```

**Linux/Mac:**
```bash
chmod +x start_full_stack.sh
./start_full_stack.sh
```

### 2. Start Manually

**Terminal 1 - Backend:**
```bash
python start_backend.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Access Test Console

Open your browser: **http://localhost:5173/#test**

## What You'll See

### 🎨 Beautiful Testing Interface

The test console provides:

#### Left Panel - Request Configuration
- **Endpoint Configuration**
  - Backend URL input
  - Health check button
  
- **Request Builder**
  - Request type dropdown (30+ types)
  - Location input
  - Reason input
  - Estimated cost (optional)
  - Custom JSON fields
  - Submit button
  
- **Response Display**
  - Job ID
  - Agent type (shows routing)
  - Status (queued/running/succeeded/failed)
  - Decision details
  - Full JSON response

#### Right Panel - Activity Logs
- Real-time log streaming
- Color-coded messages
  - 🔵 Blue = Info
  - ✅ Green = Success
  - ⚠️ Yellow = Warning
  - ❌ Red = Error
- Timestamps
- Clear logs button
- Polling status

#### Bottom - Quick Test Scenarios
Three preset buttons for instant testing:
- 💧 **Water Query** - Tests water department
- 🏗️ **Engineering Query** - Tests engineering with cost
- 🚒 **Fire Query** - Tests fire department

## Features

### ✅ Complete Request Testing
- Select from 30+ predefined request types
- Automatic agent routing
- Real-time status updates
- Auto-polling for results

### ✅ All 6 Departments Supported
1. **Water** - capacity_query, schedule_shift_request, maintenance_request, etc.
2. **Engineering** - project_planning, road_repair, infrastructure_assessment, etc.
3. **Fire** - fire_inspection, fire_emergency, hazmat_response, etc.
4. **Sanitation** - waste_collection, street_cleaning, recycling_request, etc.
5. **Health** - health_inspection, disease_outbreak, vaccination_campaign, etc.
6. **Finance** - budget_approval, cost_estimation, financial_audit, etc.

### ✅ Visual Feedback
- Loading states
- Polling animation
- Success/error states
- Color-coded logs
- Progress indicators

### ✅ Developer-Friendly
- Full JSON responses
- Request/response logging
- Error details
- Expandable details
- Copy-paste ready

## Testing Workflow

### Basic Test

1. **Check Backend Health**
   - Click "🏥 Check Health"
   - Should see: ✅ Backend healthy, Coordinator: initialized

2. **Select Request Type**
   - Choose from dropdown (e.g., "capacity_query")
   - Notice it shows: "Will route to: water agent"

3. **Fill Details**
   - Location: "Downtown"
   - Reason: "Testing water pressure"

4. **Submit**
   - Click "🚀 Submit Query"
   - Watch logs stream in real-time
   - Job ID appears
   - Polling starts automatically

5. **View Results**
   - Status updates every 2 seconds
   - Final decision appears
   - See full details

### What You're Testing

```
Your Browser (Test Console)
    ↓
    POST /api/v1/query
    ↓
Backend (FastAPI)
    ↓
    coordinator.query_agent()
    ↓
Coordination Agent
    ↓
    AgentDispatcher
    ↓
Department Agent (Water/Engineering/Fire/etc.)
    ↓
    13-node LangGraph workflow
    ↓
    6 LLM API calls
    ↓
    Coordination checkpoint
    ↓
Agent Decision
    ↓
Response back through chain
    ↓
Your Browser shows result
```

## Request Types by Department

### 💧 Water Department
- `capacity_query` - Check water capacity/pressure
- `schedule_shift_request` - Request schedule change
- `emergency_response` - Emergency water issue
- `maintenance_request` - Routine maintenance
- `pipeline_repair` - Pipeline repair work
- `water_quality_check` - Water quality assessment

### 🏗️ Engineering Department
- `project_planning` - Plan infrastructure project
- `infrastructure_assessment` - Assess infrastructure
- `road_repair` - Road repair work
- `bridge_inspection` - Bridge inspection
- `construction_approval` - Construction approval

### 🚒 Fire Department
- `fire_emergency` - Fire emergency response
- `fire_inspection` - Fire safety inspection
- `fire_safety_assessment` - Safety assessment
- `hazmat_response` - Hazardous materials
- `rescue_operation` - Rescue operation

### 🗑️ Sanitation Department
- `waste_collection` - Waste collection
- `street_cleaning` - Street cleaning
- `sanitation_inspection` - Sanitation inspection
- `recycling_request` - Recycling request
- `hazardous_waste_disposal` - Hazardous waste

### 🏥 Health Department
- `health_inspection` - Health inspection
- `disease_outbreak` - Disease outbreak response
- `vaccination_campaign` - Vaccination campaign
- `restaurant_inspection` - Restaurant inspection
- `public_health_assessment` - Public health assessment

### 💰 Finance Department
- `budget_approval` - Budget approval
- `cost_estimation` - Cost estimation
- `financial_audit` - Financial audit
- `revenue_forecast` - Revenue forecast
- `expenditure_review` - Expenditure review

## Understanding Results

### Decision Types

#### "escalate"
```json
{
  "decision": "escalate",
  "requires_human_review": true,
  "details": {
    "feasible": true,
    "policy_compliant": false,
    "confidence": 0.62
  }
}
```
**Means:** Agent needs human review
**Reasons:** Policy violation, high risk, budget exceeded, conflicts

#### "recommend"
```json
{
  "decision": "recommend",
  "requires_human_review": false,
  "recommendation": {
    "action": "proceed",
    "confidence": 0.85
  }
}
```
**Means:** Agent approved, can proceed
**Details:** High confidence, all criteria met

### Status Flow

1. **queued** - Job submitted, waiting to start
2. **running** - Agent executing workflow
3. **succeeded** - Completed successfully
4. **failed** - Error occurred (check error field)

## Advanced Testing

### Custom Fields

Add custom JSON in the "Custom Fields" box:

```json
{
  "priority": "high",
  "deadline": "2026-02-10",
  "requester": "City Manager",
  "urgency": "critical"
}
```

These will be merged with your request.

### Test Conflict Detection

1. Submit first query:
   ```
   Type: project_planning
   Location: Downtown
   Cost: 50000
   ```

2. While first is running, submit second:
   ```
   Type: capacity_query
   Location: Downtown
   ```

3. Second agent should detect first agent's active plan in coordination checkpoint!

### Test Different Costs

Try different costs to see budget handling:
- Small: 1000 (should approve)
- Medium: 50000 (might need review)
- Large: 500000 (likely escalate)

## Troubleshooting

### ❌ "Failed to fetch"
**Problem:** Can't connect to backend

**Check:**
1. Is backend running? `http://localhost:8000/docs`
2. Correct URL in endpoint config?
3. CORS enabled in backend? (Should be by default)

### ⚠️ "Polling timeout"
**Problem:** Results not returned in 60 seconds

**Reasons:**
- First request takes ~10 seconds (cold start)
- LLM API issues
- Database connection problems

**Try:**
- Wait and retry
- Check backend logs
- Verify GROQ_API_KEY is set

### ⚠️ "Coordinator not initialized"
**Problem:** Backend started but coordinator failed

**Check:**
1. Backend logs for errors
2. Database connection
3. Python dependencies installed

## Performance Expectations

### First Request (Cold Start)
- Submit → Running: ~1 second
- Running → Succeeded: ~8-10 seconds
- **Total: ~10 seconds**

Why? Agent instantiation + LLM calls + database queries

### Subsequent Requests (Warm)
- Submit → Running: ~0 seconds
- Running → Succeeded: ~2-3 seconds
- **Total: ~3 seconds**

Why? Agent cached, only LLM calls needed

## Tips & Tricks

### 💡 Tip 1: Keep Logs Open
The activity logs show exactly what's happening. Watch for:
- Request sent
- Job ID received
- Polling started
- Status updates
- Final result

### 💡 Tip 2: Use Quick Scenarios
The three quick buttons are perfect for:
- Quick smoke tests
- Testing after code changes
- Demo purposes

### 💡 Tip 3: Check Full JSON
Click "Full JSON Response" to see:
- Complete agent decision
- All plan details
- Tool execution results
- Observations and feasibility

### 💡 Tip 4: Test All Departments
Make sure to test each department:
- Water ✅
- Engineering ✅
- Fire ✅
- Sanitation ✅
- Health ✅
- Finance ✅

### 💡 Tip 5: Monitor Backend Logs
Keep backend terminal visible to see:
- Agent workflow execution
- LLM API calls
- Coordination checkpoints
- Database queries

## Next Steps

After testing successfully:

1. **Integrate with Main UI**
   - Add query submission to main frontend
   - Display results in dashboard
   - Show agent status

2. **Add Real-time Updates**
   - WebSocket for instant updates
   - No more polling
   - Live progress

3. **Build Monitoring Dashboard**
   - Active jobs
   - Agent status
   - Success/failure rates
   - Performance metrics

4. **Add History**
   - Store past queries
   - View previous results
   - Compare decisions

## Screenshots Guide

### Initial View
- Clean interface with two panels
- Request builder on left
- Empty logs on right
- Quick scenarios at bottom

### After Submit
- Job ID displayed
- Logs showing activity
- Polling animation
- Status updates

### Completed
- Green success message
- Decision details
- Full response
- Expandable JSON

## Architecture Validated

This test console validates the complete architecture:

✅ **Backend Integration**
- FastAPI receiving requests
- CORS working
- Job creation and storage

✅ **Coordinator Integration**
- Requests routed through coordinator
- Agent type determination working
- AgentDispatcher functioning

✅ **Agent Execution**
- Full 13-node workflow
- 6 LLM API calls
- Coordination checkpoint
- Decision generation

✅ **Bidirectional Communication**
- Backend → Coordinator → Agent
- Agent → Coordinator (checkpoint)
- Response flowing back correctly

---

**Access:** http://localhost:5173/#test  
**Status:** ✅ Ready to use  
**Last Updated:** February 4, 2026
