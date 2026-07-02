import sys
import os
import urllib.request
import json
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.db.session import SessionLocal
from app.features.indicators.models import Indicator

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

db = SessionLocal()
ind = db.query(Indicator).first()
if not ind:
    print("No indicators found in the database. Exiting.")
    sys.exit(0)
    
ind_id = ind.id
print(f"Testing /graph/indicator/{ind_id}?depth=2...")

graph_json = request_url(f"{BASE_URL}/graph/indicator/{ind_id}?depth=2")
if "nodes" not in graph_json or "edges" not in graph_json:
    print("Error: Missing nodes or edges in JSON")
    sys.exit(1)
    
print(f"Success! Graph depth 2 generated.")
print(f"Nodes: {len(graph_json['nodes'])}")
print(f"Edges: {len(graph_json['edges'])}")

print("All Graph endpoints tested successfully!")
