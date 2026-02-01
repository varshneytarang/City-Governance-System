"""
Example: Water Agent with Transparency Logging

This shows how to integrate the transparency logging system
into existing water agent nodes.

Key Changes:
1. Import transparency logger
2. Add log calls at decision points
3. Include rationale, cost, citizen impact
"""

from typing import Dict, Any
from water_agent.state import DepartmentState
from transparency_logger import get_transparency_logger

# Get singleton logger
t_logger = get_transparency_logger()


# ==============================================================================
# EXAMPLE 1: Decision Router with Logging
# ==============================================================================

def decision_router_with_logging(state: DepartmentState) -> DepartmentState:
    """
    Decision router that logs all routing decisions for transparency
    
    Original logic + transparency logging
    """
    confidence = state.get("confidence", 0.0)
    feasible = state.get("feasible", False)
    policy_ok = state.get("policy_ok", True)
    
    # Original decision logic
    if confidence < 0.6:
        state["decision"] = "escalate"
        state["escalate"] = True
        decision = "escalate"
        rationale = f"Low confidence ({confidence:.0%}) below threshold - requires human review"
    elif not feasible:
        state["decision"] = "escalate"
        state["escalate"] = True
        decision = "escalate"
        rationale = f"Plan not feasible: {state.get('feasibility_reason', 'unknown reason')}"
    elif not policy_ok:
        state["decision"] = "escalate"
        state["escalate"] = True
        decision = "escalate"
        rationale = f"Policy violation: {', '.join(state.get('policy_violations', ['unknown']))}"
    else:
        state["decision"] = "recommend"
        state["escalate"] = False
        decision = "recommend"
        rationale = f"High confidence ({confidence:.0%}), feasible plan, policy compliant"
    
    # ===== TRANSPARENCY LOGGING =====
    t_logger.log_decision(
        agent_type="water",
        node_name="decision_router",
        decision=decision,
        context={
            "request": state.get("input_event", {}),
            "confidence": confidence,
            "feasible": feasible,
            "policy_ok": policy_ok,
            "location": state.get("input_event", {}).get("location", "unknown")
        },
        rationale=rationale,
        confidence=confidence,
        cost_impact=state.get("estimated_cost", 0),
        affected_citizens=state.get("affected_population", 0),
        policy_references=state.get("applicable_policies", []),
        metadata={
            "requires_human_review": state.get("escalate", False),
            "priority": state.get("input_event", {}).get("priority", "routine")
        }
    )
    
    return state


# ==============================================================================
# EXAMPLE 2: Planner with Historical Context from RAG
# ==============================================================================

def planner_with_rag_context(state: DepartmentState) -> DepartmentState:
    """
    Planner that uses RAG to find similar past decisions
    and includes that context in planning
    """
    request = state.get("input_event", {})
    request_type = request.get("type", "unknown")
    location = request.get("location", "unknown")
    
    # ===== RAG: Search for similar past decisions =====
    query = f"{request_type} in {location} water department"
    similar_decisions = t_logger.search_decisions(
        query=query,
        n_results=5,
        filter_agent="water",
        min_confidence=0.7
    )
    
    # Extract lessons from history
    if similar_decisions:
        past_costs = [float(d['metadata']['cost_impact']) for d in similar_decisions]
        past_confidence = [float(d['metadata']['confidence']) for d in similar_decisions]
        
        historical_context = {
            "similar_cases": len(similar_decisions),
            "avg_past_cost": sum(past_costs) / len(past_costs),
            "avg_past_confidence": sum(past_confidence) / len(past_confidence),
            "lessons_learned": [
                d['metadata']['rationale'][:100]
                for d in similar_decisions[:3]
            ]
        }
        
        state["historical_context"] = historical_context
        
        # Adjust estimates based on history
        if "estimated_cost" in state:
            # If our estimate is way off from historical average, flag it
            cost_ratio = state["estimated_cost"] / historical_context["avg_past_cost"]
            if cost_ratio > 1.5 or cost_ratio < 0.5:
                state["cost_variance_flag"] = f"Estimate differs {cost_ratio:.1f}x from historical average"
    
    # Original planning logic here...
    # plans = generate_plans(state)
    plans = [{"name": "Sample Plan", "steps": ["step1", "step2"]}]  # Placeholder
    state["plans"] = plans
    
    # ===== TRANSPARENCY LOGGING =====
    t_logger.log_decision(
        agent_type="water",
        node_name="planner",
        decision=f"generated_{len(plans)}_plans",
        context={
            "request": request,
            "historical_context": state.get("historical_context", {}),
            "plans_count": len(plans)
        },
        rationale=f"Generated {len(plans)} plan(s) based on request and {len(similar_decisions)} similar historical cases",
        confidence=state.get("confidence", 0.8),
        cost_impact=state.get("estimated_cost", 0),
        affected_citizens=state.get("affected_population", 0),
        metadata={
            "used_rag": len(similar_decisions) > 0,
            "historical_cases": len(similar_decisions)
        }
    )
    
    return state


# ==============================================================================
# EXAMPLE 3: Feasibility Evaluator with Detailed Logging
# ==============================================================================

def feasibility_evaluator_with_logging(state: DepartmentState) -> DepartmentState:
    """
    Feasibility evaluator that logs detailed feasibility analysis
    """
    plans = state.get("plans", [])
    observations = state.get("observations", [])
    context = state.get("context", {})
    
    # Original feasibility logic
    workers_available = context.get("workers", {}).get("available", 0)
    workers_needed = 5  # Simplified
    budget_available = context.get("budget", {}).get("available", 0)
    estimated_cost = state.get("estimated_cost", 0)
    
    reasons = []
    if workers_available < workers_needed:
        reasons.append(f"Insufficient workers: need {workers_needed}, have {workers_available}")
    if budget_available < estimated_cost:
        reasons.append(f"Insufficient budget: need Rs.{estimated_cost:,}, have Rs.{budget_available:,}")
    
    feasible = len(reasons) == 0
    state["feasible"] = feasible
    state["feasibility_reason"] = "; ".join(reasons) if reasons else "All resources available"
    
    # ===== TRANSPARENCY LOGGING =====
    t_logger.log_decision(
        agent_type="water",
        node_name="feasibility_evaluator",
        decision="feasible" if feasible else "not_feasible",
        context={
            "workers_available": workers_available,
            "workers_needed": workers_needed,
            "budget_available": budget_available,
            "estimated_cost": estimated_cost,
            "constraints_checked": ["workforce", "budget", "schedule"]
        },
        rationale=state["feasibility_reason"],
        confidence=1.0 if feasible else 0.0,  # Binary feasibility
        cost_impact=estimated_cost,
        affected_citizens=state.get("affected_population", 0),
        metadata={
            "blocking_constraints": reasons if not feasible else [],
            "plans_evaluated": len(plans)
        }
    )
    
    return state


# ==============================================================================
# EXAMPLE 4: Policy Validator with Policy Tracking
# ==============================================================================

def policy_validator_with_logging(state: DepartmentState) -> DepartmentState:
    """
    Policy validator that tracks which policies were checked
    """
    request = state.get("input_event", {})
    request_type = request.get("type", "")
    location = request.get("location", "")
    
    # Simulate policy checks (replace with actual logic)
    policies_checked = [
        "water_quality_standards_2024",
        "environmental_impact_mandate",
        "citizen_consultation_requirement"
    ]
    
    violations = []
    
    # Check each policy
    if request_type == "expansion" and "consultation" not in request:
        violations.append("Missing citizen consultation for expansion project")
    
    policy_ok = len(violations) == 0
    state["policy_ok"] = policy_ok
    state["policy_violations"] = violations
    state["applicable_policies"] = policies_checked
    
    # ===== TRANSPARENCY LOGGING =====
    t_logger.log_decision(
        agent_type="water",
        node_name="policy_validator",
        decision="compliant" if policy_ok else "violation",
        context={
            "request_type": request_type,
            "location": location,
            "policies_checked": policies_checked,
            "violations_found": violations
        },
        rationale="All policies satisfied" if policy_ok else f"Policy violations: {', '.join(violations)}",
        confidence=1.0 if policy_ok else 0.0,
        cost_impact=state.get("estimated_cost", 0),
        affected_citizens=state.get("affected_population", 0),
        policy_references=policies_checked,
        metadata={
            "total_policies_checked": len(policies_checked),
            "violations_count": len(violations)
        }
    )
    
    return state


# ==============================================================================
# EXAMPLE 5: Simplified Node Logging
# ==============================================================================

def any_node_simple_logging(state: DepartmentState) -> DepartmentState:
    """
    For simpler nodes, use log_node_execution() for quick logging
    """
    # Your node logic
    result = do_some_work(state)
    
    # Simple logging
    t_logger.log_node_execution(
        agent_type="water",
        node_name="my_node",
        state=state,
        action="work_completed",
        result=result
    )
    
    return state


def do_some_work(state):
    """Placeholder for actual work"""
    return {"status": "success"}


# ==============================================================================
# USAGE EXAMPLE
# ==============================================================================

def example_usage():
    """Example of running nodes with transparency logging"""
    
    # Simulate a request
    state = {
        "input_event": {
            "type": "emergency_repair",
            "location": "Zone-A",
            "reason": "Pipeline burst",
            "priority": "emergency"
        },
        "confidence": 0.92,
        "estimated_cost": 650000,
        "affected_population": 60000,
        "feasible": True,
        "policy_ok": True,
        "context": {
            "workers": {"available": 10},
            "budget": {"available": 1000000}
        }
    }
    
    print("="*70)
    print("WATER AGENT WITH TRANSPARENCY LOGGING")
    print("="*70)
    
    # Run nodes with logging
    print("\n1. Running planner with RAG context...")
    state = planner_with_rag_context(state)
    
    print("\n2. Running feasibility evaluator...")
    state = feasibility_evaluator_with_logging(state)
    
    print("\n3. Running policy validator...")
    state = policy_validator_with_logging(state)
    
    print("\n4. Running decision router...")
    state = decision_router_with_logging(state)
    
    print("\n5. Final Decision:", state["decision"])
    
    # Search for what we just logged
    print("\n" + "="*70)
    print("SEARCHING TRANSPARENCY LOGS")
    print("="*70)
    
    results = t_logger.search_decisions(
        query="emergency repair Zone-A",
        n_results=5
    )
    
    print(f"\nFound {len(results)} logged decisions:")
    for i, result in enumerate(results, 1):
        meta = result['metadata']
        print(f"\n{i}. {meta['node_name'].upper()}")
        print(f"   Decision: {meta['decision']}")
        print(f"   Rationale: {meta['rationale'][:80]}...")
        print(f"   Confidence: {meta['confidence']:.0%}")
    
    # Generate transparency report
    print("\n" + "="*70)
    print("TRANSPARENCY REPORT")
    print("="*70)
    
    report = t_logger.generate_transparency_report(agent_type="water")
    print(f"\nWater Department Statistics:")
    print(f"  Total Decisions: {report['statistics']['total_decisions']}")
    print(f"  Total Cost: Rs.{report['statistics']['total_cost_impact']:,.0f}")
    print(f"  Avg Confidence: {report['statistics']['average_confidence']:.0%}")
    print(f"  Citizens Affected: {report['statistics']['total_citizens_affected']:,}")
    
    t_logger.close()


if __name__ == "__main__":
    example_usage()
