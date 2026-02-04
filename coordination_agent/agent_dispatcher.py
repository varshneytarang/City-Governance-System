"""
Agent Dispatcher - Enables Coordination Agent to call other agents

This module provides the coordination agent with the ability to:
1. Instantiate any department agent on demand
2. Send queries to specific agents
3. Collect responses from agents
4. Cache agent instances for efficiency
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentDispatcher:
    """
    Dispatcher that allows coordination agent to call other agents
    
    Usage:
        dispatcher = AgentDispatcher()
        response = dispatcher.query_agent("water", {
            "type": "capacity_query",
            "location": "Downtown"
        })
    """
    
    def __init__(self):
        """Initialize the agent dispatcher with lazy loading"""
        self._agent_cache = {}
        self._agent_classes = {
            "water": None,
            "engineering": None,
            "fire": None,
            "sanitation": None,
            "health": None,
            "finance": None
        }
        logger.info("✓ Agent Dispatcher initialized")
    
    def _get_agent_class(self, agent_type: str):
        """Lazy load agent class to avoid circular imports"""
        if self._agent_classes[agent_type] is None:
            try:
                if agent_type == "water":
                    from water_agent.agent import WaterDepartmentAgent
                    self._agent_classes["water"] = WaterDepartmentAgent
                elif agent_type == "engineering":
                    from engineering_agent.agent import EngineeringDepartmentAgent
                    self._agent_classes["engineering"] = EngineeringDepartmentAgent
                elif agent_type == "fire":
                    from fire_agent.agent import FireDepartmentAgent
                    self._agent_classes["fire"] = FireDepartmentAgent
                elif agent_type == "sanitation":
                    from sanitation_agent.agent import SanitationDepartmentAgent
                    self._agent_classes["sanitation"] = SanitationDepartmentAgent
                elif agent_type == "health":
                    from health_agent.agent import HealthDepartmentAgent
                    self._agent_classes["health"] = HealthDepartmentAgent
                elif agent_type == "finance":
                    from finance_agent.agent import FinanceDepartmentAgent
                    self._agent_classes["finance"] = FinanceDepartmentAgent
                else:
                    raise ValueError(f"Unknown agent type: {agent_type}")
            except ImportError as e:
                logger.error(f"Failed to import {agent_type} agent: {e}")
                raise
        
        return self._agent_classes[agent_type]
    
    def _get_agent_instance(self, agent_type: str):
        """Get or create cached agent instance"""
        if agent_type not in self._agent_cache:
            logger.info(f"📥 Instantiating {agent_type} agent for coordination query")
            agent_class = self._get_agent_class(agent_type)
            self._agent_cache[agent_type] = agent_class()
        
        return self._agent_cache[agent_type]
    
    def query_agent(
        self,
        agent_type: str,
        request: Dict[str, Any],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Send query to a specific agent and get response
        
        Args:
            agent_type: Type of agent to query (water, engineering, fire, etc.)
            request: Request dict to send to the agent
            timeout: Maximum time to wait for response (seconds)
            
        Returns:
            Agent's response dict
            
        Example:
            response = dispatcher.query_agent("water", {
                "type": "capacity_query",
                "location": "Downtown",
                "query": "What is current water pressure?"
            })
        """
        logger.info(f"🔄 Coordination → {agent_type.upper()} Agent")
        logger.info(f"   Request: {request.get('type', 'unknown')}")
        
        try:
            # Get agent instance
            agent = self._get_agent_instance(agent_type)
            
            # Call agent's decide method
            start_time = datetime.now()
            response = agent.decide(request)
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ {agent_type.upper()} Agent responded in {duration:.2f}s")
            logger.info(f"   Decision: {response.get('decision', 'N/A')}")
            
            return {
                "success": True,
                "agent_type": agent_type,
                "response": response,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to query {agent_type} agent: {e}", exc_info=True)
            return {
                "success": False,
                "agent_type": agent_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def query_multiple_agents(
        self,
        queries: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Query multiple agents and collect responses
        
        Args:
            queries: Dict mapping agent_type to request dict
            
        Returns:
            Dict mapping agent_type to response dict
            
        Example:
            responses = dispatcher.query_multiple_agents({
                "water": {"type": "capacity_query", "location": "Downtown"},
                "engineering": {"type": "project_planning", "location": "Downtown"}
            })
        """
        logger.info(f"📡 Querying {len(queries)} agents simultaneously")
        
        responses = {}
        for agent_type, request in queries.items():
            responses[agent_type] = self.query_agent(agent_type, request)
        
        successful = sum(1 for r in responses.values() if r.get("success"))
        logger.info(f"✅ {successful}/{len(queries)} agents responded successfully")
        
        return responses
    
    def get_agent_info(self, agent_type: str) -> Dict[str, Any]:
        """
        Get information about an agent without calling its decide method
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Dict with agent metadata
        """
        try:
            agent = self._get_agent_instance(agent_type)
            
            return {
                "agent_type": agent_type,
                "version": getattr(agent, "agent_version", "unknown"),
                "settings": getattr(agent, "settings", {}),
                "available": True
            }
        except Exception as e:
            logger.warning(f"Could not get info for {agent_type}: {e}")
            return {
                "agent_type": agent_type,
                "available": False,
                "error": str(e)
            }
    
    def close_all_agents(self):
        """Close all cached agent instances"""
        logger.info(f"🔒 Closing {len(self._agent_cache)} cached agents")
        
        for agent_type, agent in self._agent_cache.items():
            try:
                if hasattr(agent, "close"):
                    agent.close()
                    logger.info(f"   ✓ {agent_type} agent closed")
            except Exception as e:
                logger.warning(f"   ⚠ Error closing {agent_type}: {e}")
        
        self._agent_cache.clear()
        logger.info("✓ All agents closed")
    
    def clear_cache(self):
        """Clear agent cache without closing"""
        self._agent_cache.clear()
        logger.info("✓ Agent cache cleared")


# Singleton instance
_dispatcher_instance = None


def get_dispatcher() -> AgentDispatcher:
    """Get singleton dispatcher instance"""
    global _dispatcher_instance
    if _dispatcher_instance is None:
        _dispatcher_instance = AgentDispatcher()
    return _dispatcher_instance
