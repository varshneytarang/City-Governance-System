"""
PHASE 14: Output Generation Node

Generate either a recommendation or escalation request with conversational LLM response.
"""

import logging
import json

from ..state import DepartmentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)


def output_generator_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 14: Output Generation
    
    Generates final response in conversational format using LLM.
    """
    
    logger.info("Output Generator")
    
    try:
        escalate = state.get("escalate", False)
        confidence = state.get("confidence", 0.0)
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        
        # Get user's original query
        original_request = state.get("request", {})
        user_query = original_request.get("reason", "User inquiry about health operations")
        
        # Try to generate conversational response with LLM
        llm_client = get_llm_client()
        conversational_response = None
        
        if llm_client:
            conversational_response = _generate_conversational_response(
                llm_client, state, escalate, confidence, feasible, policy_ok, user_query
            )
        
        response = {}
        
        if escalate:
            # ESCALATION RESPONSE
            reason_text = conversational_response or state.get("escalation_reason", "Escalation required")
            response = {
                "decision": "escalate",
                "reason": reason_text,
                "requires_human_review": True,
                "details": {
                    "feasible": feasible,
                    "policy_compliant": policy_ok,
                    "confidence": confidence,
                    "risk_level": state.get("risk_level", "unknown"),
                    "plan": state.get("plan", {})
                }
            }
            logger.info("  -> Escalation response generated")
        
        else:
            # RECOMMENDATION RESPONSE
            reason_text = conversational_response or f"All criteria satisfied. Confidence: {confidence:.2%}"
            response = {
                "decision": "recommend",
                "reason": reason_text,
                "requires_human_review": False,
                "recommendation": {
                    "action": "proceed",
                    "plan": state.get("plan", {}),
                    "constraints": state.get("plan", {}).get("constraints", []),
                    "confidence": confidence
                },
                "details": {
                    "feasible": feasible,
                    "policy_compliant": policy_ok,
                    "risk_level": state.get("risk_level", "unknown"),
                    "feasibility_reason": state.get("feasibility_reason", ""),
                    "safety_concerns": state.get("safety_concerns", [])
                }
            }
            logger.info("  -> Recommendation response generated")
        
        state["response"] = response
        
        # Log response
        logger.info(f"Response ready")
        logger.info(f"  Decision: {response.get('decision')}")
        logger.info(f"  Confidence: {confidence:.2%}")
        
    except Exception as e:
        logger.error(f"Output generator error: {e}")
        state["response"] = {
            "decision": "escalate",
            "reason": f"Output generation error: {str(e)}",
            "error": str(e)
        }
    
    return state


def _generate_conversational_response(client, state: dict, escalate: bool, 
                                     confidence: float, feasible: bool, 
                                     policy_ok: bool, user_query: str) -> str:
    """Generate a conversational, ChatGPT-like response using LLM"""
    try:
        tool_results = state.get("tool_results", {})
        observations = state.get("observations", {})
        plan = state.get("plan", {})
        risk_level = state.get("risk_level", "unknown")
        
        context_parts = []
        if tool_results:
            context_parts.append(f"Tool Results: {json.dumps(tool_results, default=str)}")
        if observations:
            context_parts.append(f"Observations: {json.dumps(observations, default=str)}")
        if plan:
            context_parts.append(f"Plan: {json.dumps(plan, default=str)}")
            
        context_text = "\n".join(context_parts) if context_parts else "No additional context available"
        
        decision_status = "ESCALATION NEEDED" if escalate else "RECOMMENDATION"
        
        prompt = f"""You are a helpful Health Department AI assistant. A user asked: "{user_query}"

ANALYSIS RESULTS:
- Decision: {decision_status}
- Feasible: {feasible}
- Policy Compliant: {policy_ok}
- Confidence: {confidence:.0%}
- Risk Level: {risk_level}

DETAILED CONTEXT:
{context_text}

Respond to the user's query in a natural, conversational way like ChatGPT would. 
- Be helpful, informative, and friendly
- Explain what you found in the database/analysis
- Give specific details and numbers when available
- If recommending action, explain why it's safe and feasible
- If escalating, explain what concerns were found and why human review is needed
- Write 2-4 paragraphs as a natural conversation
- Don't just list bullet points - write flowing, natural sentences

Your response:"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a friendly, knowledgeable Health Department AI assistant. Respond naturally and conversationally."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"LLM response generation failed: {e}")
        return None

