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
    
    logger.info("\n" + "="*60)
    logger.info("📤 [OUTPUT GENERATOR - FINAL RESPONSE]")
    logger.info("="*60)
    
    try:
        escalate = state.get("escalate", False)
        confidence = state.get("confidence", 0.0)
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        
        logger.info("\n📊 DECISION METRICS:")
        logger.info(f"   ✅ Feasible: {feasible}")
        logger.info(f"   📜 Policy OK: {policy_ok}")
        logger.info(f"   📊 Confidence: {confidence:.2%}")
        logger.info(f"   {'⬆️' if escalate else '✅'} Escalate: {escalate}")
        logger.info(f"   ⚠️  Risk Level: {state.get('risk_level', 'unknown')}")
        
        # Get user's original query
        original_request = state.get("request", {})
        user_query = original_request.get("reason", "User inquiry about water management")
        print(f"\n💬 User Query: {user_query}")
        
        # Try to generate conversational response with LLM
        print("\n🔍 Checking LLM availability...")
        llm_client = get_llm_client()
        conversational_response = None
        
        if llm_client:
            print("✅ LLM client available - generating conversational response...")
            conversational_response = _generate_conversational_response(
                llm_client, state, escalate, confidence, feasible, policy_ok, user_query
            )
            if conversational_response:
                print(f"✅ Conversational response generated ({len(conversational_response)} chars)")
                print(f"   Preview: {conversational_response[:150]}...")
            else:
                print("⚠️  LLM response generation returned None")
        else:
            print("⚠️  No LLM client - using basic response")
        
        response = {}
        
        if escalate:
            # ESCALATION RESPONSE
            print("\n⚠️  Building ESCALATION response...")
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
            print("✅ Escalation response built")
            print(f"   📝 Reason: {reason_text[:100]}...")
        
        else:
            # RECOMMENDATION RESPONSE
            print("\n✅ Building RECOMMENDATION response...")
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
            print("✅ Recommendation response built")
            print(f"   📝 Reason: {reason_text[:100]}...")
            print(f"   🎯 Action: proceed")
        
        state["response"] = response
        
        # Log response summary
        print("\n" + "="*60)
        print("✅ RESPONSE READY")
        print("="*60)
        print(f"   Decision: {response.get('decision').upper()}")
        print(f"   Confidence: {confidence:.2%}")
        print(f"   Human Review Required: {response.get('requires_human_review', False)}")
        print(f"   Response Keys: {list(response.keys())}")
        print("="*60 + "\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ OUTPUT GENERATION ERROR")
        print("="*60)
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        print("="*60)
        
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
    
    print("\n" + "-"*60)
    print("💬 Generating conversational response with LLM...")
    print("-"*60)
    
    try:
        # Build context from state
        tool_results = state.get("tool_results", {})
        observations = state.get("observations", {})
        plan = state.get("plan", {})
        risk_level = state.get("risk_level", "unknown")
        
        print(f"📊 Building context from state...")
        print(f"   Tool Results: {len(str(tool_results))} chars")
        print(f"   Observations: {len(str(observations))} chars")
        print(f"   Plan: {len(str(plan))} chars")
        
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
        
        print(f"\n📑 Context summary:")
        print(f"   Decision: {decision_status}")
        print(f"   Feasible: {feasible}")
        print(f"   Policy OK: {policy_ok}")
        print(f"   Confidence: {confidence:.0%}")
        print(f"   Risk: {risk_level}")
        
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

        print(f"\n📝 Prompt built ({len(prompt)} chars)")
        print(f"\n🌐 Calling LLM API...")
        print(f"   Client: {type(client).__name__}")
        print(f"   Model: {settings.LLM_MODEL}")
        print(f"   Temperature: 0.7")
        print(f"   Max tokens: 800")
        
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a friendly, knowledgeable Water Department AI assistant. Respond naturally and conversationally, like you're chatting with someone who needs help. Be informative but approachable."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        llm_response = response.choices[0].message.content.strip()
        print(f"\n✅ LLM API call successful!")
        print(f"📤 Response length: {len(llm_response)} chars")
        print(f"📤 Preview: {llm_response[:200]}...")
        print("-"*60)
        
        return llm_response
        
    except Exception as e:
        print(f"\n❌ CONVERSATIONAL RESPONSE GENERATION FAILED")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        print("-"*60)
        return None

