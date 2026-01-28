"""
SQLAlchemy Models for City Governance System
Matches PostgreSQL schema with additions for Water & Fire agents
"""
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, Date, DateTime, Text, 
    ForeignKey, CheckConstraint, Index, Float
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


# ============= AGENT DECISION AUDIT TABLE (Professional Edition) =============

class AgentDecision(Base):
    """
    Audit trail for all agent decisions
    Stores complete decision context for explainability
    """
    __tablename__ = "agent_decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Agent metadata
    agent_type = Column(String(50), nullable=False, index=True)  # water_department, fire_department, etc.
    request_type = Column(String(100), nullable=False, index=True)
    
    # Request data
    request_data = Column(JSONB, nullable=False)  # Original input event
    context_snapshot = Column(JSONB)  # Context at decision time
    
    # Plan and execution
    plan_attempted = Column(JSONB)  # Which plan was tried
    tool_results = Column(JSONB)  # Tool execution results
    
    # Evaluation results
    feasible = Column(Boolean)
    feasibility_reason = Column(Text)
    policy_compliant = Column(Boolean)
    policy_violations = Column(JSONB)
    
    # Confidence
    confidence = Column(Float)
    confidence_factors = Column(JSONB)
    
    # Final decision
    decision = Column(String(50), index=True)  # approved, denied, escalate
    reasoning = Column(Text)
    escalation_reason = Column(Text)
    
    # Response
    response = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=func.current_timestamp(), index=True)
    completed_at = Column(DateTime)
    agent_version = Column(String(20))
    execution_time_ms = Column(Integer)
    retry_count = Column(Integer, default=0)
    
    # Indexes for querying
    __table_args__ = (
        Index('idx_agent_timestamp', 'agent_type', 'created_at'),
        Index('idx_decision_type', 'decision', 'request_type'),
    )


# ============= CORE GOVERNANCE TABLES =============

class Department(Base):
    __tablename__ = "departments"
    
    department_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)
    zone = Column(Text, nullable=False)
    max_parallel_projects = Column(Integer, default=2)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    projects = relationship("Project", back_populates="department")
    manpower = relationship("Manpower", back_populates="department")
    resources = relationship("Resource", back_populates="department")
    budgets = relationship("Budget", back_populates="department")


class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.department_id", ondelete="SET NULL"))
    
    project_type = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    priority = Column(Text, CheckConstraint("priority IN ('low','medium','high')"))
    
    start_date = Column(Date)
    end_date = Column(Date)
    
    estimated_cost = Column(Numeric)
    actual_cost = Column(Numeric)
    
    nuisance_score = Column(Numeric)
    status = Column(Text, CheckConstraint("status IN ('planned','active','completed')"))
    
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    department = relationship("Department", back_populates="projects")
    negotiation_logs = relationship("NegotiationLog", back_populates="project")
    
    __table_args__ = (
        Index('idx_projects_location', 'location'),
        Index('idx_projects_status', 'status'),
    )


class Manpower(Base):
    __tablename__ = "manpower"
    
    worker_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.department_id", ondelete="CASCADE"))
    
    skill = Column(Text, nullable=False)
    availability = Column(Boolean, default=True)
    assigned_project = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="SET NULL"))
    
    max_hours_per_week = Column(Integer, default=40)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    department = relationship("Department", back_populates="manpower")
    
    __table_args__ = (
        Index('idx_manpower_department', 'department_id'),
    )


class Resource(Base):
    __tablename__ = "resources"
    
    resource_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.department_id", ondelete="CASCADE"))
    
    resource_type = Column(Text, nullable=False)
    availability = Column(Boolean, default=True)
    assigned_project = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="SET NULL"))
    
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    department = relationship("Department", back_populates="resources")


class Budget(Base):
    __tablename__ = "budgets"
    
    budget_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.department_id", ondelete="CASCADE"))
    
    fiscal_year = Column(Integer, nullable=False)
    allocated_amount = Column(Numeric, nullable=False)
    used_amount = Column(Numeric, default=0)
    remaining_amount = Column(Numeric, nullable=False)
    
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    department = relationship("Department", back_populates="budgets")
    
    __table_args__ = (
        CheckConstraint('remaining_amount = allocated_amount - used_amount', name='budget_balance_check'),
        Index('idx_budget_department_year', 'department_id', 'fiscal_year'),
    )


class NegotiationLog(Base):
    __tablename__ = "negotiation_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"))
    
    agents_involved = Column(JSONB)
    proposals = Column(JSONB)
    final_decision = Column(JSONB)
    
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    project = relationship("Project", back_populates="negotiation_logs")


# ============= WATER AGENT TABLES =============

class WaterInfrastructure(Base):
    __tablename__ = "water_infrastructure"
    
    pipeline_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    location = Column(Text, nullable=False)
    zone = Column(Text, nullable=False)
    
    # Geospatial (simplified - use PostGIS for production)
    latitude = Column(Numeric(precision=10, scale=7))
    longitude = Column(Numeric(precision=10, scale=7))
    
    pipeline_type = Column(Text, nullable=False)  # 'supply', 'drainage', 'sewage'
    diameter_mm = Column(Integer)
    material = Column(Text)  # 'PVC', 'cast_iron', 'concrete'
    
    condition = Column(Text, CheckConstraint("condition IN ('excellent','good','fair','poor','critical')"))
    capacity_liters_per_min = Column(Integer)
    
    installation_date = Column(Date)
    last_maintenance = Column(Date)
    next_maintenance_due = Column(Date)
    
    risk_level = Column(Text, CheckConstraint("risk_level IN ('low','medium','high','critical')"))
    operational_status = Column(Text, CheckConstraint("operational_status IN ('active','inactive','under_repair')"))
    
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    incidents = relationship("WaterIncident", back_populates="infrastructure")
    
    __table_args__ = (
        Index('idx_water_infra_location', 'location'),
        Index('idx_water_infra_risk', 'risk_level'),
        Index('idx_water_infra_status', 'operational_status'),
    )


class WaterIncident(Base):
    __tablename__ = "water_incidents"
    
    incident_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    incident_type = Column(Text, nullable=False)  # 'leakage', 'blockage', 'contamination', 'pressure_drop'
    location = Column(Text, nullable=False)
    
    pipeline_id = Column(UUID(as_uuid=True), ForeignKey("water_infrastructure.pipeline_id", ondelete="SET NULL"))
    
    severity = Column(Text, CheckConstraint("severity IN ('low','medium','high','critical')"))
    priority = Column(Text, CheckConstraint("priority IN ('low','medium','high','urgent')"))
    
    reported_by = Column(Text)
    reported_at = Column(DateTime, default=func.current_timestamp())
    
    description = Column(Text)
    estimated_impact = Column(Text)  # e.g., "500 households affected"
    
    status = Column(Text, CheckConstraint("status IN ('reported','assigned','in_progress','resolved','closed')"))
    assigned_crew_id = Column(UUID(as_uuid=True))
    
    response_time_minutes = Column(Integer)
    resolution_time_minutes = Column(Integer)
    
    action_taken = Column(Text)
    cost = Column(Numeric)
    
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    infrastructure = relationship("WaterInfrastructure", back_populates="incidents")
    
    __table_args__ = (
        Index('idx_water_incident_status', 'status'),
        Index('idx_water_incident_severity', 'severity'),
        Index('idx_water_incident_type', 'incident_type'),
    )


class WaterResource(Base):
    __tablename__ = "water_resources"
    
    resource_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    resource_type = Column(Text, nullable=False)  # 'reservoir', 'pump', 'treatment_plant', 'storage_tank'
    name = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    
    capacity_liters = Column(Integer)
    current_level_liters = Column(Integer)
    level_percentage = Column(Numeric(precision=5, scale=2))
    
    operational_status = Column(Text, CheckConstraint("operational_status IN ('active','inactive','maintenance','emergency')"))
    
    last_reading = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_water_resource_type', 'resource_type'),
        Index('idx_water_resource_status', 'operational_status'),
    )


# ============= FIRE AGENT TABLES =============

class FireStation(Base):
    __tablename__ = "fire_stations"
    
    station_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    zone = Column(Text, nullable=False)
    
    # Geospatial
    latitude = Column(Numeric(precision=10, scale=7))
    longitude = Column(Numeric(precision=10, scale=7))
    
    total_vehicles = Column(Integer, default=0)
    available_vehicles = Column(Integer, default=0)
    
    total_crew = Column(Integer, default=0)
    available_crew = Column(Integer, default=0)
    
    coverage_radius_km = Column(Numeric(precision=5, scale=2))
    
    operational_status = Column(Text, CheckConstraint("operational_status IN ('active','limited','inactive')"))
    
    equipment_list = Column(JSONB)  # {"ladder_trucks": 2, "pumpers": 3, "ambulances": 1}
    
    contact_number = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    incidents = relationship("EmergencyIncident", back_populates="responding_station")
    
    __table_args__ = (
        Index('idx_fire_station_zone', 'zone'),
        Index('idx_fire_station_status', 'operational_status'),
    )


class EmergencyIncident(Base):
    __tablename__ = "emergency_incidents"
    
    incident_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    incident_type = Column(Text, nullable=False)  # 'fire', 'flood', 'accident', 'medical', 'rescue', 'hazmat'
    location = Column(Text, nullable=False)
    
    latitude = Column(Numeric(precision=10, scale=7))
    longitude = Column(Numeric(precision=10, scale=7))
    
    severity = Column(Text, CheckConstraint("severity IN ('low','medium','high','critical')"))
    priority = Column(Text, CheckConstraint("priority IN ('routine','urgent','emergency','disaster')"))
    
    reported_by = Column(Text)
    reported_at = Column(DateTime, default=func.current_timestamp())
    
    description = Column(Text)
    building_info = Column(JSONB)  # {"type": "residential", "floors": 5, "occupancy": 50}
    
    status = Column(Text, CheckConstraint("status IN ('reported','dispatched','on_scene','active','contained','resolved','closed')"))
    
    responding_station_id = Column(UUID(as_uuid=True), ForeignKey("fire_stations.station_id", ondelete="SET NULL"))
    units_dispatched = Column(Integer, default=0)
    personnel_count = Column(Integer, default=0)
    
    dispatch_time = Column(DateTime)
    arrival_time = Column(DateTime)
    contained_time = Column(DateTime)
    resolved_time = Column(DateTime)
    closed_time = Column(DateTime)
    
    response_time_minutes = Column(Integer)  # arrival_time - dispatch_time
    total_duration_minutes = Column(Integer)  # resolved_time - dispatch_time
    
    casualties = Column(Integer, default=0)
    injuries = Column(Integer, default=0)
    property_damage_estimate = Column(Numeric)
    
    action_taken = Column(Text)
    resources_used = Column(JSONB)
    
    coordination_required = Column(JSONB)  # ["water", "health", "roads"]
    
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    responding_station = relationship("FireStation", back_populates="incidents")
    
    __table_args__ = (
        Index('idx_emergency_incident_type', 'incident_type'),
        Index('idx_emergency_incident_status', 'status'),
        Index('idx_emergency_incident_severity', 'severity'),
        Index('idx_emergency_incident_reported', 'reported_at'),
    )


# ============= INTER-AGENT COMMUNICATION =============

class AgentMessage(Base):
    __tablename__ = "agent_messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    from_agent = Column(Text, nullable=False)
    to_agent = Column(Text, nullable=False)
    
    message_type = Column(Text, nullable=False)  # 'alert', 'request', 'response', 'notification'
    priority = Column(Text, CheckConstraint("priority IN ('low','medium','high','urgent')"))
    
    subject = Column(Text)
    payload = Column(JSONB, nullable=False)
    
    status = Column(Text, CheckConstraint("status IN ('pending','delivered','acknowledged','processed','failed')"))
    
    sent_at = Column(DateTime, default=func.current_timestamp())
    delivered_at = Column(DateTime)
    acknowledged_at = Column(DateTime)
    
    response_required = Column(Boolean, default=False)
    response_message_id = Column(UUID(as_uuid=True), ForeignKey("agent_messages.message_id", ondelete="SET NULL"))
    
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_agent_message_from', 'from_agent'),
        Index('idx_agent_message_to', 'to_agent'),
        Index('idx_agent_message_status', 'status'),
        Index('idx_agent_message_priority', 'priority'),
        Index('idx_agent_message_sent', 'sent_at'),
    )


# ============= PROFESSIONAL AGENT ARCHITECTURE MODELS =============

class Worker(Base):
    """Workers/Manpower for resource allocation"""
    __tablename__ = "workers"
    
    worker_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department = Column(String(50), nullable=False, index=True)
    worker_name = Column(String(255), nullable=False)
    role = Column(String(100))
    skills = Column(JSONB)
    certifications = Column(JSONB)
    status = Column(String(20), CheckConstraint("status IN ('active', 'on_leave', 'sick', 'inactive')"))
    phone = Column(String(20))
    email = Column(String(255))
    hire_date = Column(Date)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class Pipeline(Base):
    """Pipeline infrastructure for water department"""
    __tablename__ = "pipelines"
    
    pipeline_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(Text, nullable=False, index=True)
    zone = Column(String(50), index=True)
    pipeline_type = Column(String(20), CheckConstraint("pipeline_type IN ('supply', 'drainage', 'sewage')"))
    diameter_mm = Column(Integer)
    material = Column(String(50))
    length_meters = Column(Numeric(10, 2))
    pressure_psi = Column(Numeric(6, 2))
    flow_rate = Column(Numeric(10, 2))
    condition = Column(String(20), CheckConstraint("condition IN ('excellent', 'good', 'fair', 'poor', 'critical')"))
    installation_date = Column(Date)
    last_inspection_date = Column(Date)
    next_inspection_due = Column(Date)
    operational_status = Column(String(20), CheckConstraint("operational_status IN ('active', 'inactive', 'under_repair', 'retired')"))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    notes = Column(Text)


class Reservoir(Base):
    """Water reservoirs for emergency backup calculations"""
    __tablename__ = "reservoirs"
    
    reservoir_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    location = Column(Text, nullable=False, index=True)
    capacity_liters = Column(Integer, nullable=False)
    current_level_liters = Column(Integer)
    operational_status = Column(String(20), CheckConstraint("operational_status IN ('active', 'maintenance', 'emergency', 'inactive')"))
    last_reading_time = Column(DateTime)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class Incident(Base):
    """Incidents for safety risk tracking"""
    __tablename__ = "incidents"
    
    incident_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department = Column(String(50), nullable=False, index=True)
    incident_type = Column(String(100), nullable=False)
    location = Column(Text, nullable=False, index=True)
    severity = Column(String(20), CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')"))
    reported_date = Column(DateTime, nullable=False, default=func.current_timestamp(), index=True)
    reported_by = Column(String(255))
    description = Column(Text)
    status = Column(String(20), CheckConstraint("status IN ('reported', 'investigating', 'resolved', 'closed')"))
    resolution_date = Column(DateTime)
    created_at = Column(DateTime, default=func.current_timestamp())
    notes = Column(Text)


class WorkSchedule(Base):
    """Work schedules for conflict detection"""
    __tablename__ = "work_schedules"
    
    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department = Column(String(50), nullable=False, index=True)
    activity_type = Column(String(100), nullable=False)
    location = Column(Text, nullable=False, index=True)
    scheduled_date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    priority = Column(String(20), CheckConstraint("priority IN ('low', 'medium', 'high', 'critical')"))
    workers_assigned = Column(Integer)
    equipment_assigned = Column(JSONB)
    status = Column(String(20), CheckConstraint("status IN ('scheduled', 'in_progress', 'completed', 'cancelled')"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    notes = Column(Text)


class DepartmentBudget(Base):
    """Department budgets for financial tracking"""
    __tablename__ = "department_budgets"
    
    budget_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department = Column(String(50), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_budget = Column(Numeric(15, 2), nullable=False)
    allocated = Column(Numeric(15, 2), default=0)
    spent = Column(Numeric(15, 2), default=0)
    status = Column(String(20))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("month BETWEEN 1 AND 12", name='month_range_check'),
        CheckConstraint("status IN ('active', 'depleted', 'frozen', 'closed')", name='status_check'),
        Index('idx_budget_department', 'department'),
        Index('idx_budget_period', 'year', 'month'),
        {},
    )

