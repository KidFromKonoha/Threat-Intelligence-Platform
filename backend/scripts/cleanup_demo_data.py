#!/usr/bin/env python3
"""
cleanup_demo_data.py - Administrator maintenance script to remove development artifacts.

This script scans core domain entities for records created during development, testing,
or demos (e.g., names starting with "Test", "Demo", "Sample", "Dummy") and safely 
removes them.

It does NOT delete:
- Feed configurations
- Imported indicators (MISP, ThreatFox, etc.)
- Users, Roles, Organizations, or Settings

This script is idempotent and safe to run multiple times.
"""

import sys
import os

# Add the backend directory to sys.path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import or_
from app.db.session import SessionLocal

# Import models
from app.features.watchlists.models import Watchlist
from app.features.vulnerabilities.models import Vulnerability
from app.features.threat_actors.models import ThreatActor
from app.features.reports.models import Report
from app.features.malware.models import Malware
from app.features.investigations.models import Investigation
from app.features.campaigns.models import Campaign
from app.features.assets.models import Asset

# Configure target models and their corresponding string fields used for matching
MODELS_TO_CLEAN = [
    (Investigation, "title"),
    (ThreatActor, "name"),
    (Malware, "name"),
    (Campaign, "name"),
    (Report, "title"),
    (Watchlist, "name"),
    (Vulnerability, "cve"),
    (Asset, "name"),
]

# Case-insensitive prefixes that identify dev/test data
PREFIXES = ["Test", "Demo", "Sample", "Dummy"]


def main() -> None:
    print("Starting development data cleanup...")
    print(f"Matching prefixes: {', '.join(PREFIXES)}\n")

    db = SessionLocal()
    deleted_counts = {model.__name__: 0 for model, _ in MODELS_TO_CLEAN}
    
    try:
        for model, field_name in MODELS_TO_CLEAN:
            field = getattr(model, field_name)
            
            # Build an OR condition: field.ilike("Test%"), field.ilike("Demo%"), etc.
            conditions = [field.ilike(f"{prefix}%") for prefix in PREFIXES]
            query = db.query(model).filter(or_(*conditions))
            
            # Fetch all matching records
            records = query.all()
            
            if records:
                # Use ORM delete() on each instance to ensure cascade logic fires correctly
                for record in records:
                    db.delete(record)
                deleted_counts[model.__name__] = len(records)
                
        db.commit()

        # Print summary
        print("Deleted:")
        any_deleted = False
        for model_name, count in deleted_counts.items():
            if count > 0:
                print(f"- {count} {model_name}(s)")
                any_deleted = True
        if not any_deleted:
            print("- (None)")

        print("\nSkipped (0 items found):")
        any_skipped = False
        for model_name, count in deleted_counts.items():
            if count == 0:
                print(f"- {model_name}(s)")
                any_skipped = True
        if not any_skipped:
            print("- (None)")
            
        print("\nCleanup completed successfully.")

    except Exception as exc:
        db.rollback()
        print(f"\n[ERROR] Cleanup failed: {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
