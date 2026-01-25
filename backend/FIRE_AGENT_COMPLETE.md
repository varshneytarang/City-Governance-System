# 🚒 Fire Agent Implementation - Complete

## Overview
The Fire Department Agent has been successfully implemented with complete emergency response capabilities, fire station dispatch, and cross-department coordination using LangGraph multi-agent workflow.

## ✅ Implementation Status
**Status**: COMPLETE  
**Date**: January 24, 2026  
**Agent Type**: Emergency Response & Fire Safety  

## 🏗️ Architecture

### File Structure
```
backend/app/agents/fire/
├── __init__.py           # Package initialization
├── state.py              # FireState TypedDict (40+ fields)
├── tools.py              # Database queries & utilities (9 functions)
├── prompts.py            # LLM prompts (6 templates)
├── policies.py           # Decision policies (8 policy functions)
└── graph.py              # LangGraph workflow (6 nodes)

backend/app/routes/
└── fire.py               # FastAPI endpoints (6 routes)

backend/
└── test_fire_agent.py    # Test scenarios (4 emergency scenarios)
```

### State Management (state.py)
**FireState TypedDict** with 40+ fields across 7 phases:
- **Input Phase**: request_type, emergency_type, location, casualties, building_type, fire_intensity
- **Validation Phase**: validation_status, validation_errors
- **Data Collection Phase**: nearby_stations, active_incidents, station_resources, historical patterns
- **Analysis Phase**: severity_assessment, risk_level, dispatch_plan, response_requirements
- **Decision Phase**: decision, reasoning, estimated_cost, estimated_duration
- **Coordination Phase**: departments_to_notify, coordination_messages
- **Response Phase**: action_items, next_steps, response

### Tools (tools.py) - 9 Functions

1. **fetch_nearby_stations()**: Find fire stations within radius using Haversine distance
2. **get_available_resources()**: Query station personnel, vehicles, equipment
3. **check_active_incidents()**: Find ongoing emergencies in area
4. **get_historical_incident_patterns()**: Analyze past incidents (90-day window)
5. **calculate_distance()**: Haversine formula for lat/long distance
6. **calculate_eta()**: Estimate arrival time (default 50 km/h for emergency vehicles)
7. **assess_severity_score()**: Calculate 0-100 severity score based on incident parameters
8. **calculate_required_resources()**: Determine personnel, vehicles, equipment needed
9. **create_dispatch_plan()**: Build optimal dispatch with primary/backup stations

### Prompts (prompts.py) - 6 Templates

1. **EMERGENCY_ANALYSIS_PROMPT**: Analyze fire/rescue incidents with severity, risks, strategy
2. **INSPECTION_ANALYSIS_PROMPT**: Evaluate fire safety inspection requests
3. **AWARENESS_ANALYSIS_PROMPT**: Review fire safety education program requests
4. **MAINTENANCE_ANALYSIS_PROMPT**: Assess equipment maintenance priorities
5. **DECISION_PROMPT**: Final decision recommendation with reasoning
6. **COORDINATION_PROMPT**: Generate cross-department coordination messages

### Policies (policies.py) - 8 Functions

1. **apply_safety_policy()**: Check casualties, fire intensity, building risks → safety actions
2. **apply_resource_policy()**: Validate personnel/vehicle adequacy → mutual aid triggers
3. **apply_coordination_policy()**: Determine which departments need coordination (Water, Health, Police, etc.)
4. **apply_escalation_policy()**: Decide if escalation to Fire Chief or City Emergency Manager needed
5. **apply_dispatch_policy()**: Make APPROVE/DENY/ESCALATE/COORDINATE decision
6. **calculate_estimated_cost()**: Cost calculation based on personnel, vehicles, duration, severity
7. **calculate_estimated_duration()**: Time estimation (minutes for emergency, hours for others)

**Policy Logic**:
- **Safety First**: Always approve emergencies even with resource constraints
- **Mutual Aid**: Request when resources insufficient
- **Coordination Triggers**: 
  - Water Dept → Major fires (moderate/major/conflagration intensity)
  - Health Dept → Any casualties reported
  - Police Dept → High-rise buildings or mass casualties (>5)
  - Public Works → Industrial/hazmat incidents
  - Environmental → Hazmat incidents
- **Escalation Criteria**:
  - Severity score ≥80 → City Emergency Manager
  - Casualties ≥10 → City Emergency Manager
  - Mutual aid + severity ≥60 → Fire Chief
  - Cost >₹500,000 → Fire Chief

### LangGraph Workflow (graph.py) - 6 Nodes

**Node 1: input_validation_node**
- Validate required fields (request_type, location, description)
- Emergency-specific checks (emergency_type for emergency_response)
- Set casualties to 0 if not provided

**Node 2: data_collection_node**
- Fetch nearby stations (15km radius)
- Get station resources (personnel, vehicles, equipment)
- Check active incidents (5km radius, last 24 hours)
- Analyze historical patterns (90-day window)
- Calculate total available resources

**Node 3: analysis_node**
- Calculate severity score (0-100) for emergencies
- Determine severity level (Low/Medium/High/Critical)
- Calculate required resources (personnel, vehicles, equipment)
- Create dispatch plan (primary stations + backup)
- Build LLM prompt based on request type
- Get LLM analysis for strategic decision-making

**Node 4: decision_node**
- Apply safety policy → safety_check_passed
- Apply resource policy → resource_check_passed
- Apply coordination policy → departments_to_notify
- Apply escalation policy → escalation_required
- Get dispatch decision (APPROVE/DENY/ESCALATE/COORDINATE)
- Calculate estimated cost and duration

**Node 5: coordination_node**
- Build coordination messages for each department
- Include incident type, location, reason, urgency
- Set coordination_status (completed/not_required)

**Node 6: response_node**
- Generate action items (dispatch instructions, conditions)
- Build next steps (coordination, escalation)
- Compile final response object

**Conditional Routing**:
- Decision → Coordination (if coordination_required)
- Decision → Response (if no coordination needed)

### API Endpoints (fire.py) - 6 Routes

1. **POST /api/fire/emergency**
   - Handle emergency response (fire, rescue, medical, hazmat)
   - Input: EmergencyRequest (location, emergency_type, casualties, building_type, fire_intensity)
   - Output: Decision, dispatch plan, cost, duration, coordination status

2. **POST /api/fire/inspection**
   - Handle fire safety inspection requests
   - Input: InspectionRequest (inspection_location, description)
   - Output: Inspection priority, risk assessment, timeline

3. **POST /api/fire/awareness**
   - Handle fire awareness program requests
   - Input: AwarenessRequest (location, target_audience, description)
   - Output: Program approval, recommended content, resource allocation

4. **POST /api/fire/maintenance**
   - Handle equipment maintenance requests
   - Input: MaintenanceRequest (equipment_type, description)
   - Output: Maintenance priority, scheduling, operational impact

5. **GET /api/fire/stations**
   - List all fire stations with resources
   - Output: Station details (name, location, personnel, vehicles, equipment)

6. **GET /api/fire/incidents/active**
   - Get active emergency incidents (last 24 hours)
   - Output: Incident details (type, severity, status, location)

## 🧪 Test Scenarios (test_fire_agent.py)

### Scenario 1: Building Fire with Casualties
- **Type**: Commercial building fire
- **Intensity**: Major
- **Casualties**: 5 people
- **Location**: Connaught Place, Central Delhi
- **Expected**: APPROVE with maximum resources, coordinate with Water + Health + Police

### Scenario 2: High-Rise Fire
- **Type**: High-rise building fire (15th floor)
- **Intensity**: Moderate
- **Casualties**: 0
- **Location**: Nehru Place, South Delhi
- **Expected**: APPROVE with aerial ladder, coordinate with Police for evacuation

### Scenario 3: Medical Emergency
- **Type**: Cardiac arrest
- **Casualties**: 1
- **Location**: Civil Lines, North Delhi
- **Expected**: APPROVE, coordinate with Health Department

### Scenario 4: Industrial Hazmat Incident
- **Type**: Chemical spill in industrial facility
- **Casualties**: 2
- **Location**: Industrial Area, Wazirpur
- **Expected**: APPROVE with hazmat equipment, coordinate with multiple departments

## 🔗 Integration

### Main Application (main.py)
```python
from app.routes.fire import router as fire_router
app.include_router(fire_router)
```

### Database Models (models.py)
- **FireStation**: Stations with personnel, vehicles, equipment
- **EmergencyIncident**: Emergency records with severity, status, casualties
- **AgentMessage**: Inter-agent communication

## 📋 Key Features

✅ **Emergency Response**: Full dispatch workflow with severity assessment  
✅ **Station Management**: Query nearby stations, calculate ETA, optimize dispatch  
✅ **Risk Assessment**: 0-100 severity scoring, multi-factor risk analysis  
✅ **Resource Planning**: Personnel/vehicle requirements, mutual aid triggers  
✅ **Cross-Department Coordination**: Automatic coordination with Water, Health, Police, Public Works  
✅ **Escalation Logic**: Smart escalation to Fire Chief or City Emergency Manager  
✅ **Historical Analysis**: 90-day incident pattern analysis  
✅ **Cost Estimation**: Dynamic cost calculation based on severity and resources  
✅ **LLM Integration**: GPT-4 powered strategic analysis and recommendations  
✅ **Policy-Based Decisions**: 8 policy functions for deterministic logic  

## 🚀 Testing Instructions

### ⚠️ Required: Set OpenAI API Key
Before running tests, add your OpenAI API key to `.env`:
```bash
OPENAI_API_KEY=your-actual-openai-api-key-here
```

### Run Tests
```bash
cd backend
.\venv\Scripts\Activate.ps1
python test_fire_agent.py
```

### Start API Server
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

API will be available at: http://localhost:8000

### Example API Request
```bash
curl -X POST http://localhost:8000/api/fire/emergency \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "location": {
      "latitude": 28.6139,
      "longitude": 77.2090,
      "address": "Connaught Place, Central Delhi"
    },
    "description": "Large fire in commercial building",
    "emergency_type": "fire",
    "priority": "critical",
    "casualties": 5,
    "building_type": "commercial",
    "fire_intensity": "major"
  }'
```

## 📊 Agent Comparison

| Feature | Water Agent | Fire Agent |
|---------|-------------|------------|
| **Request Types** | 1 (water_request) | 4 (emergency, inspection, awareness, maintenance) |
| **State Fields** | 30+ | 40+ |
| **Tools** | 8 functions | 9 functions |
| **Policies** | 7 functions | 8 functions |
| **Prompts** | 6 templates | 6 templates |
| **Workflow Nodes** | 6 nodes | 6 nodes |
| **API Endpoints** | 3 routes | 6 routes |
| **Key Feature** | Infrastructure analysis | Emergency dispatch |
| **Decision Logic** | Pipeline conflict detection | Severity scoring + dispatch |
| **Coordination** | Other utilities | Multiple departments |

## 🎯 Next Steps

Now that both Water and Fire Agents are complete, you can:

1. **Test Both Agents**: Run both test scripts to validate full functionality
2. **Build Inter-Agent Messaging**: Implement message bus for agent-to-agent coordination
3. **Create Frontend Dashboard**: Build UI for submitting requests and viewing responses
4. **Add More Agents**: Health, Police, Public Works following same pattern
5. **Implement Real-time Updates**: WebSocket support for live incident tracking
6. **Add Authentication**: Secure API endpoints with user authentication
7. **Deploy Database Triggers**: Automatic message sending on database events

## 📝 Notes

- Fire Agent uses same LangGraph architecture as Water Agent for consistency
- Both agents can coordinate through AgentMessage table
- Fire Agent has more complex dispatch logic due to emergency response requirements
- Severity scoring enables prioritization and resource allocation
- Policy-based decisions ensure safety-first approach
- LLM provides strategic analysis while policies handle deterministic logic

---

**Status**: ✅ Fire Agent fully implemented and ready for testing (requires OPENAI_API_KEY)  
**Next**: Set OpenAI API key in `.env` and run tests
