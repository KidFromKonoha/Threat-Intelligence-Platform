import sys
import json
import urllib.request
import os

BASE_URL = "http://localhost:8000/api/v1"

def request_url(url, method="GET", parse_json=True):
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read()
            if parse_json:
                return json.loads(content.decode())
            return content
    except urllib.error.HTTPError as e:
        print(f"HTTPError {e.code}: {e.read().decode()}")
        sys.exit(1)

print("Testing /reports/daily...")
daily_json = request_url(f"{BASE_URL}/reports/daily")
if "platform_overview" not in daily_json:
    print("Error: Missing platform_overview in JSON")
    sys.exit(1)
print("Success! JSON payload has expected keys.")

print("Testing /reports/daily/export?format=csv...")
csv_content = request_url(f"{BASE_URL}/reports/daily/export?format=csv", parse_json=False).decode()
if "--- PLATFORM OVERVIEW ---" not in csv_content:
    print("Error: Invalid CSV format")
    sys.exit(1)
print("Success! CSV successfully generated.")

print("Testing /reports/daily/export?format=pdf...")
pdf_content = request_url(f"{BASE_URL}/reports/daily/export?format=pdf", parse_json=False)
if not pdf_content.startswith(b"%PDF-"):
    print("Error: Invalid PDF format")
    sys.exit(1)
print("Success! PDF successfully generated.")

print("All Reports endpoints tested successfully!")
