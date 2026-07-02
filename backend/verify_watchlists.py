import sys
import json
import urllib.request
from app.db.session import SessionLocal
from app.features.indicators.models import Indicator
from app.features.threat_actors.models import ThreatActor
from app.features.watchlists.models import Watchlist, WatchlistMatch

BASE_URL = "http://localhost:8000/api/v1"

def request_json(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(data).encode('utf-8')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTPError {e.code}: {e.read().decode()}")
        sys.exit(1)

# Cleanup existing
with SessionLocal() as db:
    db.query(WatchlistMatch).delete()
    db.query(Watchlist).delete()
    db.commit()

# Create watchlist via API
print("Creating Watchlist...")
w_data = {
    "name": "Test Indicator Watchlist",
    "description": "Watch for specific IP",
    "watchlist_type": "indicator",
    "values": ["1.2.3.4"]
}
w_res = request_json(f"{BASE_URL}/watchlists", method="POST", data=w_data)
print(f"Created: {w_res['id']}")

# Create indicator
with SessionLocal() as db:
    ind = db.query(Indicator).filter_by(value="1.2.3.4").first()
    if not ind:
        ind = Indicator(type="ipv4", value="1.2.3.4", normalized_value="1.2.3.4", confidence=50)
        db.add(ind)
        db.commit()
    ind_id = ind.id
    
print(f"Indicator ID: {ind_id}")

# Evaluate
print("Evaluating Watchlist...")
eval_res = request_json(f"{BASE_URL}/watchlists/{w_res['id']}/evaluate?indicator_id={ind_id}", method="POST")
print(f"Matches created: {len(eval_res)}")
for m in eval_res:
    print(f"  - Match: {m['match_reason']}")

# Get matches
print("Listing Matches...")
matches = request_json(f"{BASE_URL}/watchlists/matches")
print(f"Total Matches: {len(matches)}")
if len(matches) != 1:
    print("Error: Expected exactly 1 match")
    sys.exit(1)
    
print("All Watchlist tests passed!")
