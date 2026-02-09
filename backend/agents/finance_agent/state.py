"""
State definition for Finance Agent with proactive coordination support
"""

from typing import TypedDict, Optional, Dict, List, Any
from datetime import datetime


class FinanceAgentState(TypedDict, total=False):
    """Extended state for Finance Department Agent with coordination support."""
    
    # Input and context
    input_event: Dict[str, Any]
    context: Dict[str, Any]
    
    # Financial analysis
    revenue_forecast: Dict[str, Any]
    cost_estimates: Dict[str, Any]
    
    # Validation
    fiscal_feasible: bool
    policy_ok: bool
    
    # Output
    response: Dict[str, Any]
    escalate: bool
    escalation_reason: Optional[str]
    
    # Timestamps
    started_at: datetime
    completed_at: Optional[datetime]
    agent_version: str
    execution_time_ms: int
    
    # Database queries
    queries: Optional[Any]
    
    # Proactive Coordination fields
    coordination_check: Optional[Dict[str, Any]]  # Response from coordination agent
    coordination_approved: bool  # Whether coordinator approved the plan
    coordination_recommendations: List[str]  # Suggestions from coordinator


# Alias for backward compatibility with imports expecting DepartmentState
DepartmentState = FinanceAgentState
