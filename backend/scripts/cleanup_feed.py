#!/usr/bin/env python3
import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from app.db.session import SessionLocal
from app.features.feeds.models import Feed, FeedRun
from app.features.indicators.models import Indicator
from app.db.associations import indicator_feed

def cleanup_feed(feed_identifier: str):
    db: Session = SessionLocal()
    try:
        # Find the feed by ID or name
        feed = db.query(Feed).filter(
            or_(Feed.id == feed_identifier, Feed.name.ilike(feed_identifier))
        ).first()

        if not feed:
            print(f"Feed '{feed_identifier}' not found.")
            return

        print(f"Found feed: {feed.name} (ID: {feed.id})")

        # 1. Delete all FeedRuns for this feed
        deleted_runs = db.query(FeedRun).filter(FeedRun.feed_id == feed.id).delete()
        print(f"Deleted {deleted_runs} feed runs.")

        # 2. Find and handle indicators
        # We need to find all indicators linked to this feed.
        # If they are ONLY linked to this feed, delete them.
        # If they are linked to other feeds too, just remove the association.
        
        # Get indicator IDs linked to this feed
        linked_indicators = db.execute(
            text("SELECT indicator_id FROM indicator_feed WHERE feed_id = :feed_id"),
            {"feed_id": feed.id}
        ).fetchall()
        
        indicator_ids = [row[0] for row in linked_indicators]
        
        if indicator_ids:
            # Delete from the association table for this feed
            db.execute(
                text("DELETE FROM indicator_feed WHERE feed_id = :feed_id"),
                {"feed_id": feed.id}
            )
            
            # Find which indicators no longer have ANY feed associations
            # Actually, to be safe and clean, we can just check if they exist in indicator_feed
            # after deleting the feed's links.
            remaining_links = db.execute(
                text("SELECT DISTINCT indicator_id FROM indicator_feed WHERE indicator_id IN :inds"),
                {"inds": tuple(indicator_ids)}
            ).fetchall()
            
            remaining_indicator_ids = {row[0] for row in remaining_links}
            orphaned_indicator_ids = set(indicator_ids) - remaining_indicator_ids
            
            if orphaned_indicator_ids:
                deleted_indicators = db.query(Indicator).filter(
                    Indicator.id.in_(orphaned_indicator_ids)
                ).delete(synchronize_session=False)
                print(f"Deleted {deleted_indicators} orphaned indicators.")
            else:
                print("No orphaned indicators to delete.")
            
            print(f"Removed association for {len(indicator_ids)} indicators.")
        else:
            print("No indicators associated with this feed.")

        # 3. Reset feed stats
        feed.records_imported = 0
        feed.last_success = None
        feed.last_failure = None
        feed.status = "active"
        
        db.commit()
        print(f"Cleanup for feed '{feed.name}' completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up a feed's history and indicators")
    parser.add_argument("--feed", required=True, help="Feed Name or ID to clean up")
    args = parser.parse_args()

    cleanup_feed(args.feed)
