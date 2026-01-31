# Engineering Department Agent

## Overview

A bounded autonomous agent for Indian municipal engineering department operations. Handles infrastructure projects, contractor management, tender processing, and safety compliance while respecting monsoon constraints and audit requirements.

## Architecture

**Same proven architecture as Water Department Agent:**

```
Input Event → Context Loader → Intent & Risk Analysis → Goal Setter →
Planner (LLM) → Tool Execution → Observe → Feasibility Evaluation →
Policy Validation → Memory Logger → Confidence Estimation → 
Decision Router → Output Generation → END
```

## Indian Municipal Engineering Realities

The agent is designed to reflect real constraints in Indian municipal engineering:

- **Monsoon Blackout**: No construction during July-September
- **Tender Requirements**: Projects > ₹5 lakh need formal tender process  
- **Approval Hierarchy**: 
  - < ₹1 lakh: Junior Engineer
  - < ₹5 lakh: Executive Engineer
  - < ₹20 lakh: Superintendent Engineer
  - ≥ ₹20 lakh: Chief Engineer
- **Contractor Ratings**: Minimum 3.5/5 rating required
- **Safety Score**: Minimum 4.0/5 safety compliance score
- **Concurrent Projects**: Maximum 10 active projects
- **CAG Audit Trail**: All decisions logged for audit

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configuration

Uses the same `.env` file as Water Department Agent:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=departments
DB_USER=postgres
DB_PASSWORD=your_password

GROQ_API_KEY=your_groq_api_key
LLM_MODEL=llama-3.3-70b-versatile
```

### 3. Basic Usage

```python
from engineering_agent import EngineeringDepartmentAgent

# Initialize agent
agent = EngineeringDepartmentAgent()

# Example: Project approval request
request = {
    "type": "project_approval_request",
    "location": "Ward-12",
    "project_type": "road_construction",
    "estimated_cost": 750000,
    "planned_start_month": 10,
    "reason": "Road damaged in monsoon"
}

# Get autonomous decision
result = agent.decide(request)
print(result)

# Close when done
agent.close()
```

## Supported Request Types

1. **project_approval_request** - Evaluate new project proposals
2. **tender_evaluation** - Assess tender requirements and process
3. **contractor_assignment** - Validate contractor qualifications
4. **safety_inspection** - Evaluate safety compliance
5. **equipment_allocation** - Check equipment availability
6. **budget_request** - Validate budget availability
7. **maintenance_scheduling** - Schedule maintenance work
8. **emergency_infrastructure** - Handle infrastructure emergencies

## Engineering-Specific Tools

The agent has access to 13 tools for gathering facts:

### Project Management
- `check_active_projects()` - Get current project load
- `get_active_projects_count()` - Quick project count

### Contractor Management
- `check_contractor_availability()` - Find qualified contractors
- Validates contractor ratings against requirements

### Budget & Tenders
- `check_budget_availability()` - Verify budget sufficiency
- `check_tender_requirements()` - Determine tender process needs

### Weather & Seasonal
- `check_monsoon_restrictions()` - Verify monsoon constraints
- Auto-blocks construction during July-September

### Safety & Compliance
- `check_safety_compliance()` - Review safety violations
- `check_recent_incidents()` - Check incident history

### Equipment & Scheduling
- `check_equipment_availability()` - Equipment status
- `check_schedule_conflicts()` - Detect scheduling conflicts

## Example Scenarios

### Scenario 1: Routine Road Maintenance

```python
request = {
    "type": "project_approval_request",
    "location": "Zone-A",
    "project_type": "road_maintenance",
    "estimated_cost": 100000,  # ₹1 lakh
    "reason": "Pothole repair"
}

result = agent.decide(request)
# Expected: RECOMMEND (low cost, routine work)
```

### Scenario 2: Major Bridge Construction

```python
request = {
    "type": "project_approval_request",
    "location": "Zone-B",
    "project_type": "bridge_construction",
    "estimated_cost": 5000000,  # ₹50 lakh
    "contractor_id": "CTR-001",
    "planned_start_month": 8,  # August - MONSOON!
    "reason": "New bridge across river"
}

result = agent.decide(request)
# Expected: ESCALATE (high cost + monsoon season)
```

### Scenario 3: Emergency Infrastructure Repair

```python
request = {
    "type": "emergency_infrastructure",
    "location": "Zone-C",
    "emergency_type": "road_collapse",
    "estimated_cost": 250000,
    "reason": "Road collapsed after heavy rain"
}

result = agent.decide(request)
# Expected: RECOMMEND (emergency, within budget)
```

## Decision Output Format

### Recommendation (Confident & Feasible)

```json
{
  "decision": "recommend",
  "summary": "Project feasible within constraints",
  "confidence": 0.85,
  "details": {
    "feasible": true,
    "policy_ok": true,
    "risk_level": "low",
    "budget_available": true,
    "monsoon_safe": true,
    "contractor_qualified": true
  },
  "constraints": [
    "Must complete before monsoon season",
    "Requires Executive Engineer approval"
  ]
}
```

### Escalation (High Risk/Cost or Policy Violation)

```json
{
  "decision": "escalate",
  "reason": "Cost exceeds tender threshold and monsoon season conflict",
  "risk_level": "high",
  "requires_approval": "Chief Engineer",
  "details": {
    "feasible": false,
    "policy_ok": false,
    "confidence": 0.45,
    "policy_violations": [
      "Monsoon blackout period (August)",
      "Cost exceeds ₹20 lakh threshold"
    ]
  }
}
```

## Testing

Run comprehensive tests:

```bash
# All engineering agent tests
python -m pytest test_engineering_agent.py -v

# Specific test
python -m pytest test_engineering_agent.py::test_summary_engineering_agent -v
```

## Engineering-Specific Constraints

### Monsoon Restrictions
- **Blackout Months**: July, August, September
- **Action**: Auto-escalate or recommend delay

### Tender Thresholds
- **< ₹5 lakh**: Direct approval possible
- **≥ ₹5 lakh**: Formal tender process required
- **≥ ₹20 lakh**: Chief Engineer approval mandatory

### Safety Requirements
- **Minimum Safety Score**: 4.0/5
- **Zero Tolerance**: Critical violations block approval
- **Audit Trail**: All violations logged

### Resource Limits
- **Max Concurrent Projects**: 10
- **Contractor Rating**: Minimum 3.5/5
- **Budget Utilization**: 85% maximum

## Differences from Water Department Agent

| Aspect | Water Agent | Engineering Agent |
|--------|-------------|-------------------|
| **Focus** | Water supply & pipelines | Infrastructure & construction |
| **Seasonal** | Monsoon affects operations | Monsoon BLOCKS construction |
| **Cost Threshold** | Budget-based | Tender-based (₹5L, ₹20L) |
| **Contractors** | Workers/crew | Rated contractors |
| **Tools** | 8 tools | 13 tools |
| **Primary Risk** | Water shortage | Safety violations |

## Known Limitations

⚠️ **Same as Water Agent:**
- No coordination node for human approval workflow
- Agent escalates → Returns JSON → Workflow ENDS
- Missing: Agent escalates → Waits for human → Incorporates feedback

This will be addressed in future versions with a coordination/approval gateway.

## Project Structure

```
engineering_agent/
├── __init__.py              # Package initialization
├── agent.py                 # Main EngineeringDepartmentAgent
├── config.py                # Settings and thresholds
├── state.py                 # EngineeringState definition
├── database.py              # Database queries
├── tools.py                 # Engineering-specific tools
├── nodes/                   # LangGraph nodes (12 modules)
│   ├── __init__.py
│   ├── context_loader.py
│   ├── intent_analyzer.py
│   ├── goal_setter.py
│   ├── planner.py
│   ├── tool_executor.py
│   ├── observer.py
│   ├── feasibility_evaluator.py
│   ├── policy_validator.py
│   ├── memory_logger.py
│   ├── confidence_estimator.py
│   ├── decision_router.py
│   └── output_generator.py
└── rules/                   # Business rules
    ├── __init__.py
    ├── feasibility_rules.py
    ├── policy_rules.py
    └── confidence_calculator.py
```

## Next Steps

1. ✅ Engineering agent complete and tested
2. ✅ Shares database with Water Department Agent
3. ✅ 7/7 tests passing
4. 🔄 Add specialized engineering rules (monsoon, tender, safety)
5. 🔄 Create coordination node for human approval
6. 🔄 Add more request types as needed
7. 🔄 Fine-tune confidence thresholds based on real usage

## Support

For issues or questions, refer to:
- [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) - Overall architecture
- [README_AGENT.md](../README_AGENT.md) - Water agent documentation (similar design)
- Test file: `test_engineering_agent.py` - Working examples

---

**Status**: ✅ Functional | 🔄 Coordination Node Pending | 🎯 Production-Ready Architecture
