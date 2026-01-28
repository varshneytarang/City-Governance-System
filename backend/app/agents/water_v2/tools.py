"""
Department Agent Tools
PHASE 7: Tool Execution - Convert plan into facts
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models import Pipeline, WorkSchedule, Incident, Worker, Reservoir, DepartmentBudget, Project

logger = logging.getLogger(__name__)


# ============================================================
# TOOL: Check Pipeline Health
# ============================================================

async def check_pipeline_health(db: AsyncSession, location: str) -> Dict[str, Any]:
    """
    Check health status of pipelines in specified location
    
    Returns:
        {
            "pressure_ok": bool,
            "leak_count": int,
            "last_maintenance": str,
            "health_score": float  # 0.0 to 1.0
        }
    """
    try:
        # Query pipelines in location
        query = select(Pipeline).where(
            Pipeline.location.ilike(f"%{location}%")
        )
        result = await db.execute(query)
        pipelines = result.scalars().all()
        
        if not pipelines:
            return {
                "pressure_ok": False,
                "leak_count": 0,
                "last_maintenance": None,
                "health_score": 0.0,
                "error": "No pipelines found in location"
            }
        
        # Calculate health metrics
        total_pressure_ok = sum(1 for p in pipelines if p.pressure_psi >= 40)
        leak_count = sum(1 for p in pipelines if p.operational_status == "under_repair")
        
        # Health score: combination of pressure and leak status
        pressure_score = total_pressure_ok / len(pipelines)
        leak_penalty = min(leak_count * 0.2, 0.5)
        health_score = max(0.0, pressure_score - leak_penalty)
        
        return {
            "pressure_ok": pressure_score >= 0.8,
            "leak_count": leak_count,
            "last_maintenance": pipelines[0].last_inspection_date.isoformat() if pipelines[0].last_inspection_date else None,
            "health_score": round(health_score, 2),
            "pipeline_count": len(pipelines)
        }
        
    except Exception as e:
        logger.error(f"Error checking pipeline health: {e}")
        return {
            "pressure_ok": False,
            "leak_count": 0,
            "last_maintenance": None,
            "health_score": 0.0,
            "error": str(e)
        }


# ============================================================
# TOOL: Check Manpower Availability
# ============================================================

async def check_manpower_availability(
    db: AsyncSession, 
    location: str, 
    days_ahead: int
) -> Dict[str, Any]:
    """
    Check if manpower is available for requested period
    
    Returns:
        {
            "available": int,
            "required": int,
            "sufficient": bool,
            "allocated_to": List[str]
        }
    """
    try:
        # Query active workers
        worker_query = select(Worker).where(Worker.status == "active")
        worker_result = await db.execute(worker_query)
        total_workers = len(worker_result.scalars().all())
        
        # Check work schedules for next N days
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_ahead)
        
        schedule_query = select(WorkSchedule).where(
            and_(
                WorkSchedule.scheduled_date >= start_date,
                WorkSchedule.scheduled_date <= end_date,
                WorkSchedule.status == "scheduled"
            )
        )
        result = await db.execute(schedule_query)
        schedules = result.scalars().all()
        
        # Calculate allocated workers
        workers_allocated = sum(s.workers_assigned or 0 for s in schedules)
        workers_available = max(0, total_workers - workers_allocated)
        workers_required = 5  # Standard requirement
        
        allocated_to = [s.activity_type for s in schedules] if schedules else []
        
        return {
            "available": workers_available,
            "required": workers_required,
            "sufficient": workers_available >= workers_required,
            "allocated_to": allocated_to,
            "scheduled_work_count": len(schedules)
        }
        
    except Exception as e:
        logger.error(f"Error checking manpower: {e}")
        return {
            "available": 0,
            "required": 5,
            "sufficient": False,
            "allocated_to": [],
            "error": str(e)
        }


# ============================================================
# TOOL: Check Emergency Backup System
# ============================================================

async def check_emergency_backup(db: AsyncSession, location: str) -> Dict[str, Any]:
    """
    Check if emergency backup water supply is available
    
    Returns:
        {
            "backup_available": bool,
            "backup_capacity_liters": int,
            "duration_hours": int
        }
    """
    try:
        # Query for reservoir availability
        query = select(Reservoir).where(
            Reservoir.location.ilike(f"%{location}%")
        )
        result = await db.execute(query)
        reservoirs = result.scalars().all()
        
        if reservoirs:
            # Calculate total backup capacity
            total_capacity = sum(r.current_level_liters or 0 for r in reservoirs)
            # Assume 50,000L/hour consumption rate
            duration_hours = (total_capacity / 50000) if total_capacity > 0 else 0
            
            return {
                "backup_available": True,
                "backup_capacity_liters": total_capacity,
                "duration_hours": int(duration_hours),
                "reservoir_count": len(reservoirs)
            }
        else:
            return {
                "backup_available": False,
                "backup_capacity_liters": 0,
                "duration_hours": 0,
                "reservoir_count": 0
            }
            
    except Exception as e:
        logger.error(f"Error checking emergency backup: {e}")
        return {
            "backup_available": False,
            "backup_capacity_liters": 0,
            "duration_hours": 0,
            "error": str(e)
        }


# ============================================================
# TOOL: Check Safety Risk
# ============================================================

async def check_safety_risk(db: AsyncSession, location: str) -> Dict[str, Any]:
    """
    Check recent safety incidents in location
    
    Returns:
        {
            "safety_risk": str,  # low, medium, high
            "recent_incidents": int,
            "severity": str
        }
    """
    try:
        # Check incidents in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        query = select(Incident).where(
            and_(
                Incident.location.ilike(f"%{location}%"),
                Incident.reported_date >= thirty_days_ago
            )
        )
        result = await db.execute(query)
        incidents = result.scalars().all()
        
        incident_count = len(incidents)
        
        # Determine risk level
        if incident_count == 0:
            safety_risk = "low"
            severity = "none"
        elif incident_count <= 2:
            safety_risk = "medium"
            severity = "minor"
        else:
            safety_risk = "high"
            severity = "major"
        
        return {
            "safety_risk": safety_risk,
            "recent_incidents": incident_count,
            "severity": severity,
            "incident_types": [i.incident_type for i in incidents] if incidents else []
        }
        
    except Exception as e:
        logger.error(f"Error checking safety risk: {e}")
        return {
            "safety_risk": "unknown",
            "recent_incidents": 0,
            "severity": "unknown",
            "error": str(e)
        }


# ============================================================
# TOOL: Check Schedule Conflicts
# ============================================================

async def check_schedule_conflicts(
    db: AsyncSession, 
    location: str, 
    requested_days: int
) -> Dict[str, Any]:
    """
    Check if there are scheduling conflicts
    
    Returns:
        {
            "conflicts": bool,
            "conflict_count": int,
            "conflicting_activities": List[str]
        }
    """
    try:
        # Check schedules in requested period
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=requested_days)
        
        query = select(WorkSchedule).where(
            and_(
                WorkSchedule.location.ilike(f"%{location}%"),
                WorkSchedule.scheduled_date >= start_date,
                WorkSchedule.scheduled_date <= end_date
            )
        )
        result = await db.execute(query)
        schedules = result.scalars().all()
        
        conflicting = [s.activity_type for s in schedules if s.priority in ("high", "critical")]
        
        return {
            "conflicts": len(conflicting) > 0,
            "conflict_count": len(conflicting),
            "conflicting_activities": conflicting,
            "total_scheduled": len(schedules)
        }
        
    except Exception as e:
        logger.error(f"Error checking schedule conflicts: {e}")
        return {
            "conflicts": False,
            "conflict_count": 0,
            "conflicting_activities": [],
            "error": str(e)
        }


# ============================================================
# TOOL: Check Budget Availability
# ============================================================

async def check_budget_availability(
    db: AsyncSession,
    location: str,
    requested_days: int
) -> Dict[str, Any]:
    """
    Check if budget is available for requested work
    
    Returns:
        {
            "budget_available": float,
            "estimated_cost": float,
            "sufficient": bool,
            "utilization_percent": float
        }
    """
    try:
        # Estimate cost based on requested days
        # Base cost: 10,000 per day + manpower cost (5 workers × 500/day)
        daily_base_cost = 10000
        daily_manpower_cost = 5 * 500
        estimated_cost = requested_days * (daily_base_cost + daily_manpower_cost)
        
        # Query department budget (simplified - would normally query Budget table)
        # For now, assume monthly budget of 500,000 with some already spent
        from app.models import Budget, Project
        
        # Get current month budget
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Simplified: assume 500,000 monthly budget
        monthly_budget = 500000
        
        # Query spent amount this month (from projects)
        spent_query = select(Project).where(
            and_(
                Project.location.ilike(f"%{location}%"),
                Project.start_date >= datetime(current_year, current_month, 1)
            )
        )
        result = await db.execute(spent_query)
        projects = result.scalars().all()
        
        amount_spent = sum(p.actual_cost or 0 for p in projects)
        budget_available = monthly_budget - amount_spent
        
        # Check if sufficient
        sufficient = budget_available >= estimated_cost
        utilization_percent = (amount_spent / monthly_budget) * 100 if monthly_budget > 0 else 0
        
        return {
            "budget_available": round(budget_available, 2),
            "estimated_cost": round(estimated_cost, 2),
            "sufficient": sufficient,
            "utilization_percent": round(utilization_percent, 2),
            "monthly_budget": monthly_budget,
            "amount_spent": round(amount_spent, 2)
        }
        
    except Exception as e:
        logger.error(f"Error checking budget availability: {e}")
        return {
            "budget_available": 0,
            "estimated_cost": 0,
            "sufficient": False,
            "utilization_percent": 0,
            "error": str(e)
        }


# ============================================================
# TOOL REGISTRY
# ============================================================

AVAILABLE_TOOLS = {
    "check_pipeline_health": check_pipeline_health,
    "check_manpower_availability": check_manpower_availability,
    "check_emergency_backup": check_emergency_backup,
    "check_safety_risk": check_safety_risk,
    "check_schedule_conflicts": check_schedule_conflicts,
    "check_budget_availability": check_budget_availability,
}


async def execute_tool(
    tool_name: str, 
    db: AsyncSession, 
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a tool by name with parameters
    
    Args:
        tool_name: Name of tool to execute
        db: Database session
        params: Tool parameters
        
    Returns:
        Tool result dictionary
    """
    if tool_name not in AVAILABLE_TOOLS:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
    
    try:
        tool_func = AVAILABLE_TOOLS[tool_name]
        result = await tool_func(db, **params)
        return {
            "success": True,
            "tool_name": tool_name,
            "data": result
        }
    except Exception as e:
        logger.error(f"Tool execution error ({tool_name}): {e}")
        return {
            "success": False,
            "tool_name": tool_name,
            "error": str(e)
        }
