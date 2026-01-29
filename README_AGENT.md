# City Governance System - Water Department Agent

## Architecture Overview

This is a **single bounded autonomous decision unit** that helps the Water Department make operational decisions.

### Design Principle
- **LLM proposes** → **Rules validate** → **Humans approve**

The agent does NOT execute real-world actions. It only recommends or escalates.

## Project Structure

```
water_agent/
├── __init__.py
├── config.py              # Environment and configuration
├── database.py            # Database connection and queries
├── state.py               # Agent state definition
├── tools.py               # Tool implementations
├── nodes/                 # LangGraph nodes
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
│   └── decision_router.py
├── rules/                 # Business rules
│   ├── __init__.py
│   ├── feasibility_rules.py
│   ├── policy_rules.py
│   └── confidence_calculator.py
├── agent.py               # Main agent orchestration
└── visualize.py           # Mermaid visualization
```

## Phases Implemented

1. ✅ Input Format Validation
2. ✅ State Definition
3. ✅ Context Loader
4. ✅ Intent + Risk Analyzer
5. ✅ Goal Setter
6. ✅ Planner (LLM)
7. ✅ Tool Execution
8. ✅ Observe Results
9. ✅ Feasibility Evaluator (with loop)
10. ✅ Policy Validator
11. ✅ Memory Logger
12. ✅ Confidence Estimator
13. ✅ Decision Router
14. ✅ Output Generator
15. ✅ Visualization

## Example Usage

```python
from water_agent.agent import WaterDepartmentAgent

# Initialize agent
agent = WaterDepartmentAgent()

# Define request
request = {
    "type": "schedule_shift_request",
    "from": "Coordinator",
    "location": "Zone-1",
    "requested_shift_days": 2,
    "reason": "Joint underground work"
}

# Run agent
result = agent.decide(request)
print(result)
```

## Key Features

- **Autonomous but bounded** - Makes decisions within strict constraints
- **Explainable** - Every decision has reasoning
- **Deterministic validation** - Rules, not LLM, decide feasibility
- **Auditable** - All decisions logged to agent_decisions table
- **Safe** - High-risk requests escalated immediately
- **Loop control** - Retries alternatives if feasible

## Testing

Run tests with:
```bash
python -m pytest tests/
```
