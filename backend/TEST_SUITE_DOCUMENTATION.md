# Test Suite Documentation

## 🧪 Overview

Two comprehensive test suites for the Professional Water Department Agent:

1. **Agent-to-Human Tests** - Escalation scenarios
2. **Agent-to-Agent Tests** - Collaboration scenarios

---

## 📁 Test Files

```
backend/
├── test_agent_to_human.py      # 6 escalation tests
├── test_agent_to_agent.py      # 7 collaboration tests
└── pytest.ini                   # Pytest configuration (create if needed)
```

---

## 🎯 Agent-to-Human Tests (`test_agent_to_human.py`)

### Purpose
Test scenarios where the agent **must escalate** to human decision-makers instead of making autonomous decisions.

### Test Scenarios

#### 1. **Low Confidence Escalation**
```python
Input: Vague request with missing critical details
Expected: confidence < 0.7 → escalate
Trigger: Incomplete location, vague description
```

#### 2. **Policy Violation Escalation**
```python
Input: Request violating department policies
Expected: policy_compliant = False → escalate
Trigger: requested_shift_days (5) > max_delay_days (3)
```

#### 3. **High Risk Escalation**
```python
Input: Request in high-risk location
Expected: risk_level = "high" → escalate
Trigger: Multiple recent incidents (safety_risk check)
```

#### 4. **All Plans Infeasible**
```python
Input: Request with no feasible solution
Expected: attempts = 3, feasible = False → escalate
Trigger: All LLM-generated plans fail constraints
```

#### 5. **Budget Constraint Violation**
```python
Input: Large project exceeding budget
Expected: budget constraint fails → escalate
Trigger: estimated_cost > budget_available OR utilization > 90%
```

#### 6. **Emergency Override Request**
```python
Input: Critical emergency needing authorization
Expected: Decision made (approve or escalate)
Trigger: priority = "critical", location = critical infrastructure
```

### Running the Tests

```powershell
# Run all agent-to-human tests
python -m pytest test_agent_to_human.py -v -s

# Run specific test
python -m pytest test_agent_to_human.py::test_low_confidence_escalation -v -s

# Run with output capture disabled (see prints)
python test_agent_to_human.py

# Run with detailed output
python -m pytest test_agent_to_human.py -vvs
```

### Expected Output

```
🧪 AGENT-TO-HUMAN ESCALATION TEST SUITE
========================================
Started: 2026-01-28 14:30:00

TEST 1: LOW CONFIDENCE ESCALATION
========================================
📊 Result Summary:
  Decision: escalate
  Confidence: 0.45
  Escalation Reason: Low confidence (0.45) - insufficient data for autonomous decision
✅ TEST PASSED: Low confidence correctly triggers escalation

TEST 2: POLICY VIOLATION ESCALATION
========================================
📊 Result Summary:
  Decision: escalate
  Policy Compliant: False
  Violations: ['Requested delay (5 days) exceeds maximum (3 days)']
✅ TEST PASSED: Policy violation correctly triggers escalation

... (remaining tests)

📊 TEST SUMMARY
========================================
Total Tests: 6
✅ Passed: 6
❌ Failed: 0
Completed: 2026-01-28 14:32:15
```

---

## 🤝 Agent-to-Agent Tests (`test_agent_to_agent.py`)

### Purpose
Test scenarios where the Water Agent must **coordinate with other departments** or handle cross-department dependencies.

### Test Scenarios

#### 1. **Water-Fire Coordination**
```python
Input: Maintenance affecting fire hydrants
Expected: Considers fire department dependencies
Checks: Context mentions fire/hydrant, safety risk assessed
```

#### 2. **Water-Roads Coordination**
```python
Input: Pipe repair requiring road excavation
Expected: Identifies road work dependency
Checks: Plan mentions road/excavation/traffic
```

#### 3. **Water-Electric Coordination**
```python
Input: Pump maintenance requiring power
Expected: Considers backup power, coordinates shutdown
Checks: Emergency backup duration >= 24 hours
```

#### 4. **Multi-Agent Resource Conflict**
```python
Input: Multiple departments need same workers
Expected: Detects schedule conflicts, proposes alternatives
Checks: Manpower availability, schedule conflicts
```

#### 5. **Sequential Agent Workflow**
```python
Input: Work requiring prior department approval
Expected: Recognizes dependency, sequences work
Checks: Dependencies identified, steps sequenced
```

#### 6. **Cross-Department Data Query**
```python
Input: Request requiring integrated data
Expected: Queries shared database, integrates data
Checks: Multiple tools used (pipeline, safety, resources)
```

#### 7. **Complex Multi-Agent Project**
```python
Input: Large project requiring all departments
Expected: Identifies all dependencies, checks all constraints
Checks: All 6 tools executed, comprehensive feasibility check
```

### Running the Tests

```powershell
# Run all agent-to-agent tests
python -m pytest test_agent_to_agent.py -v -s

# Run specific test
python -m pytest test_agent_to_agent.py::test_water_fire_coordination -v -s

# Run directly
python test_agent_to_agent.py

# Run with markers (if configured)
python -m pytest test_agent_to_agent.py -m "coordination" -v
```

### Expected Output

```
🤝 AGENT-TO-AGENT COLLABORATION TEST SUITE
========================================
Started: 2026-01-28 14:35:00

TEST 1: WATER-FIRE AGENT COORDINATION
========================================
📊 Result Summary:
  Decision: approve
  Context Considered: 5 factors
  Safety Considerations: low

🔍 Coordination Check:
  Fire-related context: True
  Safety risk assessed: True
✅ TEST PASSED: Water-Fire coordination scenario handled

TEST 2: WATER-ROADS DEPARTMENT COORDINATION
========================================
📊 Result Summary:
  Decision: approve
  Plan: Deploy crew for underground water main repair with road excavation...
  Dependencies: 2 identified

🔍 Dependencies Check:
  Road work mentioned: True
  Traffic considered: True
✅ TEST PASSED: Water-Roads coordination scenario handled

... (remaining tests)

📊 TEST SUMMARY
========================================
Total Tests: 7
✅ Passed: 7
❌ Failed: 0
Completed: 2026-01-28 14:38:45
```

---

## ⚙️ Test Configuration

### pytest.ini (Optional)

Create `backend/pytest.ini`:

```ini
[pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

markers =
    escalation: Tests for agent-to-human escalation
    coordination: Tests for agent-to-agent coordination
    slow: Tests that take longer to run

addopts = 
    -v
    --tb=short
    --strict-markers
```

### Using Markers

```python
# In test file
import pytest

@pytest.mark.escalation
async def test_low_confidence_escalation():
    ...

@pytest.mark.coordination
async def test_water_fire_coordination():
    ...
```

Run by marker:
```powershell
pytest -m escalation
pytest -m coordination
```

---

## 🔍 Debugging Failed Tests

### Verbose Mode

```powershell
# Show full stack traces
pytest test_agent_to_human.py -vvs --tb=long

# Show local variables in failures
pytest test_agent_to_human.py -l

# Stop on first failure
pytest test_agent_to_human.py -x
```

### Logging

```python
# Add to test file
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Inspection

```sql
-- Check agent decisions
SELECT decision, feasible, confidence, feasibility_reason
FROM agent_decisions
ORDER BY created_at DESC
LIMIT 10;

-- Check budget
SELECT department, total_budget, spent, utilization_percent
FROM department_budgets
WHERE year = 2026 AND month = 1;

-- Check workers
SELECT COUNT(*) as total, status
FROM workers
GROUP BY status;
```

---

## 📊 Test Coverage

### Generate Coverage Report

```powershell
# Install coverage
pip install pytest-cov

# Run with coverage
pytest test_agent_to_human.py test_agent_to_agent.py \
  --cov=app.agents.water_v2 \
  --cov-report=html \
  --cov-report=term

# View report
start htmlcov/index.html  # Windows
```

### Expected Coverage

```
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
app/agents/water_v2/__init__.py          3      0   100%
app/agents/water_v2/state.py            45      2    96%
app/agents/water_v2/tools.py           120     15    88%
app/agents/water_v2/agent.py           180     25    86%
app/agents/water_v2/graph.py            35      3    91%
---------------------------------------------------------
TOTAL                                  383     45    88%
```

---

## 🎯 Test Data Requirements

### Database Must Have:

1. **Workers** - At least 8 workers (various statuses)
2. **Pipelines** - Multiple pipelines with varying pressure
3. **Reservoirs** - 2-3 reservoirs with current levels
4. **Incidents** - Some recent incidents for safety checks
5. **Budgets** - Department budgets for current month
6. **Work Schedules** - Some scheduled work for conflict detection

### Provided by Migration

The `002_professional_agent_architecture.sql` migration inserts all necessary sample data.

Verify:
```powershell
python run_migration_v2.py
```

---

## 🚨 Common Issues

### Issue: Tests timeout

**Solution:**
```python
# Increase timeout in test
@pytest.mark.timeout(60)  # 60 seconds
async def test_long_running():
    ...
```

### Issue: Database connection errors

**Solution:**
```powershell
# Check .env file
cat .env | grep DATABASE_URL

# Test connection
python -c "import asyncpg, asyncio; asyncio.run(asyncpg.connect('postgresql://postgres:password@localhost/city_mas'))"
```

### Issue: Groq API rate limits

**Solution:**
```python
# Add delays between tests
import asyncio

@pytest.fixture(autouse=True)
async def delay():
    await asyncio.sleep(1)  # 1 second delay
```

### Issue: Assertions fail unexpectedly

**Solution:**
```python
# Add detailed output
result = await workflow.ainvoke(initial_state)
print(f"Full result: {json.dumps(result, indent=2)}")
assert result.get("decision") == "escalate", f"Expected escalate, got {result.get('decision')}"
```

---

## 📋 Test Checklist

Before running tests:

- [ ] PostgreSQL running
- [ ] Database `city_mas` exists
- [ ] Migrations applied (`run_migration_v2.py`)
- [ ] Sample data loaded (verify with SQL queries)
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with DATABASE_URL and GROQ_API_KEY
- [ ] Groq API key valid (test with simple query)

---

## 🎉 Success Criteria

**All Tests Pass:**
- 6/6 agent-to-human tests ✅
- 7/7 agent-to-agent tests ✅
- Total: 13/13 tests passing

**Expected Runtime:**
- Agent-to-human suite: ~2-3 minutes
- Agent-to-agent suite: ~3-4 minutes
- Total: ~5-7 minutes

---

## 📞 Support

If tests fail:

1. Check database connection
2. Verify sample data exists
3. Review Groq API quota
4. Check logs for detailed errors
5. Run single test with `-vvs` flag for debugging

**Remember:** These tests verify the entire agent pipeline:
- Input validation
- Context gathering
- Tool execution
- Constraint checking
- Decision making
- Response generation

A passing test suite means the professional agent architecture is working correctly! 🎉
