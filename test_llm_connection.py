"""
Test LLM Connection - Quick verification of API key and connectivity
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 60)
print("LLM CONNECTION TEST")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'NOT SET')}")
print(f"   OPENAI_API_KEY: {'SET ✓' if os.getenv('OPENAI_API_KEY') else 'NOT SET ✗'}")
print(f"   LLM_MODEL: {os.getenv('LLM_MODEL', 'NOT SET')}")

# Check if API key is actually set
openai_key = os.getenv('OPENAI_API_KEY', '')
if not openai_key or openai_key.strip() == '':
    print("\n❌ OPENAI_API_KEY is empty or not set!")
    print("\n   To enable LLM:")
    print("   1. Get an API key from https://platform.openai.com/api-keys")
    print("   2. Edit .env file and set: OPENAI_API_KEY=sk-...")
    print("\n   Note: Agents work WITHOUT LLM using deterministic fallbacks.")
    print("   But LLM provides better planning, observation, and confidence scoring.")
    exit(1)

print(f"   Key length: {len(openai_key)} characters")
print(f"   Key prefix: {openai_key[:10]}...")

# Try to initialize OpenAI client
print("\n2. Testing OpenAI Connection:")
try:
    import openai
    client = openai.OpenAI(api_key=openai_key)
    
    print("   ✓ OpenAI library imported")
    print("   ✓ Client initialized")
    
    # Test API call
    print("\n3. Testing API Call (simple completion):")
    response = client.chat.completions.create(
        model=os.getenv('LLM_MODEL', 'gpt-4'),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'API connection successful' and nothing else."}
        ],
        max_tokens=20,
        temperature=0
    )
    
    result = response.choices[0].message.content.strip()
    print(f"   Response: {result}")
    print("\n✅ LLM IS WORKING CORRECTLY!")
    print("\nYour agents will now use LLM for:")
    print("   • Intent analysis")
    print("   • Action planning")
    print("   • Observation analysis")
    print("   • Confidence estimation")
    
except ImportError:
    print("   ✗ OpenAI library not installed")
    print("   Run: pip install openai")
    exit(1)
    
except openai.AuthenticationError:
    print("   ✗ Authentication failed - Invalid API key")
    print("   Check your OPENAI_API_KEY in .env file")
    exit(1)
    
except openai.RateLimitError:
    print("   ✗ Rate limit exceeded or insufficient quota")
    print("   Check your OpenAI account billing")
    exit(1)
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("=" * 60)
