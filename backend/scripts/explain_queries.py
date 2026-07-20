import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
queries = [
    "EXPLAIN ANALYZE SELECT * FROM indicators WHERE type = 'ipv4' AND normalized_value = '100.1.0.0';",
    "EXPLAIN ANALYZE SELECT * FROM indicators WHERE risk_score > 80;",
    "EXPLAIN ANALYZE SELECT * FROM watchlists JOIN watchlist_rules ON watchlists.id = watchlist_rules.watchlist_id WHERE watchlists.enabled = true;"
]

for q in queries:
    print(f"Query: {q}")
    results = db.execute(text(q)).fetchall()
    for row in results:
        print(row[0])
    print("-" * 40)
