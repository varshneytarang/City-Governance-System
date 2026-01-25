"""
Fire Agent State Definitions

This module defines the state structure for the Fire Agent's workflow.
"""

from typing import TypedDict, Optional, Dict, Any, List


class FireState(TypedDict, total=False):
    """
    State structure for Fire Agent LangGraph workflow
    
    Phases:
    1. Input Phase - Initial request data
    2. Validation Phase - Request validation
    3. Data Collection Phase - Gather station, incident, resource data
    4. Analysis Phase - Emergency severity and dispatch planning
    5. Decision Phase - Approve/deny/escalate decision
    6. Coordination Phase - Cross-department coordination
    7. Response Phase - Final response
    """
    
    # ===== INPUT PHASE =====
    request_id: str
    request_type: str  # "emergency_response", "fire_inspection", "awareness_program", "equipment_maintenance"
    department_id: int  # Fire department ID
    user_id: int
    location: Dict[str, Any]  # {"latitude": float, "longitude": float, "address": str}
    description: str
    priority: str  # "low", "medium", "high", "critical"
    timestamp: str
    
    # Emergency-specific fields
    emergency_type: Optional[str]  # "fire", "rescue", "medical", "hazmat", "other"
    casualties: Optional[int]
    building_type: Optional[str]  # "residential", "commercial", "industrial", "high-rise"
    fire_intensity: Optional[str]  # "minor", "moderate", "major", "conflagration"
    
    # Inspection/Program fields
    inspection_location: Optional[str]
    target_audience: Optional[str]  # For awareness programs
    equipment_type: Optional[str]
    
    # ===== VALIDATION PHASE =====
    validation_status: str  # "valid", "invalid"
    validation_errors: List[str]
    
    # ===== DATA COLLECTION PHASE =====
    # Fire stations data
    nearby_stations: List[Dict[str, Any]]
    available_stations: List[Dict[str, Any]]
    station_distances: Dict[int, float]  # station_id -> distance in km
    
    # Emergency incidents data
    active_incidents: List[Dict[str, Any]]
    historical_incidents: List[Dict[str, Any]]
    incident_patterns: Dict[str, Any]
    
    # Station resources
    station_resources: Dict[int, Dict[str, Any]]  # station_id -> resource data
    total_personnel: int
    available_personnel: int
    total_vehicles: int
    available_vehicles: int
    
    # ===== ANALYSIS PHASE =====
    # LLM Analysis
    llm_analysis: str
    severity_assessment: Dict[str, Any]  # {"level": str, "factors": List[str], "score": int}
    response_requirements: Dict[str, Any]  # {"personnel": int, "vehicles": int, "equipment": List[str]}
    
    # Risk Analysis
    risk_level: str  # "low", "medium", "high", "critical"
    risk_factors: List[str]
    estimated_response_time: int  # minutes
    
    # Dispatch Planning
    recommended_stations: List[int]
    dispatch_plan: Dict[str, Any]  # {"stations": List, "eta": int, "personnel": int}
    backup_required: bool
    mutual_aid_needed: bool
    
    # ===== DECISION PHASE =====
    decision: str  # "APPROVE", "DENY", "ESCALATE", "COORDINATE"
    reasoning: str
    conditions: List[str]
    estimated_cost: float
    estimated_duration: int  # hours for non-emergency, minutes for emergency
    
    # Policy flags
    safety_check_passed: bool
    resource_check_passed: bool
    coordination_required: bool
    
    # ===== COORDINATION PHASE =====
    coordination_needed: bool
    departments_to_notify: List[str]  # ["Water Department", "Health Department", etc.]
    coordination_messages: List[Dict[str, Any]]
    coordination_status: str  # "pending", "completed", "not_required"
    
    # ===== RESPONSE PHASE =====
    response: Dict[str, Any]
    action_items: List[str]
    next_steps: List[str]
    
    # ===== METADATA =====
    workflow_status: str  # "in_progress", "completed", "failed"
    current_node: str
    errors: List[str]
    execution_time: float
