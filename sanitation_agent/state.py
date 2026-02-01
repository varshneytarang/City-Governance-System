"""
PHASE 2: Define Agent State (LangGraph)

This is the backbone. Every decision must appear here.
"""

from typing import TypedDict, Optional, Any, List
from datetime import datetime


class DepartmentState(TypedDict):
    """
    Complete state of the Sanitation Department Agent decision process.
    
    This TypedDict tracks every stage of the agent's reasoning from
    input to final decision.
    """
    
    # ========== PHASE 1: INPUT ==========
    input_event: dict
    
    # ========== PHASE 3: CONTEXT LOADER ==========
    context: dict  # reality snapshot: routes, trucks, schedules, landfills, complaints
    
    # ========== PHASE 4: INTENT + RISK ANALYSIS ==========
    intent: str  # what is the request trying to accomplish?
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    safety_concerns: List[str]  # list of identified safety issues
    
    # ========== PHASE 5: GOAL SETTER ==========
    goal: str  # specific goal derived from intent
    
    # ========== PHASE 6: PLANNER (LLM) ==========
    plan: dict  # LLM-proposed plan with steps and alternatives
    alternative_plans: List[dict]  # backup options
    
    # ========== PHASE 7: TOOL EXECUTION ==========
    tool_results: dict  # results from tool execution
    
    # ========== PHASE 8: OBSERVE ==========
    observations: dict  # normalized tool outputs
    
    # ========== PHASE 9: FEASIBILITY EVALUATOR ==========
    feasible: bool  # is the plan feasible?
    feasibility_reason: str  # why or why not?
    feasibility_details: dict  # detailed constraint analysis
    
    # ========== PHASE 10: POLICY VALIDATION ==========
    policy_ok: bool  # does it comply with department rules?
    policy_violations: List[str]  # list of violations if any
    
    # ========== PHASE 11: MEMORY LOGGER ==========
    decision_id: Optional[str]  # UUID of this decision in agent_decisions table
    
    # ========== PHASE 12: CONFIDENCE ESTIMATION ==========
    confidence: float  # 0.0-1.0, how confident is the recommendation?
    confidence_factors: dict  # breakdown of confidence calculation
    
    # ========== PHASE 13: DECISION ROUTER ==========
    response: dict  # final response (approve/escalate with reasoning)
    escalate: bool  # should this be escalated to human?
    escalation_reason: Optional[str]  # why escalate?
    
    # ========== LOOP CONTROL ==========
    attempts: int  # how many planning attempts so far?
    max_attempts: int  # max retries allowed
    retry_needed: bool  # flag for alternative plan retry
    
    # ========== METADATA ==========
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    agent_version: str
    execution_time_ms: int
