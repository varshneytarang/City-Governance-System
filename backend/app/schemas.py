"""
Pydantic schemas for request/response validation
Separates API contracts from database models
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# ============= CORE GOVERNANCE SCHEMAS =============

class DepartmentBase(BaseModel):
    name: str
    zone: str
    max_parallel_projects: int = 2


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    department_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    project_type: str
    location: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_cost: Optional[Decimal] = None
    nuisance_score: Optional[Decimal] = None
    status: str = Field("planned", pattern="^(planned|active|completed)$")


class ProjectCreate(ProjectBase):
    department_id: UUID


class ProjectResponse(ProjectBase):
    project_id: UUID
    department_id: Optional[UUID] = None
    actual_cost: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentDecisionBase(BaseModel):
    agent_name: str
    decision: str
    reasoning: str
    confidence: Optional[Decimal] = None
    input_summary: Optional[Dict[str, Any]] = None


class AgentDecisionCreate(AgentDecisionBase):
    related_project: Optional[UUID] = None


class AgentDecisionResponse(AgentDecisionBase):
    decision_id: UUID
    related_project: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= WATER AGENT SCHEMAS =============

class WaterInfrastructureBase(BaseModel):
    location: str
    zone: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    pipeline_type: str = Field(..., pattern="^(supply|drainage|sewage)$")
    diameter_mm: Optional[int] = None
    material: Optional[str] = None
    condition: str = Field("good", pattern="^(excellent|good|fair|poor|critical)$")
    capacity_liters_per_min: Optional[int] = None
    risk_level: str = Field("low", pattern="^(low|medium|high|critical)$")
    operational_status: str = Field("active", pattern="^(active|inactive|under_repair)$")


class WaterInfrastructureCreate(WaterInfrastructureBase):
    installation_date: Optional[date] = None
    last_maintenance: Optional[date] = None
    next_maintenance_due: Optional[date] = None
    notes: Optional[str] = None


class WaterInfrastructureResponse(WaterInfrastructureBase):
    pipeline_id: UUID
    installation_date: Optional[date] = None
    last_maintenance: Optional[date] = None
    next_maintenance_due: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WaterIncidentBase(BaseModel):
    incident_type: str = Field(..., pattern="^(leakage|blockage|contamination|pressure_drop)$")
    location: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$")
    description: Optional[str] = None
    estimated_impact: Optional[str] = None


class WaterIncidentCreate(WaterIncidentBase):
    pipeline_id: Optional[UUID] = None
    reported_by: Optional[str] = None


class WaterIncidentResponse(WaterIncidentBase):
    incident_id: UUID
    pipeline_id: Optional[UUID] = None
    reported_by: Optional[str] = None
    reported_at: datetime
    status: str
    assigned_crew_id: Optional[UUID] = None
    response_time_minutes: Optional[int] = None
    resolution_time_minutes: Optional[int] = None
    action_taken: Optional[str] = None
    cost: Optional[Decimal] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WaterResourceBase(BaseModel):
    resource_type: str = Field(..., pattern="^(reservoir|pump|treatment_plant|storage_tank)$")
    name: str
    location: str
    capacity_liters: Optional[int] = None
    current_level_liters: Optional[int] = None
    operational_status: str = Field("active", pattern="^(active|inactive|maintenance|emergency)$")


class WaterResourceCreate(WaterResourceBase):
    notes: Optional[str] = None


class WaterResourceResponse(WaterResourceBase):
    resource_id: UUID
    level_percentage: Optional[Decimal] = None
    last_reading: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= FIRE AGENT SCHEMAS =============

class FireStationBase(BaseModel):
    name: str
    location: str
    zone: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    total_vehicles: int = 0
    available_vehicles: int = 0
    total_crew: int = 0
    available_crew: int = 0
    coverage_radius_km: Optional[Decimal] = None
    operational_status: str = Field("active", pattern="^(active|limited|inactive)$")


class FireStationCreate(FireStationBase):
    equipment_list: Optional[Dict[str, Any]] = None
    contact_number: Optional[str] = None
    notes: Optional[str] = None


class FireStationResponse(FireStationBase):
    station_id: UUID
    equipment_list: Optional[Dict[str, Any]] = None
    contact_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmergencyIncidentBase(BaseModel):
    incident_type: str = Field(..., pattern="^(fire|flood|accident|medical|rescue|hazmat)$")
    location: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    priority: str = Field(..., pattern="^(routine|urgent|emergency|disaster)$")
    description: Optional[str] = None


class EmergencyIncidentCreate(EmergencyIncidentBase):
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    reported_by: Optional[str] = None
    building_info: Optional[Dict[str, Any]] = None


class EmergencyIncidentResponse(EmergencyIncidentBase):
    incident_id: UUID
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    reported_by: Optional[str] = None
    reported_at: datetime
    building_info: Optional[Dict[str, Any]] = None
    status: str
    responding_station_id: Optional[UUID] = None
    units_dispatched: int = 0
    personnel_count: int = 0
    dispatch_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    contained_time: Optional[datetime] = None
    resolved_time: Optional[datetime] = None
    closed_time: Optional[datetime] = None
    response_time_minutes: Optional[int] = None
    total_duration_minutes: Optional[int] = None
    casualties: int = 0
    injuries: int = 0
    property_damage_estimate: Optional[Decimal] = None
    action_taken: Optional[str] = None
    resources_used: Optional[Dict[str, Any]] = None
    coordination_required: Optional[List[str]] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= INTER-AGENT MESSAGING SCHEMAS =============

class AgentMessageBase(BaseModel):
    from_agent: str
    to_agent: str
    message_type: str = Field(..., pattern="^(alert|request|response|notification)$")
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    subject: Optional[str] = None
    payload: Dict[str, Any]
    response_required: bool = False


class AgentMessageCreate(AgentMessageBase):
    pass


class AgentMessageResponse(AgentMessageBase):
    message_id: UUID
    status: str
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    response_message_id: Optional[UUID] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= AGENT-SPECIFIC REQUEST SCHEMAS =============

class WaterAgentRequest(BaseModel):
    """Request schema for Water Agent operations"""
    request_type: str = Field(..., pattern="^(road_digging|leakage|new_project|maintenance|inspection)$")
    location: str
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    coordinates: Optional[tuple[float, float]] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    requester: Optional[str] = None


class WaterAgentResponse(BaseModel):
    """Response schema from Water Agent"""
    request_id: UUID
    decision: str = Field(..., pattern="^(approve|deny|coordinate|escalate)$")
    reasoning: str
    action_plan: Dict[str, Any]
    conflicts_detected: List[str] = Field(default_factory=list)
    notifications: List[str] = Field(default_factory=list)
    estimated_cost: Optional[Decimal] = None
    estimated_duration_days: Optional[int] = None


class FireAgentRequest(BaseModel):
    """Request schema for Fire Agent operations"""
    incident_type: str = Field(..., pattern="^(fire|flood|accident|medical|rescue|hazmat|building_permit)$")
    location: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    coordinates: Optional[tuple[float, float]] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    reported_by: Optional[str] = None


class FireAgentResponse(BaseModel):
    """Response schema from Fire Agent"""
    incident_id: UUID
    action_plan: Dict[str, Any]
    units_to_dispatch: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_response_time: int  # minutes
    coordination_required: List[str] = Field(default_factory=list)
    risk_assessment: str
    recommendations: List[str] = Field(default_factory=list)


# ============= HEALTH CHECK SCHEMAS =============

class HealthCheckResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime
    version: str
