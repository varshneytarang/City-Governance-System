"""
Add LLM integration to Observer, Policy Validator, Confidence Estimator, and Decision Router

This script contains the complete LLM-enhanced implementations.
"""

# ============================================================
# OBSERVER NODE WITH LLM
# ============================================================

OBSERVER_LLM_CODE = '''"""
PHASE 8: Observer Node (LLM-Enhanced)

Analyze tool outputs using LLM to extract insights.
"""

import logging
import json

from ..state import DepartmentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)


def observer_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 8: Observer Node (LLM-Enhanced)
    
    Uses LLM to analyze tool results and extract insights.
    """
    
    logger.info("👁️  [NODE: Observer]")
    
    try:
        tool_results = state.get("tool_results", {})
        plan = state.get("plan", {})
        
        # Try LLM first
        llm_client = get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for observation analysis...")
            llm_observations = _analyze_with_llm(llm_client, tool_results, plan)
            
            if llm_observations:
                logger.info(f"✓ LLM extracted {len(llm_observations.get('key_observations', []))} observations")
                state["observations"] = llm_observations
                return state
        
        # Fallback to deterministic
        logger.info("Using deterministic fallback")
        observations = _extract_observations_deterministic(tool_results)
        
        logger.info(f"✓ Observations normalized: {len(observations.get('extracted_facts', {}))} facts")
        state["observations"] = observations
        
    except Exception as e:
        logger.error(f"✗ Observer error: {e}")
        state["observations"] = {"error": str(e)}
    
    return state


def _analyze_with_llm(client, tool_results: dict, plan: dict) -> dict:
    """Use LLM to analyze tool results"""
    try:
        prompt = f"""Analyze these tool execution results and extract key insights.

TOOL RESULTS:
{json.dumps(tool_results, indent=2)}

ORIGINAL PLAN:
{json.dumps(plan, indent=2)}

Return ONLY valid JSON:
{{
  "key_observations": ["observation 1", "observation 2", ...],
  "discrepancies": ["any issues or unexpected results"],
  "resource_status": {{"workers": "sufficient/insufficient", "budget": "within/over"}},
  "recommendations": ["action 1", "action 2"]
}}

Focus on:
1. Resource availability vs requirements
2. Any conflicts or issues detected  
3. Comparison with planned actions
4. Risk factors identified"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Water Department observation AI. Analyze tool results and extract actionable insights. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=600
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Clean markdown
        if llm_output.startswith("```json"):
            llm_output = llm_output[7:]
        elif llm_output.startswith("```"):
            llm_output = llm_output[3:]
        if llm_output.endswith("```"):
            llm_output = llm_output[:-3]
        
        return json.loads(llm_output.strip())
        
    except Exception as e:
        logger.warning(f"LLM observation failed: {e}")
        return None


def _extract_observations_deterministic(tool_results: dict) -> dict:
    """Deterministic observation extraction"""
    observations = {
        "raw_results": tool_results,
        "extracted_facts": {}
    }
    
    if "manpower" in tool_results:
        manpower = tool_results["manpower"]
        observations["extracted_facts"]["manpower_sufficient"] = manpower.get("sufficient", False)
        observations["extracted_facts"]["available_workers"] = manpower.get("available_count", 0)
    
    if "schedule" in tool_results:
        schedule = tool_results["schedule"]
        observations["extracted_facts"]["schedule_conflict"] = schedule.get("has_conflicts", False)
    
    if "pipeline_health" in tool_results:
        pipeline = tool_results["pipeline_health"]
        observations["extracted_facts"]["pipeline_condition"] = pipeline.get("overall_condition", "unknown")
    
    return observations
'''

# ============================================================
# POLICY VALIDATOR WITH LLM
# ============================================================

POLICY_VALIDATOR_LLM_CODE = '''"""
PHASE 10: Policy Validator Node (LLM-Enhanced)

Check policy compliance using LLM for flexible interpretation.
"""

import logging
import json

from ..state import DepartmentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)


def policy_validator_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 10: Policy Validator (LLM-Enhanced)
    
    Uses LLM to check policy compliance with context awareness.
    """
    
    logger.info("📋 [NODE: Policy Validator]")
    
    try:
        plan = state.get("plan", {})
        input_event = state.get("input_event", {})
        risk_level = state.get("risk_level", "low")
        
        # Try LLM first
        llm_client = get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for policy validation...")
            llm_result = _validate_with_llm(llm_client, plan, input_event, risk_level)
            
            if llm_result:
                compliant = llm_result.get("compliant", False)
                violations = llm_result.get("violations", [])
                logger.info(f"  → LLM: Policy compliant: {compliant}")
                
                state["policy_ok"] = compliant
                state["policy_violations"] = violations
                return state
        
        # Fallback to deterministic
        logger.info("Using deterministic fallback")
        from ..rules.policy_rules import PolicyValidator
        
        validator = PolicyValidator()
        validation_result = validator.validate(state)
        
        state["policy_ok"] = validation_result.get("compliant", True)
        state["policy_violations"] = validation_result.get("violations", [])
        
        logger.info(f"  → Policy compliant: {state['policy_ok']}")
        
    except Exception as e:
        logger.error(f"✗ Policy validation error: {e}")
        state["policy_ok"] = False
        state["policy_violations"] = [f"Validation error: {str(e)}"]
    
    return state


def _validate_with_llm(client, plan: dict, input_event: dict, risk_level: str) -> dict:
    """Use LLM for policy validation"""
    try:
        prompt = f"""Check if this plan complies with Water Department policies.

PLAN:
{json.dumps(plan, indent=2)}

REQUEST:
{json.dumps(input_event, indent=2)}

RISK LEVEL: {risk_level}

POLICIES:
1. MAX_SHIFT_DELAY_DAYS = 3 (schedule changes cannot exceed 3 days)
2. MIN_MAINTENANCE_NOTICE_HOURS = 24 (maintenance requires 24h notice)
3. MAX_CONCURRENT_PROJECTS = 5 (cannot have more than 5 active projects)
4. EMERGENCY_OVERRIDE = allowed for critical situations

Return ONLY valid JSON:
{{
  "compliant": true/false,
  "violations": ["violation 1 if any", "violation 2 if any"],
  "override_possible": true/false,
  "reasoning": "explanation of compliance decision"
}}

Consider:
1. Emergency overrides are allowed for critical risks
2. Policy violations should be specific
3. Context matters for interpretation"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Water Department policy compliance AI. Check plans against policies with contextual awareness. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Clean markdown
        if llm_output.startswith("```json"):
            llm_output = llm_output[7:]
        elif llm_output.startswith("```"):
            llm_output = llm_output[3:]
        if llm_output.endswith("```"):
            llm_output = llm_output[:-3]
        
        return json.loads(llm_output.strip())
        
    except Exception as e:
        logger.warning(f"LLM policy validation failed: {e}")
        return None
'''

# ============================================================
# CONFIDENCE ESTIMATOR WITH LLM
# ============================================================

CONFIDENCE_ESTIMATOR_LLM_CODE = '''"""
PHASE 12: Confidence Estimator (LLM-Enhanced)

Calculate confidence score using LLM's assessment.
"""

import logging
import json

from ..state import DepartmentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)


def confidence_estimator_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 12: Confidence Estimator (LLM-Enhanced)
    
    Uses LLM to calculate confidence score (0.0-1.0).
    """
    
    logger.info("🎯 [NODE: Confidence Estimator]")
    
    try:
        plan = state.get("plan", {})
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        risk_level = state.get("risk_level", "medium")
        observations = state.get("observations", {})
        
        # Try LLM first
        llm_client = get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for confidence estimation...")
            llm_result = _estimate_with_llm(llm_client, plan, feasible, policy_ok, risk_level, observations)
            
            if llm_result and "confidence" in llm_result:
                confidence = llm_result["confidence"]
                logger.info(f"  → LLM Confidence: {confidence:.2f} (0.0-1.0)")
                state["confidence"] = confidence
                return state
        
        # Fallback to deterministic
        logger.info("Using deterministic fallback")
        from ..rules.confidence_calculator import ConfidenceCalculator
        
        calculator = ConfidenceCalculator()
        confidence = calculator.calculate(state)
        
        logger.info(f"  → Confidence: {confidence:.2f} (0.0-1.0)")
        state["confidence"] = confidence
        
    except Exception as e:
        logger.error(f"✗ Confidence estimation error: {e}")
        state["confidence"] = 0.5  # Medium confidence on error
    
    return state


def _estimate_with_llm(client, plan: dict, feasible: bool, policy_ok: bool, risk_level: str, observations: dict) -> dict:
    """Use LLM to estimate confidence"""
    try:
        prompt = f"""Estimate confidence (0.0-1.0) for this recommendation.

PLAN:
{json.dumps(plan, indent=2)}

STATUS:
- Feasible: {feasible}
- Policy Compliant: {policy_ok}
- Risk Level: {risk_level}

OBSERVATIONS:
{json.dumps(observations, indent=2)}

Return ONLY valid JSON:
{{
  "confidence": 0.85,
  "confidence_factors": {{
    "data_quality": 0.9,
    "plan_completeness": 0.8,
    "risk_assessment": 0.9
  }},
  "reasoning": "explanation of confidence level"
}}

Confidence scale:
- 0.9-1.0: Very high confidence, all factors positive
- 0.7-0.9: High confidence, minor concerns
- 0.5-0.7: Medium confidence, some uncertainties
- 0.3-0.5: Low confidence, significant concerns
- 0.0-0.3: Very low confidence, major issues"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Water Department confidence estimation AI. Calculate confidence scores based on multiple factors. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Clean markdown
        if llm_output.startswith("```json"):
            llm_output = llm_output[7:]
        elif llm_output.startswith("```"):
            llm_output = llm_output[3:]
        if llm_output.endswith("```"):
            llm_output = llm_output[:-3]
        
        return json.loads(llm_output.strip())
        
    except Exception as e:
        logger.warning(f"LLM confidence estimation failed: {e}")
        return None
'''

# ============================================================
# DECISION ROUTER WITH LLM
# ============================================================

DECISION_ROUTER_LLM_CODE = '''"""
PHASE 13: Decision Router (LLM-Enhanced)

Route decision: RECOMMEND or ESCALATE using LLM.
"""

import logging
import json

from ..state import DepartmentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)


def decision_router_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 13: Decision Router (LLM-Enhanced)
    
    Uses LLM to decide: RECOMMEND or ESCALATE.
    """
    
    logger.info("🔀 [NODE: Decision Router]")
    
    try:
        confidence = state.get("confidence", 0.0)
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        risk_level = state.get("risk_level", "medium")
        plan = state.get("plan", {})
        
        # Try LLM first
        llm_client = get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for routing decision...")
            llm_result = _route_with_llm(llm_client, confidence, feasible, policy_ok, risk_level, plan)
            
            if llm_result and "decision" in llm_result:
                decision = llm_result["decision"]
                reasoning = llm_result.get("reasoning", "")
                
                if decision == "recommend":
                    logger.info("✓ RECOMMEND: LLM approved")
                    state["escalate"] = False
                else:
                    logger.warning("⚠️  ESCALATE: LLM requires human review")
                    state["escalate"] = True
                    state["escalation_reason"] = reasoning
                
                return state
        
        # Fallback to deterministic
        logger.info("Using deterministic fallback")
        
        # Rule-based decision
        if not feasible:
            logger.warning("⚠️  ESCALATE: Plan is not feasible")
            state["escalate"] = True
            state["escalation_reason"] = "Plan failed feasibility check"
        elif not policy_ok:
            logger.warning("⚠️  ESCALATE: Policy violation detected")
            state["escalate"] = True
            state["escalation_reason"] = "Policy compliance failed"
        elif risk_level == "critical":
            logger.warning("⚠️  ESCALATE: Critical risk level")
            state["escalate"] = True
            state["escalation_reason"] = "Risk level is critical"
        elif confidence < settings.CONFIDENCE_THRESHOLD:
            logger.warning(f"⚠️  ESCALATE: Low confidence ({confidence:.2f} < {settings.CONFIDENCE_THRESHOLD})")
            state["escalate"] = True
            state["escalation_reason"] = f"Confidence too low: {confidence:.2f}"
        else:
            logger.info("✓ RECOMMEND: All checks passed")
            state["escalate"] = False
        
    except Exception as e:
        logger.error(f"✗ Router error: {e}")
        state["escalate"] = True
        state["escalation_reason"] = f"Router error: {str(e)}"
    
    return state


def _route_with_llm(client, confidence: float, feasible: bool, policy_ok: bool, risk_level: str, plan: dict) -> dict:
    """Use LLM for routing decision"""
    try:
        prompt = f"""Decide whether to RECOMMEND or ESCALATE this plan.

STATUS:
- Confidence: {confidence:.2f}
- Feasible: {feasible}
- Policy Compliant: {policy_ok}
- Risk Level: {risk_level}

PLAN:
{json.dumps(plan, indent=2)}

THRESHOLD: Confidence must be >= 0.7 to recommend

Return ONLY valid JSON:
{{
  "decision": "recommend" or "escalate",
  "reasoning": "detailed explanation of the decision"
}}

RECOMMEND if:
- All checks pass (feasible, policy compliant)
- Confidence >= 0.7
- Risk level is low or medium

ESCALATE if:
- Any check fails
- Confidence < 0.7
- Risk level is high or critical
- Any significant concerns"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Water Department decision routing AI. Decide whether to recommend or escalate plans. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=400
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Clean markdown
        if llm_output.startsWith("```json"):
            llm_output = llm_output[7:]
        elif llm_output.startswith("```"):
            llm_output = llm_output[3:]
        if llm_output.endswith("```"):
            llm_output = llm_output[:-3]
        
        return json.loads(llm_output.strip())
        
    except Exception as e:
        logger.warning(f"LLM routing failed: {e}")
        return None
'''

if __name__ == "__main__":
    print("LLM Integration Code Ready!")
    print("\nThis file contains the complete LLM-enhanced implementations for:")
    print("  1. Observer Node")
    print("  2. Policy Validator Node")
    print("  3. Confidence Estimator Node")
    print("  4. Decision Router Node")
    print("\nCopy each section to replace the corresponding node file.")
