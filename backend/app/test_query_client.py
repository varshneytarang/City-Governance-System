"""Simple client that submits a water agent query and polls for the job result.

Uses only Python standard library so no extra dependencies are required.
"""
import json
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


BASE = "http://127.0.0.1:8000"


def post_query(agent_id: str, payload: dict) -> dict:
    url = f"{BASE}/api/v1/agents/{agent_id}/query"
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except HTTPError as e:
        return {"error": f"HTTPError: {e.code} - {e.reason}"}
    except URLError as e:
        return {"error": f"URLError: {e.reason}"}


def get_job(agent_id: str, job_id: str) -> dict:
    url = f"{BASE}/api/v1/agents/{agent_id}/query/{job_id}"
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except HTTPError as e:
        return {"error": f"HTTPError: {e.code} - {e.reason}"}
    except URLError as e:
        return {"error": f"URLError: {e.reason}"}


def main():
    payload = {
        "type": "schedule_shift_request",
        "from": "Coordinator",
        "location": "Zone-1",
        "requested_shift_days": 2,
        "reason": "Joint underground work near mains",
    }

    print("Submitting query to water agent...")
    resp = post_query("water", payload)
    print("Submit response:", resp)

    job_id = resp.get("job_id")
    if not job_id:
        print("No job_id returned; aborting.")
        return

    print(f"Polling job {job_id} (interval=2s) ...")
    for _ in range(30):
        st = get_job("water", job_id)
        print("Job status:", json.dumps(st))
        status = st.get("status")
        if status in ("succeeded", "failed"):
            print("Final job record:", json.dumps(st, indent=2))
            return
        time.sleep(2)

    print("Timed out waiting for job to finish.")


if __name__ == "__main__":
    main()
