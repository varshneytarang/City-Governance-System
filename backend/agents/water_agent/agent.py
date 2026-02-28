"""
Water Department Agent - Main Orchestration

This implements a professional agentic system that:
- understands requests
- reasons internally
- simulates options
- validates feasibility & policy
- produces recommendations or escalates

It does NOT execute real-world actions. It only advises.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Optional
from langgraph.graph import StateGraph, START, END

from .state import DepartmentState
from .database import get_db, get_queries
from .tools import create_tools
from .config import settings
from .nodes import (
    context_loader_node,
    intent_analyzer_node,
    goal_setter_node,
    planner_node,
    coordination_checkpoint_node,
    tool_executor_node,
    observer_node,
    feasibility_evaluator_node,
    policy_validator_node,
    memory_logger_node,
    confidence_estimator_node,
    decision_router_node,
    output_generator_node
)

logger = logging.getLogger(__name__)


class WaterDepartmentAgent:
    """
    Water Department Agent - Bounded Autonomous Decision Unit
    
    Architecture:
    Input Event → Context Loader → Intent Analysis → Goal Setter →
    Planner (LLM) → Tool Execution → Observe → Feasibility (loop) →
    Policy Validation → Memory Logger → Confidence → Decision Router →
    Output Generation → End
    """
    
    def __init__(self):
        """Initialize agent"""
        self.db = get_db()
        self.queries = get_queries(self.db)
        self.tools = create_tools(self.db, self.queries)
        self.graph = self._build_graph()
        self.agent_version = "1.0"
        
        logger.info("✓ Water Department Agent initialized")
    
    def _build_graph(self):
        """Build LangGraph workflow"""
        
        logger.info("🔨 Building agent workflow graph...")
        
        builder = StateGraph(DepartmentState)
        
        # Add nodes
        logger.info("  → Adding context loader")
        builder.add_node(
            "context_loader",
            lambda state: context_loader_node(state, self.queries)
        )
        
        logger.info("  → Adding intent analyzer")
        builder.add_node(
            "intent_analyzer",
            lambda state: intent_analyzer_node(state, self.tools)
        )
        
        logger.info("  → Adding goal setter")
        builder.add_node("goal_setter", goal_setter_node)
        
        logger.info("  → Adding planner")
        builder.add_node("planner", planner_node)
        
        logger.info("  → Adding coordination checkpoint (PROACTIVE)")
        builder.add_node("coordination_checkpoint", coordination_checkpoint_node)
        
        logger.info("  → Adding tool executor")
        builder.add_node(
            "tool_executor",
            lambda state: tool_executor_node(state, self.tools)
        )
        
        logger.info("  → Adding observer")
        builder.add_node("observer", observer_node)
        
        logger.info("  → Adding feasibility evaluator")
        builder.add_node("feasibility_evaluator", feasibility_evaluator_node)
        
        logger.info("  → Adding policy validator")
        builder.add_node("policy_validator", policy_validator_node)
        
        logger.info("  → Adding memory logger")
        builder.add_node(
            "memory_logger",
            lambda state: memory_logger_node(state, self.queries)
        )
        
        logger.info("  → Adding confidence estimator")
        builder.add_node("confidence_estimator", confidence_estimator_node)
        
        logger.info("  → Adding decision router")
        builder.add_node("decision_router", decision_router_node)
        
        logger.info("  → Adding output generator")
        builder.add_node("output_generator", output_generator_node)
        
        # Define edges (workflow)
        logger.info("  → Wiring edges...")
        
        # Start → context loader
        builder.add_edge(START, "context_loader")
        
        # Context loader → intent analyzer
        builder.add_edge("context_loader", "intent_analyzer")
        
        # Intent analyzer: check for immediate escalation
        def should_escalate_intent(state: DepartmentState):
            if state.get("escalate"):
                return "output_generator"  # Skip to output if critical risk
            return "goal_setter"
        
        builder.add_conditional_edges(
            "intent_analyzer",
            should_escalate_intent,
            {
                "goal_setter": "goal_setter",
                "output_generator": "output_generator"
            }
        )
        
        # Goal setter → planner
        builder.add_edge("goal_setter", "planner")
        
        # Planner → coordination checkpoint (PROACTIVE CHECK)
        builder.add_edge("planner", "coordination_checkpoint")
        
        # Coordination checkpoint: decide next step based on conflicts
        def route_after_coordination(state: DepartmentState):
            # If escalating due to conflicts, skip to output
            if state.get("escalate"):
                return "output_generator"
            # If retry needed due to conflicts, go back to planner
            if state.get("retry_needed"):
                return "planner"
            # Otherwise proceed with plan
            return "tool_executor"
        
        builder.add_conditional_edges(
            "coordination_checkpoint",
            route_after_coordination,
            {
                "planner": "planner",
                "tool_executor": "tool_executor",
                "output_generator": "output_generator"
            }
        )
        
        # Tool executor → observer
        builder.add_edge("tool_executor", "observer")
        
        # Observer → feasibility evaluator
        builder.add_edge("observer", "feasibility_evaluator")
        
        # Feasibility evaluator: loop control
        def check_feasibility(state: DepartmentState):
            if state.get("retry_needed"):
                return "tool_executor"  # Retry with alternative plan
            return "policy_validator"
        
        builder.add_conditional_edges(
            "feasibility_evaluator",
            check_feasibility,
            {
                "tool_executor": "tool_executor",
                "policy_validator": "policy_validator"
            }
        )
        
        # Policy validator → memory logger
        builder.add_edge("policy_validator", "memory_logger")
        
        # Memory logger → confidence estimator
        builder.add_edge("memory_logger", "confidence_estimator")
        
        # Confidence estimator → decision router
        builder.add_edge("confidence_estimator", "decision_router")
        
        # Decision router → output generator
        builder.add_edge("decision_router", "output_generator")
        
        # Output generator → end
        builder.add_edge("output_generator", END)
        
        graph = builder.compile()
        logger.info("✓ Graph compiled successfully")
        
        return graph
    
    def decide(self, request: Dict) -> Dict:
        """
        Run the agent on a request.
        
        Input: structured request dict
        Output: recommendation or escalation
        
        Example request:
        {
            "type": "schedule_shift_request",
            "from": "Coordinator",
            "location": "Zone-1",
            "requested_shift_days": 2,
            "reason": "Joint underground work"
        }
        """
        
        print("=" * 60)
        print("🚀 WATER DEPARTMENT AGENT - NEW DECISION")
        print("=" * 60)
        print(f"📥 Request Type: {request.get('type', 'UNKNOWN')}")
        print(f"📍 Location: {request.get('location', 'N/A')}")
        print(f"📋 Full Request: {json.dumps(request, indent=2)}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Validate input
            print("\n🔍 Validating input...")
            self._validate_input(request)
            print("✅ Input validation passed")
            
            # Initialize state
            print("\n🔧 Initializing agent state...")
            initial_state: DepartmentState = {
                "input_event": request,
                "context": {},
                "intent": "",
                "risk_level": "low",
                "safety_concerns": [],
                "goal": "",
                "plan": {},
                "alternative_plans": [],
                "coordination_check": None,
                "coordination_approved": True,
                "coordination_recommendations": [],
                "tool_results": {},
                "observations": {},
                "feasible": False,
                "feasibility_reason": "",
                "feasibility_details": {},
                "policy_ok": False,
                "policy_violations": [],
                "decision_id": None,
                "confidence": 0.0,
                "confidence_factors": {},
                "response": {},
                "escalate": False,
                "escalation_reason": None,
                "attempts": 0,
                "max_attempts": settings.MAX_PLANNING_ATTEMPTS,
                "started_at": start_time,
                "completed_at": None,
                "agent_version": self.agent_version,
                "execution_time_ms": 0,
                "retry_needed": False
            }
            
            print("✅ State initialized successfully")
            print(f"📊 State keys: {list(initial_state.keys())}")
            
            # Run graph
            print("\n" + "="*60)
            print("🔄 EXECUTING WORKFLOW GRAPH...")
            print("="*60)
            print(f"📋 Request type: {request.get('type')}")
            print(f"📍 Location: {request.get('location', 'N/A')}")
            print(f"🔢 Max attempts: {settings.MAX_PLANNING_ATTEMPTS}")
            
            result_state = self.graph.invoke(initial_state)
            
            print("\n" + "="*60)
            print("✅ WORKFLOW COMPLETED")
            print("="*60)
            
            # Calculate execution time
            end_time = datetime.now()
            execution_ms = int((end_time - start_time).total_seconds() * 1000)
            
            print(f"⏱️  Total execution time: {execution_ms}ms")
            
            result_state["completed_at"] = end_time.isoformat()
            result_state["execution_time_ms"] = execution_ms
            # Convert started_at to string if present
            if "started_at" in result_state and isinstance(result_state["started_at"], datetime):
                result_state["started_at"] = result_state["started_at"].isoformat()
            
            # Extract response
            print("\n📦 Extracting final response...")
            response = result_state.get("response", {})
            
            print("\n" + "=" * 60)
            print("🎯 FINAL DECISION")
            print("=" * 60)
            print(f"✅ DECISION: {response.get('decision', 'unknown').upper()}")
            print(f"📊 Confidence: {result_state.get('confidence', 0):.2%}")
            print(f"⏱️  Execution time: {execution_ms}ms")
            print(f"📤 Response keys: {list(response.keys())}")
            print("=" * 60)
            
            return response
        
        except Exception as e:
            logger.error(f"✗ Agent error: {e}", exc_info=True)
            return {
                "decision": "escalate",
                "reason": f"Agent processing error: {str(e)}",
                "error": str(e),
                "execution_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
    
    def _validate_input(self, request: Dict) -> None:
        """Validate input request structure"""
        
        required_fields = ["type", "location"]
        missing = [f for f in required_fields if f not in request]
        
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        # Allow any request type - agent will handle all queries
    
    def visualize(self, output_file: str = "agent_graph.png") -> str:
        """
        PHASE 15: Visualization
        
        Generate Mermaid diagram of the agent workflow.
        """
        
        logger.info(f"🎨 Generating visualization: {output_file}")
        
        try:
            # Get Mermaid representation
            mermaid_code = self.graph.get_graph().draw_mermaid()
            
            logger.info("✓ Mermaid code generated")
            logger.debug(f"\n{mermaid_code}")
            
            return mermaid_code
        
        except Exception as e:
            logger.error(f"✗ Visualization error: {e}")
            return None
    
    def close(self):
        """Clean up resources"""
        self.db.close()
        logger.info("✓ Agent closed")
