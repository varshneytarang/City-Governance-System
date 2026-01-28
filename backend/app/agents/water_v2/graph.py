"""
LangGraph Workflow Definition
PHASE 15: Orchestration with loops and conditional routing
"""

from typing import Literal
from datetime import datetime
import logging

from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from .state import DepartmentState
from .agent import WaterDepartmentAgent

logger = logging.getLogger(__name__)


def create_water_department_agent(db: AsyncSession) -> StateGraph:
    """
    Create professional water department agent workflow
    
    Flow:
        Input → Context → Intent/Risk → Goal → Plan → Tools → Observe 
        → Feasibility → [Loop if not feasible] → Policy → Memory 
        → Confidence → Route → Output
    """
    
    # Initialize agent
    agent = WaterDepartmentAgent(db)
    
    # Create state graph
    workflow = StateGraph(DepartmentState)
    
    # ========== ADD ALL NODES ==========
    
    # Phase 3: Context Loading
    workflow.add_node("load_context", agent.load_context)
    
    # Phase 4: Intent & Risk Analysis
    workflow.add_node("analyze_intent_risk", agent.analyze_intent_and_risk)
    
    # Phase 5: Goal Setting
    workflow.add_node("set_goal", agent.set_goal)
    
    # Phase 6: Planning (LLM)
    workflow.add_node("generate_plan", agent.generate_plan)
    
    # Phase 7: Tool Execution
    workflow.add_node("execute_tools", agent.execute_tools)
    
    # Phase 8: Observation
    workflow.add_node("observe_results", agent.observe_results)
    
    # Phase 9: Feasibility Evaluation (CRITICAL)
    workflow.add_node("evaluate_feasibility", agent.evaluate_feasibility)
    
    # Phase 10: Policy Validation
    workflow.add_node("validate_policy", agent.validate_policy)
    
    # Phase 11: Memory Logging
    workflow.add_node("log_memory", agent.log_to_memory)
    
    # Phase 12: Confidence Estimation
    workflow.add_node("estimate_confidence", agent.estimate_confidence)
    
    # Phase 13: Decision Routing
    workflow.add_node("route_decision", agent.route_decision)
    
    # Phase 14: Output Generation
    workflow.add_node("generate_output", agent.generate_output)
    
    # ========== DEFINE FLOW ==========
    
    # Entry point
    workflow.set_entry_point("load_context")
    
    # Linear flow until feasibility check
    workflow.add_edge("load_context", "analyze_intent_risk")
    workflow.add_edge("analyze_intent_risk", "set_goal")
    workflow.add_edge("set_goal", "generate_plan")
    workflow.add_edge("generate_plan", "execute_tools")
    workflow.add_edge("execute_tools", "observe_results")
    workflow.add_edge("observe_results", "evaluate_feasibility")
    
    # ========== CRITICAL: LOOP CONTROL ==========
    
    def should_retry_plan(state: DepartmentState) -> Literal["retry_plan", "continue_to_policy"]:
        """
        Decide if we should try another plan alternative
        
        Retry if:
        - Current plan not feasible
        - Haven't exceeded max attempts
        - Still have alternative plans to try
        """
        if state.get("escalate"):
            # Already decided to escalate (e.g., critical risk)
            return "continue_to_policy"
        
        if state["feasible"]:
            # Current plan works!
            return "continue_to_policy"
        
        # Not feasible - check if we can retry
        attempts = state["attempts"]
        max_attempts = state["max_attempts"]
        plan_index = state["current_plan_index"]
        total_plans = len(state["plan"])
        
        if attempts >= max_attempts:
            logger.warning(f"⚠️ Max attempts ({max_attempts}) reached")
            return "continue_to_policy"
        
        if plan_index + 1 >= total_plans:
            logger.warning(f"⚠️ No more plan alternatives")
            return "continue_to_policy"
        
        # We can retry!
        logger.info(f"🔄 Retrying with alternative plan ({plan_index + 1}/{total_plans})")
        return "retry_plan"
    
    workflow.add_conditional_edges(
        "evaluate_feasibility",
        should_retry_plan,
        {
            "retry_plan": "retry_plan_node",
            "continue_to_policy": "validate_policy",
        }
    )
    
    # Retry node: increment attempt counter and try next plan
    async def retry_plan_node(state: DepartmentState) -> DepartmentState:
        """Prepare for retry with next plan alternative"""
        state["attempts"] += 1
        state["current_plan_index"] += 1
        logger.info(f"🔄 Attempt {state['attempts']}: Trying plan alternative {state['current_plan_index']}")
        return state
    
    workflow.add_node("retry_plan_node", retry_plan_node)
    
    # Loop back to tool execution with new plan
    workflow.add_edge("retry_plan_node", "execute_tools")
    
    # ========== CONTINUE FLOW AFTER FEASIBILITY ==========
    
    workflow.add_edge("validate_policy", "log_memory")
    workflow.add_edge("log_memory", "estimate_confidence")
    workflow.add_edge("estimate_confidence", "route_decision")
    workflow.add_edge("route_decision", "generate_output")
    
    # ========== END ==========
    
    workflow.add_edge("generate_output", END)
    
    # Compile
    return workflow.compile()


# ========== HELPER: Initialize State ==========

def initialize_state(input_event: dict) -> DepartmentState:
    """
    Create initial state from input event
    """
    return DepartmentState(
        # Input
        input_event=input_event,
        
        # Context (to be loaded)
        context={},
        
        # Intent & Risk (to be determined)
        intent="",
        risk_level="low",
        
        # Goal (to be set)
        goal="",
        
        # Planning (to be generated)
        plan=[],
        current_plan_index=0,
        
        # Tool execution (to be filled)
        tool_results={},
        observations={},
        
        # Feasibility (to be evaluated)
        feasible=False,
        feasibility_reason="",
        
        # Policy (to be validated)
        policy_ok=False,
        policy_violations=[],
        
        # Memory (to be logged)
        decision_id=None,
        
        # Confidence (to be calculated)
        confidence=0.0,
        confidence_factors={},
        
        # Output (to be generated)
        response={},
        escalate=False,
        escalation_reason=None,
        
        # Loop control
        attempts=0,
        max_attempts=3,
        
        # Metadata
        timestamp=datetime.now().isoformat(),
        processing_time_ms=None,
        error=None,
    )


# ========== MAIN ENTRY POINT ==========

async def process_request(db: AsyncSession, input_event: dict) -> dict:
    """
    Main entry point for department agent
    
    Args:
        db: Database session
        input_event: Structured request
        
    Returns:
        Agent response dictionary
    """
    logger.info("=" * 60)
    logger.info("🚀 WATER DEPARTMENT AGENT - Processing Request")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    # Create workflow
    workflow = create_water_department_agent(db)
    
    # Initialize state
    initial_state = initialize_state(input_event)
    
    # Execute workflow
    try:
        final_state = await workflow.ainvoke(initial_state)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        final_state["processing_time_ms"] = processing_time
        
        logger.info("=" * 60)
        logger.info(f"✅ COMPLETE - Decision: {final_state['response']['decision']}")
        logger.info(f"⏱️  Processing time: {processing_time:.0f}ms")
        logger.info("=" * 60)
        
        return final_state["response"]
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}")
        return {
            "decision": "error",
            "reasoning": f"Internal error: {str(e)}",
            "confidence": 0.0,
            "escalation_reason": "System error - requires manual intervention",
        }


# Alias for backwards compatibility
create_workflow = create_water_department_agent

