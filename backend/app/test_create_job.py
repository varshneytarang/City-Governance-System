from backend.app import jobs

payload = {
    "type": "schedule_shift_request",
    "from": "Coordinator",
    "location": "Zone-1",
}

try:
    job_id = jobs.create_job("water", payload)
    print("Created job:", job_id)
except Exception as e:
    print("create_job raised:", type(e).__name__, e)
