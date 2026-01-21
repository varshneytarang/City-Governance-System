from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.governance_graph import create_governance_workflow
from langchain_core.messages import HumanMessage

router = APIRouter(prefix="/api/governance", tags=["governance"])

# Initialize the workflow
governance_workflow = create_governance_workflow()


class GovernanceRequest(BaseModel):
    """Model for governance request"""
    message: str
    context: Optional[Dict[str, Any]] = {}


class GovernanceResponse(BaseModel):
    """Model for governance response"""
    status: str
    result: str
    step: str


@router.post("/process", response_model=GovernanceResponse)
async def process_governance_request(request: GovernanceRequest):
    """
    Process a governance request using LangGraph workflow
    """
    try:
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=request.message)],
            "current_step": "initial",
            "data": request.context
        }
        
        # Run the workflow
        result = governance_workflow.invoke(initial_state)
        
        return GovernanceResponse(
            status="success",
            result=result["messages"][-1].content,
            step=result["current_step"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/status")
async def get_workflow_status():
    """Get the status of the governance workflow"""
    return {
        "status": "active",
        "workflow": "governance_graph",
        "version": "1.0.0"
    }
