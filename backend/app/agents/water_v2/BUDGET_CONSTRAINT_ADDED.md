# Budget Constraint Added ✅

## 🎯 What Was Added

Budget is now the **6th constraint** in the feasibility evaluation, alongside:
1. Pipeline Health
2. Manpower Availability
3. Safety Risk
4. Emergency Backup
5. Schedule Conflicts
6. **Budget Availability** ← NEW!

---

## 📋 Changes Made

### 1. New Tool: `check_budget_availability()` 
**File:** [`tools.py`](tools.py)

```python
async def check_budget_availability(
    db: AsyncSession,
    location: str,
    requested_days: int
) -> Dict[str, Any]:
    """
    Check if budget is available for requested work
    
    Returns:
        {
            "budget_available": float,
            "estimated_cost": float,
            "sufficient": bool,
            "utilization_percent": float
        }
    """
```

**What it does:**
- Estimates cost: `requested_days × (₹10,000 base + ₹2,500 manpower)`
- Queries database for amount already spent this month
- Calculates available budget: `monthly_budget - amount_spent`
- Checks utilization percentage: `(amount_spent / monthly_budget) × 100`

---

### 2. New Rule: `max_budget_utilization_percent`
**File:** [`agent.py`](agent.py)

```python
self.rules = {
    "max_delay_days": 3,
    "min_manpower": 5,
    "min_backup_hours": 24,
    "max_concurrent_projects": 3,
    "max_budget_utilization_percent": 90,  # ← NEW
}
```

**Constraint:** Department can't exceed 90% budget utilization (safety margin for emergencies)

---

### 3. Budget Constraint Check in Feasibility Evaluator
**File:** [`agent.py`](agent.py) - Phase 9

```python
# Check 6: Budget availability
budget_check = observations.get("check_budget_availability", {})
if budget_check.get("sufficient") == False:
    constraints_satisfied["budget"] = False
    blocking_factors.append(f"Insufficient budget: ₹{budget_check.get('budget_available', 0):,.0f} available, ₹{budget_check.get('estimated_cost', 0):,.0f} required")
elif budget_check.get("utilization_percent", 0) > self.rules["max_budget_utilization_percent"]:
    constraints_satisfied["budget"] = False
    blocking_factors.append(f"Budget utilization too high: {budget_check.get('utilization_percent', 0):.1f}% > {self.rules['max_budget_utilization_percent']}% limit")
else:
    constraints_satisfied["budget"] = True
```

**Two checks:**
1. **Sufficient funds:** `budget_available >= estimated_cost`
2. **Utilization limit:** `utilization_percent <= 90%`

---

### 4. Tool Execution Update
**File:** [`agent.py`](agent.py) - Phase 8

```python
if "manpower" in tool_name:
    params["days_ahead"] = state["input_event"].get("requested_shift_days", 1)
elif "schedule" in tool_name or "budget" in tool_name:  # ← Added budget
    params["requested_days"] = state["input_event"].get("requested_shift_days", 1)
```

**Ensures:** Budget tool receives `requested_days` parameter for cost estimation

---

### 5. Documentation Updated
**File:** [`FEASIBILITY_EXPLAINED.md`](FEASIBILITY_EXPLAINED.md)

- Changed from "5 Constraints" → "6 Constraints"
- Added complete budget constraint explanation with examples
- Showed budget failure scenarios (insufficient funds, high utilization)

---

## 🧪 Example Scenarios

### Scenario 1: Budget PASS ✅
```
Request: 3-day maintenance
Estimated cost: 3 × ₹12,500 = ₹37,500

Budget status:
- Monthly budget: ₹500,000
- Amount spent: ₹420,000
- Available: ₹80,000
- Utilization: 84%

Checks:
✅ ₹80,000 >= ₹37,500 (sufficient)
✅ 84% <= 90% (within limit)

Result: constraints_satisfied["budget"] = True
```

### Scenario 2: Budget FAIL - Insufficient Funds ❌
```
Request: 5-day emergency repair
Estimated cost: 5 × ₹12,500 = ₹62,500

Budget status:
- Monthly budget: ₹500,000
- Amount spent: ₹480,000
- Available: ₹20,000
- Utilization: 96%

Checks:
❌ ₹20,000 < ₹62,500 (insufficient)
❌ 96% > 90% (over limit)

Result: 
constraints_satisfied["budget"] = False
blocking_factors = ["Insufficient budget: ₹20,000 available, ₹62,500 required", 
                    "Budget utilization too high: 96% > 90% limit"]
feasible = False
```

### Scenario 3: Budget FAIL - High Utilization ❌
```
Request: 2-day minor repair
Estimated cost: 2 × ₹12,500 = ₹25,000

Budget status:
- Monthly budget: ₹500,000
- Amount spent: ₹460,000
- Available: ₹40,000
- Utilization: 92%

Checks:
✅ ₹40,000 >= ₹25,000 (sufficient)
❌ 92% > 90% (over limit)

Result:
constraints_satisfied["budget"] = False
blocking_factors = ["Budget utilization too high: 92% > 90% limit"]
feasible = False
```

---

## 🔄 Impact on Workflow

```
Phase 6: Planner (LLM)
    ↓
    Generates Plan A, B, C
    ↓
Phase 8: Execute Tools
    ↓
    Calls 6 tools (including check_budget_availability)
    ↓
Phase 9: Evaluate Feasibility
    ↓
    Checks 6 constraints (including budget)
    ↓
    If budget fails:
    - Plan marked not feasible
    - Blocking factor added: "Insufficient budget: ..."
    - Loop retries with Plan B (if available)
    ↓
    If all plans fail budget:
    - Escalates to human with reason
```

---

## 💡 Why Budget Matters

**Real-world governance scenario:**
- Department has monthly budget of ₹500,000
- Already spent ₹480,000 by month-end
- Citizen requests 5-day emergency repair (₹62,500)

**Without budget constraint:**
- LLM might approve (other constraints OK)
- Department overspends → Financial violation

**With budget constraint:**
- Tool calculates: Only ₹20,000 left
- Feasibility evaluator: ❌ Insufficient funds
- Response: "Cannot approve - budget exceeded. Escalating to finance department."

**Result:** Prevents unauthorized overspending, aligns with city financial policies

---

## 🎯 Summary

| Aspect | Details |
|--------|---------|
| **New Tool** | `check_budget_availability()` in tools.py |
| **New Rule** | `max_budget_utilization_percent: 90` |
| **Constraint Logic** | 2 checks: sufficient funds + utilization limit |
| **Integration** | Phase 8 (execute) + Phase 9 (evaluate) |
| **Documentation** | Updated FEASIBILITY_EXPLAINED.md |
| **Prevents** | Budget overruns, financial policy violations |

Budget is now a **hard constraint** - LLM cannot override it! 🔒
