# Database Migrations

This directory contains SQL scripts for database schema creation and test data seeding.

## Files

- **complete_schema.sql** - Full database schema with all tables
- **seed_test_data.sql** - Comprehensive test data with edge cases
- **drop_all_tables.sql** - Drop all tables (use with caution)
- **fire_schema.sql** - Fire department specific schema
- **sanitation_schema.sql** - Sanitation department specific schema

## Quick Start

### 1. Create Database (if not exists)

```bash
# Using psql command line
psql -U postgres -c "CREATE DATABASE departments;"
```

### 2. Run Schema Migration

```bash
# Windows PowerShell
$env:PGPASSWORD="password"; psql -U postgres -d departments -f migrations/complete_schema.sql

# Linux/Mac
PGPASSWORD=password psql -U postgres -d departments -f migrations/complete_schema.sql
```

### 3. Load Test Data

```bash
# Windows PowerShell
$env:PGPASSWORD="password"; psql -U postgres -d departments -f migrations/seed_test_data.sql

# Linux/Mac
PGPASSWORD=password psql -U postgres -d departments -f migrations/seed_test_data.sql
```

### 4. Verify Data Loaded

```bash
$env:PGPASSWORD="password"; psql -U postgres -d departments -c "SELECT COUNT(*) FROM workers; SELECT COUNT(*) FROM incidents;"
```

## Alternative: Using Python Script

For easier execution, use the provided Python helper:

```bash
python migrations/load_test_data.py
```

## Test Data Summary

The seed_test_data.sql file includes realistic test scenarios:

### Edge Cases Covered

#### Budget Edge Cases
- ✅ Normal budget (Water Department)
- ✅ Under-utilized budget (Fire Department - 85% available)
- ✅ **DEPLETED budget** (Engineering - $5k over allocation)
- ✅ **FROZEN budget** (Health - pending investigation)
- ✅ Nearly depleted (Sanitation - $500 remaining)

#### Infrastructure Edge Cases
- ✅ **Critical/Empty reservoir** (North - 11% capacity)
- ✅ **Contaminated water** (East - quality score 45.3)
- ✅ **Over capacity/Flood risk** (West - 103% full)
- ✅ **Burst pipeline** (Emergency Line E - pressure 12.3 PSI)
- ✅ Old aging infrastructure (1985 cast iron)

#### Workforce Edge Cases
- ✅ Workers with varied skill levels (junior to expert)
- ✅ **Unavailable workers** (on leave/assigned elsewhere)
- ✅ Multiple departments represented
- ✅ Different certification levels

#### Incident Edge Cases
- ✅ **Active critical emergencies** (major leak, contamination)
- ✅ High severity incidents
- ✅ Routine incidents
- ✅ **Stale/old unresolved tickets** (30+ days old)
- ✅ Historical resolved incidents

#### Project Edge Cases
- ✅ On-time, on-budget projects
- ✅ **Over-budget projects** (+21% over estimate)
- ✅ **Behind schedule projects**
- ✅ **Cancelled projects** (mid-construction)
- ✅ Planned but unfunded projects
- ✅ Successfully completed projects

#### Work Schedule Edge Cases
- ✅ Scheduled future work
- ✅ **In-progress active work**
- ✅ Completed historical work
- ✅ **Cancelled/postponed work**
- ✅ **Delayed/overdue work**

#### Decision History Edge Cases
- ✅ Approved decisions (high confidence)
- ✅ **Denied decisions** (budget constraints)
- ✅ **Escalated decisions** (low confidence, policy violations)
- ✅ Multi-agent coordination scenarios
- ✅ Conflict resolution examples

## Test Scenarios

After loading data, you can test these scenarios:

### Scenario 1: Emergency Response with Limited Resources
```json
{
  "type": "emergency_response",
  "location": "Zone-A",
  "severity": "critical",
  "incident_type": "major_leak"
}
```
**Expected**: Should escalate due to insufficient workers (see incident i1)

### Scenario 2: Budget-Constrained Project
```json
{
  "type": "project_planning",
  "location": "Zone-B",
  "department": "engineering",
  "estimated_cost": 50000
}
```
**Expected**: Should deny due to depleted engineering budget

### Scenario 3: Water Quality Emergency
```json
{
  "type": "emergency_response",
  "location": "Zone-C",
  "incident_type": "contamination"
}
```
**Expected**: Should approve with high priority (see reservoir r4)

### Scenario 4: Capacity Query - Critical Reservoir
```json
{
  "type": "capacity_query",
  "location": "Zone-A"
}
```
**Expected**: Should flag North Reservoir as critical (11% capacity)

### Scenario 5: Budget Reallocation
```json
{
  "type": "budget_allocation",
  "from_department": "fire",
  "to_department": "engineering",
  "amount": 100000
}
```
**Expected**: Should approve (fire has 85% available, engineering depleted)

### Scenario 6: Scheduling Conflict
```json
{
  "type": "maintenance_request",
  "location": "Zone-A",
  "worker_id": "w3"
}
```
**Expected**: Worker w3 already assigned to critical incident i1

## Data Volume

Total records in test data:
- 6 Departments
- 12 Budget records (covering edge cases)
- 5 Reservoirs (various states)
- 5 Pipelines (various conditions)
- 11 Workers (varied availability)
- 8 Work schedules (various states)
- 10 Incidents (severity range + historical)
- 8 Projects (all lifecycle stages)
- 8 Agent decisions (historical audit trail)

## Resetting Data

To clear all data and start fresh:

```bash
# Option 1: Re-run seed script (has TRUNCATE commands)
$env:PGPASSWORD="password"; psql -U postgres -d departments -f migrations/seed_test_data.sql

# Option 2: Drop and recreate database
psql -U postgres -c "DROP DATABASE departments;"
psql -U postgres -c "CREATE DATABASE departments;"
$env:PGPASSWORD="password"; psql -U postgres -d departments -f migrations/complete_schema.sql
$env:PGPASSWORD="password"; psql -U postgres -d departments -f migrations/seed_test_data.sql
```

## Environment Variables

Ensure your `.env` file has correct database credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=departments
DB_USER=postgres
DB_PASSWORD=password
```

## Troubleshooting

### Error: "database does not exist"
Create the database first:
```bash
psql -U postgres -c "CREATE DATABASE departments;"
```

### Error: "extension uuid-ossp does not exist"
Enable the extension:
```bash
psql -U postgres -d departments -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

### Error: "permission denied"
Grant permissions:
```bash
psql -U postgres -d departments -c "GRANT ALL PRIVILEGES ON DATABASE departments TO postgres;"
```

### Verification Queries

Check data was loaded correctly:

```sql
-- Check all table counts
SELECT 'departments' as table_name, COUNT(*) FROM departments
UNION ALL SELECT 'budgets', COUNT(*) FROM department_budgets
UNION ALL SELECT 'workers', COUNT(*) FROM workers
UNION ALL SELECT 'reservoirs', COUNT(*) FROM reservoirs
UNION ALL SELECT 'pipelines', COUNT(*) FROM pipelines
UNION ALL SELECT 'incidents', COUNT(*) FROM incidents
UNION ALL SELECT 'projects', COUNT(*) FROM projects
UNION ALL SELECT 'schedules', COUNT(*) FROM work_schedules
UNION ALL SELECT 'decisions', COUNT(*) FROM agent_decisions;

-- Find edge cases
SELECT * FROM department_budgets WHERE status = 'depleted';
SELECT * FROM reservoirs WHERE status = 'critical';
SELECT * FROM incidents WHERE severity = 'critical' AND status = 'open';
SELECT * FROM projects WHERE actual_cost > estimated_cost;
```

## Notes

- Test data includes realistic values based on municipal operations
- All timestamps use current date context (February 2026)
- Edge cases are intentionally included to test agent decision logic
- Historical data provides context for trend analysis
- Worker assignments reflect realistic availability constraints
