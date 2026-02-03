# Query API Examples

POST /api/v1/agents/{agent_id}/query

Example curl (submit a water agent query):

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/agents/water/query" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "schedule_shift_request",
    "from": "Coordinator",
    "location": "Zone-1",
    "requested_shift_days": 2,
    "reason": "Joint underground work near mains"
  }'
```

Response (example):

```json
{ "job_id": "<uuid>", "status": "queued" }
```

GET /api/v1/agents/{agent_id}/query/{job_id}

Example curl (poll job status/result):

```bash
curl "http://127.0.0.1:8000/api/v1/agents/water/query/<job_id>"
```

Example Python (requests) usage:

```python
import requests
url = "http://127.0.0.1:8000/api/v1/agents/water/query"
payload = {
    "type": "emergency_response",
    "from": "FieldSensor",
    "location": "Zone-3",
    "reason": "Burst main, flooding risk",
}
r = requests.post(url, json=payload)
print(r.json())

# Poll result
job_id = r.json().get("job_id")
if job_id:
    status_url = f"http://127.0.0.1:8000/api/v1/agents/water/query/{job_id}"
    resp = requests.get(status_url)
    print(resp.json())
```

---

Use the included `test_query_client.py` to run an example end-to-end without extra dependencies.
