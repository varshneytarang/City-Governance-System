"""
Coordination Agent - Main Orchestrator

Coordinates multi-agent workflows using hybrid decision system:
- Rule-based resolution for simple conflicts
- LLM-powered negotiation for complex conflicts  
- Human escalation for critical decisions

Workflow:
1. Receive decisions from multiple agents
2. Detect conflicts
3. Resolve using rules or LLM
4. Escalate to human if needed
5. Execute coordinated plan
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from langgraph.graph import StateGraph, END

from .state import CoordinationState, create_initial_state
from .config import CoordinationConfig
from .database import CoordinationQueries
from .engines import ConflictDetector, RuleEngine, LLMNegotiationEngine
from .human_interface import HumanInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoordinationAgent:
    """
    Coordination Agent for multi-agent workflow orchestration
    
    Uses hybrid decision system:
    - Simple conflicts → Rule-based resolution
    - Complex conflicts → LLM negotiation
    - Critical decisions → Human approval
    """
    
    def __init__(self):
        self.config = CoordinationConfig()
        self.config.validate()
        
        # Initialize components
        self.db = CoordinationQueries()
        self.conflict_detector = ConflictDetector()
        self.rule_engine = RuleEngine()
        self.llm_engine = LLMNegotiationEngine()
        self.human_interface = HumanInterface()
        
        # Create coordination tables
        self.db.create_coordination_tables_if_not_exists()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        logger.info("✓ Coordination Agent initialized")
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for coordination"""
        
        workflow = StateGraph(CoordinationState)
        
        # Add nodes
        workflow.add_node("detect_conflicts", self._detect_conflicts_node)
        workflow.add_node("assess_complexity", self._assess_complexity_node)
        workflow.add_node("resolve_with_rules", self._resolve_with_rules_node)
        workflow.add_node("resolve_with_llm", self._resolve_with_llm_node)
        workflow.add_node("check_human_approval", self._check_human_approval_node)
        workflow.add_node("escalate_to_human", self._escalate_to_human_node)
        workflow.add_node("finalize_decision", self._finalize_decision_node)
        
        # Set entry point
        workflow.set_entry_point("detect_conflicts")
        
        # Add edges
        workflow.add_edge("detect_conflicts", "assess_complexity")
        
        # Complexity routing
        workflow.add_conditional_edges(
            "assess_complexity",
            self._route_by_complexity,
            {
                "no_conflict": "finalize_decision",
                "simple": "resolve_with_rules",
                "complex": "resolve_with_llm"
            }
        )
        
        workflow.add_edge("resolve_with_rules", "check_human_approval")
        workflow.add_edge("resolve_with_llm", "check_human_approval")
        
        # Human approval routing
        workflow.add_conditional_edges(
            "check_human_approval",
            self._route_human_approval,
            {
                "approved": "finalize_decision",
                "needs_human": "escalate_to_human"
            }
        )
        
        workflow.add_edge("escalate_to_human", "finalize_decision")
        workflow.add_edge("finalize_decision", END)
        
        return workflow.compile()
    
    # ========================================================================
    # WORKFLOW NODES
    # ========================================================================
    
    def _detect_conflicts_node(self, state: CoordinationState) -> CoordinationState:
        """Node: Detect conflicts between agent decisions"""
        logger.info("→ Detecting conflicts...")
        state["workflow_log"].append("Detecting conflicts")
        
        state = self.conflict_detector.detect_all_conflicts(state)
        
        return state
    
    def _assess_complexity_node(self, state: CoordinationState) -> CoordinationState:
        """Node: Assess conflict complexity"""
        logger.info("→ Assessing complexity...")
        state["workflow_log"].append("Assessing complexity")
        
        if not state["has_conflicts"]:
            state["workflow_log"].append("No conflicts - proceeding directly")
            return state
        
        # Check if conflicts can be resolved with rules
        conflicts = state["conflicts_detected"]
        
        for conflict in conflicts:
            can_use_rules = self.rule_engine.can_resolve_with_rules(conflict)
            
            if can_use_rules:
                state["resolution_method"] = "rule"
            else:
                state["resolution_method"] = "llm"
                break  # If any conflict needs LLM, use LLM
        
        logger.info(f"   Resolution method: {state['resolution_method']}")
        state["workflow_log"].append(f"Resolution method: {state['resolution_method']}")
        
        return state
    
    def _resolve_with_rules_node(self, state: CoordinationState) -> CoordinationState:
        """Node: Resolve conflicts using rule-based engine"""
        logger.info("→ Resolving with rules...")
        state["workflow_log"].append("Applying rule-based resolution")
        
        conflicts = state["conflicts_detected"]
        agent_decisions = state["agent_decisions"]
        
        resolutions = []
        for conflict in conflicts:
            resolution = self.rule_engine.resolve_with_rules(conflict, agent_decisions)
            resolutions.append(resolution)
            logger.info(f"   ✓ Rule resolution: {resolution['decision']}")
        
        state["resolutions"] = resolutions
        
        return state
    
    def _resolve_with_llm_node(self, state: CoordinationState) -> CoordinationState:
        """Node: Resolve conflicts using LLM negotiation"""
        logger.info("→ Resolving with LLM...")
        state["workflow_log"].append("LLM-powered negotiation")
        
        conflicts = state["conflicts_detected"]
        agent_decisions = state["agent_decisions"]
        
        resolutions = []
        for conflict in conflicts:
            resolution = self.llm_engine.negotiate(conflict, agent_decisions)
            resolutions.append(resolution)
            logger.info(f"   ✓ LLM resolution: {resolution['decision']} (confidence: {resolution['confidence']})")
        
        state["resolutions"] = resolutions
        
        return state
    
    def _check_human_approval_node(self, state: CoordinationState) -> CoordinationState:
        """Node: Check if human approval needed"""
        logger.info("→ Checking human approval requirement...")
        
        resolutions = state["resolutions"]
        agent_decisions = state["agent_decisions"]
        
        # Calculate total cost
        total_cost = sum(d.get("estimated_cost", 0) for d in agent_decisions)
        
        # Check if any resolution requires human
        requires_human = False
        for resolution in resolutions:
            if self.human_interface.should_escalate_to_human(resolution, total_cost):
                requires_human = True
                break
        
        state["requires_human"] = requires_human
        
        if requires_human:
            logger.info("   ⚠ Human approval required")
            state["workflow_log"].append("Human approval required")
        else:
            logger.info("   ✓ Auto-approval criteria met")
            state["workflow_log"].append("Auto-approved")
        
        return state
    
    def _escalate_to_human_node(self, state: CoordinationState) -> CoordinationState:
        """Node: Escalate to human authority"""
        logger.info("→ Escalating to human...")
        state["workflow_log"].append("Escalating to human authority")
        
        # Get primary conflict (first one for simplicity)
        conflict = state["conflicts_detected"][0] if state["conflicts_detected"] else None
        resolution = state["resolutions"][0] if state["resolutions"] else None
        
        if conflict:
            # Create escalation request
            escalation = self.human_interface.create_escalation_request(
                conflict, resolution, state
            )
            
            # Notify human
            self.human_interface.notify_human_approver(escalation)
            
            # Wait for approval (mock for testing)
            human_decision = self.human_interface.wait_for_human_approval(escalation)
            
            # Apply human decision
            state = self.human_interface.apply_human_decision(
                escalation, human_decision, state
            )
        else:
            state["final_decision"] = "escalated"
            state["decision_rationale"] = "Escalated without specific conflict"
        
        return state
    
    def _finalize_decision_node(self, state: CoordinationState) -> CoordinationState:
        """Node: Finalize and log coordination decision"""
        logger.info("→ Finalizing decision...")
        state["workflow_log"].append("Finalizing decision")
        
        # Determine final decision if not set by human
        if not state.get("final_decision"):
            if not state["has_conflicts"]:
                state["final_decision"] = "approved"
                state["decision_rationale"] = "No conflicts - all agents aligned"
                state["execution_plan"] = {
                    "approved": [d["agent_id"] for d in state["agent_decisions"]],
                    "action": "execute_all"
                }
            elif state["resolutions"]:
                # Use first resolution's decision
                primary_resolution = state["resolutions"][0]
                state["final_decision"] = primary_resolution["decision"]
                state["decision_rationale"] = primary_resolution["rationale"]
                state["execution_plan"] = primary_resolution["execution_plan"]
        
        # Set completion time
        state["completed_at"] = datetime.now().isoformat()
        start_time = datetime.fromisoformat(state["started_at"])
        end_time = datetime.fromisoformat(state["completed_at"])
        state["total_processing_time"] = (end_time - start_time).total_seconds()
        
        # Log to database
        self._log_to_database(state)
        
        logger.info(f"✓ Coordination complete: {state['final_decision']}")
        logger.info(f"   Processing time: {state['total_processing_time']:.2f}s")
        
        return state
    
    # ========================================================================
    # ROUTING FUNCTIONS
    # ========================================================================
    
    def _route_by_complexity(self, state: CoordinationState) -> str:
        """Route based on conflict complexity"""
        if not state["has_conflicts"]:
            return "no_conflict"
        
        resolution_method = state.get("resolution_method", "llm")
        
        if resolution_method == "rule":
            return "simple"
        else:
            return "complex"
    
    def _route_human_approval(self, state: CoordinationState) -> str:
        """Route based on human approval requirement"""
        if state.get("requires_human", False):
            return "needs_human"
        else:
            return "approved"
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def coordinate(self, agent_decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main entry point: Coordinate multiple agent decisions
        
        Args:
            agent_decisions: List of decisions from different agents
        
        Returns:
            Coordination result with final decision and execution plan
        """
        logger.info("\n" + "="*70)
        logger.info("COORDINATION AGENT - NEW REQUEST")
        logger.info("="*70)
        logger.info(f"Coordinating {len(agent_decisions)} agent decision(s)")
        
        # Create initial state
        state = create_initial_state(agent_decisions)
        
        # Run workflow
        start_time = time.time()
        final_state = self.workflow.invoke(state)
        end_time = time.time()
        
        # Format result
        result = {
            "coordination_id": final_state["coordination_id"],
            "decision": final_state["final_decision"],
            "rationale": final_state["decision_rationale"],
            "execution_plan": final_state["execution_plan"],
            "conflicts_detected": len(final_state["conflicts_detected"]),
            "resolution_method": final_state.get("resolution_method", "none"),
            "requires_human": final_state["requires_human"],
            "processing_time": end_time - start_time,
            "workflow_log": final_state["workflow_log"]
        }
        
        logger.info(f"\n✓ Coordination completed: {result['decision']}")
        logger.info(f"  Conflicts: {result['conflicts_detected']}")
        logger.info(f"  Method: {result['resolution_method']}")
        logger.info(f"  Time: {result['processing_time']:.2f}s")
        logger.info("="*70 + "\n")
        
        return result
    
    def _log_to_database(self, state: CoordinationState):
        """Log coordination decision to database"""
        try:
            # Get primary conflict and resolution
            conflict = state["conflicts_detected"][0] if state["conflicts_detected"] else None
            resolution = state["resolutions"][0] if state["resolutions"] else None
            
            conflict_type = conflict["conflict_type"] if conflict else "none"
            agents_involved = [d["agent_id"] for d in state["agent_decisions"]]
            
            resolution_method = state.get("resolution_method", "none")
            llm_confidence = resolution.get("confidence") if resolution and resolution.get("method") == "llm" else None
            
            human_approver = None
            if state.get("human_escalation"):
                human_approver = state["human_escalation"].get("approver")
            
            self.db.log_coordination_decision(
                coordination_id=state["coordination_id"],
                conflict_type=conflict_type,
                agents_involved=agents_involved,
                resolution_method=resolution_method,
                resolution_rationale=state["decision_rationale"],
                llm_confidence=llm_confidence,
                human_approver=human_approver,
                outcome=state["final_decision"]
            )
            
        except Exception as e:
            logger.warning(f"Failed to log to database: {e}")
    
    def close(self):
        """Close database connections"""
        if hasattr(self.db, 'db'):
            self.db.db.close()
        logger.info("Coordination Agent closed")
