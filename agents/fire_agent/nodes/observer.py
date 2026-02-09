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
        
        # Extract key facts from fire-specific tool results
        if "check_truck_availability" in tool_results:
            trucks = tool_results["check_truck_availability"]
            observations["extracted_facts"]["trucks_sufficient"] = trucks.get("sufficient", False)
            observations["extracted_facts"]["available_trucks"] = trucks.get("available_count", 0)
            observations["extracted_facts"]["truck_details"] = trucks.get("details", "")
        
        if "check_firefighter_availability" in tool_results:
            firefighters = tool_results["check_firefighter_availability"]
            observations["extracted_facts"]["firefighters_sufficient"] = firefighters.get("sufficient", False)
            observations["extracted_facts"]["available_firefighters"] = firefighters.get("available_count", 0)
            observations["extracted_facts"]["required_firefighters"] = firefighters.get("required_count", 0)
        
        if "check_equipment_status" in tool_results:
            equipment = tool_results["check_equipment_status"]
            observations["extracted_facts"]["equipment_condition"] = equipment.get("overall_condition", "unknown")
            observations["extracted_facts"]["maintenance_needed"] = equipment.get("maintenance_needed", False)
            observations["extracted_facts"]["available_equipment"] = equipment.get("available_count", 0)
        
        if "assess_response_time" in tool_results:
            response = tool_results["assess_response_time"]
            observations["extracted_facts"]["estimated_response_minutes"] = response.get("estimated_minutes", 0)
            observations["extracted_facts"]["response_acceptable"] = response.get("within_threshold", False)
            observations["extracted_facts"]["distance_km"] = response.get("distance_km", 0)
        
        if "check_hydrant_status" in tool_results:
            hydrants = tool_results["check_hydrant_status"]
            observations["extracted_facts"]["hydrants_available"] = hydrants.get("available_count", 0)
            observations["extracted_facts"]["hydrant_pressure_ok"] = hydrants.get("pressure_ok", False)
        
        if "get_incident_history" in tool_results:
            incidents = tool_results["get_incident_history"]
            observations["extracted_facts"]["historical_incidents"] = incidents.get("total_incidents", 0)
            observations["extracted_facts"]["similar_incidents"] = incidents.get("similar_count", 0)
        
        if "estimate_resource_needs" in tool_results:
            resources = tool_results["estimate_resource_needs"]
            observations["extracted_facts"]["estimated_trucks_needed"] = resources.get("trucks_needed", 0)
            observations["extracted_facts"]["estimated_firefighters_needed"] = resources.get("firefighters_needed", 0)
        
        if "check_station_capacity" in tool_results:
            station = tool_results["check_station_capacity"]
            observations["extracted_facts"]["station_capacity_ok"] = station.get("capacity_ok", False)
            observations["extracted_facts"]["on_duty_count"] = station.get("on_duty_count", 0)
        
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
                {"role": "system", "content": "You are a Fire Department observation AI. Analyze tool results and extract actionable insights for emergency response. Always return valid JSON."},
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
