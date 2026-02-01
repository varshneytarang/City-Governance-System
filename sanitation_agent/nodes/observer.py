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


def observer_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 8: Observer Node (LLM-Enhanced)
    
    Uses LLM to analyze tool results and extract insights.
    """
    
    logger.info("👁️  [NODE: Observer]")
    
    try:
        tool_results = state.get("tool_results", {})
        plan = state.get("plan", {})
        
        # Try LLM first (only if enabled)
        llm_client = get_llm_client()
        if llm_client and settings.USE_LLM_FOR_OBSERVER:
            logger.info("🤖 Using LLM for observation analysis...")
            llm_observations = _analyze_with_llm(llm_client, tool_results, plan)
            
            if llm_observations:
                logger.info(f"✓ LLM extracted {len(llm_observations.get('key_observations', []))} observations")
                state["observations"] = llm_observations
                return state
        
        # Fallback to deterministic
        logger.info("Using deterministic fallback")
        
        # Normalize observations into a consistent structure
        observations = {
            "raw_results": tool_results,
            "extracted_facts": {}
        }
        
        # Extract key facts from tool results
        if "truck_availability" in tool_results:
            trucks = tool_results["truck_availability"]
            observations["extracted_facts"]["trucks_sufficient"] = trucks.get("sufficient", False)
            observations["extracted_facts"]["available_trucks"] = trucks.get("available_count", 0)
            observations["extracted_facts"]["required_trucks"] = trucks.get("required_count", 0)
        
        if "route_capacity" in tool_results:
            route = tool_results["route_capacity"]
            observations["extracted_facts"]["route_overloaded"] = route.get("overloaded", False)
            observations["extracted_facts"]["route_current_load"] = route.get("current_load", 0)
            observations["extracted_facts"]["route_max_capacity"] = route.get("max_capacity", 0)
        
        if "landfill_capacity" in tool_results:
            landfill = tool_results["landfill_capacity"]
            observations["extracted_facts"]["landfill_available"] = len(landfill.get("available_landfills", []))
            observations["extracted_facts"]["landfill_overloaded"] = landfill.get("all_overloaded", False)
        
        if "collection_delay" in tool_results:
            delay = tool_results["collection_delay"]
            observations["extracted_facts"]["route_delayed"] = delay.get("delayed", False)
            observations["extracted_facts"]["days_delayed"] = delay.get("days_delayed", 0)
        
        if "equipment_status" in tool_results:
            equipment = tool_results["equipment_status"]
            observations["extracted_facts"]["equipment_condition"] = equipment.get("overall_condition", "unknown")
            observations["extracted_facts"]["maintenance_needed"] = equipment.get("maintenance_needed", False)
        
        if "complaint_history" in tool_results:
            complaints = tool_results["complaint_history"]
            observations["extracted_facts"]["complaint_count"] = complaints.get("total_complaints", 0)
            observations["extracted_facts"]["high_complaint_area"] = complaints.get("complaint_count", 0) > 10
        
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
  "resource_status": {{"trucks": "sufficient/insufficient", "workers": "sufficient/insufficient", "budget": "within/over"}},
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
                {"role": "system", "content": "You are a Sanitation Department observation AI. Analyze tool results and extract actionable insights. Always return valid JSON."},
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
