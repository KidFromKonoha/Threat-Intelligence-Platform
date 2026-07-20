import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text("UPDATE indicators SET risk_score = 95;"))
db.commit()
print("Updated risk scores to 95.")
