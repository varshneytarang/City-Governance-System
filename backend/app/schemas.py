from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class InputEvent(BaseModel):
    type: str
    from_: Optional[str] = Field(None, alias="from")
    location: str
    requested_shift_days: Optional[int] = None
    reason: Optional[str] = None
    estimated_cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class DecisionResponse(BaseModel):
    decision: str
    reason: Optional[str] = None
    recommendation: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = 0.0
    requires_human_review: Optional[bool] = False
    details: Optional[Dict[str, Any]] = None
    decision_id: Optional[str] = None
    error: Optional[str] = None


class JobStatus(BaseModel):
    id: str
    status: str
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    result: Optional[DecisionResponse] = None
    error: Optional[str] = None
