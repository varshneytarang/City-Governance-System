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
        
        # Get user's original query from input_event (consistent across agents)
        original_request = state.get("input_event", {})
        user_query = original_request.get("reason") or original_request.get("query") or "User inquiry about sanitation operations"

        # Prefer deterministic concise reply for worker/budget queries when we have context
        conversational_response = None
        ctx = state.get("context", {}) or {}
        # Budget may be stored under context['budget']['total']
        budget_total = None
        if isinstance(ctx.get("budget"), dict):
            budget_total = ctx["budget"].get("total")

        # Worker availability deterministic reply
        if ("worker" in user_query.lower() or "available workers" in user_query.lower() or "avalai" in user_query.lower() or "work" in user_query.lower() and "available" in user_query.lower()):
            workers = ctx.get("available_workers") or []
            total = ctx.get("total_workers_available") or len(workers)
            if total and (workers or total > 0):
                # Build concise reply listing up to 5 workers
                try:
                    names = [w.get("worker_name") or w.get("name") or str(w.get("worker_id") or "") for w in workers[:5]]
                    names_text = ", ".join([n for n in names if n])
                    conversational_response = f"There are {total} sanitation workers available. Sample: {names_text}."
                except Exception:
                    conversational_response = f"There are {total} sanitation workers available."
                logger.info("  → Using deterministic concise worker availability response (no LLM)")

        # Budget deterministic reply
        if conversational_response is None and budget_total is not None and ("budget" in user_query.lower() or "available" in user_query.lower()):
            try:
                conversational_response = f"The total sanitation budget is ${float(budget_total):,.2f}."
                logger.info("  → Using deterministic concise budget response (no LLM)")
            except Exception:
                conversational_response = None

        # Otherwise, use the LLM dynamic system prompt flow
        if conversational_response is None:
            llm_client = get_llm_client()
            if llm_client:
                conversational_response = _generate_conversational_response_v2(
                    llm_client, state, escalate, confidence, feasible, policy_ok, user_query
                )
            else:
                # No LLM available: produce a concise deterministic summary from context
                try:
                    ctx = state.get("context", {}) or {}
                    parts = []
                    if ctx.get("total_inspections") is not None:
                        parts.append(f"{ctx.get('total_inspections')} recent inspections")
                    if ctx.get("total_projects") is not None:
                        parts.append(f"{ctx.get('total_projects')} active projects")
                    if ctx.get("scheduled_work_items") is not None:
                        parts.append(f"{ctx.get('scheduled_work_items')} scheduled work items")
                    if ctx.get("total_workers_available") is not None:
                        parts.append(f"{ctx.get('total_workers_available')} available workers")
                    if ctx.get("total_incidents") is not None:
                        parts.append(f"{ctx.get('total_incidents')} recent incidents")
                    if isinstance(ctx.get("budget"), dict):
                        parts.append(f"budget remaining ${float(ctx['budget'].get('remaining') or 0):,.2f}")

                    if parts:
                        conversational_response = "Sanitation summary: " + ", ".join(parts) + "."
                    else:
                        conversational_response = "Sanitation Department handles waste collection, scheduling, inspections, and budgeting for the city."
                except Exception:
                    conversational_response = "Sanitation Department handles waste collection, scheduling, inspections, and budgeting for the city."
        
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
        
        prompt = f"""You are a helpful Sanitation Department AI assistant. A user asked: "{user_query}"

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
                {"role": "system", "content": "You are a friendly, knowledgeable Sanitation Department AI assistant. Respond naturally and conversationally."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"LLM response generation failed: {e}")
        return None


def _generate_conversational_response_v2(client, state: dict, escalate: bool,
                                         confidence: float, feasible: bool,
                                         policy_ok: bool, user_query: str) -> str:
    """Dynamic system prompt + LLM conversational output (shared pattern)."""
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

        # Inject budget context if available (budget.total stored under context['budget'])
        budget_total = None
        if isinstance(state.get("context", {}).get("budget"), dict):
            budget_total = state.get("context", {}).get("budget", {}).get("total")
        if budget_total is not None and "budget" not in context_text:
            context_text = f"Budget Total: {budget_total}\n" + context_text

        user_prompt = (
            f"User Query: \"{user_query}\"\n\n"
            f"ANALYSIS RESULTS:\n- Decision: {decision_status}\n- Feasible: {feasible}\n"
            f"- Policy Compliant: {policy_ok}\n- Confidence: {confidence:.0%}\n- Risk Level: {risk_level}\n\n"
            f"DETAILED CONTEXT:\n{context_text}\n\nRespond concisely and helpfully."
        )

        # Meta-prompt to generate a focused system prompt
        dynamic_system_prompt = None
        try:
            meta_prompt = (
                "Generate a 1-2 sentence system prompt instructing an assistant to reply concisely and professionally to the user query. "
                f"User query: {user_query}. Context: {context_text[:500]}"
            )
            sys_resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at producing concise system prompts for AI assistants."},
                    {"role": "user", "content": meta_prompt}
                ],
                temperature=0.5,
                max_tokens=120,
            )
            dynamic_system_prompt = sys_resp.choices[0].message.content.strip()
            if dynamic_system_prompt:
                dynamic_system_prompt = dynamic_system_prompt.replace('`', '').strip()
        except Exception as e:
            logger.warning(f"Dynamic system prompt generation failed: {e}")

        system_prompt = dynamic_system_prompt or "You are a friendly, knowledgeable Sanitation Department AI assistant. Reply concisely and helpfully."

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=600,
        )

        llm_response = response.choices[0].message.content.strip()
        return llm_response

    except Exception as e:
        logger.error(f"LLM v2 generation failed: {e}")
        return None
