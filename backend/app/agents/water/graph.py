"""
Water Agent LangGraph Workflow
Main workflow definition with nodes and routing logic
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
import os

from .state import WaterState
from .tools import (
    fetch_pipeline_data,
    check_conflicts_with_projects,
    get_reservoir_status,
    estimate_water_demand,
    check_incident_history,
    assess_risk_level
)
from .policies import (
    apply_safety_policy,
    apply_resource_policy,
    apply_coordination_policy,
    calculate_priority_score,
    estimate_project_cost,
    determine_response_timeline
)
from .prompts import (
    WATER_SYSTEM_PROMPT,
    CONFLICT_ANALYSIS_PROMPT,
    ROAD_DIGGING_DECISION_PROMPT,
    LEAKAGE_RESPONSE_PROMPT,
    NEW_PROJECT_ANALYSIS_PROMPT
)


class WaterAgent:
    """Water Supply and Drainage Management Agent"""
    
    def __init__(self, db_session: AsyncSession, llm: ChatGroq = None):
        self.db = db_session
        self.llm = llm if llm else ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.agent_name = "water_agent"
    
    async def input_validation_node(self, state: WaterState) -> WaterState:
        """Validate and normalize input request"""
        print(f"🔍 [{self.agent_name}] Validating input...")
        
        # Add metadata
        state["agent_name"] = self.agent_name
        state["timestamp"] = datetime.now().isoformat()
        state["current_step"] = "input_validation"
        
        # Initialize lists with empty values if not present
        if "conflicts_detected" not in state:
            state["conflicts_detected"] = []
        if "notifications" not in state:
            state["notifications"] = []
        if "messages_to_send" not in state:
            state["messages_to_send"] = []
        if "reasoning_chain" not in state:
            state["reasoning_chain"] = []
        
        # Normalize location to zone
        location = state.get("location", "")
        if "zone-1" in location.lower() or "downtown" in location.lower():
            state["zone"] = "Zone-1"
        elif "zone-2" in location.lower() or "east" in location.lower():
            state["zone"] = "Zone-2"
        elif "zone-3" in location.lower() or "north" in location.lower():
            state["zone"] = "Zone-3"
        else:
            state["zone"] = "Zone-1"  # Default
        
        state["reasoning_chain"].append(f"Input validated: {state['request_type']} at {state['location']}")
        return state
    
    async def data_collection_node(self, state: WaterState) -> WaterState:
        """Collect relevant data from database"""
        print(f"📊 [{self.agent_name}] Collecting data...")
        
        state["current_step"] = "data_collection"
        location = state["location"]
        
        # Fetch pipeline data
        pipelines = await fetch_pipeline_data(self.db, location)
        state["pipeline_data"] = pipelines
        
        # Check project conflicts
        conflicts = await check_conflicts_with_projects(self.db, location)
        state["nearby_projects"] = conflicts
        
        # Get reservoir status
        reservoir_status = await get_reservoir_status(self.db)
        state["reservoir_levels"] = reservoir_status
        
        # Check incident history
        incident_history = await check_incident_history(self.db, location)
        
        state["reasoning_chain"].append(
            f"Data collected: {len(pipelines)} pipelines, {len(conflicts)} conflicts, "
            f"reservoir at {reservoir_status.get('average_level_percentage', 0)}%"
        )
        
        return state
    
    async def conflict_analysis_node(self, state: WaterState) -> WaterState:
        """Analyze conflicts and assess risks using LLM"""
        print(f"⚠️ [{self.agent_name}] Analyzing conflicts...")
        
        state["current_step"] = "conflict_analysis"
        
        # Prepare context for LLM
        pipeline_summary = "\n".join([
            f"- {p['location']}: {p['type']} pipeline, {p['condition']} condition, {p['risk_level']} risk"
            for p in state["pipeline_data"][:5]
        ]) or "No pipelines found in immediate area"
        
        project_summary = "\n".join([
            f"- {p['project_type']} at {p['location']}, status: {p['status']}, priority: {p['priority']}"
            for p in state["nearby_projects"]
        ]) or "No active projects in area"
        
        # Create LLM prompt
        prompt = CONFLICT_ANALYSIS_PROMPT.format(
            request_type=state["request_type"],
            location=state["location"],
            zone=state["zone"],
            priority=state["priority"],
            pipeline_data=pipeline_summary,
            nearby_projects=project_summary,
            incident_history="Normal",
            reservoir_status=f"{state['reservoir_levels'].get('average_level_percentage', 0)}% - {state['reservoir_levels'].get('status', 'unknown')}"
        )
        
        # Get LLM analysis
        try:
            messages = [
                SystemMessage(content=WATER_SYSTEM_PROMPT.format(
                    pipeline_count=len(state["pipeline_data"]),
                    avg_condition="fair",
                    reservoir_level=state["reservoir_levels"].get('average_level_percentage', 0),
                    active_projects=len(state["nearby_projects"]),
                    recent_incidents=0
                )),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            llm_analysis = response.content
            
            state["reasoning_chain"].append(f"LLM Analysis: {llm_analysis[:200]}...")
        
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}, using rule-based fallback")
            llm_analysis = "Fallback to rule-based analysis"
        
        # Detect conflicts
        if state["nearby_projects"]:
            state["conflicts_detected"].extend([
                f"Active {p['project_type']} project at {p['location']}"
                for p in state["nearby_projects"]
            ])
        
        # Calculate risk assessment
        pipeline_conditions = [p.get("condition", "unknown") for p in state["pipeline_data"]]
        worst_condition = "fair"
        if "critical" in pipeline_conditions:
            worst_condition = "critical"
        elif "poor" in pipeline_conditions:
            worst_condition = "poor"
        
        state["risk_assessment"] = assess_risk_level(
            pipeline_condition=worst_condition,
            conflicts_count=len(state["conflicts_detected"]),
            incident_history=0,
            reservoir_status=state["reservoir_levels"].get("status", "normal")
        )
        
        state["impact_analysis"] = llm_analysis
        
        return state
    
    async def decision_node(self, state: WaterState) -> WaterState:
        """Make decision based on analysis and policies"""
        print(f"✅ [{self.agent_name}] Making decision...")
        
        state["current_step"] = "decision"
        
        # Apply safety policy
        pipeline_condition = state["pipeline_data"][0]["condition"] if state["pipeline_data"] else "unknown"
        safety_decision = apply_safety_policy(pipeline_condition, state["risk_assessment"])
        
        # Apply resource policy for new projects
        if state["request_type"] == "new_project":
            reservoir_level = state["reservoir_levels"].get("average_level_percentage", 100)
            resource_decision = apply_resource_policy(reservoir_level, 10.0)
            
            if not resource_decision["allowed"]:
                state["decision"] = "deny"
                state["reasoning_chain"].append(f"Decision: DENY - {resource_decision['reason']}")
                state["action_plan"] = {"reason": resource_decision["reason"], "required_action": resource_decision.get("required_action", "")}
                state["confidence"] = 0.95
                return state
        
        # Determine decision
        if not safety_decision["allowed"]:
            state["decision"] = "deny"
            state["reasoning_chain"].append(f"Decision: DENY - {safety_decision['reason']}")
        elif state["conflicts_detected"]:
            state["decision"] = "coordinate"
            state["reasoning_chain"].append("Decision: COORDINATE - Conflicts detected, coordination required")
        elif state["risk_assessment"] in ["high", "critical"]:
            state["decision"] = "escalate"
            state["reasoning_chain"].append("Decision: ESCALATE - High risk requires senior approval")
        else:
            state["decision"] = "approve"
            state["reasoning_chain"].append("Decision: APPROVE - Safe to proceed with conditions")
        
        # Generate action plan
        state["action_plan"] = {
            "decision": state["decision"],
            "conditions": safety_decision.get("conditions", []),
            "reason": safety_decision.get("reason", ""),
            "next_steps": self._generate_next_steps(state)
        }
        
        # Calculate estimates
        costs = estimate_project_cost(
            request_type=state["request_type"],
            pipeline_length_m=state["details"].get("length_m", 0),
            repairs_needed=state["risk_assessment"] in ["high", "critical"]
        )
        state["estimated_cost"] = costs["total"]
        
        timeline = determine_response_timeline(
            request_type=state["request_type"],
            severity=state["risk_assessment"],
            priority_score=calculate_priority_score(
                state["request_type"],
                state["risk_assessment"],
                len(state["conflicts_detected"])
            )
        )
        state["estimated_duration_days"] = int(timeline["estimated_completion_days"])
        
        # Set confidence
        state["confidence"] = 0.85 if state["risk_assessment"] == "low" else 0.70
        
        return state
    
    async def coordination_node(self, state: WaterState) -> WaterState:
        """Prepare coordination messages for other agents"""
        print(f"📨 [{self.agent_name}] Preparing coordination...")
        
        state["current_step"] = "coordination"
        
        # Determine coordination needs
        coordination = apply_coordination_policy(
            state["nearby_projects"],
            state["risk_assessment"],
            state["request_type"]
        )
        
        state["coordination_required"] = list(coordination.keys())
        
        # Prepare messages
        for dept, reasons in coordination.items():
            message = {
                "from_agent": "water",
                "to_agent": dept,
                "message_type": "request" if state["decision"] == "coordinate" else "notification",
                "priority": state["priority"],
                "subject": f"Water infrastructure coordination for {state['location']}",
                "payload": {
                    "request_id": state["request_id"],
                    "request_type": state["request_type"],
                    "location": state["location"],
                    "reasons": reasons,
                    "risk_level": state["risk_assessment"],
                    "action_required": state["decision"] == "coordinate"
                }
            }
            state["messages_to_send"].append(message)
        
        # Add notifications
        if state["decision"] in ["approve", "coordinate"]:
            state["notifications"].append({
                "type": "resident_notification",
                "message": f"Water work scheduled at {state['location']} - Expected duration: {state['estimated_duration_days']} days"
            })
        
        state["reasoning_chain"].append(f"Coordination prepared: {len(state['messages_to_send'])} messages, {len(state['coordination_required'])} departments")
        
        return state
    
    async def response_generation_node(self, state: WaterState) -> WaterState:
        """Generate final response"""
        print(f"📝 [{self.agent_name}] Generating response...")
        
        state["current_step"] = "complete"
        
        state["reasoning_chain"].append(
            f"Response generated: {state['decision'].upper()} with {state['confidence']*100:.0f}% confidence"
        )
        
        print(f"✅ [{self.agent_name}] Decision: {state['decision'].upper()} | Risk: {state['risk_assessment']} | Cost: ₹{state.get('estimated_cost', 0):,.0f}")
        
        return state
    
    def _generate_next_steps(self, state: WaterState) -> list:
        """Generate next steps based on decision"""
        steps = []
        
        if state["decision"] == "approve":
            steps = [
                "Obtain necessary permits",
                "Schedule work crew",
                "Notify affected residents",
                "Begin work as scheduled"
            ]
        elif state["decision"] == "coordinate":
            steps = [
                f"Coordinate with {', '.join(state.get('coordination_required', []))}",
                "Conduct joint site inspection",
                "Prepare collaborative plan",
                "Obtain multi-department approval"
            ]
        elif state["decision"] == "deny":
            steps = [
                "Inform requester of denial",
                "Provide alternative solutions",
                "Schedule infrastructure assessment if needed"
            ]
        elif state["decision"] == "escalate":
            steps = [
                "Prepare detailed risk report",
                "Request senior management review",
                "Conduct emergency planning if needed"
            ]
        
        return steps


def should_coordinate(state: WaterState) -> str:
    """Routing logic: determine if coordination is needed"""
    if state["decision"] in ["coordinate", "escalate"]:
        return "coordinate"
    return "respond"


def create_water_agent_workflow(db_session: AsyncSession, llm: ChatGroq = None) -> StateGraph:
    """
    Create and compile the Water Agent LangGraph workflow
    
    Args:
        db_session: Async database session
        llm: Optional ChatGroq instance
    
    Returns:
        Compiled StateGraph workflow
    """
    # Initialize agent
    agent = WaterAgent(db_session, llm)
    
    # Create workflow
    workflow = StateGraph(WaterState)
    
    # Add nodes
    workflow.add_node("input_validation", agent.input_validation_node)
    workflow.add_node("data_collection", agent.data_collection_node)
    workflow.add_node("conflict_analysis", agent.conflict_analysis_node)
    workflow.add_node("decision", agent.decision_node)
    workflow.add_node("coordination", agent.coordination_node)
    workflow.add_node("response", agent.response_generation_node)
    
    # Add edges
    workflow.set_entry_point("input_validation")
    workflow.add_edge("input_validation", "data_collection")
    workflow.add_edge("data_collection", "conflict_analysis")
    workflow.add_edge("conflict_analysis", "decision")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "decision",
        should_coordinate,
        {
            "coordinate": "coordination",
            "respond": "response"
        }
    )
    
    workflow.add_edge("coordination", "response")
    workflow.add_edge("response", END)
    
    return workflow.compile()
