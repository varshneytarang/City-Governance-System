# Test Scenarios for Edge Cases

This document describes specific test scenarios you can run using the loaded test data to verify agent behavior with edge cases.

## Quick Start

1. Load the test data:
```bash
python migrations/load_test_data.py
```

2. Start the backend:
```bash
python start_backend.py
```

3. Use the API test page or send requests to test agents

---

## 🔴 Critical Edge Cases

### Scenario 1: Emergency with Insufficient Resources

**Situation**: Major water leak but not enough workers or budget available

**Test Data**: Incident `i1` - Major leak in Zone-A, only 2 workers available (need 5), budget shortfall

**Request**:
```json
POST /api/v1/query
{
  "type": "emergency_response",
  "location": "Zone-A",
  "severity": "critical",
  "incident_type": "major_leak",
  "user_request": "Major water main break on Main Street flooding road"
}
```

**Expected Behavior**:
- Agent should detect insufficient workers (w1, w3 available but need 5)
- Budget check shows shortfall ($125k needed, only $50k available)
- **Decision**: `escalate`
- **Confidence**: Low (~0.45)
- **Reasoning**: "Insufficient resources - requires human approval for budget/worker reallocation"

**Verify**: Check `agent_decisions` table for escalation reasoning

---

### Scenario 2: Depleted Department Budget

**Situation**: Engineering department has negative budget, new project requested

**Test Data**: Engineering budget shows -$5,000 (over allocated), status `depleted`

**Request**:
```json
POST /api/v1/query
{
  "type": "project_planning",
  "location": "Zone-B",
  "project_type": "road_repair",
  "estimated_cost": 85000,
  "user_request": "Need to repair potholes on Oak Street"
}
```

**Expected Behavior**:
- Agent checks department_budgets table
- Finds status = 'depleted', spent > total_budget
- **Decision**: `deny`
- **Policy Violation**: Budget compliance policy
- **Reasoning**: "Cannot approve project when department budget is depleted"

**Verify**: Response should mention budget constraint and suggest reallocation

---

### Scenario 3: Contaminated Water Emergency

**Situation**: Reservoir with critically low water quality score

**Test Data**: Reservoir `r4` (East Reservoir) has quality score 45.3 (critical), status `emergency`

**Request**:
```json
POST /api/v1/query
{
  "type": "emergency_response",
  "location": "Zone-C",
  "incident_type": "contamination",
  "severity": "critical",
  "user_request": "Residents reporting illness, suspected water contamination"
}
```

**Expected Behavior**:
- Agent queries reservoirs serving Zone-C
- Finds East Reservoir with quality_score = 45.3 (danger threshold)
- Checks incident `i2` already investigating contamination
- **Decision**: `approve` emergency response with high priority
- **Actions**: Isolate reservoir, notify health department, distribute bottled water
- **Confidence**: High (clear emergency protocol)

---

### Scenario 4: Critical Low Reservoir Capacity

**Situation**: Reservoir at 11% capacity (near empty)

**Test Data**: Reservoir `r1` (North Reservoir) at 550k/5M liters (11%), status `critical`

**Request**:
```json
POST /api/v1/query
{
  "type": "capacity_query",
  "location": "Zone-A",
  "user_request": "What is current water supply status?"
}
```

**Expected Behavior**:
- Agent finds North Reservoir serving Zone-A
- Calculates capacity: 11% (critical threshold usually 15%)
- **Decision**: `approve` query with urgent warning
- **Recommendations**: 
  - Immediate water conservation measures
  - Transfer water from other reservoirs
  - Alert engineering about refill priority
- **Confidence**: High (data-driven assessment)

---

### Scenario 5: Over Capacity Reservoir (Flood Risk)

**Situation**: Reservoir at 103% capacity

**Test Data**: Reservoir `r5` (West Reservoir) at 7.2M/7M liters (103%), status `critical`

**Request**:
```json
POST /api/v1/query
{
  "type": "emergency_response",
  "location": "Zone-D",
  "incident_type": "flooding_risk",
  "severity": "high",
  "user_request": "West Reservoir water level alarming"
}
```

**Expected Behavior**:
- Agent detects over-capacity condition (103%)
- Risk of structural damage or overflow
- **Decision**: `approve` emergency drainage
- **Actions**: Open spillways, transfer to other reservoirs, inspect dam integrity
- **Coordination**: May require engineering department involvement

---

## ⚠️ Resource Constraint Cases

### Scenario 6: All Skilled Workers Unavailable

**Situation**: Need pipeline specialist but all are busy/unavailable

**Test Data**: Worker `w6` (Pipeline Specialist) has `available = false`

**Request**:
```json
POST /api/v1/query
{
  "type": "maintenance_request",
  "location": "Zone-E",
  "activity": "pipeline_repair",
  "priority": "high",
  "user_request": "Need specialist for pipeline welding repair"
}
```

**Expected Behavior**:
- Agent searches for workers with `pipeline_repair` or `welding` skills
- Finds w6 has skills but available = false
- Alternative: w1 has pipeline_repair but different specialization
- **Decision**: Either `approve` with w1 (may note skill gap) or `escalate` if specialist required

---

### Scenario 7: Budget Reallocation Between Departments

**Situation**: Fire has 85% unused budget, Engineering depleted

**Test Data**: 
- Fire budget: $750k total, only $95k spent (87% available)
- Engineering budget: Depleted (-$5k)

**Request** (to Finance Agent):
```json
POST /api/v1/query
{
  "type": "budget_allocation",
  "from_department": "fire",
  "to_department": "engineering",
  "amount": 100000,
  "reason": "critical infrastructure repairs needed",
  "user_request": "Transfer $100k from Fire to Engineering for emergency road repairs"
}
```

**Expected Behavior**:
- Finance agent checks both department budgets
- Fire utilization: 15% (very low, reallocation acceptable)
- Engineering: Depleted (urgent need)
- Policy check: Inter-department transfers allowed up to $150k
- **Decision**: `approve`
- **Confidence**: High (~0.87)
- **Reasoning**: "Source department under-utilizing, target has critical need"

---

## 🏗️ Project Management Edge Cases

### Scenario 8: Over-Budget Ongoing Project

**Situation**: Project exceeded estimate by 21%

**Test Data**: Project `prj2` (Downtown Bridge) estimated $350k, actual $425k

**Request**:
```json
POST /api/v1/query
{
  "type": "project_status",
  "project_id": "prj2",
  "user_request": "What's the status of Downtown Bridge repairs?"
}
```

**Expected Behavior**:
- Agent retrieves project from projects table
- Calculates variance: +$75k (21% over budget)
- Status: `in_progress` but over budget
- **Decision**: `approve` status report with warning
- **Flags**: Budget overrun, may need supplemental funding
- **Recommendations**: Review cost controls, assess if more overruns expected

---

### Scenario 9: Behind Schedule Project

**Situation**: Project end date passed but still in progress

**Test Data**: Project `prj3` (North Reservoir Expansion) end_date `2026-02-28`, status `in_progress`, now Feb 8

**Request**:
```json
POST /api/v1/query
{
  "type": "project_planning",
  "location": "Zone-A",
  "project_type": "expansion",
  "user_request": "When will North Reservoir expansion be complete?"
}
```

**Expected Behavior**:
- Agent finds existing project prj3
- Detects end_date approaching in 20 days but notes indicate delays
- **Decision**: `approve` status update
- **Timeline**: Extension requested to April 2026
- **Reasons**: Weather delays, equipment availability

---

## 🚨 Policy Violation Cases

### Scenario 10: Request Violating City Ordinance

**Situation**: Sunday collection violates noise ordinance

**Test Data**: Historical decision showing Sunday operation denial

**Request** (to Sanitation Agent):
```json
POST /api/v1/query
{
  "type": "collection_schedule",
  "location": "Zone-F",
  "requested_day": "Sunday",
  "requested_time": "06:00",
  "reason": "reduce weekday traffic",
  "user_request": "Can we do garbage collection Sunday mornings instead?"
}
```

**Expected Behavior**:
- Agent checks schedule policies and ordinances
- Finds violations:
  - Sunday operations prohibited (city ordinance)
  - Operations before 7am require special permit
- **Decision**: `escalate`
- **Policy Violations**: 
  - `noise_ordinance` (high severity)
  - `early_hours_restriction` (medium severity)
- **Reasoning**: "Requires City Council approval to override ordinances"

---

## 🔄 Multi-Agent Coordination Cases

### Scenario 11: Location Conflict (Water + Engineering)

**Situation**: Both departments want to work on same street

**Request** (to Coordination Agent):
```json
POST /api/v1/query
{
  "type": "coordination_request",
  "agents_involved": ["water", "engineering"],
  "location": "Zone-B, Main Street",
  "water_request": {
    "type": "maintenance_request",
    "activity": "pipeline_replacement",
    "duration_days": 5
  },
  "engineering_request": {
    "type": "project_planning", 
    "activity": "road_resurfacing",
    "duration_days": 4
  }
}
```

**Expected Behavior**:
- Coordination agent detects location overlap
- Analyzes dependencies: road resurfacing should follow pipeline work
- **Decision**: `approve` coordinated schedule
- **Resolution**: Water works Feb 10-15, Engineering starts Feb 18
- **Reasoning**: "Sequential execution prevents rework - water pipe must be complete before repaving"

---

### Scenario 12: Emergency Requiring Multi-Department Response

**Situation**: Fire hydrant caught fire, needs both Fire and Water departments

**Request**:
```json
POST /api/v1/query
{
  "type": "emergency_response",
  "location": "Zone-C, Industrial Park",
  "incident_type": "hydrant_fire",
  "severity": "critical",
  "user_request": "Fire hydrant on fire, electrical issue, need immediate response"
}
```

**Expected Behavior**:
- Coordination agent identifies need for both departments
- Fire: Emergency response and electrical hazard handling
- Water: Isolate hydrant, manage pressure, prevent system damage
- **Decision**: `approve` coordinated multi-agent response
- **Actions**: 
  - Fire deploys unit and electrical specialist
  - Water increases Zone-C pressure, monitors for issues
- **Coordination**: Both agents work simultaneously

---

## 📊 Historical Data Analysis Cases

### Scenario 13: Trend Analysis Request

**Request**:
```json
POST /api/v1/query
{
  "type": "analytics_request",
  "department": "water",
  "query_type": "incident_trends",
  "time_period": "last_30_days",
  "user_request": "Show me water incident trends for the past month"
}
```

**Expected Behavior**:
- Agent queries incidents table with date filter
- Finds mix of resolved and open incidents
- Categories: major_leak (2), contamination (1), minor_leak (2), etc.
- **Decision**: `approve` analytics report
- **Insights**: 
  - 60% of incidents in Zone-A (infrastructure aging)
  - 3 critical incidents in Feb (above average)
  - Recommendation: Prioritize Zone-A pipeline replacement

---

## 🧪 Stress Test Cases

### Scenario 14: Cascade Failure Simulation

**Situation**: Multiple simultaneous emergencies

**Request** (rapid sequence):
```json
// Request 1 (already active):
{"type": "emergency_response", "location": "Zone-A", "incident_type": "major_leak"}

// Request 2:
{"type": "emergency_response", "location": "Zone-C", "incident_type": "contamination"}

// Request 3:
{"type": "emergency_response", "location": "Zone-D", "incident_type": "pressure_drop"}
```

**Expected Behavior**:
- Agents detect resource exhaustion
- Workers already assigned: w3 (Zone-A), w4 (Zone-C)
- Remaining workers: w1, w2, w5 (need prioritization)
- **Decisions**: 
  - Zone-A: In progress (critical leak)
  - Zone-C: In progress (contamination)
  - Zone-D: `escalate` - insufficient resources
- **Coordination**: May suggest mutual aid request or contractor support

---

## Running the Tests

### Using the API Test Page

1. Navigate to `http://localhost:8000/test` (if frontend running)
2. Select department
3. Choose scenario from above
4. Submit and observe response

### Using cURL

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "type": "emergency_response",
    "location": "Zone-A",
    "severity": "critical",
    "incident_type": "major_leak"
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "type": "emergency_response",
        "location": "Zone-A",
        "severity": "critical",
        "incident_type": "major_leak"
    }
)

print(response.json())
```

---

## Verifying Results

After each test, verify the results:

```sql
-- Check latest agent decision
SELECT 
    agent_type, 
    request_type, 
    decision, 
    confidence, 
    reasoning,
    created_at
FROM agent_decisions 
ORDER BY created_at DESC 
LIMIT 1;

-- Check if workers were assigned
SELECT 
    worker_id, 
    task_description, 
    status, 
    priority 
FROM work_schedules 
WHERE status = 'in_progress';

-- Check budget impact
SELECT 
    department, 
    total_budget, 
    spent, 
    remaining,
    status 
FROM department_budgets 
WHERE year = 2026 AND month = 2;
```

---

## Expected Outcomes Summary

| Scenario | Expected Decision | Confidence | Key Edge Case |
|----------|------------------|------------|---------------|
| 1. Insufficient Resources | Escalate | Low (~0.45) | Resource shortage |
| 2. Depleted Budget | Deny | High (~0.88) | Budget constraint |
| 3. Contamination | Approve (Emergency) | High (~0.95) | Water quality |
| 4. Low Reservoir | Approve (Warning) | High (~0.90) | Capacity critical |
| 5. Over Capacity | Approve (Emergency) | High (~0.93) | Flood risk |
| 6. No Workers | Escalate or Delegate | Medium (~0.60) | Skill shortage |
| 7. Budget Transfer | Approve | High (~0.87) | Inter-dept allocation |
| 8. Over Budget Project | Approve (Flagged) | Medium (~0.75) | Cost overrun |
| 9. Behind Schedule | Approve (Extended) | Medium (~0.70) | Timeline slip |
| 10. Policy Violation | Escalate | High (~0.91) | Ordinance conflict |
| 11. Location Conflict | Approve (Coordinated) | High (~0.89) | Multi-agent sync |
| 12. Multi-Dept Emergency | Approve (Coordinated) | High (~0.92) | Joint response |

---

## Tips for Testing

1. **Start Simple**: Test basic capacity queries before emergencies
2. **Check Database**: Verify test data loaded correctly before testing
3. **Monitor Logs**: Watch backend logs for agent decision reasoning
4. **Test Sequences**: Try related scenarios in sequence to see state changes
5. **Verify Persistence**: Check if decisions are saved to agent_decisions table
6. **Compare Historical**: Look at pre-loaded historical decisions for pattern matching

---

## Troubleshooting

**Issue**: Agent returns generic response, not using test data

**Solution**: 
- Verify database connection in .env
- Check if test data loaded: `python migrations/load_test_data.py --verify-only`
- Restart backend to clear any caches

**Issue**: Budget calculations seem wrong

**Solution**:
- Refresh budget data: Re-run seed_test_data.sql
- Check fiscal period: Test data uses Feb 2026

**Issue**: Workers shown as available but shouldn't be

**Solution**:
- Check work_schedules table for active assignments
- Worker availability is separate from current assignments
