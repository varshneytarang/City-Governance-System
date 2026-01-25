from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

from app.routes.water import router as water_router
from app.routes.fire import router as fire_router
from app.database import close_db

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting City Governance System API...")
    print("✅ Water Agent initialized")
    print("✅ Fire Agent initialized")
    yield
    # Shutdown
    print("🛑 Shutting down...")
    await close_db()


# Initialize FastAPI app
app = FastAPI(
    title="City Governance System API",
    description="Backend API for City Governance System with LangGraph integration",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(water_router)
app.include_router(fire_router)

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
