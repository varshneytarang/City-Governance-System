"""
Start Backend Server with Coordination Agent Integration

This script starts the FastAPI backend which routes all requests
through the Coordination Agent to the appropriate department agent.
"""

import os
import sys
import logging

# Configure logging FIRST to capture all agent logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("\n" + "=" * 80)
print("🚀 STARTING CITY GOVERNANCE BACKEND")
print("=" * 80)
print("\nArchitecture:")
print("  Client → Backend → Coordinator → Department Agent → Response")
print("\nFeatures:")
print("  ✅ Automatic agent routing based on request type")
print("  ✅ Coordination agent handles conflicts")
print("  ✅ Full LLM integration (6 nodes per request)")
print("  ✅ Agent instance caching for performance")
print("  ✅ Async job processing")
print("\n" + "=" * 80)

# Check if dependencies are installed
try:
    import fastapi
    import uvicorn
    print("\n✅ FastAPI installed")
except ImportError:
    print("\n❌ FastAPI not installed!")
    print("   Run: pip install fastapi uvicorn")
    sys.exit(1)

# Check if coordination agent is available
try:
    from agents.coordination_agent.agent import CoordinationAgent
    print("✅ Coordination Agent available")
except ImportError as e:
    print(f"\n❌ Coordination Agent import failed: {e}")
    sys.exit(1)

# Check environment variables
from global_config import global_llm_settings

print("\n" + "-" * 80)
print("Configuration Check:")
print("-" * 80)
print(f"LLM Provider: {global_llm_settings.LLM_PROVIDER}")
print(f"Model: {global_llm_settings.LLM_MODEL}")

if global_llm_settings.LLM_PROVIDER == "groq":
    if global_llm_settings.GROQ_API_KEY:
        print(f"Groq API Key: {global_llm_settings.GROQ_API_KEY[:10]}...")
        print("✅ LLM configured")
    else:
        print("⚠️  GROQ_API_KEY not set - agents will use fallback mode")
elif global_llm_settings.LLM_PROVIDER == "openai":
    if global_llm_settings.OPENAI_API_KEY:
        print(f"OpenAI API Key: {global_llm_settings.OPENAI_API_KEY[:10]}...")
        print("✅ LLM configured")
    else:
        print("⚠️  OPENAI_API_KEY not set - agents will use fallback mode")

print("-" * 80)

print("\n" + "=" * 80)
print("STARTING SERVER...")
print("=" * 80)
print("\nEndpoints:")
print("  POST   /api/v1/query           - Submit query (routed to appropriate agent)")
print("  GET    /api/v1/query/{job_id}  - Get query result")
print("  GET    /api/v1/health           - Health check")
print("\nDocumentation:")
print("  http://localhost:8000/docs      - Interactive API docs")
print("\nTest Integration:")
print("  python test_backend_coordinator.py")
print("\n" + "=" * 80)
print("\n🌐 Starting server on http://localhost:8000")
print("   Press CTRL+C to stop\n")

# Import the FastAPI app to make it available for uvicorn
from app.server import app

# Start the server
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
