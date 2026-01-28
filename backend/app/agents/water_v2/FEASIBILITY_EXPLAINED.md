# Feasibility Calculation Explained

## 🎯 What is Feasibility?

**Feasibility** = Can this plan be safely executed given current reality?

It's calculated by **Phase 9: Feasibility Evaluator** - the **MOST CRITICAL** node in the workflow.

---

## 🔧 NO LLM - Pure Deterministic Logic

```python
# This is NOT LLM
# This is NOT "AI guessing"
# This is PURE PYTHON LOGIC
```

**Why?** Because feasibility is about **safety and reality**, not creativity.

---

## 📊 The 6 Constraints Checked

Feasibility is calculated by checking **6 independent constraints**. **ALL must pass** for plan to be feasible.

```python
feasible = (
    pipeline_health_ok AND
    manpower_sufficient AND
    safety_acceptable AND
    backup_adequate AND
    no_schedule_conflicts AND
    budget_available
)
```

If **ANY** constraint fails → `feasible = False`

---

## 1️⃣ Pipeline Health Check

### What it checks:
```python
pipeline_check = observations["check_pipeline_health"]

if pipeline_check["pressure_ok"] == False:
    feasible = False
    reason = "Pipeline pressure inadequate"
```

### How `pressure_ok` is calculated (in tools.py):

```python
# Step 1: Query all pipelines in location from database
pipelines = db.query(WaterInfrastructure).filter(location=zone).all()

# Step 2: Count how many have adequate pressure (>= 40 PSI)
pressure_ok_count = count(p for p in pipelines if p.pressure_psi >= 40)

# Step 3: Calculate percentage
pressure_score = pressure_ok_count / total_pipelines

# Step 4: Determine if acceptable
pressure_ok = (pressure_score >= 0.8)  # At least 80% pipes must be good
```

### Real example:
```
Location: Zone-12
Total pipelines: 10

Pipeline data from DB:
- Pipe 1: 45 PSI ✓
- Pipe 2: 38 PSI ✗
- Pipe 3: 50 PSI ✓
- Pipe 4: 42 PSI ✓
... (7 more pipes with adequate pressure)

Calculation:
pressure_ok_count = 8 pipes
pressure_score = 8/10 = 0.8 = 80%
pressure_ok = (0.8 >= 0.8) = TRUE ✅

Constraint: SATISFIED
```

---

## 2️⃣ Manpower Availability Check

### What it checks:
```python
manpower_check = observations["check_manpower_availability"]

if manpower_check["sufficient"] == False:
    feasible = False
    reason = f"Insufficient manpower: {available}/{required}"
```

### How `sufficient` is calculated:

```python
# Step 1: Check existing scheduled work in requested period
scheduled_work = db.query(MaintenanceSchedule).filter(
    date >= now AND date <= now + requested_days
).all()

# Step 2: Calculate workers already allocated
total_workers = 10  # Department has 10 workers
workers_per_job = 3
workers_allocated = len(scheduled_work) * 3

# Step 3: Calculate available workers
workers_available = total_workers - workers_allocated

# Step 4: Compare with required
workers_required = 5  # Standard requirement
sufficient = (workers_available >= workers_required)
```

### Real example:
```
Request: 2-day maintenance shift

Current schedule (from DB):
- Day 1: Pipeline repair (3 workers)
- Day 2: Pump maintenance (3 workers)

Calculation:
total_workers = 10
workers_allocated = 2 jobs × 3 workers = 6
workers_available = 10 - 6 = 4
workers_required = 5

sufficient = (4 >= 5) = FALSE ✗

Constraint: FAILED
Blocking factor: "Insufficient manpower: 4/5"
```

---

## 3️⃣ Safety Risk Check

### What it checks:
```python
safety_check = observations["check_safety_risk"]

if safety_check["safety_risk"] == "high":
    feasible = False
    reason = "High safety risk in area"
```

### How `safety_risk` is calculated:

```python
# Step 1: Check recent incidents in last 30 days
incidents = db.query(WaterIncident).filter(
    location = zone AND
    incident_date >= (now - 30 days)
).all()

# Step 2: Count incidents
incident_count = len(incidents)

# Step 3: Classify risk level
if incident_count == 0:
    safety_risk = "low"
elif incident_count <= 2:
    safety_risk = "medium"
else:
    safety_risk = "high"
```

### Real example:
```
Location: Zone-12
Last 30 days incidents (from DB):

- 2024-01-05: Pipeline burst
- 2024-01-15: Contamination detected
- 2024-01-20: Pressure surge
- 2024-01-25: Leak reported

Calculation:
incident_count = 4

Risk classification:
4 > 2 → safety_risk = "high"

Constraint: FAILED (high risk not acceptable)
```

---

## 4️⃣ Emergency Backup Check

### What it checks:
```python
backup_check = observations["check_emergency_backup"]

min_backup_hours = 24  # Department rule

if backup_check["duration_hours"] < min_backup_hours:
    feasible = False
    reason = f"Insufficient backup: {duration}h < {min_backup_hours}h required"
```

### How `duration_hours` is calculated:

```python
# Step 1: Query reservoirs in location
reservoirs = db.query(WaterInfrastructure).filter(
    location = zone AND
    type = "reservoir"
).all()

# Step 2: Calculate total backup capacity
total_capacity_liters = sum(r.capacity for r in reservoirs)

# Step 3: Calculate duration
population = 1000  # People in zone
consumption_per_day = 50  # Liters per person per day
daily_consumption = population * consumption_per_day

duration_days = total_capacity_liters / daily_consumption
duration_hours = duration_days * 24
```

### Real example:
```
Location: Zone-12

Reservoirs (from DB):
- Reservoir A: 30,000 L
- Reservoir B: 20,000 L

Calculation:
total_capacity = 30,000 + 20,000 = 50,000 L
population = 1,000 people
daily_consumption = 1,000 × 50 = 50,000 L/day

duration_days = 50,000 / 50,000 = 1 day
duration_hours = 1 × 24 = 24 hours

Check:
24 hours >= 24 hours required = TRUE ✅

Constraint: SATISFIED
```

---

## 5️⃣ Schedule Conflict Check

### What it checks:
```python
schedule_check = observations["check_schedule_conflicts"]

if schedule_check["conflicts"] == True:
    feasible = False
    reason = f"Schedule conflicts: {conflict_count} conflicting activities"
```

### How `conflicts` is calculated:

```python
# Step 1: Query high-priority scheduled work in requested period
conflicting_work = db.query(MaintenanceSchedule).filter(
    location = zone AND
    date >= start_date AND
    date <= end_date AND
    priority = "high"  # Only high-priority creates conflict
).all()

# Step 2: Check if any found
conflicts = (len(conflicting_work) > 0)
```

### Real example:
```
Request: Maintenance on Jan 29-30

Schedule (from DB):
- Jan 29: Routine cleaning (priority: low) → OK
- Jan 30: Critical pump repair (priority: high) → CONFLICT!

Calculation:
high_priority_work = ["Critical pump repair"]
conflict_count = 1
conflicts = TRUE

Constraint: FAILED
Blocking factor: "Schedule conflicts: 1 conflicting activities"
```

---

## 6️⃣ Budget Availability Check

### What it checks:
```python
budget_check = observations["check_budget_availability"]

# Check 1: Sufficient funds
if budget_check["sufficient"] == False:
    feasible = False
    reason = f"Insufficient budget: ₹{budget_check['budget_available']:,.0f} available, ₹{budget_check['estimated_cost']:,.0f} required"

# Check 2: Utilization under limit
if budget_check["utilization_percent"] > max_budget_utilization_percent (90%):
    feasible = False
    reason = f"Budget utilization too high: {budget_check['utilization_percent']:.1f}% > 90% limit"
```

### How budget is calculated:

```python
# Step 1: Estimate cost for requested work
daily_base_cost = 10000  # Materials, equipment
daily_manpower_cost = 5 workers × 500 = 2500
estimated_cost = requested_days × (10000 + 2500)

# Step 2: Query spent amount this month
amount_spent = db.query(Project).filter(
    location = zone AND
    start_date >= first_day_of_month
).sum(actual_cost)

# Step 3: Calculate available budget
monthly_budget = 500000  # Department budget
budget_available = monthly_budget - amount_spent

# Step 4: Calculate utilization percentage
utilization_percent = (amount_spent / monthly_budget) × 100

# Step 5: Check constraints
sufficient = (budget_available >= estimated_cost)
within_limit = (utilization_percent <= 90)
```

### Real example:
```
Request: 3-day maintenance

Cost estimation:
- Daily base: ₹10,000
- Daily manpower: 5 × ₹500 = ₹2,500
- Estimated: 3 × ₹12,500 = ₹37,500

Budget check (from DB):
- Monthly budget: ₹500,000
- Spent this month: ₹420,000
- Available: ₹80,000
- Utilization: 84%

Calculation:
sufficient = (₹80,000 >= ₹37,500) = TRUE ✅
within_limit = (84% <= 90%) = TRUE ✅

Constraint: PASSED
```

---

## 🧮 Final Feasibility Calculation

```python
constraints_satisfied = {
    "pipeline_health": True/False,
    "manpower": True/False,
    "safety": True/False,
    "backup": True/False,
    "schedule": True/False,
    "budget": True/False
}

# ALL must be True
feasible = all(constraints_satisfied.values())
```

### Example 1: FEASIBLE
```python
constraints_satisfied = {
    "pipeline_health": True,   ✅
    "manpower": True,          ✅
    "safety": True,            ✅
    "backup": True,            ✅
    "schedule": True,          ✅
    "budget": True,            ✅
    "safety": True,            ✅
    "backup": True,            ✅
    "schedule": True           ✅
}

feasible = True
reason = "All constraints satisfied"
```

### Example 2: NOT FEASIBLE (Budget Exceeded)
```python
constraints_satisfied = {
    "pipeline_health": True,   ✅
    "manpower": True,          ✅
    "safety": True,            ✅
    "backup": True,            ✅
    "schedule": True,          ✅
    "budget": False,           ❌ (₹20k available, ₹62.5k required)
}

feasible = False
reason = "Blocking factors: Insufficient budget: ₹20,000 available, ₹62,500 required"
```

### Example 3: NOT FEASIBLE (Multiple Failures)
```python
constraints_satisfied = {
    "pipeline_health": True,   ✅
    "manpower": False,         ❌ (4/5 workers)
    "safety": True,            ✅
    "backup": True,            ✅
    "schedule": False,         ❌ (1 conflict)
    "budget": False,           ❌ (96% utilization > 90%)
}

feasible = False
reason = "Blocking factors: Insufficient manpower: 4/5, Schedule conflicts: 1 conflicting activities, Budget utilization too high: 96% > 90% limit"
```

---

## 📋 Complete Feasibility Flow

```
1. Tools execute (Phase 7)
      ↓
   [Database queries return real data]
      ↓
2. Observations normalized (Phase 8)
      ↓
   {
     "check_pipeline_health": {"pressure_ok": True, ...},
     "check_manpower_availability": {"sufficient": False, "available": 4, "required": 5},
     "check_safety_risk": {"safety_risk": "low", ...},
     "check_emergency_backup": {"duration_hours": 30, ...},
     "check_schedule_conflicts": {"conflicts": True, "conflict_count": 1}
   }
      ↓
3. Feasibility evaluated (Phase 9)
      ↓
   Constraint 1: pipeline_health
      pressure_ok = True ✅
   
   Constraint 2: manpower
      sufficient = False ❌
      → blocking_factor = "Insufficient manpower: 4/5"
   
   Constraint 3: safety
      safety_risk = "low" (not "high") ✅
   
   Constraint 4: backup
      duration_hours (30) >= min_required (24) ✅
   
   Constraint 5: schedule
      conflicts = True ❌
      → blocking_factor = "Schedule conflicts: 1 conflicting activities"
      ↓
4. Final calculation
      ↓
   constraints_satisfied = {
     "pipeline_health": True,
     "manpower": False,
     "safety": True,
     "backup": True,
     "schedule": False
   }
   
   feasible = all([True, False, True, True, False])
   feasible = False
   
   feasibility_reason = "Blocking factors: Insufficient manpower: 4/5, Schedule conflicts: 1 conflicting activities"
```

---

## 🎯 Why This Approach?

### ✅ **Deterministic**
- Same inputs → Same result (every time)
- No randomness, no "AI hallucination"
- Fully reproducible

### ✅ **Explainable**
- Know exactly WHY plan failed
- Can tell user: "Need 5 workers, only 4 available"
- Audit trail clear

### ✅ **Safe**
- Critical infrastructure decisions
- Can't risk LLM making safety calls
- Hard constraints enforced

### ✅ **Debuggable**
- If wrong, check which constraint failed
- Trace back to database query
- Fix data or logic, not "prompt engineering"

### ✅ **Testable**
- Unit test each constraint independently
- Mock database responses
- Verify all edge cases

---

## 🔄 How This Fits in Loop

```
Try Plan A → Execute tools → Observe → Evaluate feasibility
                                            ↓
                                    feasible = False
                                    (manpower: 4/5)
                                            ↓
                                    Can retry? YES
                                            ↓
Try Plan B → Execute tools → Observe → Evaluate feasibility
                                            ↓
                                    feasible = True
                                    (manpower: 6/5) ✅
                                            ↓
                                    Continue to policy
```

**Different plans may satisfy different constraints:**
- Plan A: needs 5 workers (not available)
- Plan B: needs 3 workers (available!)

**Feasibility check is THE SAME** - only input data changes.

---

## 🎓 Key Insight

> **Feasibility is NOT a guess or prediction.**
> 
> **It's a FACT CHECK against current reality.**

- Pipeline pressure: **FACT** (from sensors/DB)
- Manpower: **FACT** (from schedule/DB)
- Safety: **FACT** (from incident history)
- Backup: **FACT** (from reservoir levels)
- Schedule: **FACT** (from calendar)

**If facts don't support plan → Plan is NOT feasible.**

No LLM. No uncertainty. Just logic.

---

## 📊 Summary Table

| Constraint | Data Source | Logic | Pass Criteria |
|------------|-------------|-------|---------------|
| **Pipeline Health** | `water_infrastructure` table | Pressure >= 40 PSI | 80%+ pipes OK |
| **Manpower** | `maintenance_schedule` table | Total - Allocated | Available >= Required |
| **Safety Risk** | `water_incidents` table | Count last 30 days | <= 2 incidents |
| **Emergency Backup** | `water_infrastructure` table | Capacity / Consumption | >= 24 hours |
| **Schedule Conflicts** | `maintenance_schedule` table | High-priority overlaps | 0 conflicts |

**Feasible = ALL constraints pass**

This is professional-grade constraint satisfaction, not AI guessing.
