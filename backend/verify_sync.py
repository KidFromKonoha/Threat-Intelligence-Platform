import sys
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from app.db.session import SessionLocal
from app.features.feeds.models import Feed
from app.features.feeds.runner import FeedRunner
import json

# Setup basic logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")

db = SessionLocal()
feed = db.query(Feed).filter(Feed.name == 'misp').first()

def mock_urlopen(req, context=None):
    # Just return empty so it finishes fast
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": []}).encode('utf-8')
    mock_resp.__enter__.return_value = mock_resp
    return mock_resp

with patch('urllib.request.urlopen', side_effect=mock_urlopen) as mock_req:
    print('\n======================================================')
    print('SCENARIO 1: First run, no previous sync, auth.timestamp')
    print('======================================================')
    feed.last_success = None
    auth = feed.authentication.copy()
    auth['timestamp'] = '7d'
    feed.authentication = auth
    db.commit()
    FeedRunner('misp').run(full_sync=False)

    print('\n======================================================')
    print('SCENARIO 2: First run, no previous sync, no timestamp')
    print('======================================================')
    feed.last_success = None
    auth = feed.authentication.copy()
    if 'timestamp' in auth:
        del auth['timestamp']
    feed.authentication = auth
    db.commit()
    FeedRunner('misp').run(full_sync=False)

    print('\n======================================================')
    print('SCENARIO 3: Normal incremental sync using last_success')
    print('======================================================')
    feed.last_success = datetime.now(timezone.utc) - timedelta(hours=1)
    db.commit()
    FeedRunner('misp').run(full_sync=False)

    print('\n======================================================')
    print('SCENARIO 4: Failed sync does not advance last_success')
    print('======================================================')
    old_success = feed.last_success
    with patch('urllib.request.urlopen', side_effect=Exception("Simulated network failure")):
        FeedRunner('misp').run(full_sync=False)
    db.refresh(feed)
    print(f"last_success advanced? {old_success != feed.last_success}")

    print('\n======================================================')
    print('SCENARIO 5: Manual full_sync ignores all filters')
    print('======================================================')
    FeedRunner('misp').run(full_sync=True)
