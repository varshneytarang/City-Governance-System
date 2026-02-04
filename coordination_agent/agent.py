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
from .agent_dispatcher import AgentDispatcher

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
        self.agent_dispatcher = AgentDispatcher()  # NEW: Enable calling other agents
        
        # Create coordination tables
        self.db.create_coordination_tables_if_not_exists()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
        
        logger.info("✓ Coordination Agent initialized (with agent dispatcher)")
    
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
    
    def check_plan_conflicts(
        self, 
        agent_id: str,
        agent_type: str,
        plan: Dict[str, Any],
        location: str,
        resources_needed: List[str],
        estimated_cost: float,
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Real-time conflict check during agent workflow (PROACTIVE)
        
        Called by agents during planning phase to check for conflicts
        BEFORE executing the plan.
        
        Args:
            agent_id: Identifier of requesting agent
            agent_type: Type of agent (water, engineering, etc.)
            plan: The proposed plan
            location: Where plan will be executed
            resources_needed: List of required resources
            estimated_cost: Cost estimate
            priority: Request priority
        
        Returns:
            {
                "has_conflicts": bool,
                "conflict_types": List[str],
                "recommendations": List[str],
                "should_proceed": bool,
                "alternative_suggestions": List[str],
                "requires_human": bool
            }
        """
        logger.info(f"\n🔍 PROACTIVE CONFLICT CHECK - {agent_type.upper()}")
        logger.info(f"   Location: {location}")
        logger.info(f"   Resources: {', '.join(resources_needed)}")
        
        # Query active decisions from database for same location/resources
        active_decisions = self._get_active_decisions_for_location(location)
        
        conflicts = []
        conflict_types = []
        recommendations = []
        alternative_suggestions = []
        
        # Check for resource conflicts
        for active in active_decisions:
            if active.get("agent_type") != agent_type:
                # Different agent working in same area
                active_resources = active.get("resources_needed", [])
                overlapping = set(resources_needed) & set(active_resources)
                
                if overlapping:
                    conflicts.append({
                        "type": "resource_conflict",
                        "with_agent": active.get("agent_type"),
                        "resources": list(overlapping),
                        "severity": "high"
                    })
                    conflict_types.append("resource_conflict")
                    recommendations.append(
                        f"Resource conflict with {active['agent_type']} dept. "
                        f"Consider alternative timing or resources."
                    )
        
        # Check for location conflicts
        for active in active_decisions:
            if active.get("location") == location and active.get("agent_type") != agent_type:
                conflicts.append({
                    "type": "location_conflict",
                    "with_agent": active.get("agent_type"),
                    "location": location,
                    "severity": "medium"
                })
                if "location_conflict" not in conflict_types:
                    conflict_types.append("location_conflict")
                    recommendations.append(
                        f"Multiple departments working in {location}. "
                        f"Coordinate timing with {active['agent_type']}."
                    )
        
        # Check for budget conflicts
        total_active_cost = sum(d.get("estimated_cost", 0) for d in active_decisions)
        if total_active_cost + estimated_cost > 1000000:  # 10 lakh threshold
            conflicts.append({
                "type": "budget_conflict",
                "total_cost": total_active_cost + estimated_cost,
                "severity": "high"
            })
            conflict_types.append("budget_conflict")
            recommendations.append(
                f"Combined budget exceeds threshold. Consider phasing the work."
            )
        
        # Determine if agent should proceed
        has_conflicts = len(conflicts) > 0
        high_severity_conflicts = [c for c in conflicts if c.get("severity") == "high"]
        should_proceed = len(high_severity_conflicts) == 0
        requires_human = len(high_severity_conflicts) > 0 or len(conflicts) >= 3
        
        # Generate alternatives if conflicts found
        if has_conflicts:
            alternative_suggestions.append(f"Delay start by 2-3 days")
            alternative_suggestions.append(f"Use alternative location near {location}")
            alternative_suggestions.append(f"Reduce scope to minimize resource needs")
        
        result = {
            "has_conflicts": has_conflicts,
            "conflicts": conflicts,
            "conflict_types": list(set(conflict_types)),
            "recommendations": recommendations,
            "should_proceed": should_proceed,
            "alternative_suggestions": alternative_suggestions,
            "requires_human": requires_human,
            "checked_at": datetime.now().isoformat()
        }
        
        logger.info(f"   Conflicts Found: {len(conflicts)}")
        logger.info(f"   Should Proceed: {should_proceed}")
        logger.info(f"   Requires Human: {requires_human}")
        
        return result
    
    def _get_active_decisions_for_location(self, location: str) -> List[Dict[str, Any]]:
        """Get recent active decisions for a location from database"""
        try:
            # Query recent decisions (last 24 hours)
            query = """
                SELECT agent_type, location, resources_needed, estimated_cost, 
                       decision, created_at
                FROM coordination_decisions
                WHERE location = %s
                  AND created_at > NOW() - INTERVAL '24 hours'
                  AND decision IN ('approved', 'in_progress')
                ORDER BY created_at DESC
                LIMIT 10
            """
            results = self.db.db.execute_query(query, (location,))
            return results if results else []
        except Exception as e:
            logger.warning(f"Could not query active decisions: {e}")
            return []
    
    def close(self):
        """Close database connections and agent dispatcher"""
        if hasattr(self.db, 'db'):
            self.db.db.close()
        if hasattr(self, 'agent_dispatcher'):
            self.agent_dispatcher.close_all_agents()
        logger.info("Coordination Agent closed")
    
    # ========================================================================
    # Agent Query Methods - NEW: Coordinator can call other agents
    # ========================================================================
    
    def query_agent(
        self,
        agent_type: str,
        request: Dict[str, Any],
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query a specific agent for information during coordination
        
        Args:
            agent_type: Type of agent to query (water, engineering, fire, etc.)
            request: Request dict to send to the agent
            reason: Optional reason for the query (for logging/transparency)
            
        Returns:
            Agent's response dict
            
        Example:
            # During conflict resolution, ask Water agent about capacity
            response = self.query_agent("water", {
                "type": "capacity_query",
                "location": "Downtown",
                "query": "What is current water pressure and availability?"
            }, reason="Checking water capacity for conflict resolution")
        """
        if reason:
            logger.info(f"🔍 Coordinator querying {agent_type} agent: {reason}")
        
        return self.agent_dispatcher.query_agent(agent_type, request)
    
    def query_multiple_agents(
        self,
        queries: Dict[str, Dict[str, Any]],
        reason: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Query multiple agents simultaneously
        
        Args:
            queries: Dict mapping agent_type to request dict
            reason: Optional reason for the queries
            
        Returns:
            Dict mapping agent_type to response dict
            
        Example:
            # Ask both Water and Engineering about Downtown work
            responses = self.query_multiple_agents({
                "water": {"type": "capacity_query", "location": "Downtown"},
                "engineering": {"type": "project_planning", "location": "Downtown"}
            }, reason="Gathering context for conflict resolution")
        """
        if reason:
            logger.info(f"🔍 Coordinator querying multiple agents: {reason}")
        
        return self.agent_dispatcher.query_multiple_agents(queries)
    
    def get_agent_status(self, agent_type: str) -> Dict[str, Any]:
        """
        Get status information about an agent
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Dict with agent metadata and availability
        """
        return self.agent_dispatcher.get_agent_info(agent_type)
    
    def gather_agent_context(
        self,
        agent_types: List[str],
        location: str,
        context_type: str = "capacity_query"
    ) -> Dict[str, Any]:
        """
        Gather context from multiple agents about a specific location
        
        This is useful during conflict resolution to understand what
        each department is doing or planning in a location.
        
        Args:
            agent_types: List of agent types to query
            location: Location to ask about
            context_type: Type of query (capacity_query, status_check, etc.)
            
        Returns:
            Dict with responses from all agents
            
        Example:
            # During conflict in Downtown, ask all agents about their work
            context = self.gather_agent_context(
                ["water", "engineering", "fire"],
                "Downtown",
                "capacity_query"
            )
        """
        logger.info(f"📊 Gathering context from {len(agent_types)} agents for {location}")
        
        queries = {}
        for agent_type in agent_types:
            queries[agent_type] = {
                "type": context_type,
                "location": location,
                "query": f"What is your current status and planned work in {location}?"
            }
        
        responses = self.query_multiple_agents(
            queries,
            reason=f"Gathering context for {location}"
        )
        
        # Summarize responses
        summary = {
            "location": location,
            "agents_queried": agent_types,
            "responses": responses,
            "successful_responses": sum(1 for r in responses.values() if r.get("success")),
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
