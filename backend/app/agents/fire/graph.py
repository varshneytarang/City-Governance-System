"""
Fire Agent LangGraph Workflow

Main workflow implementation for the Fire Department Agent using LangGraph.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
import os

from app.agents.fire.state import FireState
from app.agents.fire import tools, prompts, policies
from app.database import get_async_db


class FireAgent:
    """
    Fire Department Agent using LangGraph for emergency response and fire safety operations
    """
    
    def __init__(self, db_session):
        self.db = db_session
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    async def input_validation_node(self, state: FireState) -> FireState:
        """
        Node 1: Validate input request
        """
        errors = []
        
        # Required fields check
        if not state.get("request_type"):
            errors.append("request_type is required")
        
        if not state.get("location"):
            errors.append("location is required")
        
        if not state.get("description"):
            errors.append("description is required")
        
        # Emergency-specific validation
        if state.get("request_type") == "emergency_response":
            if not state.get("emergency_type"):
                errors.append("emergency_type is required for emergency response")
            
            if state.get("casualties") is None:
                state["casualties"] = 0
        
        # Set validation result
        if errors:
            state["validation_status"] = "invalid"
            state["validation_errors"] = errors
        else:
            state["validation_status"] = "valid"
            state["validation_errors"] = []
        
        state["current_node"] = "input_validation"
        return state
    
    async def data_collection_node(self, state: FireState) -> FireState:
        """
        Node 2: Collect data from database
        """
        location = state["location"]
        
        # Fetch nearby fire stations
        nearby_stations = await tools.fetch_nearby_stations(
            self.db,
            location,
            max_distance_km=15.0
        )
        state["nearby_stations"] = nearby_stations
        
        # Get station distances
        station_distances = {s["id"]: s["distance_km"] for s in nearby_stations}
        state["station_distances"] = station_distances
        
        # Get available resources from nearby stations
        if nearby_stations:
            station_ids = [s["id"] for s in nearby_stations]
            station_resources = await tools.get_available_resources(self.db, station_ids)
            state["station_resources"] = station_resources
            
            # Calculate total resources
            total_personnel = sum(r["personnel_count"] for r in station_resources.values())
            total_vehicles = sum(r["vehicle_count"] for r in station_resources.values())
            state["total_personnel"] = total_personnel
            state["total_vehicles"] = total_vehicles
        
        # Check active incidents
        active_incidents = await tools.check_active_incidents(
            self.db,
            location,
            radius_km=5.0
        )
        state["active_incidents"] = active_incidents
        
        # Get historical patterns
        incident_type = state.get("emergency_type")
        historical_patterns = await tools.get_historical_incident_patterns(
            self.db,
            location,
            incident_type=incident_type,
            days=90
        )
        state["incident_patterns"] = historical_patterns
        
        state["current_node"] = "data_collection"
        return state
    
    async def analysis_node(self, state: FireState) -> FireState:
        """
        Node 3: Analyze incident and perform risk assessment
        """
        request_type = state["request_type"]
        
        # Calculate severity score for emergencies
        if request_type == "emergency_response":
            incident_type = state.get("emergency_type", "other")
            casualties = state.get("casualties", 0)
            building_type = state.get("building_type")
            fire_intensity = state.get("fire_intensity")
            
            severity_score = tools.assess_severity_score(
                incident_type,
                casualties,
                building_type,
                fire_intensity
            )
            
            # Determine severity level
            if severity_score >= 70:
                severity_level = "Critical"
            elif severity_score >= 50:
                severity_level = "High"
            elif severity_score >= 30:
                severity_level = "Medium"
            else:
                severity_level = "Low"
            
            state["severity_assessment"] = {
                "level": severity_level,
                "score": severity_score,
                "factors": [
                    f"Incident type: {incident_type}",
                    f"Casualties: {casualties}",
                    f"Building type: {building_type or 'N/A'}",
                    f"Fire intensity: {fire_intensity or 'N/A'}"
                ]
            }
            
            # Calculate required resources
            required_resources = tools.calculate_required_resources(
                severity_score,
                incident_type,
                building_type
            )
            state["response_requirements"] = required_resources
            
            # Create dispatch plan
            dispatch_plan = await tools.create_dispatch_plan(
                self.db,
                state["nearby_stations"],
                required_resources,
                state["location"]
            )
            state["dispatch_plan"] = dispatch_plan
            state["estimated_response_time"] = dispatch_plan["estimated_eta"]
        
        # Determine risk level
        if request_type == "emergency_response":
            severity_level = state["severity_assessment"]["level"]
            if severity_level == "Critical":
                risk_level = "critical"
            elif severity_level == "High":
                risk_level = "high"
            else:
                risk_level = "medium"
        else:
            risk_level = "low"
        
        state["risk_level"] = risk_level
        
        # Build LLM analysis prompt
        if request_type == "emergency_response":
            prompt = self._build_emergency_prompt(state)
        elif request_type == "fire_inspection":
            prompt = self._build_inspection_prompt(state)
        elif request_type == "awareness_program":
            prompt = self._build_awareness_prompt(state)
        else:
            prompt = self._build_maintenance_prompt(state)
        
        # Get LLM analysis
        response = await self.llm.ainvoke(prompt)
        state["llm_analysis"] = response.content
        
        state["current_node"] = "analysis"
        return state
    
    async def decision_node(self, state: FireState) -> FireState:
        """
        Node 4: Make decision based on policies and analysis
        """
        # Apply safety policy
        safety_result = policies.apply_safety_policy(state)
        state["safety_check_passed"] = safety_result["passed"]
        state["risk_factors"] = safety_result["issues"]
        
        # Apply resource policy
        resource_result = policies.apply_resource_policy(state)
        state["resource_check_passed"] = resource_result["passed"]
        
        # Apply coordination policy
        coordination_result = policies.apply_coordination_policy(state)
        state["coordination_required"] = coordination_result["required"]
        state["departments_to_notify"] = coordination_result["departments"]
        
        # Apply escalation policy
        escalation_result = policies.apply_escalation_policy(state)
        state["escalation_required"] = escalation_result["required"]
        
        # Get dispatch decision
        dispatch_decision = policies.apply_dispatch_policy(state)
        state["decision"] = dispatch_decision["decision"]
        state["reasoning"] = dispatch_decision["reasoning"]
        
        # Calculate costs and duration
        state["estimated_cost"] = policies.calculate_estimated_cost(state)
        state["estimated_duration"] = policies.calculate_estimated_duration(state)
        
        # Set conditions
        conditions = []
        if not safety_result["passed"]:
            conditions.extend(safety_result["actions"])
        if not resource_result["passed"]:
            conditions.extend(resource_result["recommendations"])
        
        state["conditions"] = conditions
        
        state["current_node"] = "decision"
        return state
    
    async def coordination_node(self, state: FireState) -> FireState:
        """
        Node 5: Handle cross-department coordination
        """
        if state.get("coordination_required", False):
            departments = state.get("departments_to_notify", [])
            
            # Build coordination messages
            messages = []
            coordination_result = policies.apply_coordination_policy(state)
            
            for dept in departments:
                reason = coordination_result["reasons"].get(dept, "Coordination required")
                messages.append({
                    "to_department": dept,
                    "from_department": "Fire Department",
                    "message_type": "coordination_request",
                    "priority": state.get("priority", "medium"),
                    "content": {
                        "incident_type": state.get("emergency_type", state.get("request_type")),
                        "location": state["location"],
                        "reason": reason,
                        "urgency": "immediate" if state.get("risk_level") == "critical" else "standard"
                    }
                })
            
            state["coordination_messages"] = messages
            state["coordination_status"] = "completed"
        else:
            state["coordination_messages"] = []
            state["coordination_status"] = "not_required"
        
        state["current_node"] = "coordination"
        return state
    
    async def response_node(self, state: FireState) -> FireState:
        """
        Node 6: Generate final response
        """
        request_type = state["request_type"]
        decision = state["decision"]
        
        # Build action items
        action_items = []
        
        if request_type == "emergency_response" and decision in ["APPROVE", "ESCALATE"]:
            dispatch_plan = state.get("dispatch_plan", {})
            for station_dispatch in dispatch_plan.get("stations", []):
                action_items.append(
                    f"Dispatch {station_dispatch['station_name']}: "
                    f"{station_dispatch['personnel']} personnel, "
                    f"{station_dispatch['vehicles']} vehicles, "
                    f"ETA {station_dispatch['eta_minutes']} minutes"
                )
            
            if state.get("conditions"):
                action_items.extend(state["conditions"])
        
        # Build next steps
        next_steps = []
        if state.get("coordination_required"):
            next_steps.append("Coordinate with: " + ", ".join(state["departments_to_notify"]))
        
        if state.get("escalation_required"):
            escalation = policies.apply_escalation_policy(state)
            next_steps.append(f"Escalate to: {escalation['escalation_level']}")
        
        state["action_items"] = action_items
        state["next_steps"] = next_steps
        
        # Build response
        response = {
            "request_id": state["request_id"],
            "decision": decision,
            "reasoning": state["reasoning"],
            "estimated_cost": state["estimated_cost"],
            "estimated_duration": state["estimated_duration"],
            "risk_level": state["risk_level"],
            "conditions": state.get("conditions", []),
            "action_items": action_items,
            "next_steps": next_steps,
            "llm_analysis": state.get("llm_analysis", ""),
            "dispatch_plan": state.get("dispatch_plan", {}),
            "coordination_status": state.get("coordination_status", "not_required")
        }
        
        state["response"] = response
        state["workflow_status"] = "completed"
        state["current_node"] = "response"
        
        return state
    
    def _build_emergency_prompt(self, state: FireState) -> str:
        """Build emergency analysis prompt"""
        nearby_stations = state.get("nearby_stations", [])
        stations_info = "\n".join([
            f"- {s['name']}: {s['distance_km']}km away, "
            f"{s['personnel_count']} personnel, {s['vehicle_count']} vehicles"
            for s in nearby_stations[:5]
        ]) or "No stations found"
        
        active_incidents = state.get("active_incidents", [])
        incidents_info = "\n".join([
            f"- {i['incident_type']} ({i['severity']}): {i['distance_km']}km away, Status: {i['status']}"
            for i in active_incidents
        ]) or "No active incidents"
        
        patterns = state.get("incident_patterns", {})
        patterns_info = f"Total: {patterns.get('total_incidents', 0)}, Types: {patterns.get('incident_types', {})}"
        
        response_req = state.get("response_requirements", {})
        
        return prompts.EMERGENCY_ANALYSIS_PROMPT.format(
            incident_type=state.get("emergency_type", "unknown"),
            location_address=state["location"].get("address", "Unknown"),
            description=state["description"],
            casualties=state.get("casualties", 0),
            building_type=state.get("building_type", "N/A"),
            fire_intensity=state.get("fire_intensity", "N/A"),
            priority=state.get("priority", "medium"),
            station_count=len(nearby_stations),
            stations_info=stations_info,
            active_incidents=incidents_info,
            historical_patterns=patterns_info,
            required_personnel=response_req.get("personnel", 4),
            required_vehicles=response_req.get("vehicles", 1),
            required_equipment=", ".join(response_req.get("equipment", []))
        )
    
    def _build_inspection_prompt(self, state: FireState) -> str:
        """Build inspection analysis prompt"""
        nearby_stations = state.get("nearby_stations", [])
        stations_info = "\n".join([
            f"- {s['name']}: {s['distance_km']}km away"
            for s in nearby_stations[:3]
        ]) or "No stations found"
        
        patterns = state.get("incident_patterns", {})
        patterns_info = f"Total incidents: {patterns.get('total_incidents', 0)}, Types: {patterns.get('incident_types', {})}"
        
        return prompts.INSPECTION_ANALYSIS_PROMPT.format(
            request_type=state["request_type"],
            inspection_location=state.get("inspection_location", state["location"].get("address")),
            description=state["description"],
            priority=state.get("priority", "medium"),
            stations_info=stations_info,
            historical_patterns=patterns_info
        )
    
    def _build_awareness_prompt(self, state: FireState) -> str:
        """Build awareness program prompt"""
        patterns = state.get("incident_patterns", {})
        patterns_info = f"Total incidents: {patterns.get('total_incidents', 0)}, Types: {patterns.get('incident_types', {})}"
        
        return prompts.AWARENESS_ANALYSIS_PROMPT.format(
            request_type=state["request_type"],
            target_audience=state.get("target_audience", "General public"),
            location_address=state["location"].get("address", "Unknown"),
            description=state["description"],
            historical_patterns=patterns_info
        )
    
    def _build_maintenance_prompt(self, state: FireState) -> str:
        """Build maintenance analysis prompt"""
        station_resources = state.get("station_resources", {})
        resources_info = "Station resources loaded"
        
        active_incidents = state.get("active_incidents", [])
        incidents_info = f"{len(active_incidents)} active incidents in area"
        
        return prompts.MAINTENANCE_ANALYSIS_PROMPT.format(
            equipment_type=state.get("equipment_type", "General equipment"),
            station_name="Fire Station",
            description=state["description"],
            priority=state.get("priority", "medium"),
            station_resources=resources_info,
            active_incidents=incidents_info
        )


def should_coordinate(state: FireState) -> str:
    """
    Conditional edge: determine if coordination is needed
    """
    if state.get("coordination_required", False):
        return "coordination"
    else:
        return "response"


def create_fire_agent_workflow(db_session):
    """
    Create and compile the Fire Agent workflow
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create agent instance
    agent = FireAgent(db_session)
    
    # Create workflow
    workflow = StateGraph(FireState)
    
    # Add nodes
    workflow.add_node("validate_input", agent.input_validation_node)
    workflow.add_node("collect_data", agent.data_collection_node)
    workflow.add_node("analyze", agent.analysis_node)
    workflow.add_node("make_decision", agent.decision_node)
    workflow.add_node("coordinate", agent.coordination_node)
    workflow.add_node("generate_response", agent.response_node)
    
    # Set entry point
    workflow.set_entry_point("validate_input")
    
    # Add edges
    workflow.add_edge("validate_input", "collect_data")
    workflow.add_edge("collect_data", "analyze")
    workflow.add_edge("analyze", "make_decision")
    
    # Conditional edge for coordination
    workflow.add_conditional_edges(
        "make_decision",
        should_coordinate,
        {
            "coordination": "coordinate",
            "response": "generate_response"
        }
    )
    
    workflow.add_edge("coordinate", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Compile and return
    return workflow.compile()
