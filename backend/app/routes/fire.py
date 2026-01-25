"""
Fire Agent API Routes

FastAPI endpoints for the Fire Department Agent.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import uuid
from datetime import datetime

from app.database import get_async_db
from app.agents.fire.graph import create_fire_agent_workflow
from app.agents.fire.state import FireState
from pydantic import BaseModel, Field
from typing import Optional, List


# Request Models
class EmergencyRequest(BaseModel):
    """Emergency response request"""
    user_id: int
    location: Dict[str, Any] = Field(..., description="Location with latitude, longitude, address")
    description: str
    emergency_type: str = Field(..., description="fire, rescue, medical, hazmat, other")
    priority: str = Field(default="high", description="low, medium, high, critical")
    casualties: int = Field(default=0)
    building_type: Optional[str] = Field(None, description="residential, commercial, industrial, high-rise")
    fire_intensity: Optional[str] = Field(None, description="minor, moderate, major, conflagration")


class InspectionRequest(BaseModel):
    """Fire inspection request"""
    user_id: int
    inspection_location: str
    description: str
    priority: str = Field(default="medium")


class AwarenessRequest(BaseModel):
    """Fire awareness program request"""
    user_id: int
    location: Dict[str, Any]
    description: str
    target_audience: str = Field(..., description="Target audience for the program")
    priority: str = Field(default="low")


class MaintenanceRequest(BaseModel):
    """Equipment maintenance request"""
    user_id: int
    location: Dict[str, Any]
    equipment_type: str
    description: str
    priority: str = Field(default="medium")


# Create router
router = APIRouter(prefix="/api/fire", tags=["fire"])


@router.post("/emergency")
async def handle_emergency(
    request: EmergencyRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Handle emergency response request
    
    This endpoint processes emergency incidents and dispatches fire stations.
    """
    try:
        # Create workflow
        workflow = create_fire_agent_workflow(db)
        
        # Prepare initial state
        initial_state: FireState = {
            "request_id": str(uuid.uuid4()),
            "request_type": "emergency_response",
            "department_id": 2,  # Fire Department ID
            "user_id": request.user_id,
            "location": request.location,
            "description": request.description,
            "priority": request.priority,
            "timestamp": datetime.utcnow().isoformat(),
            "emergency_type": request.emergency_type,
            "casualties": request.casualties,
            "building_type": request.building_type,
            "fire_intensity": request.fire_intensity,
            "validation_status": "",
            "validation_errors": [],
            "nearby_stations": [],
            "available_stations": [],
            "station_distances": {},
            "active_incidents": [],
            "historical_incidents": [],
            "incident_patterns": {},
            "station_resources": {},
            "total_personnel": 0,
            "available_personnel": 0,
            "total_vehicles": 0,
            "available_vehicles": 0,
            "llm_analysis": "",
            "severity_assessment": {},
            "response_requirements": {},
            "risk_level": "",
            "risk_factors": [],
            "estimated_response_time": 0,
            "recommended_stations": [],
            "dispatch_plan": {},
            "backup_required": False,
            "mutual_aid_needed": False,
            "decision": "",
            "reasoning": "",
            "conditions": [],
            "estimated_cost": 0.0,
            "estimated_duration": 0,
            "safety_check_passed": False,
            "resource_check_passed": False,
            "coordination_required": False,
            "coordination_needed": False,
            "departments_to_notify": [],
            "coordination_messages": [],
            "coordination_status": "",
            "response": {},
            "action_items": [],
            "next_steps": [],
            "workflow_status": "in_progress",
            "current_node": "",
            "errors": [],
            "execution_time": 0.0
        }
        
        # Execute workflow
        result = await workflow.ainvoke(initial_state)
        
        return {
            "status": "success",
            "data": result.get("response", {}),
            "workflow_status": result.get("workflow_status", "completed")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency processing failed: {str(e)}")


@router.post("/inspection")
async def handle_inspection(
    request: InspectionRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Handle fire inspection request
    """
    try:
        workflow = create_fire_agent_workflow(db)
        
        # Create a basic location dict for inspection
        location = {
            "latitude": 0.0,
            "longitude": 0.0,
            "address": request.inspection_location
        }
        
        initial_state: FireState = {
            "request_id": str(uuid.uuid4()),
            "request_type": "fire_inspection",
            "department_id": 2,
            "user_id": request.user_id,
            "location": location,
            "description": request.description,
            "priority": request.priority,
            "timestamp": datetime.utcnow().isoformat(),
            "inspection_location": request.inspection_location,
            "validation_status": "",
            "validation_errors": [],
            "nearby_stations": [],
            "available_stations": [],
            "station_distances": {},
            "active_incidents": [],
            "historical_incidents": [],
            "incident_patterns": {},
            "station_resources": {},
            "total_personnel": 0,
            "available_personnel": 0,
            "total_vehicles": 0,
            "available_vehicles": 0,
            "llm_analysis": "",
            "severity_assessment": {},
            "response_requirements": {},
            "risk_level": "",
            "risk_factors": [],
            "estimated_response_time": 0,
            "recommended_stations": [],
            "dispatch_plan": {},
            "backup_required": False,
            "mutual_aid_needed": False,
            "decision": "",
            "reasoning": "",
            "conditions": [],
            "estimated_cost": 0.0,
            "estimated_duration": 0,
            "safety_check_passed": False,
            "resource_check_passed": False,
            "coordination_required": False,
            "coordination_needed": False,
            "departments_to_notify": [],
            "coordination_messages": [],
            "coordination_status": "",
            "response": {},
            "action_items": [],
            "next_steps": [],
            "workflow_status": "in_progress",
            "current_node": "",
            "errors": [],
            "execution_time": 0.0
        }
        
        result = await workflow.ainvoke(initial_state)
        
        return {
            "status": "success",
            "data": result.get("response", {}),
            "workflow_status": result.get("workflow_status", "completed")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inspection processing failed: {str(e)}")


@router.post("/awareness")
async def handle_awareness_program(
    request: AwarenessRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Handle fire awareness program request
    """
    try:
        workflow = create_fire_agent_workflow(db)
        
        initial_state: FireState = {
            "request_id": str(uuid.uuid4()),
            "request_type": "awareness_program",
            "department_id": 2,
            "user_id": request.user_id,
            "location": request.location,
            "description": request.description,
            "priority": request.priority,
            "timestamp": datetime.utcnow().isoformat(),
            "target_audience": request.target_audience,
            "validation_status": "",
            "validation_errors": [],
            "nearby_stations": [],
            "available_stations": [],
            "station_distances": {},
            "active_incidents": [],
            "historical_incidents": [],
            "incident_patterns": {},
            "station_resources": {},
            "total_personnel": 0,
            "available_personnel": 0,
            "total_vehicles": 0,
            "available_vehicles": 0,
            "llm_analysis": "",
            "severity_assessment": {},
            "response_requirements": {},
            "risk_level": "",
            "risk_factors": [],
            "estimated_response_time": 0,
            "recommended_stations": [],
            "dispatch_plan": {},
            "backup_required": False,
            "mutual_aid_needed": False,
            "decision": "",
            "reasoning": "",
            "conditions": [],
            "estimated_cost": 0.0,
            "estimated_duration": 0,
            "safety_check_passed": False,
            "resource_check_passed": False,
            "coordination_required": False,
            "coordination_needed": False,
            "departments_to_notify": [],
            "coordination_messages": [],
            "coordination_status": "",
            "response": {},
            "action_items": [],
            "next_steps": [],
            "workflow_status": "in_progress",
            "current_node": "",
            "errors": [],
            "execution_time": 0.0
        }
        
        result = await workflow.ainvoke(initial_state)
        
        return {
            "status": "success",
            "data": result.get("response", {}),
            "workflow_status": result.get("workflow_status", "completed")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Awareness program processing failed: {str(e)}")


@router.post("/maintenance")
async def handle_maintenance(
    request: MaintenanceRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Handle equipment maintenance request
    """
    try:
        workflow = create_fire_agent_workflow(db)
        
        initial_state: FireState = {
            "request_id": str(uuid.uuid4()),
            "request_type": "equipment_maintenance",
            "department_id": 2,
            "user_id": request.user_id,
            "location": request.location,
            "description": request.description,
            "priority": request.priority,
            "timestamp": datetime.utcnow().isoformat(),
            "equipment_type": request.equipment_type,
            "validation_status": "",
            "validation_errors": [],
            "nearby_stations": [],
            "available_stations": [],
            "station_distances": {},
            "active_incidents": [],
            "historical_incidents": [],
            "incident_patterns": {},
            "station_resources": {},
            "total_personnel": 0,
            "available_personnel": 0,
            "total_vehicles": 0,
            "available_vehicles": 0,
            "llm_analysis": "",
            "severity_assessment": {},
            "response_requirements": {},
            "risk_level": "",
            "risk_factors": [],
            "estimated_response_time": 0,
            "recommended_stations": [],
            "dispatch_plan": {},
            "backup_required": False,
            "mutual_aid_needed": False,
            "decision": "",
            "reasoning": "",
            "conditions": [],
            "estimated_cost": 0.0,
            "estimated_duration": 0,
            "safety_check_passed": False,
            "resource_check_passed": False,
            "coordination_required": False,
            "coordination_needed": False,
            "departments_to_notify": [],
            "coordination_messages": [],
            "coordination_status": "",
            "response": {},
            "action_items": [],
            "next_steps": [],
            "workflow_status": "in_progress",
            "current_node": "",
            "errors": [],
            "execution_time": 0.0
        }
        
        result = await workflow.ainvoke(initial_state)
        
        return {
            "status": "success",
            "data": result.get("response", {}),
            "workflow_status": result.get("workflow_status", "completed")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Maintenance processing failed: {str(e)}")


@router.get("/stations")
async def get_fire_stations(
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get list of all fire stations
    """
    from sqlalchemy import select
    from app.models import FireStation
    
    try:
        query = select(FireStation)
        result = await db.execute(query)
        stations = result.scalars().all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": s.id,
                    "name": s.name,
                    "location": s.location,
                    "personnel_count": s.personnel_count,
                    "vehicle_count": s.vehicle_count,
                    "equipment": s.equipment,
                    "operational_status": s.operational_status,
                    "response_time_avg": s.response_time_avg
                }
                for s in stations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stations: {str(e)}")


@router.get("/incidents/active")
async def get_active_incidents(
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get list of active emergency incidents
    """
    from sqlalchemy import select, and_
    from app.models import EmergencyIncident
    from datetime import datetime, timedelta
    
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        
        query = select(EmergencyIncident).where(
            and_(
                EmergencyIncident.reported_at >= time_threshold,
                EmergencyIncident.status.in_(["reported", "dispatched", "responding", "on_scene"])
            )
        )
        result = await db.execute(query)
        incidents = result.scalars().all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": i.id,
                    "incident_type": i.incident_type,
                    "severity": i.severity,
                    "status": i.status,
                    "location": i.location,
                    "reported_at": i.reported_at.isoformat(),
                    "responding_stations": i.responding_stations,
                    "casualties": i.casualties
                }
                for i in incidents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch incidents: {str(e)}")
