from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.features.feeds.models import Feed, FeedRun
from app.features.feeds.schemas import FeedCreate, FeedUpdate
from app.features.feeds.tasks import run_collector
from fastapi import HTTPException, status
from app.core.logging import get_logger

logger = get_logger(__name__)

class FeedService:
    @staticmethod
    def get_feeds(db: Session, skip: int = 0, limit: int = 100) -> list[Feed]:
        return db.query(Feed).offset(skip).limit(limit).all()

    @staticmethod
    def get_feed(db: Session, feed_id: str) -> Feed:
        feed = db.query(Feed).filter(Feed.id == feed_id).first()
        if not feed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feed not found")
        return feed

    @staticmethod
    def create_feed(db: Session, feed_in: FeedCreate) -> Feed:
        # Check duplicate name
        existing = db.query(Feed).filter(Feed.name == feed_in.name).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feed name already exists")
        
        feed = Feed(**feed_in.model_dump(exclude_unset=True))
        db.add(feed)
        db.commit()
        db.refresh(feed)
        logger.info("Feed created: %s", feed.name)
        return feed

    @staticmethod
    def update_feed(db: Session, feed_id: str, feed_in: FeedUpdate) -> Feed:
        feed = FeedService.get_feed(db, feed_id)
        
        if feed_in.name and feed_in.name != feed.name:
            existing = db.query(Feed).filter(Feed.name == feed_in.name).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feed name already exists")

        update_data = feed_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(feed, key, value)
            
        db.commit()
        db.refresh(feed)
        logger.info("Feed updated: %s", feed.name)
        return feed

    @staticmethod
    def delete_feed(db: Session, feed_id: str) -> None:
        feed = FeedService.get_feed(db, feed_id)
        db.delete(feed)
        db.commit()
        logger.info("Feed deleted: %s", feed.name)

    @staticmethod
    def run_feed_manual(db: Session, feed_id: str) -> dict[str, str]:
        feed = FeedService.get_feed(db, feed_id)
        if not feed.enabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot run a disabled feed")
        
        # Dispatch celery task
        run_collector.delay(feed.name)
        logger.info("Manual execution triggered for feed: %s", feed.name)
        return {"message": "Feed execution started"}

    @staticmethod
    def get_feed_runs(db: Session, feed_id: str, skip: int = 0, limit: int = 100) -> list[FeedRun]:
        # Validate feed exists
        FeedService.get_feed(db, feed_id)
        
        runs = db.query(FeedRun).filter(FeedRun.feed_id == feed_id)\
                 .order_by(FeedRun.start_time.desc())\
                 .offset(skip).limit(limit).all()
        return runs

    @staticmethod
    def get_feeds_status(db: Session) -> list[dict[str, Any]]:
        # Compute feed statistics from FeedRun rather than duplicating them in Feed model
        # For lightweight dashboard
        status_list = []
        feeds = db.query(Feed).all()
        for feed in feeds:
            # Aggregate stats from feed_runs
            stats = db.query(
                func.sum(FeedRun.records_added).label("total_added"),
                func.sum(FeedRun.records_updated).label("total_updated"),
                func.count(FeedRun.id).label("total_runs")
            ).filter(FeedRun.feed_id == feed.id).first()
            
            latest_run = db.query(FeedRun).filter(FeedRun.feed_id == feed.id)\
                           .order_by(FeedRun.start_time.desc()).first()
                           
            status_list.append({
                "feed_id": feed.id,
                "feed_name": feed.name,
                "status": feed.status,
                "enabled": feed.enabled,
                "records_added": stats.total_added or 0,
                "records_updated": stats.total_updated or 0,
                "total_runs": stats.total_runs or 0,
                "last_run_status": latest_run.status if latest_run else None,
                "last_run_time": latest_run.start_time if latest_run else None,
            })
            
        return status_list
