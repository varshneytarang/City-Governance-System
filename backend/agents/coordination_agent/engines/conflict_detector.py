"""
Conflict Detection Engine

Identifies conflicts between multiple agent decisions based on:
- Resource overlaps (budget, workers, equipment)
- Location overlaps (same area, infrastructure dependencies)
- Timing conflicts (scheduling, sequential dependencies)
- Policy conflicts (regulatory contradictions)
- Priority conflicts (emergency vs routine)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..state import AgentDecision, Conflict, CoordinationState
from ..config import CoordinationConfig

logger = logging.getLogger(__name__)


class ConflictDetector:
    """Detects conflicts between agent decisions"""
    
    def __init__(self):
        self.config = CoordinationConfig()
    
    def detect_all_conflicts(self, state: CoordinationState) -> CoordinationState:
        """
        Main entry point: detect all types of conflicts
        
        Returns updated state with conflicts_detected populated
        """
        agent_decisions = state["agent_decisions"]
        
        if len(agent_decisions) < 2:
            # No conflicts possible with single agent
            state["has_conflicts"] = False
            state["workflow_log"].append("Single agent decision - no conflicts")
            return state
        
        conflicts: List[Conflict] = []
        
        # Run all conflict detection checks
        conflicts.extend(self._detect_resource_conflicts(agent_decisions))
        conflicts.extend(self._detect_location_conflicts(agent_decisions))
        conflicts.extend(self._detect_timing_conflicts(agent_decisions))
        conflicts.extend(self._detect_policy_conflicts(agent_decisions))
        conflicts.extend(self._detect_budget_conflicts(agent_decisions))
        
        # Update state
        state["conflicts_detected"] = conflicts
        state["has_conflicts"] = len(conflicts) > 0
        
        if conflicts:
            conflict_summary = ", ".join([c["conflict_type"] for c in conflicts])
            state["workflow_log"].append(f"Detected {len(conflicts)} conflict(s): {conflict_summary}")
            logger.info(f"✓ Detected {len(conflicts)} conflicts")
        else:
            state["workflow_log"].append("No conflicts detected - all agents aligned")
            logger.info("✓ No conflicts detected")
        
        return state
    
    def _detect_resource_conflicts(self, decisions: List[AgentDecision]) -> List[Conflict]:
        """Detect conflicts in resource allocation (workers, equipment)"""
        conflicts = []
        
        # Group decisions by resources needed
        resource_map: Dict[str, List[AgentDecision]] = {}
        
        for decision in decisions:
            for resource in decision.get("resources_needed", []):
                if resource not in resource_map:
                    resource_map[resource] = []
                resource_map[resource].append(decision)
        
        # Check for overlapping resource requests
        for resource, requesting_agents in resource_map.items():
            if len(requesting_agents) > 1:
                # Multiple agents need same resource
                agents_involved = [d["agent_id"] for d in requesting_agents]
                
                # Calculate severity based on priority
                priorities = [d.get("priority", "routine") for d in requesting_agents]
                severity = self._calculate_conflict_severity(priorities)
                
                conflict: Conflict = {
                    "conflict_id": str(uuid.uuid4()),
                    "conflict_type": "resource",
                    "agents_involved": agents_involved,
                    "description": f"Multiple agents need resource: {resource}",
                    "severity": severity,
                    "complexity_score": self._calculate_complexity(requesting_agents),
                    "detected_at": datetime.now().isoformat()
                }
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_location_conflicts(self, decisions: List[AgentDecision]) -> List[Conflict]:
        """Detect conflicts in work locations"""
        conflicts = []
        
        # Group by location
        location_map: Dict[str, List[AgentDecision]] = {}
        
        for decision in decisions:
            location = decision.get("location", "")
            if location:
                if location not in location_map:
                    location_map[location] = []
                location_map[location].append(decision)
        
        # Check for overlapping locations
        for location, agents_at_location in location_map.items():
            if len(agents_at_location) > 1:
                agents_involved = [d["agent_id"] for d in agents_at_location]
                priorities = [d.get("priority", "routine") for d in agents_at_location]
                severity = self._calculate_conflict_severity(priorities)
                
                conflict: Conflict = {
                    "conflict_id": str(uuid.uuid4()),
                    "conflict_type": "location",
                    "agents_involved": agents_involved,
                    "description": f"Multiple agents working at: {location}",
                    "severity": severity,
                    "complexity_score": self._calculate_complexity(agents_at_location),
                    "detected_at": datetime.now().isoformat()
                }
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_timing_conflicts(self, decisions: List[AgentDecision]) -> List[Conflict]:
        """Detect timing and scheduling conflicts"""
        conflicts = []
        
        # Check if any decisions specify timeline constraints
        decisions_with_timeline = [d for d in decisions if d.get("timeline")]
        
        if len(decisions_with_timeline) >= 2:
            # For now, simple check: if multiple agents have timelines, flag as potential conflict
            # More sophisticated: parse timelines and check for overlaps
            
            agents_involved = [d["agent_id"] for d in decisions_with_timeline]
            
            conflict: Conflict = {
                "conflict_id": str(uuid.uuid4()),
                "conflict_type": "timing",
                "agents_involved": agents_involved,
                "description": "Multiple agents have timeline constraints",
                "severity": "medium",
                "complexity_score": 0.5,
                "detected_at": datetime.now().isoformat()
            }
            conflicts.append(conflict)
        
        return conflicts
    
    def _detect_policy_conflicts(self, decisions: List[AgentDecision]) -> List[Conflict]:
        """Detect policy or regulatory conflicts"""
        conflicts = []
        
        # Check for monsoon conflicts
        current_month = datetime.now().month
        if current_month in self.config.MONSOON_MONTHS:
            outdoor_projects = [
                d for d in decisions
                if d.get("request", {}).get("project_type") in [
                    "construction", "road_work", "outdoor_maintenance"
                ]
            ]
            
            if outdoor_projects:
                agents_involved = [d["agent_id"] for d in outdoor_projects]
                
                conflict: Conflict = {
                    "conflict_id": str(uuid.uuid4()),
                    "conflict_type": "policy",
                    "agents_involved": agents_involved,
                    "description": "Outdoor work during monsoon season (policy violation)",
                    "severity": "high",
                    "complexity_score": 0.4,  # Simple rule-based
                    "detected_at": datetime.now().isoformat()
                }
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_budget_conflicts(self, decisions: List[AgentDecision]) -> List[Conflict]:
        """Detect budget allocation conflicts"""
        conflicts = []
        
        # Calculate total budget requested
        total_requested = sum(d.get("estimated_cost", 0) for d in decisions)
        
        # If multiple high-cost projects, flag as budget conflict
        if total_requested > 1000000:  # ₹10 lakh
            high_cost_decisions = [d for d in decisions if d.get("estimated_cost", 0) > 200000]
            
            if len(high_cost_decisions) > 1:
                agents_involved = [d["agent_id"] for d in high_cost_decisions]
                
                conflict: Conflict = {
                    "conflict_id": str(uuid.uuid4()),
                    "conflict_type": "budget",
                    "agents_involved": agents_involved,
                    "description": f"Multiple high-cost projects (total: ₹{total_requested:,})",
                    "severity": "high" if total_requested > 5000000 else "medium",
                    "complexity_score": 0.7 if len(agents_involved) > 2 else 0.5,
                    "detected_at": datetime.now().isoformat()
                }
                conflicts.append(conflict)
        
        return conflicts
    
    def _calculate_conflict_severity(self, priorities: List[str]) -> str:
        """Calculate conflict severity based on priorities involved"""
        priority_levels = self.config.PRIORITY_LEVELS
        
        max_priority = max(priority_levels.get(p, 0) for p in priorities)
        
        if max_priority >= 9:
            return "critical"
        elif max_priority >= 7:
            return "high"
        elif max_priority >= 4:
            return "medium"
        else:
            return "low"
    
    def _calculate_complexity(self, decisions: List[AgentDecision]) -> float:
        """
        Calculate complexity score for conflict
        
        Factors:
        - Number of agents involved
        - Cost magnitude
        - Priority differences
        - Resource constraints
        
        Returns: 0.0 - 1.0 (higher = more complex)
        """
        # Start with low base complexity
        complexity = 0.0
        
        # Add complexity for number of agents (but keep it low for 2 agents)
        if len(decisions) == 2:
            complexity += 0.1  # Simple 2-agent conflicts
        else:
            complexity += min(len(decisions) * 0.15, 0.5)
        
        # Add complexity for high costs
        max_cost = max(d.get("estimated_cost", 0) for d in decisions)
        if max_cost > 5000000:  # ₹50 lakh
            complexity += 0.3
        elif max_cost > 1000000:  # ₹10 lakh
            complexity += 0.15
        elif max_cost > 500000:  # ₹5 lakh
            complexity += 0.1
        
        # Add complexity for priority mismatches (but not if one is emergency)
        priorities = [d.get("priority", "routine") for d in decisions]
        if "emergency" in priorities:
            # Emergency conflicts are simple (clear priority)
            complexity = min(complexity, 0.3)
        else:
            unique_priorities = len(set(priorities))
            if unique_priorities > 1:
                complexity += 0.1
        
        return min(complexity, 1.0)
