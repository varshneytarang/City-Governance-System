"""
Department Agent State Definition
PHASE 1-2: Define Agent Input Format & State
"""

from typing import TypedDict, List, Dict, Any, Literal, Optional
from pydantic import BaseModel, Field


# ============================================================
# PHASE 1: INPUT EVENT FORMAT (Structured, No Natural Language)
# ============================================================

class InputEvent(BaseModel):
    """Structured input event for department agent"""
    
    type: Literal[
        "schedule_shift_request",
        "pipeline_maintenance_request",
        "emergency_repair_request",
        "new_connection_request",
        "quality_check_request",
        "capacity_assessment_request",
    ] = Field(..., description="Type of request")
    
    from_entity: str = Field(..., description="Source: Coordinator, Citizen, or Other Department")
    
    location: str = Field(..., description="Zone/Area identifier")
    
    # Request-specific parameters
    requested_shift_days: Optional[int] = Field(None, description="For schedule shifts")
    reason: Optional[str] = Field(None, description="Reason for request")
    priority: Literal["low", "medium", "high", "critical"] = Field("medium", description="Request priority")
    
    # Additional context
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "schedule_shift_request",
                "from_entity": "Coordinator",
                "location": "Zone-12",
                "requested_shift_days": 2,
                "reason": "Joint underground work",
                "priority": "medium",
                "metadata": {}
            }
        }


# ============================================================
# PHASE 2: DEPARTMENT STATE (LangGraph State - Backbone)
# ============================================================

class DepartmentState(TypedDict):
    """
    Complete state for department agent workflow
    Every decision must appear here
    """
    
    # ========== INPUT ==========
    input_event: Dict[str, Any]  # Original request
    
    # ========== CONTEXT (Phase 3) ==========
    context: Dict[str, Any]  # Loaded reality: projects, schedules, risks
    
    # ========== INTENT & RISK (Phase 4) ==========
    intent: str  # negotiate, approve, deny, escalate
    risk_level: Literal["low", "medium", "high", "critical"]
    
    # ========== GOAL (Phase 5) ==========
    goal: str  # Agent's purpose for this request
    
    # ========== PLANNING (Phase 6) ==========
    plan: List[Dict[str, Any]]  # LLM-generated plan with alternatives
    current_plan_index: int  # Which alternative is being tried
    
    # ========== TOOL EXECUTION (Phase 7-8) ==========
    tool_results: Dict[str, Any]  # Results from tools
    observations: Dict[str, Any]  # Normalized tool outputs
    
    # ========== FEASIBILITY (Phase 9) ==========
    feasible: bool  # Is current plan feasible?
    feasibility_reason: str  # Why feasible/not feasible
    
    # ========== POLICY (Phase 10) ==========
    policy_ok: bool  # Complies with department rules?
    policy_violations: List[str]  # List of violations if any
    
    # ========== MEMORY (Phase 11) ==========
    decision_id: Optional[str]  # Database record ID for audit trail
    
    # ========== CONFIDENCE (Phase 12) ==========
    confidence: float  # 0.0 to 1.0
    confidence_factors: Dict[str, float]  # Breakdown of confidence calculation
    
    # ========== OUTPUT (Phase 13-14) ==========
    response: Dict[str, Any]  # Final output
    escalate: bool  # Should escalate to human?
    escalation_reason: Optional[str]  # Why escalating
    
    # ========== LOOP CONTROL ==========
    attempts: int  # Number of plan attempts
    max_attempts: int  # Maximum allowed attempts
    
    # ========== METADATA ==========
    timestamp: str  # When request received
    processing_time_ms: Optional[float]  # How long processing took
    error: Optional[str]  # Error message if any


# ============================================================
# SUPPORTING DATA STRUCTURES
# ============================================================

class Plan(BaseModel):
    """Structured plan from LLM"""
    steps: List[str] = Field(..., description="Ordered list of steps")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative approaches")
    estimated_impact: str = Field(..., description="Expected impact of plan")


class ToolResult(BaseModel):
    """Standardized tool result"""
    tool_name: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None


class FeasibilityAssessment(BaseModel):
    """Result of feasibility evaluation"""
    feasible: bool
    reason: str
    constraints_satisfied: Dict[str, bool]
    blocking_factors: List[str] = Field(default_factory=list)


class PolicyCheck(BaseModel):
    """Result of policy validation"""
    compliant: bool
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ConfidenceScore(BaseModel):
    """Confidence calculation breakdown"""
    overall: float = Field(..., ge=0.0, le=1.0)
    data_completeness: float = Field(..., ge=0.0, le=1.0)
    risk_factor: float = Field(..., ge=0.0, le=1.0)
    historical_similarity: float = Field(..., ge=0.0, le=1.0)
    retry_penalty: float = Field(..., ge=0.0, le=1.0)


class AgentResponse(BaseModel):
    """Final agent output"""
    decision: Literal["approved", "denied", "escalate", "conditional"]
    constraints: Optional[str] = None
    conditions: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Explanation of decision")
    escalation_reason: Optional[str] = None
    recommended_action: Optional[str] = None
