"""Submit a capacity_query to the water agent requesting employee count and names,
then poll the result endpoint until completion. Uses standard library only.
"""
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "http://127.0.0.1:8000"


def post_query(payload: dict) -> dict:
    url = f"{BASE}/api/v1/agents/water/query"
    req = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except HTTPError as e:
        print("POST HTTPError", e.code)
        try:
            print(e.read().decode())
        except Exception:
            pass
        return {"error": True}
    except URLError as e:
        print("POST URLError", e.reason)
        return {"error": True}


def get_result(job_id: str) -> dict:
    url = f"{BASE}/api/v1/agents/water/query/{job_id}/result"
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except HTTPError as e:
        print("GET HTTPError", e.code)
        try:
            print(e.read().decode())
        except Exception:
            pass
        return {"error": True}
    except URLError as e:
        print("GET URLError", e.reason)
        return {"error": True}


def main():
    payload = {
        "type": "capacity_query",
        "from": "AutomatedTest",
        "location": "Water Department",
        "reason": "Return total number of employees in water department and their names",
        "metadata": {"query_intent": "employee_list"}
    }

    print("Submitting employee list query...")
    resp = post_query(payload)
    print("Submit response:", resp)
    job_id = resp.get("job_id")
    if not job_id:
        print("Failed to create job")
        return

    print(f"Polling result for job {job_id}...")
    for i in range(60):
        res = get_result(job_id)
        print(f"Poll {i}:", res)
        if res.get("status") in ("succeeded", "failed"):
            print("Final result:")
            print(json.dumps(res.get("result"), indent=2))
            return
        time.sleep(2)

    print("Timed out waiting for result")


if __name__ == "__main__":
    main()
