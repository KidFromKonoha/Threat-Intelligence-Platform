import sys
import json
import urllib.request
from urllib.error import HTTPError

BASE_URL = "http://localhost:8000/api/v1"

def request_url(url, method="GET", data=None, headers=None, parse_json=True):
    if headers is None:
        headers = {}
    if data and not isinstance(data, bytes):
        data = data.encode()
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read()
            if parse_json:
                return json.loads(content.decode())
            return content
    except HTTPError as e:
        return {"error": True, "status": e.code, "body": e.read().decode()}

print("Testing unauthenticated access to /users (should fail 401)")
res = request_url(f"{BASE_URL}/users")
assert res.get("error") and res.get("status") == 401, f"Expected 401, got {res}"
print("Pass: 401 Unauthorized")

print("Testing unauthenticated access to /indicators (should fail 401)")
res = request_url(f"{BASE_URL}/indicators")
assert res.get("error") and res.get("status") == 401, f"Expected 401, got {res}"
print("Pass: 401 Unauthorized")

print("Testing login")
login_data = "username=admin&password=password123"
login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
res = request_url(f"{BASE_URL}/auth/login", method="POST", data=login_data, headers=login_headers)
assert "access_token" in res, f"Expected access_token, got {res}"
token = res["access_token"]
print("Pass: Login successful")

print("Testing authenticated access to /users (requires admin)")
headers = {"Authorization": f"Bearer {token}"}
res = request_url(f"{BASE_URL}/users", headers=headers)
assert isinstance(res, list), f"Expected list of users, got {res}"
assert res[0]["username"] == "admin"
print("Pass: /users returned successfully")

print("Testing authenticated access to /indicators (requires viewer)")
res = request_url(f"{BASE_URL}/indicators", headers=headers)
assert "items" in res, f"Expected items in paginated response, got {res}"
print("Pass: /indicators returned successfully")

print("All tests passed!")
