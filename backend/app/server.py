"""
FastAPI Backend - Routes all requests through Coordination Agent

The backend serves as the entry point for all city governance requests.
All requests are routed through the Coordination Agent which dispatches
them to the appropriate department agent.

Flow:
  Client → Backend → Coordination Agent → Department Agent → Response
"""

import logging
import uuid
import asyncio
import json
from datetime import datetime
from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import InputEvent, DecisionResponse
from . import jobs, storage

# Import Coordination Agent
from coordination_agent.agent import CoordinationAgent

logger = logging.getLogger("backend.server")

app = FastAPI(title="City Governance - Query API", version="0.2")

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Common React port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Coordination Agent instance
coordinator: Optional[CoordinationAgent] = None


@app.on_event("startup")
async def startup_event():
    """Initialize coordination agent on startup"""
    global coordinator
    logger.info("🚀 Starting City Governance Backend...")
    logger.info("   Initializing Coordination Agent...")
    
    try:
        coordinator = CoordinationAgent()
        logger.info("✅ Coordination Agent initialized and ready")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Coordination Agent: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global coordinator
    if coordinator:
        logger.info("🔒 Shutting down Coordination Agent...")
        coordinator.close()
        logger.info("✅ Coordination Agent closed")
    logger.info("👋 Backend shutdown complete")


@app.post("/api/v1/query")
async def submit_query(payload: InputEvent) -> Any:
	"""
	Submit a query that will be routed through the Coordination Agent.
	
	The Coordination Agent will:
	1. Analyze the request
	2. Route to appropriate department agent(s)
	3. Handle any conflicts
	4. Return unified response
	
	Flow: Client → Backend → Coordinator → Department Agent(s) → Response
	
	Request body must include:
	- type: Request type (capacity_query, emergency_response, etc.)
	- location: Location affected
	- Other optional fields depending on request type
	
	Returns:
	- job_id: Unique identifier to poll for results
	- status: "queued" - job is processing in background
	"""
	global coordinator
	
	if not coordinator:
		raise HTTPException(status_code=503, detail="Coordination Agent not initialized")
	
	# Normalize payload
	input_dict = payload.dict(by_alias=True)
	
	# Determine which agent should handle this request
	agent_type = _determine_agent_type(input_dict.get("type", ""))
	
	logger.info(f"📥 New query received: {input_dict.get('type')} → {agent_type} agent")
	
	# Create and persist a job record
	job_id = str(uuid.uuid4())
	now = datetime.utcnow().isoformat() + "Z"
	job = {
		"id": job_id,
		"agent_id": agent_type,
		"status": "queued",
		"created_at": now,
		"started_at": None,
		"finished_at": None,
		"result": None,
		"error": None,
	}
	
	try:
		storage.save_job_record(job)
	except Exception:
		logger.exception("Failed to save initial job record")
		raise HTTPException(status_code=500, detail="Failed to persist job record")
	
	# Background task: route through coordinator and persist response
	async def _route_through_coordinator(job_id: str, agent_type: str, input_event: dict):
		start_ts = datetime.utcnow().isoformat() + "Z"
		try:
			storage.update_job_record(job_id, {"status": "running", "started_at": start_ts})
			
			logger.info(f"🔄 Routing to coordination agent...")
			
			# Call coordination agent which will query the appropriate department agent
			def _call_coordinator():
				return coordinator.query_agent(
					agent_type=agent_type,
					request=input_event,
					reason=f"Backend query {job_id}"
				)
			
			# Run in thread to avoid blocking
			coord_response = await asyncio.to_thread(_call_coordinator)
			
			if coord_response.get("success"):
				result = coord_response.get("response", {})
				logger.info(f"✅ Agent responded: {result.get('decision', 'N/A')}")
			else:
				error_msg = coord_response.get("error", "Unknown error")
				logger.error(f"❌ Agent query failed: {error_msg}")
				raise RuntimeError(error_msg)
			
			finish_ts = datetime.utcnow().isoformat() + "Z"
			storage.update_job_record(job_id, {
				"status": "succeeded",
				"finished_at": finish_ts,
				"result": result
			})
			
			try:
				storage.log_decision(agent_type, input_event, result, job_id=job_id)
			except Exception:
				logger.exception("Failed to log decision to audit table")
		
		except Exception as e:
			logger.exception("Coordinator query failed: %s", e)
			finish_ts = datetime.utcnow().isoformat() + "Z"
			storage.update_job_record(job_id, {
				"status": "failed",
				"finished_at": finish_ts,
				"error": str(e)
			})
	
	# Schedule background execution
	asyncio.create_task(_route_through_coordinator(job_id, agent_type, input_dict))
	
	return {"job_id": job_id, "status": "queued", "agent_type": agent_type}


def _determine_agent_type(request_type: str) -> str:
	"""
	Determine which agent should handle the request based on type.
	
	Maps request types to department agents.
	"""
	# Water department request types
	water_types = [
		"capacity_query", "schedule_shift_request", "emergency_response",
		"maintenance_request", "pipeline_repair", "water_quality_check"
	]
	
	# Engineering department request types
	engineering_types = [
		"project_planning", "infrastructure_assessment", "road_repair",
		"bridge_inspection", "construction_approval"
	]
	
	# Fire department request types
	fire_types = [
		"fire_emergency", "fire_inspection", "fire_safety_assessment",
		"hazmat_response", "rescue_operation"
	]
	
	# Sanitation department request types
	sanitation_types = [
		"waste_collection", "street_cleaning", "sanitation_inspection",
		"recycling_request", "hazardous_waste_disposal"
	]
	
	# Health department request types
	health_types = [
		"health_inspection", "disease_outbreak", "vaccination_campaign",
		"restaurant_inspection", "public_health_assessment"
	]
	
	# Finance department request types
	finance_types = [
		"budget_approval", "cost_estimation", "financial_audit",
		"revenue_forecast", "expenditure_review"
	]
	
	if request_type in water_types:
		return "water"
	elif request_type in engineering_types:
		return "engineering"
	elif request_type in fire_types:
		return "fire"
	elif request_type in sanitation_types:
		return "sanitation"
	elif request_type in health_types:
		return "health"
	elif request_type in finance_types:
		return "finance"
	else:
		# Default to water for backward compatibility
		logger.warning(f"Unknown request type '{request_type}', defaulting to water agent")
		return "water"


@app.get("/api/v1/query/{job_id}")
def get_query_result(job_id: str) -> Any:
	"""
	Fetch status/result for a previously submitted query job.
	
	Returns job details including:
	- status: queued, running, succeeded, or failed
	- result: Agent decision (if completed)
	- error: Error message (if failed)
	"""
	job = jobs.get_job(job_id)
	if not job:
		raise HTTPException(status_code=404, detail="Job not found")
	return job


@app.get("/api/v1/query/{job_id}/result")
def get_query_decision(job_id: str) -> Any:
	"""
	Convenience endpoint: return only the job result (decision) and status.
	
	Returns JSON: {"status": <job status>, "result": <decision dict or null>}.
	"""
	job = jobs.get_job(job_id)
	if not job:
		raise HTTPException(status_code=404, detail="Job not found")
	
	return {"status": job.get("status"), "result": job.get("result")}


# Legacy endpoints (backward compatibility)
@app.post("/api/v1/agents/{agent_id}/query")
async def submit_agent_query_legacy(agent_id: str, payload: InputEvent) -> Any:
	"""
	Legacy endpoint - Routes to coordination agent.
	
	For backward compatibility. New integrations should use POST /api/v1/query
	"""
	logger.info(f"⚠️  Using legacy endpoint /agents/{agent_id}/query")
	logger.info(f"   Consider migrating to POST /api/v1/query")
	
	# Add agent_id to payload metadata if not already there
	input_dict = payload.dict(by_alias=True)
	if "metadata" not in input_dict:
		input_dict["metadata"] = {}
	input_dict["metadata"]["requested_agent"] = agent_id
	
	# Create new InputEvent with metadata
	enhanced_payload = InputEvent(**input_dict)
	
	# Route through main endpoint
	return await submit_query(enhanced_payload)


@app.get("/api/v1/agents/{agent_id}/query/{job_id}")
def get_agent_query_result(agent_id: str, job_id: str) -> Any:
	"""Legacy endpoint - Fetch query result. Use GET /api/v1/query/{job_id} instead."""
	job = jobs.get_job(job_id)
	if not job:
		raise HTTPException(status_code=404, detail="Job not found")
	# Basic check that job matches requested agent_id
	if job.get("agent_id") != agent_id:
		raise HTTPException(status_code=400, detail="Job exists but agent_id does not match")
	return job


@app.get("/api/v1/agents/{agent_id}/query/{job_id}/result")
def get_agent_decision_result(agent_id: str, job_id: str) -> Any:
	"""Legacy endpoint - Get decision result. Use GET /api/v1/query/{job_id}/result instead."""
	job = jobs.get_job(job_id)
	if not job:
		raise HTTPException(status_code=404, detail="Job not found")
	if job.get("agent_id") != agent_id:
		raise HTTPException(status_code=400, detail="Job exists but agent_id does not match")

	return {"status": job.get("status"), "result": job.get("result")}


@app.get("/api/v1/health")
def health():
	"""Health check endpoint"""
	global coordinator
	
	coordinator_status = "initialized" if coordinator else "not_initialized"
	
	return {
		"status": "ok",
		"coordinator": coordinator_status,
		"version": "0.2"
	}
