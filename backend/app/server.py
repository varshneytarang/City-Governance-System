import logging
import os
from fastapi import FastAPI, HTTPException, Query, Header, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Optional
from typing import List, Dict
from . import storage

from .schemas import InputEvent, DecisionResponse
from .agents_wrapper import run_agent_sync
from . import jobs


def require_api_key(x_api_key: str = Header(None)):
    """Compatibility helper kept for future use.

    Current configuration does not require callers to provide an API key.
    The server will still read `API_KEY` from the environment for outgoing
    integrations if needed.
    """
    return True

logger = logging.getLogger("backend.server")

app = FastAPI(title="City Governance Agents API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/agents/{agent_id}/decide", response_model=DecisionResponse)
def agent_decide(
    agent_id: str,
    payload: InputEvent,
    async_: bool = Query(False, alias="async"),
) -> Any:
    """Request a decision from an agent.

    Query `async=true` is accepted but not yet implemented; returns 501.
    """
    # Normalize payload to dict with original key names
    input_dict = payload.dict(by_alias=True)

    logger.info(f"Received decision request for agent={agent_id}")

    if async_:
        # create job and return job id wrapper
        job_id = jobs.create_job(agent_id, input_dict)
        return DecisionResponse(
            decision="queued",
            reason=f"Job queued: {job_id}",
            recommendation={"job_id": job_id},
            confidence=0.0,
        )

    result = run_agent_sync(agent_id, input_dict)

    if result is None:
        raise HTTPException(status_code=500, detail="Agent returned no result")

    # Ensure decision field exists
    if not isinstance(result, dict) or "decision" not in result:
        raise HTTPException(status_code=500, detail="Invalid agent response format")

    return DecisionResponse(**result)



@app.get("/api/v1/jobs/{job_id}")
def get_job_status(job_id: str):
    job = jobs.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.websocket("/api/v1/ws/jobs/{job_id}")
async def ws_job_updates(websocket: WebSocket, job_id: str):
    # Accept WebSocket connection without API key for simplicity
    await websocket.accept()
    q = jobs.get_queue(job_id)
    if q is None:
        await websocket.send_json({"type": "error", "error": "Job not found"})
        await websocket.close()
        return

    try:
        while True:
            msg = await q.get()
            await websocket.send_json(msg)
            if msg.get("type") in ("result", "error"):
                # close after final message
                await websocket.close()
                break
    except WebSocketDisconnect:
        return


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/coordination/coordinate")
def coordinate(agent_decisions: List[Dict[str, Any]] = Body(...)):
    """Coordinate multiple agent decisions via `coordination_agent` package.

    Body: JSON array of decision dicts as produced by agents.
    """
    try:
        from coordination_agent.agent import CoordinationAgent

        coord = CoordinationAgent()
        result = coord.coordinate(agent_decisions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/transparency/search")
def transparency_search(q: str = Query(...), agent_type: Optional[str] = None, limit: int = 10):
    """Search transparency logs. Uses `transparency_logger` if available."""
    try:
        from transparency_logger import TransparencyLogger

        tl = TransparencyLogger()
        results = tl.search_decisions(query=q, n_results=limit, filter_agent=agent_type)
        return {"results": results}
    except Exception as e:
        # If transparency subsystem not available, return informative message
        return {"results": [], "note": str(e)}


@app.get("/api/v1/decisions")
def list_decisions(limit: int = Query(50, ge=1, le=100)):
    """List recent persisted agent decisions (audit)."""
    results = storage.list_decisions(limit=limit)
    return {"results": results}


@app.get("/api/v1/decisions/{decision_id}")
def get_decision(decision_id: str):
    rec = storage.get_decision_record(decision_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Decision not found")
    return rec
