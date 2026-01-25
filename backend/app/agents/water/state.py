"""
Water Agent State Definitions
TypedDict state for LangGraph workflow
"""
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from datetime import datetime
import operator


class WaterState(TypedDict):
    """State for Water Agent workflow"""
    
    # Input - Request Information
    request_id: str
    request_type: str  # "road_digging", "leakage", "new_project", "maintenance", "inspection"
    location: str
    coordinates: Optional[tuple[float, float]]
    priority: str  # "low", "medium", "high", "urgent"
    requester: Optional[str]
    details: Dict[str, Any]
    
    # Context - Data Collection
    pipeline_data: List[Dict[str, Any]]
    nearby_projects: List[Dict[str, Any]]
    reservoir_levels: Dict[str, Any]
    weather_data: Optional[Dict[str, Any]]
    zone: str
    
    # Analysis - Risk Assessment
    risk_assessment: str  # "low", "medium", "high", "critical"
    conflicts_detected: Annotated[List[str], operator.add]
    resource_requirements: Dict[str, Any]
    impact_analysis: str
    
    # Decision - Action Planning
    decision: str  # "approve", "deny", "coordinate", "escalate"
    action_plan: Dict[str, Any]
    notifications: Annotated[List[Dict[str, str]], operator.add]
    
    # Coordination - Inter-Agent
    coordination_required: List[str]  # ["roads", "fire", "finance"]
    messages_to_send: Annotated[List[Dict[str, Any]], operator.add]
    
    # Output - Response
    reasoning_chain: Annotated[List[str], operator.add]
    confidence: float
    estimated_cost: Optional[float]
    estimated_duration_days: Optional[int]
    
    # Metadata
    timestamp: str
    current_step: str
    agent_name: str
