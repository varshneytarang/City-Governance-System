from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="City Governance System API",
    description="Backend API for City Governance System with LangGraph integration",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "City Governance System API",
        "status": "running",
        "version": "0.1.0"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-01-20"
    }

@app.get("/api/stats")
async def get_stats():
    """Get city governance statistics"""
    return {
        "totalCitizens": 125000,
        "activeProjects": 42,
        "pendingRequests": 18,
        "completedTasks": 156
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
