import asyncio
import uuid
from typing import Any, Dict, Optional
from datetime import datetime
import logging

from .agents_wrapper import run_agent_sync
from . import storage

logger = logging.getLogger(__name__)

# In-memory job store mirrors persisted store
_JOBS: Dict[str, Dict[str, Any]] = {}
# Per-job asyncio queues for websocket subscribers
_QUEUES: Dict[str, asyncio.Queue] = {}


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


async def _process_job(job_id: str, agent_id: str, input_event: Dict[str, Any]):
    """Background job runner that executes the agent in a thread and updates job state."""
    job = _JOBS[job_id]
    job["status"] = "running"
    job["started_at"] = _now_iso()
    storage.update_job_record(job_id, {"status": "running", "started_at": job["started_at"]})
    q = _QUEUES.get(job_id)

    # publish progress
    if q:
        await q.put({"type": "progress", "message": "Job started"})

    try:
        # Run the blocking agent in a thread
        result = await asyncio.to_thread(run_agent_sync, agent_id, input_event)

        job["status"] = "succeeded"
        job["finished_at"] = _now_iso()
        job["result"] = result

        # persist
        storage.update_job_record(job_id, {"status": "succeeded", "finished_at": job["finished_at"], "result": result})
        # log decision to audit table
        try:
            storage.log_decision(agent_id, input_event, result, job_id=job_id)
        except Exception:
            logger.exception("Failed to log decision to storage")

        if q:
            await q.put({"type": "result", "result": result})

    except Exception as e:
        logger.exception("Job processing failed")
        job["status"] = "failed"
        job["finished_at"] = _now_iso()
        job["error"] = str(e)
        storage.update_job_record(job_id, {"status": "failed", "finished_at": job["finished_at"], "error": str(e)})
        if q:
            await q.put({"type": "error", "error": str(e)})


def create_job(agent_id: str, input_event: Dict[str, Any]) -> str:
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "agent_id": agent_id,
        "status": "queued",
        "created_at": _now_iso(),
        "started_at": None,
        "finished_at": None,
        "result": None,
        "error": None,
    }
    _JOBS[job_id] = job
    # persist job (best-effort but raise/log if it fails)
    try:
        storage.save_job_record(job)
    except Exception as e:
        logger.exception("Failed to persist job record")
        # keep in-memory job but surface error to caller by re-raising
        raise

    # create queue for subscribers; ensure called from running loop
    try:
        _QUEUES[job_id] = asyncio.Queue()
    except RuntimeError:
        # No running loop in this thread — create a simple fallback queue
        # using asyncio.Queue tied to a new loop in a background thread is
        # complex; log and create a placeholder (non-async) queue entry.
        logger.warning("No running event loop when creating asyncio.Queue; queue will be None until background worker starts")
        _QUEUES[job_id] = None

    # schedule background processing
    try:
        asyncio.create_task(_process_job(job_id, agent_id, input_event))
    except RuntimeError:
        # If no running loop, schedule via threading as fallback
        import threading

        def _run():
            import asyncio

            asyncio.run(_process_job(job_id, agent_id, input_event))

        threading.Thread(target=_run, daemon=True).start()

    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    # prefer persisted record
    rec = storage.get_job_record(job_id)
    if rec:
        return rec
    return _JOBS.get(job_id)


def get_queue(job_id: str) -> Optional[asyncio.Queue]:
    return _QUEUES.get(job_id)
