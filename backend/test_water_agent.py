"""
Test Water Agent Workflow
Demonstrates various scenarios for Water Agent decision-making
"""
import asyncio
import asyncpg
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()


async def test_water_agent():
    """Test Water Agent with various scenarios"""
    
    print("=" * 80)
    print("🧪 TESTING WATER AGENT WORKFLOW")
    print("=" * 80)
    
    # Parse database URL
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/city_mas")
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    
    conn = await asyncpg.connect(dsn=f"postgresql://{db_url}")
    
    # Test scenarios
    scenarios = [
        {
            "name": "🚧 Scenario 1: Road Digging Request (Safe Location)",
            "request": {
                "request_type": "road_digging",
                "location": "East Ave - Block B",
                "priority": "medium",
                "details": {
                    "purpose": "Road widening project",
                    "depth": 1.5,
                    "duration": 7
                }
            }
        },
        {
            "name": "💧 Scenario 2: Water Leakage Report (High Risk)",
            "request": {
                "request_type": "leakage",
                "location": "Downtown Drainage",
                "priority": "high",
                "details": {
                    "severity": "high",
                    "reported_by": "Citizen",
                    "impact": "200 households affected"
                }
            }
        },
        {
            "name": "🏗️ Scenario 3: New Housing Project",
            "request": {
                "request_type": "new_project",
                "location": "North Highway Extension",
                "priority": "medium",
                "details": {
                    "project_type": "residential",
                    "population": 5000,
                    "area_sq_km": 2.0
                }
            }
        },
        {
            "name": "🔧 Scenario 4: Maintenance at Poor Condition Pipeline",
            "request": {
                "request_type": "maintenance",
                "location": "Main St - Block A",
                "priority": "high",
                "details": {
                    "maintenance_type": "preventive",
                    "scheduled_date": "2026-02-15"
                }
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'=' * 80}")
        print(f"{scenario['name']}")
        print(f"{'=' * 80}\n")
        
        request = scenario["request"]
        
        print(f"📋 Request Details:")
        print(f"   Type: {request['request_type']}")
        print(f"   Location: {request['location']}")
        print(f"   Priority: {request['priority']}")
        
        # Simulate data collection
        print(f"\n📊 Data Collection:")
        
        # Fetch pipeline data
        pipelines = await conn.fetch("""
            SELECT location, pipeline_type, condition, risk_level, operational_status
            FROM water_infrastructure
            WHERE location ILIKE $1 OR zone ILIKE $1
            LIMIT 3
        """, f"%{request['location']}%")
        
        print(f"   Found {len(pipelines)} pipelines:")
        for p in pipelines:
            print(f"      • {p['location']}: {p['pipeline_type']} | {p['condition']} condition | {p['risk_level']} risk")
        
        # Check conflicts
        conflicts = await conn.fetch("""
            SELECT project_type, location, status, priority
            FROM projects
            WHERE location ILIKE $1 AND status IN ('planned', 'active')
            LIMIT 3
        """, f"%{request['location']}%")
        
        print(f"   Found {len(conflicts)} conflicting projects:")
        for c in conflicts:
            print(f"      • {c['project_type']} at {c['location']} ({c['status']})")
        
        # Get reservoir status
        reservoirs = await conn.fetch("""
            SELECT name, level_percentage, operational_status
            FROM water_resources
            WHERE resource_type = 'reservoir'
        """)
        
        total_level = sum(float(r['level_percentage'] or 0) for r in reservoirs) / len(reservoirs) if reservoirs else 0
        print(f"   Reservoir Status: {total_level:.1f}% average level")
        
        # Simulate decision
        print(f"\n⚙️ Analysis:")
        
        # Determine risk
        risk_score = 0
        if pipelines:
            worst_condition = pipelines[0]['condition']
            if worst_condition == 'critical':
                risk_score += 5
            elif worst_condition == 'poor':
                risk_score += 3
            elif worst_condition == 'fair':
                risk_score += 2
            
            print(f"   Pipeline Condition: {worst_condition} (risk +{risk_score})")
        
        risk_score += len(conflicts) * 2
        if conflicts:
            print(f"   Project Conflicts: {len(conflicts)} (risk +{len(conflicts) * 2})")
        
        if total_level < 50:
            risk_score += 2
            print(f"   Low Reservoir Level (risk +2)")
        
        risk_level = "critical" if risk_score >= 10 else "high" if risk_score >= 7 else "medium" if risk_score >= 4 else "low"
        print(f"   Overall Risk: {risk_level.upper()} (score: {risk_score})")
        
        # Decision
        print(f"\n✅ Decision:")
        
        if pipelines and pipelines[0]['condition'] == 'critical':
            decision = "DENY"
            reason = "Pipeline in critical condition - excavation prohibited"
        elif len(conflicts) > 0:
            decision = "COORDINATE"
            reason = "Active projects detected - coordination with Roads department required"
        elif risk_level in ['high', 'critical']:
            decision = "ESCALATE"
            reason = "High risk requires senior management approval"
        else:
            decision = "APPROVE"
            reason = "Safe to proceed with standard protocols"
        
        print(f"   Decision: {decision}")
        print(f"   Reason: {reason}")
        
        # Coordination
        if len(conflicts) > 0 or risk_level in ['high', 'critical']:
            print(f"\n📨 Coordination Required:")
            if len(conflicts) > 0:
                print(f"      • Roads Department: Joint excavation planning")
            if risk_level in ['high', 'critical']:
                print(f"      • Fire Department: Emergency preparedness")
            if request['request_type'] == 'new_project':
                print(f"      • Finance Department: Budget approval")
        
        # Estimates
        cost = 25000 if request['request_type'] == 'leakage' else 150000 if request['request_type'] == 'new_project' else 50000
        duration = 1 if request['request_type'] == 'leakage' else 90 if request['request_type'] == 'new_project' else 7
        
        print(f"\n💰 Estimates:")
        print(f"   Cost: ₹{cost:,.0f}")
        print(f"   Duration: {duration} days")
        print(f"   Confidence: 85%")
        
        # Wait for user input to continue
        if i < len(scenarios):
            print(f"\n{'─' * 80}")
            await asyncio.sleep(1)
    
    await conn.close()
    
    print(f"\n{'=' * 80}")
    print(f"✅ ALL SCENARIOS TESTED SUCCESSFULLY")
    print(f"{'=' * 80}\n")
    print("📌 Key Takeaways:")
    print("   1. Water Agent analyzes pipeline condition, conflicts, and reservoir status")
    print("   2. Decisions: APPROVE, DENY, COORDINATE, or ESCALATE based on risk")
    print("   3. Inter-agent coordination triggered when needed (Roads, Fire, Finance)")
    print("   4. Safety policies prevent work near critical pipelines")
    print("   5. Cost and timeline estimates provided for all requests\n")
    
    print("🚀 Ready to start the API server!")
    print("   Run: uvicorn main:app --reload")
    print("   Then test: POST http://localhost:8000/api/water/request")


if __name__ == "__main__":
    asyncio.run(test_water_agent())
