# 🤖 Enabling LLM Integration

## Current Status

**Your agent currently uses DETERMINISTIC fallback logic** - it doesn't call Groq/OpenAI APIs. This is intentional for production stability.

## Why You're Not Seeing API Calls

The current `planner.py` uses `_generate_deterministic_plans()` which creates plans based on rules, not LLM.

## How to Enable LLM API Calls

### Option 1: Replace Planner (Recommended)

**Step 1:** Add Groq API key to your `.env`:
```bash
# For Groq (free tier available)
GROQ_API_KEY=gsk_your_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama3-70b-8192

# OR for OpenAI
OPENAI_API_KEY=sk-your_key_here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

**Step 2:** Replace the planner with LLM-enhanced version:
```powershell
# Backup original
Copy-Item water_agent\nodes\planner.py water_agent\nodes\planner_backup.py

# Replace with LLM version
Copy-Item water_agent\nodes\planner_llm_enhanced.py water_agent\nodes\planner.py
```

**Step 3:** Install OpenAI library:
```powershell
pip install openai
```

**Step 4:** Test LLM integration:
```powershell
python test_llm_integration.py
```

You should now see API calls in your Groq dashboard!

### Option 2: Manual Integration

Edit `water_agent/nodes/planner.py` and modify the `generate_plan()` method:

```python
def generate_plan(self, state: DepartmentState) -> Dict:
    # Add this at the start
    if os.getenv("GROQ_API_KEY"):
        import openai
        client = openai.OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a water department planner..."},
                {"role": "user", "content": f"Create plan for: {goal}"}
            ],
            temperature=0.3
        )
        
        # Parse response and return
        return parse_llm_response(response)
    
    # Otherwise use deterministic fallback
    return self._generate_deterministic_plans(...)
```

## Verifying LLM is Being Called

### Method 1: Check Dashboard
- **Groq**: https://console.groq.com/
- **OpenAI**: https://platform.openai.com/usage

### Method 2: Add Logging
Add this to `planner.py`:
```python
import logging
logger.info("🤖 Calling Groq API...")
response = client.chat.completions.create(...)
logger.info(f"✓ API Response received: {len(response.choices[0].message.content)} chars")
```

### Method 3: Run Test Suite
```powershell
python test_llm_integration.py -v
```

Look for:
```
✓ API Key found: gsk_abc123...
🤖 Calling LLM API...
✓ LLM response received
```

## Architecture Design

### Why Deterministic Fallback?

The agent is designed with **LLM-optional architecture**:

1. **LLM Proposes** → Creative plans, alternatives
2. **Rules Validate** → Deterministic feasibility checks  
3. **Humans Approve** → Final decision

This means:
- ✅ Agent works **without** LLM (deterministic mode)
- ✅ Agent enhanced **with** LLM (creative mode)
- ✅ Production-ready in both modes

### What Uses LLM?

Only **Phase 6: Planner** benefits from LLM:
- Intent Analysis: **Rules-based** (deterministic)
- Goal Setting: **Rules-based** (deterministic)
- **Planning: LLM-enhanced** ← This is where API calls happen
- Feasibility Check: **Rules-based** (deterministic)
- Policy Validation: **Rules-based** (deterministic)
- Confidence: **Rules-based** (deterministic)

## Cost Implications

### Groq (Recommended for Testing)
- **Free tier**: 14,400 requests/day
- **Model**: llama3-70b-8192
- **Speed**: ~300 tokens/sec
- **Cost**: FREE for moderate use

### OpenAI
- **gpt-4**: $0.03/1K input tokens, $0.06/1K output tokens
- **gpt-3.5-turbo**: $0.0015/1K input tokens, $0.002/1K output tokens
- Estimated: ~$0.01-0.05 per agent decision

## Testing LLM Integration

Run the comprehensive test:
```powershell
python test_llm_integration.py
```

Expected output:
```
LLM INTEGRATION STATUS CHECK
====================================
Provider: groq
API Key: ✓ Configured
Model: llama3-70b-8192

test_planner_calls_llm
✓ LLM API was called during planning!
  Call count: 1
```

## Example: Comparing Deterministic vs LLM

### Deterministic Output:
```json
{
  "steps": [
    "1. Review current work schedule",
    "2. Identify affected workers",
    "3. Shift work by 2 days"
  ]
}
```

### LLM-Enhanced Output:
```json
{
  "steps": [
    "1. Conduct comprehensive schedule analysis considering worker availability, ongoing projects, and resource constraints",
    "2. Identify critical path items and dependencies that may be affected by the 2-day shift",
    "3. Develop mitigation strategies for potential conflicts with emergency response capacity",
    "4. Coordinate with Fire Department for any joint operations during transition period",
    "5. Implement phased shift to minimize service disruption"
  ],
  "alternatives": ["Fast-track option", "Gradual transition plan"]
}
```

## Troubleshooting

### "No API calls in Groq dashboard"
1. Verify `.env` has `GROQ_API_KEY=gsk_...`
2. Check you're using `planner_llm_enhanced.py`
3. Confirm `LLM_PROVIDER=groq` in `.env`
4. Run with logging: `LOG_LEVEL=DEBUG python examples.py`

### "ModuleNotFoundError: openai"
```powershell
pip install openai
```

### "API key invalid"
Get new key from: https://console.groq.com/keys

## Quick Start (Copy-Paste)

```powershell
# 1. Add to .env
echo "GROQ_API_KEY=gsk_your_actual_key_here" >> .env
echo "LLM_PROVIDER=groq" >> .env
echo "LLM_MODEL=llama3-70b-8192" >> .env

# 2. Install dependency
pip install openai

# 3. Enable LLM planner
Copy-Item water_agent\nodes\planner_llm_enhanced.py water_agent\nodes\planner.py

# 4. Test it
python test_llm_integration.py -v

# 5. Check Groq dashboard
# https://console.groq.com/
```

## Summary

- **Current**: Deterministic mode (no API calls) ✅ Production-ready
- **Enhanced**: LLM mode (creative planning) ✅ Requires API key
- **Both work**: Architecture supports both modes
- **Your choice**: Enable LLM for better plans, or keep deterministic for reliability

Choose based on your needs! 🚀
