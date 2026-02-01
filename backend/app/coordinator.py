"""
Multi-Agent Coordinator

Orchestrates collaboration between fire and sanitation agents.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.app.communication import (
    get_message_bus, 
    AgentMessage, 
    MessageType, 
    MessagePriority
)

logger = logging.getLogger(__name__)


class MultiAgentCoordinator:
    """Coordinates multiple autonomous agents for collaborative decision-making"""
    
    def __init__(self):
        self.message_bus = get_message_bus()
        self.active_agents = {}
        logger.info("✓ Multi-Agent Coordinator initialized")
    
    def register_agent(self, agent_name: str, agent_instance: Any) -> None:
        """Register an agent with the coordinator"""
        self.active_agents[agent_name] = agent_instance
        logger.info(f"✓ Agent registered: {agent_name}")
    
    def process_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a multi-agent scenario that requires coordination.
        
        Returns a comprehensive result including all agent decisions and communications.
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🔗 MULTI-AGENT SCENARIO: {scenario.get('name', 'Unnamed')}")
        logger.info(f"{'='*70}")
        
        scenario_type = scenario.get("type")
        primary_agent = scenario.get("primary_agent")
        involves_agents = scenario.get("involves_agents", [])
        
        results = {
            "scenario_name": scenario.get("name"),
            "scenario_type": scenario_type,
            "primary_agent": primary_agent,
            "involved_agents": involves_agents,
            "timestamp": datetime.now().isoformat(),
            "agent_decisions": {},
            "messages": [],
            "coordination_summary": {}
        }
        
        logger.info(f"Primary Agent: {primary_agent}")
        logger.info(f"Involved Agents: {', '.join(involves_agents)}")
        
        # Step 1: Primary agent makes initial decision
        logger.info(f"\n📋 Step 1: {primary_agent.upper()} - Initial Assessment")
        logger.info("-" * 70)
        
        primary_request = scenario.get("primary_request")
        primary_agent_instance = self.active_agents.get(primary_agent)
        
        if not primary_agent_instance:
            logger.error(f"Agent {primary_agent} not registered!")
            return results
        
        primary_decision = primary_agent_instance.decide(primary_request)
        results["agent_decisions"][primary_agent] = primary_decision
        
        logger.info(f"Decision: {primary_decision.get('decision', 'N/A').upper()}")
        logger.info(f"Confidence: {primary_decision.get('confidence', 0)*100:.0f}%")
        
        # Step 2: Check if coordination is needed
        needs_coordination = self._needs_coordination(scenario, primary_decision)
        
        if needs_coordination:
            logger.info(f"\n🔗 Step 2: Coordination Required")
            logger.info("-" * 70)
            
            # Step 3: Send coordination messages to other agents
            for agent_name in involves_agents:
                if agent_name != primary_agent:
                    self._send_coordination_request(
                        from_agent=primary_agent,
                        to_agent=agent_name,
                        scenario=scenario,
                        primary_decision=primary_decision
                    )
            
            # Step 4: Other agents process their requests and respond
            for agent_name in involves_agents:
                if agent_name != primary_agent:
                    logger.info(f"\n📋 Step 3: {agent_name.upper()} - Response Assessment")
                    logger.info("-" * 70)
                    
                    agent_request = scenario.get(f"{agent_name}_request")
                    if agent_request:
                        agent_instance = self.active_agents.get(agent_name)
                        if agent_instance:
                            agent_decision = agent_instance.decide(agent_request)
                            results["agent_decisions"][agent_name] = agent_decision
                            
                            logger.info(f"Decision: {agent_decision.get('decision', 'N/A').upper()}")
                            logger.info(f"Confidence: {agent_decision.get('confidence', 0)*100:.0f}%")
                            
                            # Send response back
                            self._send_response(
                                from_agent=agent_name,
                                to_agent=primary_agent,
                                decision=agent_decision
                            )
        
        # Step 5: Collect all messages
        results["messages"] = self.message_bus.get_all_messages()
        
        # Step 6: Create coordination summary
        results["coordination_summary"] = self._create_coordination_summary(results)
        
        logger.info(f"\n{'='*70}")
        logger.info("✅ MULTI-AGENT SCENARIO COMPLETE")
        logger.info(f"{'='*70}")
        
        return results
    
    def _needs_coordination(
        self, 
        scenario: Dict[str, Any], 
        primary_decision: Dict[str, Any]
    ) -> bool:
        """Determine if coordination with other agents is needed"""
        
        # Coordination needed if:
        # 1. Scenario explicitly requires coordination
        # 2. Primary agent escalates with high priority
        # 3. Scenario affects multiple departments
        
        if scenario.get("requires_coordination", False):
            return True
        
        if primary_decision.get("decision") == "escalate":
            priority = scenario.get("priority", "medium")
            if priority in ["high", "critical"]:
                return True
        
        involves_agents = scenario.get("involves_agents", [])
        if len(involves_agents) > 1:
            return True
        
        return False
    
    def _send_coordination_request(
        self,
        from_agent: str,
        to_agent: str,
        scenario: Dict[str, Any],
        primary_decision: Dict[str, Any]
    ) -> None:
        """Send coordination request to another agent"""
        
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.COORDINATION_NEEDED,
            priority=MessagePriority.HIGH,
            content={
                "scenario": scenario.get("name"),
                "primary_decision": primary_decision.get("decision"),
                "reason": "Multi-department incident requires coordination",
                "requested_action": scenario.get(f"{to_agent}_action", "assess_and_respond")
            },
            context={
                "primary_confidence": primary_decision.get("confidence"),
                "scenario_type": scenario.get("type")
            }
        )
        
        self.message_bus.publish(message)
        logger.info(f"  → Coordination request sent to {to_agent}")
    
    def _send_response(
        self,
        from_agent: str,
        to_agent: str,
        decision: Dict[str, Any]
    ) -> None:
        """Send response message from one agent to another"""
        
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.STATUS_UPDATE,
            priority=MessagePriority.MEDIUM,
            content={
                "decision": decision.get("decision"),
                "confidence": decision.get("confidence"),
                "status": "ready_to_coordinate",
                "resources_available": decision.get("context", {})
            }
        )
        
        self.message_bus.publish(message)
        logger.info(f"  → Response sent from {from_agent} to {to_agent}")
    
    def _create_coordination_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the coordination process"""
        
        summary = {
            "total_agents_involved": len(results["agent_decisions"]),
            "messages_exchanged": len(results["messages"]),
            "all_decisions": {},
            "coordination_status": "completed"
        }
        
        for agent_name, decision in results["agent_decisions"].items():
            summary["all_decisions"][agent_name] = {
                "decision": decision.get("decision"),
                "confidence": decision.get("confidence", 0) * 100
            }
        
        return summary
