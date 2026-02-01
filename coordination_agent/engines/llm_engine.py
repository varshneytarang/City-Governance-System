"""
LLM-Powered Negotiation Engine

Uses Groq LLM for complex conflict resolution requiring:
- Multi-criteria trade-off analysis
- Stakeholder impact assessment
- Nuanced reasoning
- Political/social considerations
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..state import Conflict, Resolution, AgentDecision
from ..config import CoordinationConfig

logger = logging.getLogger(__name__)


class LLMNegotiationEngine:
    """LLM-powered conflict resolution for complex negotiations"""
    
    def __init__(self):
        self.config = CoordinationConfig()
        self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client (using OpenAI with Groq endpoint)"""
        try:
            import openai
            
            self.client = openai.OpenAI(
                api_key=self.config.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            logger.info("✓ Groq LLM client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise
    
    def negotiate(
        self,
        conflict: Conflict,
        agent_decisions: List[AgentDecision]
    ) -> Resolution:
        """
        Use LLM to negotiate complex conflict resolution
        
        Returns Resolution with LLM-generated execution plan
        """
        logger.info(f"LLM negotiation for conflict: {conflict['conflict_type']}")
        
        # Build comprehensive prompt
        prompt = self._build_negotiation_prompt(conflict, agent_decisions)
        
        # Query LLM
        try:
            llm_response = self._query_llm(prompt)
            
            # Parse LLM response
            resolution_data = self._parse_llm_response(llm_response)
            
            # Create Resolution object
            resolution: Resolution = {
                "resolution_id": str(uuid.uuid4()),
                "conflict_id": conflict["conflict_id"],
                "method": "llm",
                "decision": resolution_data.get("decision", "escalate"),
                "rationale": resolution_data.get("rationale", "LLM analysis"),
                "confidence": resolution_data.get("confidence", 0.5),
                "requires_human": resolution_data.get("requires_human", True),
                "execution_plan": resolution_data.get("execution_plan", {}),
                "resolved_at": datetime.now().isoformat()
            }
            
            logger.info(f"✓ LLM resolution: {resolution['decision']} (confidence: {resolution['confidence']})")
            return resolution
            
        except Exception as e:
            logger.error(f"✗ LLM negotiation failed: {e}")
            # Fallback: escalate to human
            return self._create_fallback_resolution(conflict)
    
    def _build_negotiation_prompt(
        self,
        conflict: Conflict,
        agent_decisions: List[AgentDecision]
    ) -> str:
        """Build comprehensive negotiation prompt for LLM"""
        
        # Get decisions involved in conflict
        agents_involved = conflict["agents_involved"]
        decisions = [d for d in agent_decisions if d["agent_id"] in agents_involved]
        
        # Format agent positions
        agent_positions = []
        for decision in decisions:
            position = {
                "agent": decision["agent_id"],
                "department": decision["agent_type"],
                "decision": decision["decision"],
                "priority": decision["priority"],
                "cost": decision.get("estimated_cost", 0),
                "location": decision.get("location", ""),
                "timeline": decision.get("timeline", ""),
                "rationale": decision.get("request", {}).get("reason", "")
            }
            agent_positions.append(position)
        
        # Build constraints
        constraints = {
            "budget_limit": self.config.AUTO_APPROVAL_COST_LIMIT,
            "current_month": datetime.now().month,
            "monsoon_months": self.config.MONSOON_MONTHS,
            "priority_levels": self.config.PRIORITY_LEVELS
        }
        
        prompt = f"""You are a City Governance Coordination AI making critical infrastructure decisions.

CONFLICT SITUATION:
Type: {conflict['conflict_type']}
Severity: {conflict['severity']}
Description: {conflict['description']}
Detected at: {conflict['detected_at']}

AGENTS INVOLVED:
{json.dumps(agent_positions, indent=2)}

CONSTRAINTS:
{json.dumps(constraints, indent=2)}

STAKEHOLDER ANALYSIS:
Consider impact on:
1. Public safety (HIGHEST PRIORITY)
2. Service continuity
3. Budget efficiency
4. Timeline feasibility
5. Citizen satisfaction
6. Political considerations

TASK:
Analyze each agent's position and propose an optimal resolution that:
1. Prioritizes public safety above all
2. Balances cost, timeline, and impact
3. Considers emergency vs. routine work
4. Respects policy constraints (e.g., monsoon restrictions)
5. Maximizes overall benefit to citizens

AVAILABLE RESOLUTION OPTIONS:
- approve_all: Approve all agents' requests (with coordination plan)
- approve_partial: Approve some, defer/reject others
- defer: Postpone all decisions pending further analysis
- escalate: Escalate to human authority (City Council/Mayor)
- reject: Reject conflicting requests

RESPOND IN VALID JSON:
{{
    "decision": "approve_all|approve_partial|defer|escalate|reject",
    "rationale": "Clear explanation of reasoning (200 words max)",
    "trade_offs": [
        "List of trade-offs made in this decision"
    ],
    "execution_plan": {{
        "approved": ["list of agent_ids"],
        "deferred": ["list of agent_ids"],
        "rejected": ["list of agent_ids"],
        "sequence": [
            {{"agent": "agent_id", "order": 1, "action": "specific action"}}
        ],
        "coordination_notes": "How agents should coordinate"
    }},
    "confidence": 0.0-1.0,
    "requires_human": true|false,
    "risk_factors": ["List of risks to monitor"],
    "success_metrics": ["How to measure if decision was good"]
}}

CRITICAL: Respond ONLY with valid JSON, no other text.
"""
        return prompt
    
    def _query_llm(self, prompt: str) -> str:
        """Query Groq LLM with prompt"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a city governance decision-making AI. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=2000,
                timeout=self.config.LLM_TIMEOUT
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            raise
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM JSON response"""
        try:
            # Try to extract JSON if response has extra text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx+1]
                data = json.loads(json_str)
            else:
                data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["decision", "rationale", "confidence", "requires_human"]
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing field in LLM response: {field}")
                    data[field] = self._get_default_value(field)
            
            # Ensure execution_plan exists
            if "execution_plan" not in data:
                data["execution_plan"] = {}
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON: {e}")
            logger.error(f"Response was: {response_text}")
            # Return fallback
            return {
                "decision": "escalate",
                "rationale": "Failed to parse LLM response",
                "confidence": 0.0,
                "requires_human": True,
                "execution_plan": {}
            }
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing field"""
        defaults = {
            "decision": "escalate",
            "rationale": "No rationale provided",
            "confidence": 0.0,
            "requires_human": True,
            "execution_plan": {},
            "trade_offs": [],
            "risk_factors": [],
            "success_metrics": []
        }
        return defaults.get(field, None)
    
    def _create_fallback_resolution(self, conflict: Conflict) -> Resolution:
        """Create fallback resolution when LLM fails"""
        return {
            "resolution_id": str(uuid.uuid4()),
            "conflict_id": conflict["conflict_id"],
            "method": "llm",
            "decision": "escalate",
            "rationale": "LLM negotiation failed - escalating to human authority",
            "confidence": 0.0,
            "requires_human": True,
            "execution_plan": {
                "action": "escalate_to_human",
                "reason": "llm_failure"
            },
            "resolved_at": datetime.now().isoformat()
        }
    
    def estimate_complexity(self, conflict: Conflict, agent_decisions: List[AgentDecision]) -> float:
        """
        Estimate conflict complexity to determine if LLM is needed
        
        Returns: 0.0 - 1.0 (higher = more complex)
        """
        complexity = conflict.get("complexity_score", 0.5)
        
        # Increase complexity for certain factors
        agents_involved = conflict["agents_involved"]
        decisions = [d for d in agent_decisions if d["agent_id"] in agents_involved]
        
        # Multiple departments = more complex
        unique_departments = len(set(d["agent_type"] for d in decisions))
        if unique_departments > 2:
            complexity += 0.2
        
        # High costs = more complex
        total_cost = sum(d.get("estimated_cost", 0) for d in decisions)
        if total_cost > 5000000:  # ₹50 lakh
            complexity += 0.2
        
        # Priority conflicts = more complex
        priorities = [d["priority"] for d in decisions]
        if "emergency" in priorities and len(set(priorities)) > 1:
            complexity += 0.1
        
        return min(complexity, 1.0)
