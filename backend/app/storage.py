import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime

DB_PATH = Path(__file__).parent / "local_data.db"


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Jobs table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            status TEXT,
            created_at TEXT,
            started_at TEXT,
            finished_at TEXT,
            result_json TEXT,
            error TEXT
        )
        """
    )

    # Agent decisions (audit)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_decisions (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            request_json TEXT,
            response_json TEXT,
            confidence REAL,
            created_at TEXT,
            job_id TEXT,
            summary TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def save_job_record(job: Dict[str, Any]) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "REPLACE INTO jobs (id, agent_id, status, created_at, started_at, finished_at, result_json, error) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            job.get("id"),
            job.get("agent_id"),
            job.get("status"),
            job.get("created_at"),
            job.get("started_at"),
            job.get("finished_at"),
            json.dumps(job.get("result")) if job.get("result") is not None else None,
            job.get("error"),
        ),
    )
    conn.commit()
    conn.close()


def update_job_record(job_id: str, fields: Dict[str, Any]) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # build set clause
    sets = []
    vals: List[Any] = []
    for k, v in fields.items():
        if k == "result":
            sets.append("result_json = ?")
            vals.append(json.dumps(v) if v is not None else None)
        else:
            sets.append(f"{k} = ?")
            vals.append(v)

    vals.append(job_id)
    sql = f"UPDATE jobs SET {', '.join(sets)} WHERE id = ?"
    cur.execute(sql, vals)
    conn.commit()
    conn.close()


def get_job_record(job_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, agent_id, status, created_at, started_at, finished_at, result_json, error FROM jobs WHERE id = ?", (job_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "agent_id": row[1],
        "status": row[2],
        "created_at": row[3],
        "started_at": row[4],
        "finished_at": row[5],
        "result": json.loads(row[6]) if row[6] else None,
        "error": row[7],
    }


def log_decision(agent_id: str, request: Dict[str, Any], response: Dict[str, Any], job_id: Optional[str] = None, summary: Optional[str] = None) -> str:
    """Persist agent decision to local DB. Returns generated id."""
    import uuid

    init_db()
    decision_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO agent_decisions (id, agent_id, request_json, response_json, confidence, created_at, job_id, summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            decision_id,
            agent_id,
            json.dumps(request),
            json.dumps(response),
            float(response.get("confidence", 0.0)) if response else 0.0,
            _now_iso(),
            job_id,
            summary,
        ),
    )
    conn.commit()
    conn.close()
    return decision_id


def list_decisions(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, agent_id, request_json, response_json, confidence, created_at, job_id, summary FROM agent_decisions ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    out: List[Dict[str, Any]] = []
    for r in rows:
        out.append({
            "id": r[0],
            "agent_id": r[1],
            "request": json.loads(r[2]) if r[2] else None,
            "response": json.loads(r[3]) if r[3] else None,
            "confidence": r[4],
            "created_at": r[5],
            "job_id": r[6],
            "summary": r[7] if len(r) > 7 else None,
        })
    return out


def get_decision_record(decision_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, agent_id, request_json, response_json, confidence, created_at, job_id, summary FROM agent_decisions WHERE id = ?", (decision_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id": r[0],
        "agent_id": r[1],
        "request": json.loads(r[2]) if r[2] else None,
        "response": json.loads(r[3]) if r[3] else None,
        "confidence": r[4],
        "created_at": r[5],
        "job_id": r[6],
        "summary": r[7] if len(r) > 7 else None,
    }


def list_decisions_by_agent(agent_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get decision history for a specific agent with summaries"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, agent_id, request_json, response_json, confidence, created_at, job_id, summary FROM agent_decisions WHERE agent_id = ? ORDER BY created_at DESC LIMIT ?",
        (agent_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    out: List[Dict[str, Any]] = []
    for r in rows:
        request_data = json.loads(r[2]) if r[2] else None
        response_data = json.loads(r[3]) if r[3] else None
        existing_summary = r[7] if len(r) > 7 else None
        
        # Generate summary if not exists
        if not existing_summary and request_data and response_data:
            try:
                from .summarizer import generate_chat_summary
                existing_summary = generate_chat_summary(request_data, response_data)
                # Update the record with the generated summary
                _update_decision_summary(r[0], existing_summary)
            except Exception as e:
                import logging
                logging.warning(f"Failed to generate summary: {e}")
                existing_summary = None
        
        out.append({
            "id": r[0],
            "agent_id": r[1],
            "request": request_data,
            "response": response_data,
            "confidence": r[4],
            "created_at": r[5],
            "job_id": r[6],
            "summary": existing_summary,
        })
    return out


def _update_decision_summary(decision_id: str, summary: str) -> None:
    """Update the summary for a decision record"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "UPDATE agent_decisions SET summary = ? WHERE id = ?",
            (summary, decision_id)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # Non-fatal, summary caching is optional


# Ensure DB exists on import
init_db()
