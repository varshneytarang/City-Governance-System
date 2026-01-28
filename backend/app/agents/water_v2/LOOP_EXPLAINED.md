# Loop Mechanism Explained - Water Department Agent

## 🔁 How the Loop Works

### The Loop Decision Point

After **Phase 9: Feasibility Evaluator**, the workflow makes a **conditional decision**:

```
evaluate_feasibility
        ↓
    [Decision Point]
        ↓
   Is plan feasible?
        ↓
    ┌───┴───┐
   NO      YES
    │       │
    │       └──→ continue_to_policy (no loop)
    │
Can we retry?
    │
 ┌──┴──┐
YES   NO
 │     │
 │     └──→ continue_to_policy (give up)
 │
 └──→ retry_plan_node
       ↓
   [LOOP BACK]
       ↓
   execute_tools (try alternative plan)
```

---

## 🎯 Loop Basis: 3 Conditions Checked

The loop is controlled by the `should_retry_plan()` function, which checks **3 conditions**:

### 1️⃣ **Is Current Plan Feasible?**

```python
if state["feasible"]:
    # Current plan works! Don't retry
    return "continue_to_policy"
```

**Set by:** `evaluate_feasibility()` node (Phase 9)

**Basis:** Deterministic rule checks:
- ✅ Pipeline pressure OK?
- ✅ Manpower sufficient?
- ✅ Safety risk acceptable?
- ✅ Emergency backup adequate?
- ✅ No schedule conflicts?

If **ALL constraints satisfied** → `feasible = True` → **NO LOOP**

If **ANY constraint fails** → `feasible = False` → **CHECK IF WE CAN RETRY**

---

### 2️⃣ **Have We Tried Too Many Times?**

```python
attempts = state["attempts"]  # Current attempt number
max_attempts = state["max_attempts"]  # Default: 3

if attempts >= max_attempts:
    # Give up, no more retries
    return "continue_to_policy"
```

**Prevents:** Infinite loops

**Default:** 3 attempts maximum

**Example:**
- Attempt 1: Plan A fails → Retry
- Attempt 2: Plan B fails → Retry
- Attempt 3: Plan C fails → **STOP** (max reached)

---

### 3️⃣ **Do We Have More Plan Alternatives?**

```python
plan_index = state["current_plan_index"]  # Which plan we're on
total_plans = len(state["plan"])  # Total alternatives generated

if plan_index + 1 >= total_plans:
    # No more alternatives to try
    return "continue_to_policy"
```

**Basis:** LLM generated multiple plan alternatives in Phase 6

**Example LLM Output:**
```json
{
  "alternatives": [
    {"delay_days": 2, "backup_required": true},   ← Plan 0
    {"delay_days": 1, "backup_required": false},  ← Plan 1
    {"delay_days": 3, "backup_required": true}    ← Plan 2
  ]
}
```

If we've tried all alternatives → **NO MORE RETRIES**

---

## 🔄 Loop Execution Flow

### Complete Loop Cycle

```
1. execute_tools
      ↓
   (Executes tools based on current plan alternative)
      ↓
2. observe_results
      ↓
   (Normalizes tool outputs)
      ↓
3. evaluate_feasibility
      ↓
   (Deterministic rule checks)
      ↓
   feasible = False (e.g., manpower insufficient)
      ↓
4. should_retry_plan()
      ↓
   ✓ Not feasible
   ✓ attempts = 1 < max_attempts = 3
   ✓ plan_index = 0 < total_plans = 3
      ↓
   Decision: "retry_plan"
      ↓
5. retry_plan_node
      ↓
   state["attempts"] = 2
   state["current_plan_index"] = 1  ← Next alternative
      ↓
   [LOOP BACK TO execute_tools]
      ↓
   Tools executed with Plan 1 (different parameters)
      ↓
   ... cycle repeats ...
```

---

## 📊 Concrete Example

### Scenario: Schedule Shift Request

**LLM Generated 3 Alternatives:**

```json
{
  "alternatives": [
    {"delay_days": 2, "backup_required": true, "manpower": 5},
    {"delay_days": 1, "backup_required": false, "manpower": 3},
    {"delay_days": 2, "backup_required": true, "manpower": 4}
  ]
}
```

---

### **Attempt 1: Plan 0**

```
execute_tools(plan=0)
  → check_manpower_availability(days=2)
  → Result: available=2, required=5
  
evaluate_feasibility()
  → manpower check: 2 < 5 ❌
  → feasible = False
  → blocking_factor = "Insufficient manpower: 2/5"

should_retry_plan()
  → feasible? NO
  → attempts (0) < max_attempts (3)? YES
  → plan_index (0) + 1 < total_plans (3)? YES
  → Decision: RETRY
  
retry_plan_node()
  → attempts = 1
  → current_plan_index = 1
  → LOOP BACK to execute_tools
```

---

### **Attempt 2: Plan 1**

```
execute_tools(plan=1)
  → check_manpower_availability(days=1)
  → Result: available=4, required=3
  
evaluate_feasibility()
  → manpower check: 4 >= 3 ✅
  → pipeline check: pressure_ok ✅
  → safety check: low risk ✅
  → backup check: 30 hours >= 24 ✅
  → schedule check: no conflicts ✅
  → feasible = True
  → All constraints satisfied!

should_retry_plan()
  → feasible? YES
  → Decision: CONTINUE (no loop)
  
→ Proceeds to validate_policy (Phase 10)
```

---

## 🎯 Loop Termination Conditions

The loop **stops** when **ANY** of these is true:

| Condition | Meaning | Result |
|-----------|---------|--------|
| `feasible = True` | Found working plan | ✅ Success - continue |
| `attempts >= max_attempts` | Tried too many times | ⚠️ Give up - escalate |
| `plan_index + 1 >= total_plans` | No more alternatives | ⚠️ Give up - escalate |
| `escalate = True` | Already escalating (critical risk) | ⚠️ Skip retries |

---

## 🧮 State Changes During Loop

### Initial State (Before First Execution)
```python
{
  "plan": [plan0, plan1, plan2],  # 3 alternatives from LLM
  "current_plan_index": 0,        # Start with first plan
  "attempts": 0,                  # No attempts yet
  "max_attempts": 3,              # Maximum 3 tries
  "feasible": False,              # Not evaluated yet
}
```

### After Loop Iteration 1 (Plan 0 failed)
```python
{
  "plan": [plan0, plan1, plan2],
  "current_plan_index": 1,        # ← Incremented
  "attempts": 1,                  # ← Incremented
  "max_attempts": 3,
  "feasible": False,              # Plan 0 was not feasible
  "feasibility_reason": "Insufficient manpower: 2/5",
}
```

### After Loop Iteration 2 (Plan 1 succeeded)
```python
{
  "plan": [plan0, plan1, plan2],
  "current_plan_index": 1,        # Used Plan 1
  "attempts": 2,
  "max_attempts": 3,
  "feasible": True,               # ← SUCCESS!
  "feasibility_reason": "All constraints satisfied",
}
```

---

## 🔍 Why This Loop Design?

### 1. **Intelligent Retry**
- Not all plans are equal
- LLM proposes multiple options (conservative vs aggressive)
- Try alternatives before giving up

### 2. **Bounded Exploration**
- Maximum 3 attempts prevents infinite loops
- Fail-safe termination

### 3. **Deterministic Evaluation**
- Each plan evaluated by **same rules**
- No randomness in feasibility check
- Reproducible results

### 4. **Efficient Resource Use**
- Only re-execute tools (data collection)
- Don't re-run LLM (expensive)
- Don't reload context (unnecessary)

---

## 🎬 Full Example Flow with Loop

```
User Request: "Shift maintenance by 2 days"
   ↓
LLM generates 3 plans:
   Plan A: 2 days, 5 workers, backup ON
   Plan B: 1 day, 3 workers, backup OFF
   Plan C: 2 days, 4 workers, backup ON
   ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ATTEMPT 1: Try Plan A (2 days, 5 workers)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   execute_tools()
      → check_manpower: available=2
   evaluate_feasibility()
      → 2 < 5 workers needed
      → feasible = FALSE
   should_retry_plan()
      → attempts=0 < max=3 ✓
      → plan_index=0+1 < total=3 ✓
      → RETRY!
   retry_plan_node()
      → attempts = 1
      → plan_index = 1
      → [LOOP BACK]
   ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ATTEMPT 2: Try Plan B (1 day, 3 workers)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   execute_tools()
      → check_manpower: available=4
   evaluate_feasibility()
      → 4 >= 3 workers needed ✓
      → All checks pass ✓
      → feasible = TRUE
   should_retry_plan()
      → feasible = TRUE
      → NO RETRY - CONTINUE!
   ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTINUE TO POLICY VALIDATION (no more loop)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   validate_policy()
   estimate_confidence()
   route_decision()
   generate_output()
      → Decision: APPROVED
      → Plan: 1-day delay with 3 workers
```

---

## 💡 Key Insight

**The loop is NOT random or exploratory.**

It's a **systematic search** through LLM-proposed alternatives until:
1. ✅ A **feasible** plan is found (rules validate it), OR
2. ⚠️ All options exhausted (escalate to human)

**LLM proposes** (creativity) → **Loop tries** (exploration) → **Rules validate** (safety)

---

## 🎯 Summary

| Aspect | Details |
|--------|---------|
| **Loop Trigger** | `feasible = False` after feasibility evaluation |
| **Loop Basis** | Try next LLM-generated plan alternative |
| **Loop Limit** | Max 3 attempts OR run out of alternatives |
| **Loop Back To** | `execute_tools` (re-collect data with new plan) |
| **Loop Stops When** | Plan feasible OR max attempts OR no alternatives |
| **What Changes** | `attempts++`, `current_plan_index++` |
| **What Stays Same** | Context, intent, goal (already loaded) |
| **Decision Point** | `should_retry_plan()` conditional routing |

The loop is **deterministic, bounded, and purposeful** - exactly what professional agentic systems need.
