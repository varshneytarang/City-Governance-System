"""
Test Gemini Integration for Gemini 3 Hackathon
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini():
    """Test Google Gemini API integration"""
    print("=" * 80)
    print("🚀 Testing Gemini Integration for Gemini 3 Hackathon")
    print("=" * 80)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment!")
        return False
    
    print(f"✅ Gemini API Key loaded: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # Initialize Gemini
        print("\n📦 Initializing Gemini model: gemini-pro...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.3,
            google_api_key=api_key
        )
        
        # Test simple prompt
        print("\n🧪 Testing Gemini with simple prompt...")
        response = await llm.ainvoke("What is the capital of India? Answer in one word.")
        print(f"✅ Gemini Response: {response.content}")
        
        # Test emergency analysis prompt (Fire Agent scenario)
        print("\n🧪 Testing Gemini with Fire Agent emergency prompt...")
        emergency_prompt = """You are a Fire Department AI Agent analyzing an emergency.

Emergency Details:
- Type: Building Fire
- Location: 123 Main Street
- Casualties: 3 people trapped
- Fire Intensity: High
- Building Type: 3-story residential

Analyze this emergency and provide:
1. Severity assessment (Critical/High/Medium/Low)
2. Required resources (personnel, vehicles, equipment)
3. Key safety concerns

Be concise and professional."""

        response = await llm.ainvoke(emergency_prompt)
        print(f"\n✅ Gemini Emergency Analysis:\n{response.content}\n")
        
        print("=" * 80)
        print("✅ GEMINI INTEGRATION TEST PASSED!")
        print("🎉 Your system is ready for Gemini 3 Hackathon!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing Gemini: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini())
    exit(0 if result else 1)
