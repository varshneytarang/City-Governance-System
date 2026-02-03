import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

url = "http://127.0.0.1:8000/api/v1/agents/water/query"
payload = {
    "type": "schedule_shift_request",
    "from": "Coordinator",
    "location": "Zone-1",
    "requested_shift_days": 2,
    "reason": "Joint underground work near mains",
}

data = json.dumps(payload).encode("utf-8")
req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
try:
    with urlopen(req, timeout=10) as resp:
        body = resp.read().decode()
        print("STATUS:", resp.status)
        print("BODY:", body)
except HTTPError as e:
    print("HTTPError", e.code, e.reason)
    try:
        print(e.read().decode())
    except Exception:
        pass
except URLError as e:
    print("URLError", e.reason)
