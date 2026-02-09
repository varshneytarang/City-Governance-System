"""
State definition for Health Agent with proactive coordination support
"""

from typing import TypedDict, Optional, Dict, List, Any
from datetime import datetime


class HealthAgentState(TypedDict, total=False):
    """Extended state for Health Department Agent with coordination support."""
    
    # Input and context
    input_event: Dict[str, Any]
    context: Dict[str, Any]
    intent: str
    
    # Risk assessment
    risk_level: str
    goal: str
    
    # Planning
    plan: Dict[str, Any]
    alternative_plans: List[Dict[str, Any]]
    
    # Execution
    tool_results: Dict[str, Any]
    observations: Dict[str, Any]
    
    # Validation
    feasible: bool
    policy_ok: bool
    confidence: float
    
    # Output
    response: Dict[str, Any]
    escalate: bool
    
    # Control flow
    attempts: int
    max_attempts: int
    
    # Timestamps
    started_at: datetime
    completed_at: Optional[datetime]
    agent_version: str
    execution_time_ms: int
    
    # Proactive Coordination fields
    coordination_check: Optional[Dict[str, Any]]  # Response from coordination agent
    coordination_approved: bool  # Whether coordinator approved the plan
    coordination_recommendations: List[str]  # Suggestions from coordinator
