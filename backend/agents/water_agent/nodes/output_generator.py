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
    
    logger.info("📤 [NODE: Output Generator]")
    
    try:
        escalate = state.get("escalate", False)
        confidence = state.get("confidence", 0.0)
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        
        # Get user's original query
        original_request = state.get("request", {})
        user_query = original_request.get("reason", "User inquiry about water management")
        
        # Try to generate conversational response with LLM
        llm_client = get_llm_client()
        conversational_response = None
        
        if llm_client:
            conversational_response = _generate_conversational_response_v2(
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
                    "plan": state.get("plan", {}),
                    "tool_results": state.get("tool_results", {}),
                    "observations": state.get("observations", {}),
                    "feasibility_reason": state.get("feasibility_reason", ""),
                    "policy_violations": state.get("policy_violations", [])
                }
            }
            logger.info("  → Escalation response generated")
        
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
                    "safety_concerns": state.get("safety_concerns", []),
                    "tool_results": state.get("tool_results", {}),
                    "observations": state.get("observations", {})
                }
            }
            logger.info("  → Recommendation response generated")
        
        state["response"] = response
        
        # Log response
        logger.info(f"✓ Response ready")
        logger.info(f"  Decision: {response.get('decision')}")
        logger.info(f"  Confidence: {confidence:.2%}")
        
    except Exception as e:
        logger.error(f"✗ Output generator error: {e}")
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
        # Build context from state
        tool_results = state.get("tool_results", {})
        observations = state.get("observations", {})
        plan = state.get("plan", {})
        risk_level = state.get("risk_level", "unknown")
        
        # Create comprehensive context
        context_parts = []
        
        if tool_results:
            context_parts.append(f"Tool Results: {json.dumps(tool_results, default=str)}")
        if observations:
            context_parts.append(f"Observations: {json.dumps(observations, default=str)}")
        if plan:
            context_parts.append(f"Plan: {json.dumps(plan, default=str)}")
            
        context_text = "\n".join(context_parts) if context_parts else "No additional context available"
        
        decision_status = "ESCALATION NEEDED" if escalate else "RECOMMENDATION"
        
        prompt = f"""You are a helpful Water Department AI assistant. A user asked: "{user_query}"

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
                {"role": "system", "content": "You are a friendly, knowledgeable Water Department AI assistant. Respond naturally and conversationally."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        llm_response = response.choices[0].message.content.strip()
        logger.info(f"✓ Generated conversational response ({len(llm_response)} chars)")
        return llm_response
        
    except Exception as e:
        logger.error(f"✗ LLM response generation failed: {e}")
        return None


def _generate_conversational_response_v2(client, state: dict, escalate: bool,
                                         confidence: float, feasible: bool,
                                         policy_ok: bool, user_query: str) -> str:
    """Enhanced conversational response: dynamic system prompt + logging"""
    try:
        # Build context from state
        tool_results = state.get("tool_results", {})
        observations = state.get("observations", {})
        plan = state.get("plan", {})
        risk_level = state.get("risk_level", "unknown")

        # Create comprehensive context
        context_parts = []
        if tool_results:
            context_parts.append(f"Tool Results: {json.dumps(tool_results, default=str)}")
        if observations:
            context_parts.append(f"Observations: {json.dumps(observations, default=str)}")
        if plan:
            context_parts.append(f"Plan: {json.dumps(plan, default=str)}")

        context_text = "\n".join(context_parts) if context_parts else "No additional context available"

        decision_status = "ESCALATION NEEDED" if escalate else "RECOMMENDATION"

        user_prompt = (
            f"User Query: \"{user_query}\"\n\n"
            f"ANALYSIS RESULTS:\n- Decision: {decision_status}\n- Feasible: {feasible}\n"
            f"- Policy Compliant: {policy_ok}\n- Confidence: {confidence:.0%}\n- Risk Level: {risk_level}\n\n"
            f"DETAILED CONTEXT:\n{context_text}\n\nRespond concisely and helpfully."
        )

        # Generate dynamic system prompt via meta-prompting
        dynamic_system_prompt = None
        try:
            logger.info("🔎 Generating dynamic system prompt for output generation")
            meta_prompt = (
                "Generate a concise system prompt (1-2 sentences) to instruct an assistant to reply to this user query in a "
                f"professional, conversational tone. User query: {user_query}. Context summary: {context_text[:500]}"
            )
            sys_resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at creating system prompts for AI assistants. Produce a short, specific system prompt."},
                    {"role": "user", "content": meta_prompt}
                ],
                temperature=0.5,
                max_tokens=150,
            )
            dynamic_system_prompt = sys_resp.choices[0].message.content.strip()
            if dynamic_system_prompt:
                dynamic_system_prompt = dynamic_system_prompt.replace('`', '').strip()
                logger.info(f"  🔐 Dynamic system prompt: {dynamic_system_prompt[:200]}")
        except Exception as e:
            logger.warning(f"Dynamic system prompt generation failed: {e}")

        # Fallback system prompt
        system_prompt = dynamic_system_prompt or "You are a friendly, knowledgeable Water Department AI assistant. Respond naturally and conversationally."

        logger.info(f"  🔐 Using system prompt for response generation: {system_prompt}")
        logger.info(f"  📝 User prompt (truncated): {user_prompt[:400]}")

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )

        llm_response = response.choices[0].message.content.strip()
        logger.info(f"✓ Generated conversational response ({len(llm_response)} chars); sample: {llm_response[:200]}")
        return llm_response

    except Exception as e:
        logger.error(f"✗ LLM response generation failed: {e}")
        return None

