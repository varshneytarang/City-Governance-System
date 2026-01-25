"""
Water Agent API Routes
FastAPI endpoints for Water Agent operations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_groq import ChatGroq
from typing import Optional
import uuid
from datetime import datetime

from app.database import get_async_db
from app.schemas import WaterAgentRequest, WaterAgentResponse
from app.agents.water.graph import create_water_agent_workflow
from app.config import get_settings

router = APIRouter(prefix="/api/water", tags=["water-agent"])
settings = get_settings()


@router.post("/request", response_model=WaterAgentResponse)
async def process_water_request(
    request: WaterAgentRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Process water infrastructure request through Water Agent
    
    Example request types:
    - road_digging: Request permission for excavation
    - leakage: Report water leakage
    - new_project: Plan water supply for new development
    - maintenance: Schedule pipeline maintenance
    - inspection: Request infrastructure inspection
    """
    try:
        # Initialize LLM (only if API key is available)
        llm = None
        if settings.groq_api_key:
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                api_key=settings.groq_api_key
            )
        
        # Create workflow
        workflow = create_water_agent_workflow(db, llm)
        
        # Prepare initial state
        initial_state = {
            "request_id": str(uuid.uuid4()),
            "request_type": request.request_type,
            "location": request.location,
            "coordinates": request.coordinates,
            "priority": request.priority,
            "requester": request.requester,
            "details": request.details,
            "pipeline_data": [],
            "nearby_projects": [],
            "reservoir_levels": {},
            "weather_data": None,
            "zone": "",
            "risk_assessment": "medium",
            "conflicts_detected": [],
            "resource_requirements": {},
            "impact_analysis": "",
            "decision": "pending",  # Changed from "" to avoid state key conflict
            "action_plan": {},
            "notifications": [],
            "coordination_required": [],
            "messages_to_send": [],
            "reasoning_chain": [],
            "confidence": 0.0,
            "estimated_cost": None,
            "estimated_duration_days": None,
            "timestamp": datetime.now().isoformat(),
            "current_step": "",
            "agent_name": "water_agent"
        }
        
        # Run workflow
        result = await workflow.ainvoke(initial_state)
        
        # Format response
        return WaterAgentResponse(
            request_id=uuid.UUID(result["request_id"]),
            decision=result["decision"],
            reasoning="\n".join(result["reasoning_chain"]),
            action_plan=result["action_plan"],
            conflicts_detected=result["conflicts_detected"],
            notifications=[n.get("message", "") for n in result["notifications"]],
            estimated_cost=result["estimated_cost"],
            estimated_duration_days=result["estimated_duration_days"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Water Agent error: {str(e)}")


@router.get("/status")
async def get_water_agent_status(db: AsyncSession = Depends(get_async_db)):
    """Get Water Agent status and statistics"""
    from sqlalchemy import select, func
    from app.models import WaterInfrastructure, WaterResource, WaterIncident
    
    try:
        # Get pipeline stats
        pipeline_count = await db.scalar(select(func.count(WaterInfrastructure.pipeline_id)))
        
        # Get reservoir stats
        reservoir_result = await db.execute(
            select(WaterResource).where(WaterResource.resource_type == "reservoir")
        )
        reservoirs = reservoir_result.scalars().all()
        
        total_capacity = sum(r.capacity_liters or 0 for r in reservoirs)
        total_current = sum(r.current_level_liters or 0 for r in reservoirs)
        avg_level = (total_current / total_capacity * 100) if total_capacity > 0 else 0
        
        # Get incident stats
        incident_count = await db.scalar(
            select(func.count(WaterIncident.incident_id)).where(
                WaterIncident.status.in_(["reported", "assigned", "in_progress"])
            )
        )
        
        return {
            "agent": "water_agent",
            "status": "active",
            "infrastructure": {
                "total_pipelines": pipeline_count,
                "total_reservoirs": len(reservoirs),
                "average_reservoir_level": round(avg_level, 2),
                "reservoir_status": "critical" if avg_level < 30 else "low" if avg_level < 50 else "normal"
            },
            "operations": {
                "active_incidents": incident_count,
                "llm_enabled": bool(settings.openai_api_key)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/infrastructure")
async def get_infrastructure_status(
    zone: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get water infrastructure status"""
    from sqlalchemy import select
    from app.models import WaterInfrastructure
    
    try:
        query = select(WaterInfrastructure)
        if zone:
            query = query.where(WaterInfrastructure.zone == zone)
        
        result = await db.execute(query)
        pipelines = result.scalars().all()
        
        return {
            "total_pipelines": len(pipelines),
            "zone": zone or "all",
            "condition_breakdown": {
                "excellent": sum(1 for p in pipelines if p.condition == "excellent"),
                "good": sum(1 for p in pipelines if p.condition == "good"),
                "fair": sum(1 for p in pipelines if p.condition == "fair"),
                "poor": sum(1 for p in pipelines if p.condition == "poor"),
                "critical": sum(1 for p in pipelines if p.condition == "critical")
            },
            "risk_breakdown": {
                "low": sum(1 for p in pipelines if p.risk_level == "low"),
                "medium": sum(1 for p in pipelines if p.risk_level == "medium"),
                "high": sum(1 for p in pipelines if p.risk_level == "high"),
                "critical": sum(1 for p in pipelines if p.risk_level == "critical")
            },
            "pipelines": [
                {
                    "location": p.location,
                    "type": p.pipeline_type,
                    "condition": p.condition,
                    "risk_level": p.risk_level,
                    "status": p.operational_status
                }
                for p in pipelines[:20]  # Limit to first 20
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
