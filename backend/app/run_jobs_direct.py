import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
jobs_path = ROOT / "backend" / "app" / "jobs.py"

spec = importlib.util.spec_from_file_location("jobs_module", str(jobs_path))
jobs = importlib.util.module_from_spec(spec)
sys.modules["jobs_module"] = jobs
spec.loader.exec_module(jobs)

payload = {"type": "schedule_shift_request", "from": "Coordinator", "location": "Zone-1"}
try:
    job_id = jobs.create_job("water", payload)
    print("Created job:", job_id)
except Exception as e:
    print("create_job raised:", type(e).__name__, e)
