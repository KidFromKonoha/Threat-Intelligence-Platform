import sys
import json
import urllib.request

BASE_URL = "http://localhost:8000/api/v1/dashboard"

def request_json(url):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTPError {e.code}: {e.read().decode()}")
        sys.exit(1)

endpoints = [
    "/overview",
    "/threat-activity",
    "/organization",
    "/feed-status",
    "/recent-intelligence"
]

for ep in endpoints:
    url = f"{BASE_URL}{ep}"
    print(f"Testing {ep}...")
    res = request_json(url)
    print(f"Success! Keys returned: {list(res.keys()) if isinstance(res, dict) else len(res)}")

print("All Dashboard endpoints tested successfully!")
