"""
PHASE 8: Observer Node (LLM-Enhanced)

Analyze tool outputs using LLM to extract insights.
"""

import logging
import json

from ..state import DepartmentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)

# Compatibility alias for tests that patch `_get_llm_client`
_get_llm_client = get_llm_client


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
        tool_results = state.get("tool_results", {})
        
        # Normalize observations into a consistent structure
        observations = {
            "raw_results": tool_results,
            "extracted_facts": {}
        }
        
        # Extract key facts from tool results
        if "manpower" in tool_results:
            manpower = tool_results["manpower"]
            observations["extracted_facts"]["manpower_sufficient"] = manpower.get("sufficient", False)
            observations["extracted_facts"]["available_workers"] = manpower.get("available_count", 0)
            observations["extracted_facts"]["required_workers"] = manpower.get("required_count", 0)
        
        if "schedule" in tool_results:
            schedule = tool_results["schedule"]
            observations["extracted_facts"]["schedule_conflict"] = schedule.get("has_conflicts", False)
            observations["extracted_facts"]["scheduled_activities"] = schedule.get("activity_count", 0)
        
        if "pipeline_health" in tool_results:
            pipeline = tool_results["pipeline_health"]
            observations["extracted_facts"]["pipeline_condition"] = pipeline.get("overall_condition", "unknown")
            observations["extracted_facts"]["critical_pipeline_issues"] = pipeline.get("critical_issues", 0)
        
        if "reservoir_levels" in tool_results:
            reservoir = tool_results["reservoir_levels"]
            observations["extracted_facts"]["reservoir_status"] = reservoir.get("overall_status", "unknown")
            observations["extracted_facts"]["critical_reservoirs"] = reservoir.get("critical_count", 0)
        
        if "zone_risk" in tool_results:
            risk = tool_results["zone_risk"]
            observations["extracted_facts"]["zone_risk_level"] = risk.get("risk_level", "unknown")
            observations["extracted_facts"]["zone_risk_factors"] = risk.get("contributing_factors", [])
        
        state["observations"] = observations
        logger.info(f"✓ Observations normalized: {len(observations.get('extracted_facts', {}))} facts")
        
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
