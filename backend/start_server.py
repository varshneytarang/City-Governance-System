#!/usr/bin/env python3
"""
Quick Start Script for City Governance Backend

Run this to start the backend server with proper CORS configuration.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("\n" + "=" * 80)
print("🚀 STARTING CITY GOVERNANCE BACKEND SERVER")
print("=" * 80)
print("\nBackend will be available at: http://localhost:8000")
print("API Documentation: http://localhost:8000/docs")
print("\nCORS Enabled for:")
print("  - http://localhost:3000 (React)")
print("  - http://localhost:5173 (Vite)")
print("  - http://127.0.0.1:3000")
print("  - http://127.0.0.1:5173")
print("\n" + "=" * 80)
print()

if __name__ == "__main__":
    import uvicorn
    
    # Start the server
    uvicorn.run(
        "app.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
