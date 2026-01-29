# Setup Guide - Water Department Agent

## 1. Environment Setup

### Prerequisites
- Python 3.10+
- PostgreSQL with City Governance database (use `migrations/complete_schema.sql`)
- pip or conda

### Installation

```bash
# Clone/navigate to project
cd City-Governance-System

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
nano .env  # or your preferred editor
```

**Required settings:**
- `DB_HOST` - PostgreSQL server
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_NAME` - Should be "departments"

**Optional:**
- `LLM_PROVIDER` - "openai" or "local" (default: openai)
- `OPENAI_API_KEY` - If using OpenAI
- `CONFIDENCE_THRESHOLD` - (default: 0.7)

## 2. Database Setup

The agent reads from your PostgreSQL database. Make sure the schema is initialized:

```bash
# From migrations directory
psql -U postgres -d departments -f complete_schema.sql
```

**What the agent uses:**
- `agent_decisions` - Audit trail of all decisions
- `workers` - Available manpower
- `pipelines` - Infrastructure status
- `reservoirs` - Water supply levels
- `work_schedules` - Existing commitments
- `projects` - Active projects
- `incidents` - Recent safety issues
- `department_budgets` - Resource constraints

## 3. Running the Agent

### Quick Start

```python
from water_agent import WaterDepartmentAgent

# Initialize
agent = WaterDepartmentAgent()

# Make a decision
request = {
    "type": "schedule_shift_request",
    "location": "Downtown",
    "requested_shift_days": 2,
    "reason": "Joint underground work",
    "estimated_cost": 50000
}

response = agent.decide(request)
print(response)

# Clean up
agent.close()
```

### Run Examples

```bash
python examples.py
```

This runs 4 examples:
1. Schedule shift request
2. Emergency response
3. Maintenance request
4. Workflow visualization

### Run Tests

```bash
python -m pytest test_agent.py -v
```

Tests cover:
- State management
- Feasibility rules
- Policy validation
- Confidence calculation
- Node execution
- Integration tests

## 4. Understanding the Architecture

### The 14-Phase Workflow

```
┌─────────────────────────────────────────────────────┐
│ Phase 1: Input Event                                │
│ Structured request (e.g., schedule shift)           │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 3: Context Loader                             │
│ Fetch: projects, schedule, workers, health, risks   │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 4: Intent + Risk Analysis                     │
│ Classify request, assess immediate safety risks     │
│ → If critical risk: ESCALATE                        │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 5: Goal Setter                                │
│ Define specific objective from intent               │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 6: Planner (LLM)                              │
│ Generate candidate plans                            │
│ (LLM ONLY PROPOSES - doesn't decide feasibility)   │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 7: Tool Execution                             │
│ Run tools: manpower check, schedule check, etc.     │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 8: Observe                                    │
│ Normalize tool results into standard format         │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 9: Feasibility Evaluator [LOOP]               │
│ Pure Python rules → is plan feasible?               │
│ If no: try alternative (max 3 attempts)             │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 10: Policy Validator                          │
│ Department rules: max delay, budget, SOP            │
│ → If fails: ESCALATE                                │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 11: Memory Logger                             │
│ Store decision to agent_decisions table             │
│ (Enables audit & historical analysis)               │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 12: Confidence Estimator                      │
│ Score: 0.0-1.0 based on data, risk, attempts       │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 13: Decision Router                           │
│ confidence >= 0.7 AND policy_ok → RECOMMEND         │
│ Otherwise → ESCALATE                                │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Phase 14: Output Generator                          │
│ Format response: recommendation or escalation       │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│ Response to Coordinator                             │
│ { decision, reasoning, confidence, details }        │
└─────────────────────────────────────────────────────┘
```

### Key Concepts

**LLM proposes → Rules validate → Humans approve**

- **LLM** (Phase 6): Generate plans
- **Rules** (Phase 9): Validate feasibility deterministically
- **Rules** (Phase 10): Validate policy compliance
- **Humans**: Make final decision if escalated

## 5. Adding Custom Requests

To add a new request type:

1. **Update state** → Add fields if needed
2. **Add to intent mapping** → `water_agent/nodes/intent_analyzer.py`
3. **Add goal mapping** → `water_agent/nodes/goal_setter.py`
4. **Add plan template** → `water_agent/nodes/planner.py`
5. **Add feasibility rule** → `water_agent/rules/feasibility_rules.py`
6. **Add policy rule** → `water_agent/rules/policy_rules.py`

Example: To handle "water_quality_check" requests:

```python
# In intent_analyzer.py
INTENT_MAPPING = {
    ...
    "water_quality_check": "assess_quality"
}

# In planner.py
elif intent == "assess_quality":
    plans.append({
        "id": "plan_quality_check",
        "name": "Assess water quality",
        "steps": [
            "check_reservoir_levels",
            "check_pipeline_health",
            "assess_zone_risk"
        ]
    })

# In feasibility_rules.py
@staticmethod
def evaluate_quality_assessment(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
    # Always feasible - no constraints
    return True, "Quality assessment can proceed", {}
```

## 6. Understanding Responses

### Recommendation Response

When confidence ≥ 0.7 and all checks pass:

```json
{
    "decision": "recommend",
    "reasoning": "All criteria satisfied. Confidence: 85%",
    "requires_human_review": false,
    "recommendation": {
        "action": "proceed",
        "plan": {...},
        "constraints": ["max 2 day delay"],
        "confidence": 0.85
    },
    "details": {
        "feasible": true,
        "policy_compliant": true,
        "risk_level": "low"
    }
}
```

### Escalation Response

When escalation criteria met:

```json
{
    "decision": "escalate",
    "reason": "Confidence 0.45 below threshold 0.7",
    "requires_human_review": true,
    "details": {
        "feasible": false,
        "policy_compliant": true,
        "confidence": 0.45,
        "risk_level": "medium"
    }
}
```

## 7. Debugging

### Check Agent Logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)

agent = WaterDepartmentAgent()
response = agent.decide(request)
```

### Check Decision History

```python
from water_agent.database import get_db, get_queries

db = get_db()
queries = get_queries(db)
history = queries.get_decision_history(limit=10)

for decision in history:
    print(f"{decision['created_at']}: {decision['request_type']} → {decision['decision']}")

db.close()
```

### Visualize Workflow

```python
agent = WaterDepartmentAgent()
mermaid_code = agent.visualize()
print(mermaid_code)
# Copy to https://mermaid.live to view diagram
```

## 8. Production Deployment

### Checklist

- [ ] Database secured (password, access control)
- [ ] Environment variables set securely
- [ ] LLM API key protected
- [ ] Logging enabled with rotation
- [ ] Error monitoring configured
- [ ] Decision audit trail enabled
- [ ] Regular backups of agent_decisions table
- [ ] Tests passing
- [ ] Load testing done
- [ ] Escalation process documented

### Monitoring

Watch these metrics:

```sql
-- Average confidence score
SELECT AVG(confidence), date_trunc('day', created_at)
FROM agent_decisions
GROUP BY date_trunc('day', created_at);

-- Escalation rate
SELECT COUNT(*), decision
FROM agent_decisions
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY decision;

-- Performance
SELECT COUNT(*), AVG(execution_time_ms), MAX(execution_time_ms)
FROM agent_decisions
WHERE created_at > NOW() - INTERVAL '7 days';
```

## 9. Troubleshooting

### Database Connection Failed

```
Error: Database connection failed
Solution: Check DB_HOST, DB_PORT, credentials in .env
```

### LLM API Error

```
Error: OpenAI API error
Solution: Check OPENAI_API_KEY is set and valid
```

### Location Not Found

```
Error: Location validation failed
Solution: Location must exist in pipelines/work_schedules/reservoirs
```

### Confidence Too Low

The agent is too conservative. Likely causes:
- High risk zone
- Low data completeness
- Multiple retries needed
- Policy violations

Solution: Review feasibility_rules.py and policy_rules.py

## 10. Next Steps

After Water Department Agent is working:

1. **Clone for other departments** → Fire, Roads, Sanitation
2. **Build Coordinator Agent** → Routes between departments
3. **Add LLM integration** → Replace deterministic planner
4. **Add learning** → Improve over time with historical data
5. **Scale testing** → Load tests, chaos engineering
