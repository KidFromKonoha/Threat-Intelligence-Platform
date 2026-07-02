import sys
import json
import urllib.request
from app.db.session import SessionLocal
from app.features.indicators.models import Indicator
from app.features.threat_actors.models import ThreatActor
from app.features.malware.models import Malware
from app.features.campaigns.models import Campaign
from app.features.vulnerabilities.models import Vulnerability

BASE_URL = "http://localhost:8000/api/v1"

def request_json(url):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTPError {e.code}: {e.read().decode()}")
        sys.exit(1)

with SessionLocal() as db:
    ind = db.query(Indicator).first()
    ta = db.query(ThreatActor).first()
    mal = db.query(Malware).first()
    cam = db.query(Campaign).first()
    vul = db.query(Vulnerability).first()
    
    # create if missing
    if not ind:
        ind = Indicator(type="ipv4", value="9.9.9.9", confidence=50)
        db.add(ind)
    if not ta:
        ta = ThreatActor(name="Test TA", sophistication="unknown")
        db.add(ta)
    if not mal:
        mal = Malware(name="Test Malware")
        db.add(mal)
    if not cam:
        cam = Campaign(name="Test Campaign")
        db.add(cam)
    if not vul:
        vul = Vulnerability(cve="CVE-2024-0001", kev=False, exploited=False, patch_available=False)
        db.add(vul)
        
    db.commit()
    
    ind_id = ind.id
    ta_id = ta.id
    mal_id = mal.id
    cam_id = cam.id
    vul_id = vul.id

endpoints = {
    "indicators": f"/indicators/{ind_id}",
    "threat_actors": f"/threat-actors/{ta_id}",
    "malware": f"/malware/{mal_id}",
    "campaigns": f"/campaigns/{cam_id}",
    "vulnerabilities": f"/vulnerabilities/{vul_id}",
}

for name, path in endpoints.items():
    url = f"{BASE_URL}{path}"
    print(f"Testing {name} ({path})...")
    res = request_json(url)
    print(f"Success! {name} returned keys: {list(res.keys())}")

print("All Entity Details endpoints tested successfully!")
