"""
Coordination Agent State Management
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class AgentDecision(TypedDict):
    """Structure for individual agent decision"""
    agent_id: str
    agent_type: str  # 'water', 'engineering', etc.
    decision: str  # 'recommend', 'approve', 'escalate'
    request: Dict[str, Any]
    confidence: float
    constraints: Dict[str, Any]
    resources_needed: List[str]
    location: str
    estimated_cost: int
    timeline: Optional[str]
    priority: str
    timestamp: str


class Conflict(TypedDict):
    """Structure for detected conflict"""
    conflict_id: str
    conflict_type: str  # 'resource', 'location', 'timing', 'policy', 'budget'
    agents_involved: List[str]
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    complexity_score: float
    detected_at: str


class Resolution(TypedDict):
    """Structure for conflict resolution"""
    resolution_id: str
    conflict_id: str
    method: str  # 'rule', 'llm', 'human'
    decision: str  # 'approve_all', 'approve_partial', 'defer', 'reject', 'escalate'
    rationale: str
    confidence: float
    requires_human: bool
    execution_plan: Dict[str, Any]
    resolved_at: str


class HumanEscalation(TypedDict):
    """Structure for human escalation request"""
    escalation_id: str
    conflict_id: str
    reason: str
    urgency: str  # 'low', 'medium', 'high', 'critical'
    options: List[Dict[str, Any]]
    llm_analysis: Optional[str]
    status: str  # 'pending', 'approved', 'rejected', 'modified'
    approver: Optional[str]
    approval_notes: Optional[str]
    created_at: str
    resolved_at: Optional[str]


class CoordinationState(TypedDict):
    """
    State for Coordination Agent workflow
    
    Tracks multi-agent decisions, conflicts, resolutions, and human interventions
    """
    
    # Input: Multiple agent decisions
    agent_decisions: List[AgentDecision]
    
    # Conflict Detection
    conflicts_detected: List[Conflict]
    has_conflicts: bool
    
    # Resolution
    resolutions: List[Resolution]
    resolution_method: Optional[str]  # 'rule', 'llm', 'human'
    
    # Human Intervention
    requires_human: bool
    human_escalation: Optional[HumanEscalation]
    
    # Final Decision
    final_decision: str  # 'approved', 'queued', 'escalated', 'rejected'
    execution_plan: Dict[str, Any]
    
    # Audit Trail
    workflow_log: List[str]
    decision_rationale: str
    
    # Metadata
    coordination_id: str
    started_at: str
    completed_at: Optional[str]
    total_processing_time: Optional[float]


def create_initial_state(agent_decisions: List[Dict[str, Any]]) -> CoordinationState:
    """Create initial coordination state from agent decisions"""
    
    # Convert to AgentDecision format
    formatted_decisions: List[AgentDecision] = []
    for decision in agent_decisions:
        formatted_decisions.append({
            "agent_id": decision.get("agent_id", "unknown"),
            "agent_type": decision.get("agent_type", "unknown"),
            "decision": decision.get("decision", "unknown"),
            "request": decision.get("request", {}),
            "confidence": decision.get("confidence", 0.0),
            "constraints": decision.get("constraints", {}),
            "resources_needed": decision.get("resources_needed", []),
            "location": decision.get("location", ""),
            "estimated_cost": decision.get("estimated_cost", 0),
            "timeline": decision.get("timeline"),
            "priority": decision.get("priority", "routine"),
            "timestamp": decision.get("timestamp", datetime.now().isoformat())
        })
    
    return {
        "agent_decisions": formatted_decisions,
        "conflicts_detected": [],
        "has_conflicts": False,
        "resolutions": [],
        "resolution_method": None,
        "requires_human": False,
        "human_escalation": None,
        "final_decision": "",
        "execution_plan": {},
        "workflow_log": ["Coordination workflow started"],
        "decision_rationale": "",
        "coordination_id": f"coord_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "total_processing_time": None
    }
