"""
Fire Department Agent - Main Orchestration

This implements a professional agentic system that:
- understands emergency/operational requests
- reasons internally
- simulates response options
- validates feasibility & policy
- produces recommendations or escalates

It does NOT execute real-world actions. It only advises.
"""

import logging
from datetime import datetime
from typing import Dict, Optional
from langgraph.graph import StateGraph, START, END

from .state import DepartmentState
from .database import FireDepartmentQueries
from .config import settings

# Reuse database connection from water_agent
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from water_agent.database import DatabaseConnection

from .nodes.context_loader import load_context
from .nodes.intent_analyzer import analyze_intent
from .nodes.goal_setter import set_goals
from .nodes.planner import plan_actions
from .nodes.tool_executor import execute_tools
from .nodes.observer import observer_node
from .nodes.feasibility_evaluator import feasibility_evaluator_node
from .nodes.policy_validator import policy_validator_node
from .nodes.memory_logger import memory_logger_node
from .nodes.confidence_estimator import confidence_estimator_node
from .nodes.decision_router import decision_router_node
from .nodes.output_generator import output_generator_node

logger = logging.getLogger(__name__)


class FireDepartmentAgent:
    """
    Fire Department Agent - Bounded Autonomous Decision Unit
    
    Architecture:
    Input Event → Context Loader → Intent Analysis → Goal Setter →
    Planner (LLM) → Tool Execution → Observe → Feasibility (loop) →
    Policy Validation → Memory Logger → Confidence → Decision Router →
    Output Generation → End
    """
    
    def __init__(self):
        """Initialize agent"""
        self.db = DatabaseConnection()
        self.queries = FireDepartmentQueries(self.db)
        self.graph = self._build_graph()
        self.agent_version = "1.0"
        
        logger.info("✓ Fire Department Agent initialized")
    
    def _build_graph(self):
        """Build LangGraph workflow"""
        
        logger.info("🔨 Building agent workflow graph...")
        
        builder = StateGraph(DepartmentState)
        
        # Add nodes
        logger.info("  → Adding context loader")
        builder.add_node("context_loader", load_context)
        
        logger.info("  → Adding intent analyzer")
        builder.add_node("intent_analyzer", analyze_intent)
        
        logger.info("  → Adding goal setter")
        builder.add_node("goal_setter", set_goals)
        
        logger.info("  → Adding planner")
        builder.add_node("planner", plan_actions)
        
        logger.info("  → Adding tool executor")
        builder.add_node("tool_executor", execute_tools)
        
        logger.info("  → Adding observer")
        builder.add_node("observer", observer_node)
        
        logger.info("  → Adding feasibility evaluator")
        builder.add_node("feasibility_evaluator", feasibility_evaluator_node)
        
        logger.info("  → Adding policy validator")
        builder.add_node("policy_validator", policy_validator_node)
        
        logger.info("  → Adding memory logger")
        builder.add_node("memory_logger", lambda state: memory_logger_node(state, self.queries))
        
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
        
        # Planner → tool executor
        builder.add_edge("planner", "tool_executor")
        
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
            "type": "emergency_response",
            "from": "911 Dispatch",
            "location": "Zone-1, Main Street",
            "zone": "Zone-1",
            "incident_type": "structure_fire",
            "priority": "critical",
            "casualties_reported": 0,
            "reason": "Residential building fire, 2nd floor"
        }
        """
        
        logger.info("=" * 60)
        logger.info("🚒 FIRE DEPARTMENT AGENT - NEW DECISION")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Validate input
            self._validate_input(request)
            
            # Initialize state
            initial_state: DepartmentState = {
                "request": request,
                "context": {},
                "analysis": {},
                "goals": {},
                "plan": {},
                "tool_results": [],
                "execution_summary": {},
                "observations": {},
                "feasibility": {},
                "policy_check": {},
                "decision_log": {},
                "confidence": 0.0,
                "recommendation": {},
                "response": {},
                "escalate": False,
                "retry_needed": False,
                "attempts": 0,
                "phase": "initialized"
            }
            
            # Run graph
            logger.info(f"📋 Request type: {request.get('type')}")
            logger.info(f"🔥 Incident type: {request.get('incident_type', 'N/A')}")
            logger.info(f"📍 Location: {request.get('location', 'N/A')}")
            logger.info(f"⚠️  Priority: {request.get('priority', 'medium')}")
            
            result_state = self.graph.invoke(initial_state)
            
            # Calculate execution time
            end_time = datetime.now()
            execution_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Extract response
            response = result_state.get("response", {})
            response["execution_time_ms"] = execution_ms
            
            logger.info("=" * 60)
            logger.info(f"✓ DECISION: {response.get('decision', 'unknown').upper()}")
            logger.info(f"  Confidence: {result_state.get('confidence', 0):.2%}")
            logger.info(f"  Execution time: {execution_ms}ms")
            logger.info("=" * 60)
            
            return response
        
        except Exception as e:
            logger.error(f"✗ Agent error: {e}", exc_info=True)
            return {
                "decision": "escalate",
                "reasoning": f"Agent processing error: {str(e)}",
                "error": str(e),
                "execution_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }
    
    def _validate_input(self, request: Dict) -> None:
        """Validate input request structure"""
        
        required_fields = ["type", "location"]
        missing = [f for f in required_fields if f not in request]
        
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        valid_types = [
            "emergency_response",
            "station_deployment",
            "equipment_maintenance",
            "training_request",
            "readiness_assessment",
            "hazmat_incident",
            "inspection_request"
        ]
        
        if request.get("type") not in valid_types:
            raise ValueError(f"Invalid request type. Must be one of: {valid_types}")
    
    def visualize(self, output_file: str = "fire_agent_graph.png") -> str:
        """
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
        if hasattr(self, 'db'):
            self.db.close()
        logger.info("✓ Agent closed")
