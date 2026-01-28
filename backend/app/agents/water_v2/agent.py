"""
Department Agent - Core Implementation
PHASES 3-14: All workflow nodes
"""

from typing import Dict, Any
from datetime import datetime
import logging
import json

from langchain_groq import ChatGroq
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, insert

from .state import DepartmentState, Plan, FeasibilityAssessment, PolicyCheck, ConfidenceScore
from .tools import execute_tool
from app.models import AgentDecision

logger = logging.getLogger(__name__)


class WaterDepartmentAgent:
    """
    Professional Water Department Agent
    Follows: LLM proposes → Rules validate → Humans approve
    """
    
    def __init__(self, db: AsyncSession, llm_model: str = "llama-3.3-70b-versatile"):
        self.db = db
        self.llm = ChatGroq(model=llm_model, temperature=0.0)  # Deterministic
        
        # Agent configuration
        self.max_attempts = 3
        self.confidence_threshold = 0.7
        
        # Department rules
        self.rules = {
            "max_delay_days": 3,
            "min_manpower": 5,
            "min_backup_hours": 24,
            "max_concurrent_projects": 3,
            "max_budget_utilization_percent": 90,  # Don't exceed 90% budget
        }
    
    
    # ========== PHASE 3: CONTEXT LOADER ==========
    async def load_context(self, state: DepartmentState) -> DepartmentState:
        """
        Load reality before thinking
        NO reasoning - just fetch facts
        """
        logger.info("🔄 [Context Loader] Loading current reality...")
        
        location = state["input_event"].get("location", "unknown")
        
        try:
            # Fetch active projects
            from app.models import WorkSchedule
            query = select(WorkSchedule).where(
                and_(
                    WorkSchedule.location.ilike(f"%{location}%"),
                    WorkSchedule.status == "scheduled"
                )
            )
            result = await self.db.execute(query)
            active_projects = result.scalars().all()
            
            # Get current season (simple logic)
            month = datetime.now().month
            season = "monsoon" if 6 <= month <= 9 else "summer" if 3 <= month <= 5 else "winter"
            
            # Build context
            state["context"] = {
                "active_projects": [
                    {
                        "id": p.id,
                        "description": p.description,
                        "priority": p.priority
                    }
                    for p in active_projects
                ],
                "active_project_count": len(active_projects),
                "zone_sensitivity": "medium",  # Could be fetched from config
                "season": season,
                "time_of_day": datetime.now().hour,
                "location": location,
            }
            
            logger.info(f"✅ Context loaded: {len(active_projects)} active projects, {season} season")
            
        except Exception as e:
            logger.error(f"❌ Context loading failed: {e}")
            state["context"] = {
                "error": str(e),
                "active_projects": [],
                "active_project_count": 0,
            }
        
        return state
    
    
    # ========== PHASE 4: INTENT & RISK ANALYSIS ==========
    async def analyze_intent_and_risk(self, state: DepartmentState) -> DepartmentState:
        """
        Classify request and assess risk
        Deterministic - NO LLM
        """
        logger.info("🔄 [Intent & Risk Analyzer] Classifying request...")
        
        event = state["input_event"]
        event_type = event.get("type", "unknown")
        priority = event.get("priority", "medium")
        
        # Intent classification (rule-based)
        intent_map = {
            "schedule_shift_request": "negotiate",
            "emergency_repair_request": "approve",  # Fast-track emergencies
            "new_connection_request": "evaluate",
            "capacity_assessment_request": "analyze",
        }
        state["intent"] = intent_map.get(event_type, "unknown")
        
        # Risk assessment (rule-based)
        if priority == "critical":
            risk_level = "critical"
        elif event_type == "emergency_repair_request":
            risk_level = "high"
        elif state["context"].get("active_project_count", 0) > 3:
            risk_level = "high"  # Too many concurrent projects
        elif priority == "high":
            risk_level = "medium"
        else:
            risk_level = "low"
        
        state["risk_level"] = risk_level
        
        logger.info(f"✅ Intent: {state['intent']}, Risk: {risk_level}")
        
        # Immediate escalation rule
        if risk_level == "critical":
            state["escalate"] = True
            state["escalation_reason"] = "Critical risk - requires immediate human approval"
            logger.warning(f"⚠️ IMMEDIATE ESCALATION: {state['escalation_reason']}")
        
        return state
    
    
    # ========== PHASE 5: GOAL SETTER ==========
    async def set_goal(self, state: DepartmentState) -> DepartmentState:
        """
        Give agent purpose based on intent
        Simple mapping - NO LLM
        """
        logger.info("🔄 [Goal Setter] Determining agent goal...")
        
        intent = state["intent"]
        
        goal_map = {
            "negotiate": "Evaluate feasibility of requested schedule shift",
            "approve": "Verify emergency can be handled safely",
            "evaluate": "Assess capacity and requirements for new connection",
            "analyze": "Determine current capacity and limitations",
        }
        
        state["goal"] = goal_map.get(intent, "Analyze request and determine appropriate action")
        
        logger.info(f"✅ Goal set: {state['goal']}")
        
        return state
    
    
    # ========== PHASE 6: PLANNER (LLM - ONLY PLACE LLM USED) ==========
    async def generate_plan(self, state: DepartmentState) -> DepartmentState:
        """
        LLM generates candidate plans
        LLM ONLY PROPOSES - does NOT decide feasibility
        """
        logger.info("🔄 [Planner - LLM] Generating plan alternatives...")
        
        # Constrained prompt
        prompt = f"""You are a planning assistant for Water Department.

GOAL: {state['goal']}

INPUT EVENT:
{json.dumps(state['input_event'], indent=2)}

CURRENT CONTEXT:
{json.dumps(state['context'], indent=2)}

Generate a plan with alternatives. Output ONLY valid JSON:

{{
  "steps": ["step1", "step2", "step3"],
  "alternatives": [
    {{"delay_days": 2, "backup_required": true}},
    {{"delay_days": 1, "backup_required": false}}
  ],
  "estimated_impact": "description"
}}

Use these available tools:
- check_pipeline_health
- check_manpower_availability
- check_emergency_backup
- check_safety_risk
- check_schedule_conflicts

IMPORTANT: You are ONLY planning. DO NOT decide if plan is feasible.
"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()
            
            # Extract JSON (handle markdown code blocks)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(content)
            
            state["plan"] = plan_data.get("alternatives", [plan_data])
            state["current_plan_index"] = 0
            
            logger.info(f"✅ Plan generated with {len(state['plan'])} alternatives")
            
        except Exception as e:
            logger.error(f"❌ Plan generation failed: {e}")
            # Fallback plan
            state["plan"] = [{
                "steps": ["check_pipeline_health", "check_manpower_availability"],
                "estimated_impact": "Standard assessment"
            }]
            state["current_plan_index"] = 0
        
        return state
    
    
    # ========== PHASE 7: TOOL EXECUTION ==========
    async def execute_tools(self, state: DepartmentState) -> DepartmentState:
        """
        Execute tools from plan
        Convert plan into facts
        """
        logger.info("🔄 [Tool Executor] Executing plan tools...")
        
        current_plan = state["plan"][state["current_plan_index"]]
        steps = current_plan.get("steps", [])
        
        tool_results = {}
        
        for tool_name in steps:
            logger.info(f"  🔧 Executing: {tool_name}")
            
            # Prepare parameters based on tool
            params = {"location": state["input_event"].get("location", "unknown")}
            
            if "manpower" in tool_name:
                params["days_ahead"] = state["input_event"].get("requested_shift_days", 1)
            elif "schedule" in tool_name or "budget" in tool_name:
                params["requested_days"] = state["input_event"].get("requested_shift_days", 1)
            
            result = await execute_tool(tool_name, self.db, params)
            tool_results[tool_name] = result
        
        state["tool_results"] = tool_results
        
        logger.info(f"✅ Executed {len(tool_results)} tools")
        
        return state
    
    
    # ========== PHASE 8: OBSERVE ==========
    async def observe_results(self, state: DepartmentState) -> DepartmentState:
        """
        Normalize tool outputs
        NO decision - just organize
        """
        logger.info("🔄 [Observer] Normalizing tool results...")
        
        observations = {}
        
        for tool_name, result in state["tool_results"].items():
            if result.get("success"):
                observations[tool_name] = result.get("data", {})
            else:
                observations[tool_name] = {"error": result.get("error")}
        
        state["observations"] = observations
        
        logger.info(f"✅ Observations normalized: {len(observations)} results")
        
        return state
    
    
    # ========== PHASE 9: FEASIBILITY EVALUATOR (CRITICAL - DETERMINISTIC) ==========
    async def evaluate_feasibility(self, state: DepartmentState) -> DepartmentState:
        """
        MOST IMPORTANT NODE
        Deterministic Python rules - NO LLM - NO agent
        Pure logic
        """
        logger.info("🔄 [Feasibility Evaluator] Checking constraints...")
        
        observations = state["observations"]
        current_plan = state["plan"][state["current_plan_index"]]
        
        # Constraint checks
        constraints_satisfied = {}
        blocking_factors = []
        
        # Check 1: Pipeline health
        pipeline_check = observations.get("check_pipeline_health", {})
        if pipeline_check.get("pressure_ok") == False:
            constraints_satisfied["pipeline_health"] = False
            blocking_factors.append("Pipeline pressure inadequate")
        else:
            constraints_satisfied["pipeline_health"] = True
        
        # Check 2: Manpower
        manpower_check = observations.get("check_manpower_availability", {})
        if manpower_check.get("sufficient") == False:
            constraints_satisfied["manpower"] = False
            blocking_factors.append(f"Insufficient manpower: {manpower_check.get('available', 0)}/{manpower_check.get('required', 0)}")
        else:
            constraints_satisfied["manpower"] = True
        
        # Check 3: Safety risk
        safety_check = observations.get("check_safety_risk", {})
        if safety_check.get("safety_risk") == "high":
            constraints_satisfied["safety"] = False
            blocking_factors.append("High safety risk in area")
        else:
            constraints_satisfied["safety"] = True
        
        # Check 4: Emergency backup
        backup_check = observations.get("check_emergency_backup", {})
        if backup_check.get("duration_hours", 0) < self.rules["min_backup_hours"]:
            constraints_satisfied["backup"] = False
            blocking_factors.append(f"Insufficient backup capacity: {backup_check.get('duration_hours', 0)}h < {self.rules['min_backup_hours']}h required")
        else:
            constraints_satisfied["backup"] = True
        
        # Check 5: Schedule conflicts
        schedule_check = observations.get("check_schedule_conflicts", {})
        if schedule_check.get("conflicts"):
            constraints_satisfied["schedule"] = False
            blocking_factors.append(f"Schedule conflicts: {schedule_check.get('conflict_count')} conflicting activities")
        else:
            constraints_satisfied["schedule"] = True
        
        # Check 6: Budget availability
        budget_check = observations.get("check_budget_availability", {})
        if budget_check.get("sufficient") == False:
            constraints_satisfied["budget"] = False
            blocking_factors.append(f"Insufficient budget: ₹{budget_check.get('budget_available', 0):,.0f} available, ₹{budget_check.get('estimated_cost', 0):,.0f} required")
        elif budget_check.get("utilization_percent", 0) > self.rules["max_budget_utilization_percent"]:
            constraints_satisfied["budget"] = False
            blocking_factors.append(f"Budget utilization too high: {budget_check.get('utilization_percent', 0):.1f}% > {self.rules['max_budget_utilization_percent']}% limit")
        else:
            constraints_satisfied["budget"] = True
        
        # Overall feasibility
        feasible = all(constraints_satisfied.values())
        
        state["feasible"] = feasible
        state["feasibility_reason"] = "All constraints satisfied" if feasible else f"Blocking factors: {', '.join(blocking_factors)}"
        
        if feasible:
            logger.info("✅ Plan is FEASIBLE")
        else:
            logger.warning(f"❌ Plan NOT feasible: {state['feasibility_reason']}")
        
        return state
    
    
    # ========== PHASE 10: POLICY VALIDATOR ==========
    async def validate_policy(self, state: DepartmentState) -> DepartmentState:
        """
        Check department rules and SOPs
        Deterministic - NO LLM
        """
        logger.info("🔄 [Policy Validator] Checking department rules...")
        
        violations = []
        warnings = []
        
        current_plan = state["plan"][state["current_plan_index"]]
        requested_days = state["input_event"].get("requested_shift_days", 0)
        
        # Rule 1: Max delay
        if requested_days > self.rules["max_delay_days"]:
            violations.append(f"Requested delay ({requested_days} days) exceeds maximum ({self.rules['max_delay_days']} days)")
        
        # Rule 2: Concurrent projects
        active_count = state["context"].get("active_project_count", 0)
        if active_count >= self.rules["max_concurrent_projects"]:
            warnings.append(f"Near maximum concurrent projects: {active_count}/{self.rules['max_concurrent_projects']}")
        
        # Rule 3: Service continuity during monsoon
        if state["context"].get("season") == "monsoon" and requested_days > 1:
            warnings.append("Monsoon season: delays should be minimized to ensure service continuity")
        
        state["policy_ok"] = len(violations) == 0
        state["policy_violations"] = violations
        
        if state["policy_ok"]:
            logger.info(f"✅ Policy compliant ({len(warnings)} warnings)")
        else:
            logger.warning(f"❌ Policy violations: {violations}")
        
        return state
    
    
    # ========== PHASE 11: MEMORY LOGGER ==========
    async def log_to_memory(self, state: DepartmentState) -> DepartmentState:
        """
        Persist decision trail for audit
        """
        logger.info("🔄 [Memory Logger] Persisting decision trail...")
        
        try:
            # Store in agent_decisions table
            decision_record = {
                "agent_type": "water_department",
                "request_type": state["input_event"].get("type"),
                "request_data": json.dumps(state["input_event"]),
                "context_snapshot": json.dumps(state["context"]),
                "plan_attempted": json.dumps(state["plan"][state["current_plan_index"]]),
                "feasible": state["feasible"],
                "policy_compliant": state["policy_ok"],
                "confidence": state.get("confidence", 0.0),
                "decision": state.get("response", {}).get("decision", "escalate"),
            }
            
            stmt = insert(AgentDecision).values(**decision_record).returning(AgentDecision.id)
            result = await self.db.execute(stmt)
            await self.db.commit()
            
            decision_id = result.scalar()
            state["decision_id"] = str(decision_id)
            
            logger.info(f"✅ Decision logged: ID={decision_id}")
            
        except Exception as e:
            logger.error(f"❌ Memory logging failed: {e}")
            state["decision_id"] = None
        
        return state
    
    
    # ========== PHASE 12: CONFIDENCE ESTIMATION ==========
    async def estimate_confidence(self, state: DepartmentState) -> DepartmentState:
        """
        Quantify uncertainty
        Based on: data completeness, risk, retries, historical similarity
        """
        logger.info("🔄 [Confidence Estimator] Calculating confidence...")
        
        # Factor 1: Data completeness (did all tools succeed?)
        total_tools = len(state.get("tool_results", {}))
        successful_tools = sum(1 for r in state.get("tool_results", {}).values() if r.get("success"))
        data_completeness = successful_tools / total_tools if total_tools > 0 else 0.0
        
        # Factor 2: Risk penalty
        risk_penalties = {"low": 1.0, "medium": 0.8, "high": 0.6, "critical": 0.3}
        risk_factor = risk_penalties.get(state["risk_level"], 0.5)
        
        # Factor 3: Retry penalty
        retry_penalty = 1.0 - (state["attempts"] * 0.15)  # -15% per retry
        retry_penalty = max(0.4, retry_penalty)  # Floor at 0.4
        
        # Factor 4: Historical similarity (simplified - would query past similar cases)
        historical_similarity = 0.7  # Placeholder
        
        # Overall confidence
        confidence = (
            data_completeness * 0.3 +
            risk_factor * 0.3 +
            retry_penalty * 0.2 +
            historical_similarity * 0.2
        )
        
        state["confidence"] = round(confidence, 2)
        state["confidence_factors"] = {
            "data_completeness": round(data_completeness, 2),
            "risk_factor": round(risk_factor, 2),
            "retry_penalty": round(retry_penalty, 2),
            "historical_similarity": round(historical_similarity, 2),
        }
        
        logger.info(f"✅ Confidence: {state['confidence']:.2f}")
        
        return state
    
    
    # ========== PHASE 13: DECISION ROUTER ==========
    async def route_decision(self, state: DepartmentState) -> DepartmentState:
        """
        Decide: recommend or escalate
        Based on confidence, policy, risk
        """
        logger.info("🔄 [Decision Router] Determining route...")
        
        # Escalation conditions
        should_escalate = False
        escalation_reasons = []
        
        # Condition 1: Low confidence
        if state["confidence"] < self.confidence_threshold:
            should_escalate = True
            escalation_reasons.append(f"Confidence below threshold ({state['confidence']:.2f} < {self.confidence_threshold})")
        
        # Condition 2: Policy violations
        if not state["policy_ok"]:
            should_escalate = True
            escalation_reasons.append(f"Policy violations: {', '.join(state['policy_violations'])}")
        
        # Condition 3: High/Critical risk
        if state["risk_level"] in ["high", "critical"]:
            should_escalate = True
            escalation_reasons.append(f"Risk level: {state['risk_level']}")
        
        # Condition 4: Not feasible after all retries
        if not state["feasible"] and state["attempts"] >= state["max_attempts"]:
            should_escalate = True
            escalation_reasons.append(f"No feasible plan found after {state['attempts']} attempts")
        
        state["escalate"] = should_escalate
        state["escalation_reason"] = "; ".join(escalation_reasons) if escalation_reasons else None
        
        if should_escalate:
            logger.warning(f"⚠️ ESCALATING: {state['escalation_reason']}")
        else:
            logger.info("✅ Proceeding with recommendation")
        
        return state
    
    
    # ========== PHASE 14: OUTPUT GENERATION ==========
    async def generate_output(self, state: DepartmentState) -> DepartmentState:
        """
        Create final structured response
        """
        logger.info("🔄 [Output Generator] Creating final response...")
        
        if state["escalate"]:
            # Escalate response
            response = {
                "decision": "escalate",
                "constraints": None,
                "conditions": [],
                "confidence": state["confidence"],
                "reasoning": state["escalation_reason"],
                "escalation_reason": state["escalation_reason"],
                "recommended_action": "Requires human review and approval",
            }
        else:
            # Recommend response
            if state["feasible"] and state["policy_ok"]:
                decision = "approved"
                conditions = []
                
                # Add conditions based on plan
                current_plan = state["plan"][state["current_plan_index"]]
                if current_plan.get("backup_required"):
                    conditions.append("Emergency backup must be activated")
                
                reasoning = f"Plan is feasible and compliant. {state['feasibility_reason']}"
                recommended_action = f"Approve request with {len(conditions)} condition(s)"
                
            else:
                decision = "denied"
                conditions = []
                reasoning = state["feasibility_reason"]
                recommended_action = "Deny request - constraints not satisfied"
            
            response = {
                "decision": decision,
                "constraints": state["feasibility_reason"],
                "conditions": conditions,
                "confidence": state["confidence"],
                "reasoning": reasoning,
                "escalation_reason": None,
                "recommended_action": recommended_action,
            }
        
        state["response"] = response
        state["processing_time_ms"] = None  # Would calculate actual time
        
        logger.info(f"✅ Output generated: {response['decision']}")
        
        return state
