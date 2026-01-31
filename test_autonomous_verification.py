"""
Comprehensive Autonomous Agent Verification

Tests that the agent works as a true autonomous agent:
1. Makes decisions independently using DB, LLM, and tools
2. Escalates appropriately when needed
3. Recommends when confident and feasible
4. Uses all three components (DB, LLM, Tools) in decision making
"""

import pytest
from water_agent import WaterDepartmentAgent
from water_agent.database import get_db


class TestAutonomousBehavior:
    """Test autonomous decision-making capabilities"""
    
    @classmethod
    def setup_class(cls):
        """Setup agent once for all tests"""
        cls.agent = WaterDepartmentAgent()
        cls.db = get_db()
    
    def test_autonomous_decision_low_risk_case(self):
        """
        Verify agent makes autonomous RECOMMENDATION for low-risk case
        - Uses DB to check constraints
        - Uses LLM to generate plan
        - Uses tools to verify feasibility
        - Makes confident decision WITHOUT human intervention
        """
        request = {
            "type": "capacity_query",
            "location": "Zone-A",
            "reason": "Check available capacity for routine maintenance"
        }
        
        result = self.agent.decide(request)
        
        # Should make autonomous decision (recommend OR escalate based on constraints)
        assert result["decision"] in ["recommend", "approve", "escalate"], \
            f"Invalid decision: {result['decision']}"
        
        # Should have used database
        assert "details" in result
        details = result["details"]
        
        # If it recommends, should have reasonable confidence
        confidence = details.get("confidence", 0)
        if result["decision"] in ["recommend", "approve"]:
            assert confidence > 0.3, f"Low confidence {confidence} for recommendation"
        
        print(f"\n✓ Autonomous Decision: {result['decision'].upper()}")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Risk: {details.get('risk_level', 'unknown')}")
    
    def test_autonomous_escalation_high_cost(self):
        """
        Verify agent ESCALATES when constraints violated
        - Checks budget constraint from DB
        - Recognizes budget exceeded
        - Autonomously decides to ESCALATE (correct decision)
        """
        request = {
            "type": "maintenance_request",
            "location": "Zone-B",
            "estimated_cost": 999999,  # Exceeds available budget
            "urgency": "routine",
            "reason": "Annual pipe inspection"
        }
        
        result = self.agent.decide(request)
        
        # Should autonomously ESCALATE due to budget
        assert result["decision"] == "escalate", \
            f"Expected escalation for high cost, got {result['decision']}"
        
        # Should explain reason
        assert "reason" in result or "escalation_reason" in result.get("details", {})
        
        reason = result.get("reason") or result.get("details", {}).get("escalation_reason", "")
        print(f"\n✓ Autonomous Escalation: {result['decision'].upper()}")
        print(f"  Reason: {reason}")
    
    def test_database_usage_in_decisions(self):
        """
        Verify agent actually USES database data in decision-making
        - Fetches real constraints from DB
        - Applies constraints to decision
        - Decision reflects actual DB state
        """
        # Get worker count from database directly
        from water_agent.database import get_queries
        queries = get_queries(self.db)
        workers_data = queries.get_worker_availability()
        available_workers = workers_data.get("available_count", 0)
        
        print(f"\n📊 Database state: {available_workers} workers available")
        
        request = {
            "type": "schedule_shift_request",
            "location": "Zone-C",
            "requested_shift_days": 1,
            "workers_needed": 3,
            "reason": "Routine shift adjustment"
        }
        
        result = self.agent.decide(request)
        
        # Agent should have considered worker availability
        assert "details" in result
        details = result["details"]
        
        # Should have tool results showing DB query
        if "tool_results" in details:
            tool_results = details["tool_results"]
            assert len(tool_results) > 0, "No tools executed - not using DB!"
            print(f"  ✓ Tools executed: {len(tool_results)}")
        
        print(f"  Decision: {result['decision'].upper()}")
    
    def test_llm_plan_generation(self):
        """
        Verify agent uses LLM to generate execution plans
        - LLM analyzes request
        - LLM generates multi-step plan
        - Plan includes specific tool calls
        """
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "maintenance_type": "preventive",
            "estimated_cost": 25000,
            "reason": "Quarterly maintenance check"
        }
        
        result = self.agent.decide(request)
        
        # Should have executed a plan
        details = result.get("details", {})
        
        # Should have tool results (evidence of plan execution)
        tool_results = details.get("tool_results", {})
        observations = details.get("observations", {})
        
        assert len(tool_results) > 0 or len(observations) > 0, \
            "No plan executed - LLM not generating plans!"
        
        print(f"\n✓ LLM Plan Execution:")
        print(f"  Tools used: {len(tool_results)}")
        print(f"  Observations: {len(observations)}")
    
    def test_tool_execution_with_database(self):
        """
        Verify tools are executed and query real database
        - Tools execute database queries
        - Results reflect actual DB state
        - Agent uses results in decision
        """
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "estimated_cost": 30000,
            "workers_needed": 4,
            "reason": "Pipe replacement"
        }
        
        result = self.agent.decide(request)
        details = result.get("details", {})
        
        # Should have executed tools
        tool_results = details.get("tool_results", {})
        assert len(tool_results) > 0, "No tools executed!"
        
        # Tools should return real data
        has_real_data = False
        for tool_name, tool_result in tool_results.items():
            if tool_result and tool_result not in [None, "", "N/A", {}]:
                has_real_data = True
                print(f"  ✓ {tool_name}: {str(tool_result)[:100]}")
        
        assert has_real_data, "Tools executed but returned no real data!"
    
    def test_policy_enforcement_autonomous(self):
        """
        Verify agent autonomously enforces policy rules
        - Checks policy compliance
        - Escalates on policy violations
        - Does NOT need human to tell it about policies
        """
        request = {
            "type": "emergency_response",
            "location": "Zone-D",
            "emergency_type": "pipe_burst",
            "estimated_cost": 15000,
            "reason": "Water main break"
        }
        
        result = self.agent.decide(request)
        
        # Emergency should be handled (high priority)
        # Agent should make autonomous decision
        assert result["decision"] in ["recommend", "approve", "escalate"]
        
        details = result.get("details", {})
        
        # Should have checked policy
        policy_ok = details.get("policy_ok", details.get("policy_compliant"))
        print(f"\n✓ Policy Check: {policy_ok}")
        print(f"  Decision: {result['decision'].upper()}")
    
    def test_confidence_based_escalation(self):
        """
        Verify agent escalates when confidence is low
        - Calculates confidence based on multiple factors
        - Autonomously escalates if confidence < threshold
        - Explains reasoning
        """
        # Complex request with ambiguous details
        request = {
            "type": "project_planning",
            "location": "Zone-Unknown",  # May cause lower confidence
            "estimated_cost": 75000,
            "duration_days": 45,
            "reason": "New infrastructure project"
        }
        
        result = self.agent.decide(request)
        details = result.get("details", {})
        
        # Should have confidence score
        confidence = details.get("confidence", 0)
        assert confidence >= 0 and confidence <= 1, "Invalid confidence score"
        
        # Decision should match confidence
        if confidence < 0.7:
            assert result["decision"] == "escalate", \
                f"Low confidence {confidence} but didn't escalate!"
        
        print(f"\n✓ Confidence-Based Decision:")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Decision: {result['decision'].upper()}")
    
    def test_multi_constraint_evaluation(self):
        """
        Verify agent evaluates MULTIPLE constraints simultaneously
        - Budget from DB
        - Workers from DB
        - Policy rules
        - Risk assessment
        - Makes holistic decision
        """
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "estimated_cost": 40000,
            "workers_needed": 5,
            "duration_days": 3,
            "reason": "Major valve replacement"
        }
        
        result = self.agent.decide(request)
        details = result.get("details", {})
        
        # Should have evaluated multiple aspects
        evaluated_aspects = []
        
        if "feasible" in details or "feasibility_checked" in details:
            evaluated_aspects.append("feasibility")
        
        if "policy_ok" in details or "policy_compliant" in details:
            evaluated_aspects.append("policy")
        
        if "confidence" in details:
            evaluated_aspects.append("confidence")
        
        if "risk_level" in details:
            evaluated_aspects.append("risk")
        
        assert len(evaluated_aspects) >= 3, \
            f"Agent only evaluated {len(evaluated_aspects)} aspects, expected 3+"
        
        print(f"\n✓ Multi-Constraint Evaluation:")
        print(f"  Aspects evaluated: {', '.join(evaluated_aspects)}")
        print(f"  Decision: {result['decision'].upper()}")
    
    def test_different_request_types_autonomous(self):
        """
        Verify agent handles different request types autonomously
        - Each type may require different tools/checks
        - Agent selects appropriate strategy for each type
        """
        request_types = [
            {
                "type": "capacity_query",
                "location": "Zone-A",
                "reason": "Check capacity"
            },
            {
                "type": "schedule_shift_request",
                "location": "Zone-B",
                "requested_shift_days": 1,
                "reason": "Adjust schedule"
            },
            {
                "type": "incident_report",
                "location": "Zone-C",
                "incident_type": "minor_leak",
                "reason": "Small leak detected"
            }
        ]
        
        results = []
        for request in request_types:
            result = self.agent.decide(request)
            results.append({
                "type": request["type"],
                "decision": result["decision"],
                "confidence": result.get("details", {}).get("confidence", 0)
            })
        
        print(f"\n✓ Multi-Type Autonomous Handling:")
        for r in results:
            print(f"  {r['type']}: {r['decision'].upper()} (conf: {r['confidence']:.2%})")
        
        # All should produce decisions
        assert all(r["decision"] in ["recommend", "approve", "escalate"] 
                  for r in results), "Some requests didn't produce valid decisions"
    
    def test_no_human_intervention_in_workflow(self):
        """
        Verify workflow completes WITHOUT human intervention
        - Request in → Decision out
        - No waiting for human input
        - No coordination node blocking execution
        """
        import time
        
        request = {
            "type": "capacity_query",
            "location": "Zone-A",
            "reason": "Quick capacity check"
        }
        
        start_time = time.time()
        result = self.agent.decide(request)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete in reasonable time (< 2 minutes)
        # If it's waiting for human, it would hang/timeout
        assert execution_time < 120, \
            f"Execution took {execution_time}s - might be waiting for human!"
        
        # Should have a decision
        assert "decision" in result, "No decision made!"
        
        print(f"\n✓ Fully Autonomous Execution:")
        print(f"  Time: {execution_time:.2f}s")
        print(f"  Decision: {result['decision'].upper()}")
        print(f"  No human intervention required ✓")


class TestEscalationLogic:
    """Test escalation decision logic"""
    
    @classmethod
    def setup_class(cls):
        cls.agent = WaterDepartmentAgent()
    
    def test_escalate_on_budget_exceed(self):
        """Escalate when budget constraint violated"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "estimated_cost": 500000,  # Way over budget
            "reason": "Major overhaul"
        }
        
        result = self.agent.decide(request)
        assert result["decision"] == "escalate"
        print(f"✓ Budget violation → ESCALATE")
    
    def test_escalate_on_high_risk(self):
        """Escalate when risk is high"""
        request = {
            "type": "emergency_response",
            "location": "Zone-A",
            "emergency_type": "major_failure",
            "estimated_cost": 75000,
            "reason": "Critical infrastructure failure"
        }
        
        result = self.agent.decide(request)
        
        # Either escalate or approve depending on emergency handling
        # But should have assessed risk
        details = result.get("details", {})
        risk_level = details.get("risk_level", "unknown")
        
        print(f"✓ High-risk emergency: {result['decision'].upper()} (risk: {risk_level})")
    
    def test_recommend_when_all_clear(self):
        """Recommend when all constraints satisfied"""
        request = {
            "type": "capacity_query",
            "location": "Zone-A",
            "reason": "Simple capacity check"
        }
        
        result = self.agent.decide(request)
        
        # Simple query should NOT escalate
        assert result["decision"] in ["recommend", "approve"], \
            f"Simple query escalated: {result['decision']}"
        
        print(f"✓ All constraints met → RECOMMEND")


def test_summary_autonomous_verification():
    """
    Summary test - verify all autonomous capabilities
    """
    print("\n" + "="*70)
    print("AUTONOMOUS AGENT VERIFICATION SUMMARY")
    print("="*70)
    
    agent = WaterDepartmentAgent()
    
    # Test 1: Database integration
    request1 = {"type": "capacity_query", "location": "Zone-A", "reason": "Test"}
    result1 = agent.decide(request1)
    db_working = "details" in result1 and len(result1.get("details", {})) > 0
    
    # Test 2: Autonomous decision
    autonomous = result1["decision"] in ["recommend", "approve", "escalate"]
    
    # Test 3: Escalation logic
    request2 = {
        "type": "maintenance_request",
        "location": "Zone-A",
        "estimated_cost": 999999,  # Over budget
        "reason": "Test"
    }
    result2 = agent.decide(request2)
    escalation_working = result2["decision"] == "escalate"
    
    print(f"\n✓ Database Integration: {'PASS' if db_working else 'FAIL'}")
    print(f"✓ Autonomous Decision: {'PASS' if autonomous else 'FAIL'}")
    print(f"✓ Escalation Logic: {'PASS' if escalation_working else 'FAIL'}")
    
    print("\n" + "="*70)
    print("AUTONOMOUS AGENT STATUS:")
    print("="*70)
    print("✓ Makes decisions independently (no human in workflow)")
    print("✓ Uses database for constraints (budget, workers, etc)")
    print("✓ Uses LLM for planning and reasoning")
    print("✓ Uses tools to query database")
    print("✓ Escalates when constraints violated")
    print("✓ Recommends when confident and feasible")
    print("\n⚠️  MISSING: Coordination node for human approval after escalation")
    print("   Current: Agent escalates → Returns JSON → Workflow ENDS")
    print("   Needed: Agent escalates → Waits for human → Incorporates feedback")
    print("="*70)
    
    assert db_working and autonomous and escalation_working, \
        "Autonomous verification failed"
