"""
Rule-Based Resolution Engine

Applies deterministic rules to resolve simple conflicts:
- Emergency override
- Budget priority allocation
- FIFO resource allocation
- Sequential dependency ordering
- Monsoon restrictions
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..state import Conflict, Resolution, CoordinationState, AgentDecision
from ..config import CoordinationConfig

logger = logging.getLogger(__name__)


class RuleEngine:
    """Rule-based conflict resolution for simple, deterministic conflicts"""
    
    def __init__(self):
        self.config = CoordinationConfig()
    
    def can_resolve_with_rules(self, conflict: Conflict) -> bool:
        """
        Determine if conflict can be resolved with rules
        
        Rule-based if:
        - Complexity score < threshold
        - Conflict type has clear rules
        - No multi-criteria trade-offs
        """
        if conflict["complexity_score"] >= self.config.COMPLEXITY_THRESHOLD:
            return False
        
        # These conflict types have clear rules
        rule_resolvable_types = ["resource", "policy", "timing"]
        if conflict["conflict_type"] in rule_resolvable_types:
            return True
        
        # Budget and location conflicts may need LLM
        if conflict["conflict_type"] in ["budget", "location"]:
            # Simple if only 2 agents and clear priority difference
            if len(conflict["agents_involved"]) == 2:
                return True
        
        return False
    
    def resolve_with_rules(
        self,
        conflict: Conflict,
        agent_decisions: List[AgentDecision]
    ) -> Resolution:
        """
        Apply rule-based resolution
        
        Returns Resolution with execution plan
        """
        conflict_type = conflict["conflict_type"]
        
        # Route to appropriate rule handler
        if conflict_type == "resource":
            return self._resolve_resource_conflict(conflict, agent_decisions)
        elif conflict_type == "policy":
            return self._resolve_policy_conflict(conflict, agent_decisions)
        elif conflict_type == "timing":
            return self._resolve_timing_conflict(conflict, agent_decisions)
        elif conflict_type == "budget":
            return self._resolve_budget_conflict(conflict, agent_decisions)
        elif conflict_type == "location":
            return self._resolve_location_conflict(conflict, agent_decisions)
        else:
            # Fallback: escalate
            return self._create_escalation_resolution(conflict)
    
    def _resolve_resource_conflict(
        self,
        conflict: Conflict,
        agent_decisions: List[AgentDecision]
    ) -> Resolution:
        """
        Resolve resource conflicts using priority rules
        
        Rules:
        1. Emergency override (highest priority)
        2. Priority level ordering
        3. FIFO when equal priority
        """
        agents_involved = conflict["agents_involved"]
        decisions = [d for d in agent_decisions if d["agent_id"] in agents_involved]
        
        # Rule 1: Emergency override
        emergency_decisions = [d for d in decisions if d["priority"] == "emergency"]
        if emergency_decisions:
            winner = emergency_decisions[0]
            losers = [d for d in decisions if d != winner]
            
            return self._create_resolution(
                conflict=conflict,
                decision="approve_partial",
                rationale=f"Emergency override: {winner['agent_id']} gets priority",
                execution_plan={
                    "approved": [winner["agent_id"]],
                    "queued": [d["agent_id"] for d in losers],
                    "action": "allocate_resources_to_emergency"
                },
                confidence=0.95,
                requires_human=False
            )
        
        # Rule 2: Priority-based allocation
        decisions_sorted = sorted(
            decisions,
            key=lambda d: self.config.PRIORITY_LEVELS.get(d["priority"], 0),
            reverse=True
        )
        
        # Rule 3: FIFO for equal priority
        if len(decisions_sorted) >= 2:
            if self.config.PRIORITY_LEVELS.get(decisions_sorted[0]["priority"], 0) == \
               self.config.PRIORITY_LEVELS.get(decisions_sorted[1]["priority"], 0):
                # Equal priority - use timestamp
                decisions_sorted = sorted(decisions, key=lambda d: d["timestamp"])
        
        winner = decisions_sorted[0]
        losers = decisions_sorted[1:]
        
        return self._create_resolution(
            conflict=conflict,
            decision="approve_partial",
            rationale=f"Priority rule: {winner['agent_id']} ({winner['priority']}) > others",
            execution_plan={
                "approved": [winner["agent_id"]],
                "queued": [d["agent_id"] for d in losers],
                "action": "allocate_by_priority"
            },
            confidence=0.9,
            requires_human=False
        )
    
    def _resolve_policy_conflict(
        self,
        conflict: Conflict,
        agent_decisions: List[AgentDecision]
    ) -> Resolution:
        """
        Resolve policy conflicts (e.g., monsoon restrictions)
        
        Rules:
        1. Monsoon blackout for outdoor work
        2. Safety compliance mandatory
        3. Regulatory requirements override preferences
        """
        # Check if it's a monsoon conflict
        if "monsoon" in conflict["description"].lower():
            agents_involved = conflict["agents_involved"]
            
            return self._create_resolution(
                conflict=conflict,
                decision="defer",
                rationale="Monsoon policy: Outdoor work deferred to Oct-June",
                execution_plan={
                    "deferred": agents_involved,
                    "action": "reschedule_post_monsoon",
                    "suggested_month": 10  # October
                },
                confidence=1.0,  # Policy is absolute
                requires_human=False
            )
        
        # Other policy conflicts may need human review
        return self._create_escalation_resolution(conflict)
    
    def _resolve_timing_conflict(
        self,
        conflict: Conflict,
        agent_decisions: List[AgentDecision]
    ) -> Resolution:
        """
        Resolve timing conflicts
        
        Rules:
        1. Emergency work starts immediately
        2. Sequential dependencies: engineering builds -> water maintains
        3. FIFO scheduling for independent work
        """
        agents_involved = conflict["agents_involved"]
        decisions = [d for d in agent_decisions if d["agent_id"] in agents_involved]
        
        # Check for sequential dependencies
        has_engineering = any(d["agent_type"] == "engineering" for d in decisions)
        has_water = any(d["agent_type"] == "water" for d in decisions)
        
        if has_engineering and has_water:
            # Rule: Engineering builds infrastructure, then water uses it
            engineering_decision = next(d for d in decisions if d["agent_type"] == "engineering")
            water_decision = next(d for d in decisions if d["agent_type"] == "water")
            
            if "construction" in engineering_decision.get("request", {}).get("project_type", "").lower():
                return self._create_resolution(
                    conflict=conflict,
                    decision="approve_all",
                    rationale="Sequential dependency: Engineering builds first, water follows",
                    execution_plan={
                        "sequence": [
                            {"agent": engineering_decision["agent_id"], "order": 1},
                            {"agent": water_decision["agent_id"], "order": 2}
                        ],
                        "action": "execute_sequentially"
                    },
                    confidence=0.9,
                    requires_human=False
                )
        
        # Default: FIFO scheduling
        decisions_sorted = sorted(decisions, key=lambda d: d["timestamp"])
        
        return self._create_resolution(
            conflict=conflict,
            decision="approve_all",
            rationale="FIFO scheduling applied",
            execution_plan={
                "sequence": [
                    {"agent": d["agent_id"], "order": i+1}
                    for i, d in enumerate(decisions_sorted)
                ],
                "action": "execute_in_order"
            },
            confidence=0.85,
            requires_human=False
        )
    
    def _resolve_budget_conflict(
        self,
        conflict: Conflict,
        agent_decisions: List[AgentDecision]
    ) -> Resolution:
        """
        Resolve budget conflicts
        
        Rules:
        1. Emergency gets budget priority
        2. Safety-critical projects prioritized
        3. Defer lower-priority projects
        """
        agents_involved = conflict["agents_involved"]
        decisions = [d for d in agent_decisions if d["agent_id"] in agents_involved]
        
        # Sort by priority
        decisions_sorted = sorted(
            decisions,
            key=lambda d: self.config.PRIORITY_LEVELS.get(d["priority"], 0),
            reverse=True
        )
        
        # Check if total cost exceeds auto-approval limit
        total_cost = sum(d.get("estimated_cost", 0) for d in decisions)
        if total_cost > self.config.AUTO_APPROVAL_COST_LIMIT:
            return self._create_escalation_resolution(conflict)
        
        # Allocate to highest priority
        approved = [decisions_sorted[0]["agent_id"]]
        deferred = [d["agent_id"] for d in decisions_sorted[1:]]
        
        return self._create_resolution(
            conflict=conflict,
            decision="approve_partial",
            rationale=f"Budget priority: {decisions_sorted[0]['priority']} project approved",
            execution_plan={
                "approved": approved,
                "deferred": deferred,
                "action": "allocate_budget_by_priority"
            },
            confidence=0.8,
            requires_human=len(deferred) > 0  # Human review if deferring projects
        )
    
    def _resolve_location_conflict(
        self,
        conflict: Conflict,
        agent_decisions: List[AgentDecision]
    ) -> Resolution:
        """
        Resolve location conflicts
        
        Rules:
        1. Emergency work gets location access
        2. Sequential work scheduling
        3. Coordinate simultaneous if possible
        """
        agents_involved = conflict["agents_involved"]
        decisions = [d for d in agent_decisions if d["agent_id"] in agents_involved]
        
        # Emergency override
        emergency_decisions = [d for d in decisions if d["priority"] == "emergency"]
        if emergency_decisions:
            winner = emergency_decisions[0]
            others = [d["agent_id"] for d in decisions if d != winner]
            
            return self._create_resolution(
                conflict=conflict,
                decision="approve_partial",
                rationale="Emergency work gets location priority",
                execution_plan={
                    "approved": [winner["agent_id"]],
                    "queued": others,
                    "action": "clear_location_for_emergency"
                },
                confidence=0.95,
                requires_human=False
            )
        
        # Try to coordinate simultaneous work
        if len(decisions) == 2:
            return self._create_resolution(
                conflict=conflict,
                decision="approve_all",
                rationale="Coordinate simultaneous work at same location",
                execution_plan={
                    "approved": [d["agent_id"] for d in decisions],
                    "action": "coordinate_simultaneous",
                    "coordination_required": True
                },
                confidence=0.7,
                requires_human=True  # Human should coordinate
            )
        
        # Default: sequential scheduling
        decisions_sorted = sorted(decisions, key=lambda d: d["timestamp"])
        
        return self._create_resolution(
            conflict=conflict,
            decision="approve_all",
            rationale="Sequential scheduling by timestamp",
            execution_plan={
                "sequence": [
                    {"agent": d["agent_id"], "order": i+1}
                    for i, d in enumerate(decisions_sorted)
                ],
                "action": "execute_sequentially"
            },
            confidence=0.8,
            requires_human=False
        )
    
    def _create_resolution(
        self,
        conflict: Conflict,
        decision: str,
        rationale: str,
        execution_plan: Dict[str, Any],
        confidence: float,
        requires_human: bool
    ) -> Resolution:
        """Helper to create Resolution object"""
        return {
            "resolution_id": str(uuid.uuid4()),
            "conflict_id": conflict["conflict_id"],
            "method": "rule",
            "decision": decision,
            "rationale": rationale,
            "confidence": confidence,
            "requires_human": requires_human,
            "execution_plan": execution_plan,
            "resolved_at": datetime.now().isoformat()
        }
    
    def _create_escalation_resolution(self, conflict: Conflict) -> Resolution:
        """Create resolution that escalates to LLM or human"""
        return {
            "resolution_id": str(uuid.uuid4()),
            "conflict_id": conflict["conflict_id"],
            "method": "rule",
            "decision": "escalate",
            "rationale": "Conflict too complex for rule-based resolution",
            "confidence": 0.0,
            "requires_human": True,
            "execution_plan": {
                "action": "escalate_to_llm_or_human"
            },
            "resolved_at": datetime.now().isoformat()
        }
