"""
Minimal FastAPI application — API route handlers removed.

Per request, all existing route definitions were cleared from this module.
Reintroduce endpoints as needed; this file intentionally exposes an empty
FastAPI `app` instance so the project can import it without route handlers.
"""

import logging
from typing import Any
from fastapi import FastAPI, HTTPException
from .schemas import InputEvent
from . import jobs
import logging
import uuid
import asyncio
import json
from datetime import datetime
from typing import Any
from fastapi import FastAPI, HTTPException
from .schemas import InputEvent
from . import jobs, storage

# LLM helper from water_agent
from water_agent.nodes.llm_helper import get_llm_client
from water_agent.config import settings as wa_settings

logger = logging.getLogger("backend.server")

# App exposes endpoints for queued agent queries. POST will invoke the LLM
# (in background) and persist the response so GET can return it.
app = FastAPI(title="City Governance - Query API", version="0.1")


@app.post("/api/v1/agents/{agent_id}/query")
async def submit_agent_query(agent_id: str, payload: InputEvent) -> Any:
	"""Submit a query to an agent. Currently supports `agent_id == "water"`.

	This handler is `async` so `jobs.create_job` runs inside the application's
	asyncio event loop and can create asyncio primitives (queues/tasks).
	The request is queued and processed in background; this returns a `job_id`
	which can be polled with the GET endpoint below.
	"""
	# normalize payload
	input_dict = payload.dict(by_alias=True)

	# only allow the water agent
	if agent_id != "water":
		raise HTTPException(status_code=400, detail="Only 'water' agent is supported in this endpoint")

	# Create and persist a job record immediately so GET can find it.
	job_id = str(uuid.uuid4())
	now = datetime.utcnow().isoformat() + "Z"
	job = {
		"id": job_id,
		"agent_id": agent_id,
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

	# Background task: call LLM and persist its response so GET returns it.
	async def _run_llm_and_store(job_id: str, input_event: dict):
		start_ts = datetime.utcnow().isoformat() + "Z"
		try:
			storage.update_job_record(job_id, {"status": "running", "started_at": start_ts})

			llm_client = get_llm_client()
			if not llm_client:
				raise RuntimeError("LLM client unavailable")

			# Prompt the LLM for structured JSON tailored to the input
			prompt = (
				"You are a helpful municipal data assistant. Given this query, return ONLY valid JSON with keys:"
				" 'decision' (string), 'reason' (string), and 'details' (object). If the query requests employee info, include"
				" 'details.employee_count' and 'details.employees' (list of names).\n\nUSER QUERY:\n" + json.dumps(input_event, indent=2, default=str)
			)

			def _call_llm():
				return llm_client.chat.completions.create(
					model=wa_settings.LLM_MODEL,
					messages=[
						{"role": "system", "content": "You are a municipal assistant that returns strict JSON."},
						{"role": "user", "content": prompt},
					],
					temperature=wa_settings.LLM_TEMPERATURE,
					max_tokens=512,
				)

			response = await asyncio.to_thread(_call_llm)
			llm_output = ""
			try:
				llm_output = response.choices[0].message.content.strip()
			except Exception:
				llm_output = str(response)

			# Clean fences
			if llm_output.startswith("```json"):
				llm_output = llm_output[7:]
			elif llm_output.startswith("```"):
				llm_output = llm_output[3:]
			if llm_output.endswith("```"):
				llm_output = llm_output[:-3]

			try:
				parsed = json.loads(llm_output)
			except Exception:
				parsed = {"raw": llm_output}

			result = parsed

			finish_ts = datetime.utcnow().isoformat() + "Z"
			storage.update_job_record(job_id, {"status": "succeeded", "finished_at": finish_ts, "result": result})

			try:
				storage.log_decision(agent_id, input_event, result, job_id=job_id)
			except Exception:
				logger.exception("Failed to log decision to audit table")

		except Exception as e:
			logger.exception("LLM invocation failed: %s", e)
			finish_ts = datetime.utcnow().isoformat() + "Z"
			storage.update_job_record(job_id, {"status": "failed", "finished_at": finish_ts, "error": str(e)})

	# schedule background execution
	asyncio.create_task(_run_llm_and_store(job_id, input_dict))

	return {"job_id": job_id, "status": "queued"}


@app.get("/api/v1/agents/{agent_id}/query/{job_id}")
def get_agent_query_result(agent_id: str, job_id: str) -> Any:
	"""Fetch status/result for a previously submitted query job."""
	job = jobs.get_job(job_id)
	if not job:
		raise HTTPException(status_code=404, detail="Job not found")
	# Basic check that job matches requested agent_id
	if job.get("agent_id") != agent_id:
		raise HTTPException(status_code=400, detail="Job exists but agent_id does not match")
	return job


@app.get("/api/v1/agents/{agent_id}/query/{job_id}/result")
def get_agent_decision_result(agent_id: str, job_id: str) -> Any:
	"""Convenience endpoint: return only the job result (decision) and status.

	Returns JSON: {"status": <job status>, "result": <decision dict or null>}.
	"""
	job = jobs.get_job(job_id)
	if not job:
		raise HTTPException(status_code=404, detail="Job not found")
	if job.get("agent_id") != agent_id:
		raise HTTPException(status_code=400, detail="Job exists but agent_id does not match")

	return {"status": job.get("status"), "result": job.get("result")}


@app.get("/api/v1/health")
def health():
	return {"status": "ok"}
