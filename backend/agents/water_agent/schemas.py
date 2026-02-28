from typing import List, Optional
from pydantic import BaseModel


class PlanModel(BaseModel):
    name: str
    steps: List[str]
    estimated_duration: Optional[str]
    estimated_cost: Optional[float]
    resources_needed: Optional[List[str]]
    risk_level: Optional[str]
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []


class PlannerOutput(BaseModel):
    plans: List[PlanModel]


class IntentAnalysis(BaseModel):
    intent: str
    risk_level: str
    safety_concerns: Optional[List[str]] = []
    reasoning: Optional[str] = None
