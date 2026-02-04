"""
Fire Department State

TypedDict for the department state passed between nodes.
"""

from typing import TypedDict, Dict, List, Any, Optional
from datetime import datetime


class DepartmentState(TypedDict, total=False):
    """
    State dictionary for Fire Department Agent.
    
    Passed between all LangGraph nodes.
    """
    
    # Input
    input_event: Dict[str, Any]
    
    # Context (from database)
    context: Dict[str, Any]
    
    # Intent & Risk
    intent: str
    risk_level: str
    safety_concerns: List[str]
    
    # Goal
    goal: str
    
    # Planning
    plan: Dict[str, Any]
    alternative_plans: List[Dict[str, Any]]
    
    # Tool execution
    tool_results: Dict[str, Any]
    
    # Observations
    observations: Dict[str, Any]
    
    # Feasibility
    feasible: bool
    feasibility_reason: str
    feasibility_details: Dict[str, Any]
    
    # Policy
    policy_ok: bool
    policy_violations: List[str]
    
    # Memory
    decision_id: Optional[int]
    
    # Confidence
    confidence: float
    confidence_factors: Dict[str, Any]
    
    # Output
    response: Dict[str, Any]
    
    # Escalation
    escalate: bool
    escalation_reason: Optional[str]
    
    # Loop control
    attempts: int
    max_attempts: int
    retry_needed: bool
    
    # Proactive Coordination
    coordination_check: Optional[Dict[str, Any]]
    coordination_approved: bool
    coordination_recommendations: List[str]
    
    # Metadata
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    agent_version: str
    execution_time_ms: int
