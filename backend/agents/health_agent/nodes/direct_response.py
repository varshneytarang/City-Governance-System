"""
Direct Response Generator - For informational queries

Bypasses planning workflow and directly formats database results.
Used when query_type = "informational"
"""

import logging
import json
from typing import Dict, List

from ..state import HealthAgentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)


def direct_response_generator(state: HealthAgentState) -> HealthAgentState:
    """
    Generate direct response from context data (no planning needed)
    
    For informational queries like:
    - "What medical supplies do we have?"
    - "Show me vaccination campaigns"
    - "What's our budget status?"
    """
    
    logger.info("📋 [NODE: Direct Response Generator]")
    
    try:
        input_event = state.get("input_event", {})
        query = input_event.get("reason", "Health department query")
        intent = state.get("intent", "general_status_query")
        context = state.get("context", {})
        
        # Extract relevant data based on intent
        relevant_data = _extract_relevant_data(intent, context)
        
        # Try to generate natural language response with LLM
        llm_client = get_llm_client()
        conversational_response = None
        
        if llm_client and relevant_data:
            logger.info("🤖 Generating natural language response...")
            conversational_response = _generate_conversational_response(
                llm_client, query, intent, relevant_data, context
            )
        
        # Build response
        if conversational_response:
            response_text = conversational_response
        else:
            # Fallback to structured response
            response_text = _format_structured_response(intent, relevant_data)
        
        response = {
            "decision": "inform",
            "reason": response_text,
            "data": relevant_data,
            "confidence": 0.95,  # High confidence for direct data retrieval
            "requires_human_review": False,
            "query_type": "informational"
        }
        
        state["response"] = response
        state["confidence"] = 0.95
        state["feasible"] = True
        state["policy_ok"] = True
        
        logger.info(f"✓ Direct response generated for: {intent}")
        return state
        
    except Exception as e:
        logger.error(f"Direct response generator error: {e}")
        state["response"] = {
            "decision": "error",
            "reason": f"Error retrieving data: {str(e)}",
            "error": str(e)
        }
        return state


def _extract_relevant_data(intent: str, context: Dict) -> Dict:
    """Extract relevant data from context based on intent"""
    
    data = {}
    
    if intent in ["check_medical_supplies", "check_inventory"]:
        # Extract health resources/supplies
        resources = context.get("health_resources", [])
        data["supplies"] = [
            {
                "name": r.get("resource_type"),
                "quantity": r.get("quantity"),
                "location": r.get("location"),
                "status": r.get("status"),
                "metadata": r.get("metadata", {})
            }
            for r in resources
        ]
        data["total_items"] = len(resources)
        
    elif intent in ["check_vaccination_campaigns", "check_campaigns", "vaccination_status"]:
        campaigns = context.get("vaccination_campaigns", [])
        data["campaigns"] = [
            {
                "name": c.get("name"),
                "location": c.get("location"),
                "start_date": str(c.get("start_date")),
                "end_date": str(c.get("end_date")),
                "coverage": c.get("coverage_percent"),
                "target_groups": c.get("target_groups"),
                "status": c.get("status")
            }
            for c in campaigns
        ]
        data["active_campaigns"] = len([c for c in campaigns if c.get("status") == "active"])
        
    elif intent in ["check_disease_incidents", "check_incidents", "disease_status"]:
        incidents = context.get("disease_incidents", [])
        data["incidents"] = [
            {
                "type": i.get("incident_type"),
                "location": i.get("location"),
                "severity": i.get("severity"),
                "status": i.get("status"),
                "reported_date": str(i.get("reported_date"))
            }
            for i in incidents
        ]
        data["total_incidents"] = len(incidents)
        data["critical_count"] = len([i for i in incidents if i.get("severity") == "critical"])
        
    elif intent in ["check_health_facilities", "check_facilities", "facility_status"]:
        facilities = context.get("health_facilities", [])
        data["facilities"] = [
            {
                "name": f.get("name"),
                "location": f.get("location"),
                "capacity": f.get("capacity"),
                "services": f.get("services"),
                "status": f.get("status")
            }
            for f in facilities
        ]
        data["operational_count"] = len([f for f in facilities if f.get("status") == "open"])
        
    elif intent in ["check_budget_status", "check_budget", "budget_inquiry"]:
        # Extract budget from all entries (not just context key)
        data["budget"] = context.get("budget", {})
    
    elif intent in ["check_policies", "check_health_policies", "policy_status"]:
        policies = context.get("health_policies", [])
        data["policies"] = [
            {
                "name": p.get("policy_name"),
                "description": p.get("description"),
                "effective_date": str(p.get("effective_date")),
                "metadata": p.get("metadata", {})
            }
            for p in policies
        ]
        data["total_policies"] = len(policies)
    
    elif intent in ["check_surveillance", "check_reports", "surveillance_status"]:
        reports = context.get("health_surveillance_reports", [])
        data["reports"] = [
            {
                "source": r.get("source"),
                "report_date": str(r.get("report_date")),
                "summary": r.get("summary"),
                "severity": r.get("severity_assessment")
            }
            for r in reports
        ]
        data["total_reports"] = len(reports)
        
    else:
        # General status - include ALL data points
        data["supplies_count"] = len(context.get("health_resources", []))
        data["campaigns_count"] = len(context.get("vaccination_campaigns", []))
        data["facilities_count"] = len(context.get("health_facilities", []))
        data["incidents_count"] = len(context.get("disease_incidents", []))
        data["policies_count"] = len(context.get("health_policies", []))
        data["surveillance_reports_count"] = len(context.get("health_surveillance_reports", []))
        
        # If user asked about "resources" generally, include all supplies
        if "resource" in intent.lower() or "supply" in intent.lower() or "supplies" in intent.lower():
            resources = context.get("health_resources", [])
            data["supplies"] = [
                {
                    "name": r.get("resource_type"),
                    "quantity": r.get("quantity"),
                    "location": r.get("location"),
                    "status": r.get("status")
                }
                for r in resources
            ]
    
    return data


def _generate_conversational_response(client, query: str, intent: str, 
                                     data: Dict, context: Dict) -> str:
    """Generate natural language response using LLM with dynamic prompt generation"""
    try:
        # Step 1: Generate specialized system prompt based on query context
        logger.info("🎯 Generating dynamic prompt based on query context...")
        dynamic_system_prompt = _generate_dynamic_prompt(client, query, intent, data)
        
        if not dynamic_system_prompt:
            # Fallback to default if prompt generation fails
            dynamic_system_prompt = "You are a factual Health Department data assistant. Provide direct answers based only on the provided database data."
        
        logger.info(f"📝 Generated system prompt: {dynamic_system_prompt[:100]}...")
        
        # Step 2: Generate actual response using the dynamic prompt
        user_prompt = f"""User Query: "{query}"
Query Intent: {intent}

DATABASE DATA:
{json.dumps(data, indent=2, default=str)}

INSTRUCTIONS:
Provide a direct, concise answer that:
1. Matches the brevity of the question - simple questions get brief answers (1-2 paragraphs max)
2. Includes key facts and numbers from the data
3. Uses natural conversational language - NO tables or bullet points
4. Stays focused on what was asked - don't elaborate unnecessarily
5. Provides totals and highlights, not exhaustive details

Example for "What medical supplies do we have?":
"We currently have 9 types of medical supplies in stock. The largest quantities include 15,000 N95 masks and 10,000 COVID-19 rapid test kits at City Central Health Clinic, plus 8,000 influenza vaccine doses and 2,500 COVID-19 vaccine doses across multiple facilities. We also maintain supplies of PPE kits (5,000), blood pressure monitors (120), thermometers (200), portable defibrillators (45), and emergency medical backpacks (12). All supplies are currently available."

Write your concise response now:"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": dynamic_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for factual responses
            max_tokens=500  # Reduced from 1000 to encourage brevity
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"LLM response generation failed: {e}")
        return None


def _generate_dynamic_prompt(client, query: str, intent: str, data: Dict) -> str:
    """Generate a specialized system prompt tailored to the specific query"""
    try:
        # Analyze the query and data to create an optimal system prompt
        data_summary = _summarize_data_structure(data)
        
        meta_prompt = f"""You are an expert at crafting system prompts for AI assistants. Generate an optimal system prompt for responding to this health department query.

QUERY ANALYSIS:
- User Query: "{query}"
- Query Intent: {intent}
- Data Type: {data_summary['type']}
- Data Volume: {data_summary['count']} records
- Key Fields: {', '.join(data_summary['fields'])}

CONTEXT:
The AI assistant needs to respond to a citizen's question about health department operations. The response should be:
1. CONCISE - match response length to question complexity (simple questions = 1 paragraph, complex = 2-3 max)
2. Factually accurate - based only on database data provided
3. Natural and conversational - like a knowledgeable staff member briefly explaining
4. Focused - answer what was asked, don't over-elaborate
5. Professional yet accessible - government communication standards

CRITICAL: Keep the response brief and to-the-point. Don't explain things the user didn't ask about.

Generate a concise system prompt (1-3 sentences) that will guide the AI to provide a brief, focused response. The prompt should:
- Define the assistant's role as a health department information specialist
- Emphasize BREVITY and staying on-topic
- Specify natural language (not tables)
- Set professional but conversational tone

System Prompt:"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert at designing effective system prompts for AI assistants. Create prompts that are specific, actionable, and optimized for the task."},
                {"role": "user", "content": meta_prompt}
            ],
            temperature=0.5,  # Moderate creativity for prompt design
            max_tokens=300
        )
        
        generated_prompt = response.choices[0].message.content.strip()
        
        # Remove any markdown formatting or quotes
        generated_prompt = generated_prompt.replace('"', '').replace('`', '').strip()
        
        return generated_prompt
        
    except Exception as e:
        logger.warning(f"Dynamic prompt generation failed: {e}")
        return None


def _summarize_data_structure(data: Dict) -> Dict:
    """Analyze data structure to help prompt generation"""
    summary = {
        "type": "unknown",
        "count": 0,
        "fields": []
    }
    
    # Determine data type and structure
    if "supplies" in data:
        summary["type"] = "inventory_list"
        summary["count"] = len(data.get("supplies", []))
        if data.get("supplies"):
            summary["fields"] = list(data["supplies"][0].keys())
    elif "campaigns" in data:
        summary["type"] = "campaign_list"
        summary["count"] = len(data.get("campaigns", []))
        if data.get("campaigns"):
            summary["fields"] = list(data["campaigns"][0].keys())
    elif "incidents" in data:
        summary["type"] = "incident_list"
        summary["count"] = len(data.get("incidents", []))
        if data.get("incidents"):
            summary["fields"] = list(data["incidents"][0].keys())
    elif "facilities" in data:
        summary["type"] = "facility_list"
        summary["count"] = len(data.get("facilities", []))
        if data.get("facilities"):
            summary["fields"] = list(data["facilities"][0].keys())
    elif "budget" in data:
        summary["type"] = "budget_summary"
        summary["count"] = 1
        summary["fields"] = list(data.get("budget", {}).keys())
    else:
        summary["type"] = "summary_stats"
        summary["count"] = sum(v for k, v in data.items() if k.endswith("_count"))
        summary["fields"] = list(data.keys())
    
    return summary


def _format_structured_response(intent: str, data: Dict) -> str:
    """Fallback: Format structured response without LLM"""
    
    if intent == "check_medical_supplies":
        supplies = data.get("supplies", [])
        if not supplies:
            return "No medical supplies found in the database."
        
        lines = [f"Medical Supplies Inventory ({len(supplies)} items):"]
        for supply in supplies:
            lines.append(
                f"- {supply['name']}: {supply['quantity']} units at {supply['location']} (Status: {supply['status']})"
            )
        return "\n".join(lines)
        
    elif intent == "check_vaccination_campaigns":
        campaigns = data.get("campaigns", [])
        if not campaigns:
            return "No vaccination campaigns found."
        
        lines = [f"Vaccination Campaigns ({len(campaigns)} total):"]
        for campaign in campaigns:
            lines.append(
                f"- {campaign['name']} in {campaign['location']} "
                f"({campaign['start_date']} to {campaign['end_date']}) - Status: {campaign['status']}"
            )
        return "\n".join(lines)
        
    elif intent == "check_disease_incidents":
        incidents = data.get("incidents", [])
        if not incidents:
            return "No disease incidents reported."
        
        lines = [f"Disease Incidents ({len(incidents)} total, {data.get('critical_count', 0)} critical):"]
        for incident in incidents[:10]:  # Limit to 10 most recent
            lines.append(
                f"- {incident['type']} at {incident['location']} "
                f"(Severity: {incident['severity']}, Status: {incident['status']})"
            )
        return "\n".join(lines)
        
    else:
        return f"Health department data: {json.dumps(data, indent=2, default=str)}"
