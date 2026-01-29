# LLM Integration Implementation Guide

This guide shows how to enhance all nodes with LLM decision-making while keeping feasibility rules-based.

## Architecture

**LLM-Enhanced Nodes:**
1. ✅ Intent Analyzer - LLM classifies intent and assesses risk
2. ✅ Goal Setter - LLM formulates goals
3. ✅ Planner - LLM generates plans (ALREADY DONE)
4. ✅ Observer - LLM analyzes tool results
5. ❌ Feasibility - RULES ONLY (per user request)
6. ✅ Policy Validator - LLM checks policy compliance  
7. ✅ Confidence Estimator - LLM calculates confidence
8. ✅ Decision Router - LLM makes routing decisions

## Implementation Pattern

Each node follows this pattern:

```python
from .llm_helper import get_llm_client
import json

def node_function(state):
    llm_client = get_llm_client()
    
    if llm_client:
        # Try LLM first
        result = call_llm_with_prompt(llm_client, state)
        if result:
            return result
    
    # Fallback to deterministic logic
    return deterministic_logic(state)
```

## Prompt Templates

### 1. Intent Analyzer Prompt
```
Analyze this Water Department request:

REQUEST: {input_event}
CONTEXT: {context}

Return JSON:
{
  "intent": "negotiate_schedule|emergency_response|...",
  "risk_level": "low|medium|high|critical",
  "safety_concerns": ["list"],
  "reasoning": "explanation"
}
```

### 2. Goal Setter Prompt
```
Define a clear, actionable goal for this request:

INTENT: {intent}
REQUEST: {input_event}
CONTEXT: {context}

Return JSON:
{
  "goal": "Specific, measurable goal statement",
  "success_criteria": ["criterion1", "criterion2"],
  "constraints": ["constraint1", "constraint2"]
}
```

### 3. Observer Prompt
```
Analyze these tool execution results:

TOOL RESULTS: {tool_results}
ORIGINAL PLAN: {plan}

Return JSON:
{
  "key_observations": ["observation1", "observation2"],
  "discrepancies": ["issue1", "issue2"],
  "recommendations": ["action1", "action2"]
}
```

### 4. Policy Validator Prompt
```
Check if this plan complies with Water Department policies:

PLAN: {plan}
REQUEST: {input_event}

POLICIES:
- MAX_SHIFT_DELAY_DAYS = 3
- MIN_MAINTENANCE_NOTICE_HOURS = 24
- MAX_CONCURRENT_PROJECTS = 5
- Emergency overrides allowed

Return JSON:
{
  "compliant": true/false,
  "violations": ["violation1", "violation2"],
  "override_possible": true/false,
  "reasoning": "explanation"
}
```

### 5. Confidence Estimator Prompt
```
Estimate confidence (0.0-1.0) for this recommendation:

PLAN: {plan}
FEASIBILITY: {feasible}
POLICY: {policy_ok}
RISK: {risk_level}
OBSERVATIONS: {observations}

Return JSON:
{
  "confidence": 0.85,
  "confidence_factors": {
    "data_quality": 0.9,
    "plan_completeness": 0.8,
    "risk_assessment": 0.9
  },
  "reasoning": "explanation"
}
```

### 6. Decision Router Prompt
```
Decide whether to RECOMMEND or ESCALATE:

CONFIDENCE: {confidence}
FEASIBLE: {feasible}
POLICY_OK: {policy_ok}
RISK: {risk_level}
PLAN: {plan}

Return JSON:
{
  "decision": "recommend|escalate",
  "reasoning": "explanation",
  "escalation_reason": "if escalating, why?"
}
```

## Quick Implementation

Run this to enable LLM for all nodes:

```powershell
# Install required package
pip install openai

# Update .env
echo "LLM_PROVIDER=groq" >> .env
echo "GROQ_API_KEY=your_key" >> .env
echo "LLM_MODEL=llama-3.3-70b-versatile" >> .env

# Apply LLM enhancements
python scripts/enable_llm_all_nodes.py
```

## Testing

Test LLM integration:
```powershell
python test_llm_full_integration.py
```

Expected output:
```
✓ Intent Analyzer: Using LLM
✓ Goal Setter: Using LLM
✓ Planner: Using LLM  
✓ Observer: Using LLM
✗ Feasibility: Using RULES (by design)
✓ Policy Validator: Using LLM
✓ Confidence Estimator: Using LLM
✓ Decision Router: Using LLM
```

## Benefits

1. **Better Intent Understanding** - LLM can interpret nuanced requests
2. **Creative Goal Formulation** - LLM generates better-structured goals
3. **Smarter Planning** - Already implemented, works great
4. **Insightful Observations** - LLM spots patterns in tool results
5. **Flexible Policy** - LLM understands policy exceptions
6. **Accurate Confidence** - LLM weighs multiple factors
7. **Intelligent Routing** - LLM makes better escalation decisions

## Fallback Safety

All nodes maintain deterministic fallback:
- If LLM fails → use rules-based logic
- If LLM unavailable → use rules-based logic
- If LLM returns invalid JSON → use rules-based logic

This ensures **100% uptime** even without LLM!
