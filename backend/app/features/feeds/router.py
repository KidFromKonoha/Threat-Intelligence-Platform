from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Any

from app.db.session import get_db
from app.features.feeds.schemas import FeedCreate, FeedUpdate, FeedResponse, FeedRunResponse
from app.features.feeds.service import FeedService

router = APIRouter(prefix="/feeds", tags=["Feeds"])


@router.get("", response_model=list[FeedResponse])
def get_feeds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return FeedService.get_feeds(db, skip=skip, limit=limit)


@router.get("/status")
def get_feeds_status(db: Session = Depends(get_db)):
    """Lightweight endpoint for operational dashboards."""
    return FeedService.get_feeds_status(db)


@router.get("/{feed_id}", response_model=FeedResponse)
def get_feed(feed_id: str, db: Session = Depends(get_db)):
    return FeedService.get_feed(db, feed_id)


@router.post("", response_model=FeedResponse, status_code=status.HTTP_201_CREATED)
def create_feed(feed_in: FeedCreate, db: Session = Depends(get_db)):
    return FeedService.create_feed(db, feed_in)


@router.put("/{feed_id}", response_model=FeedResponse)
def update_feed(feed_id: str, feed_in: FeedUpdate, db: Session = Depends(get_db)):
    return FeedService.update_feed(db, feed_id, feed_in)


@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feed(feed_id: str, db: Session = Depends(get_db)):
    FeedService.delete_feed(db, feed_id)


@router.post("/{feed_id}/run", status_code=status.HTTP_202_ACCEPTED)
def run_feed_manual(feed_id: str, db: Session = Depends(get_db)):
    """Trigger a manual feed run asynchronously."""
    return FeedService.run_feed_manual(db, feed_id)


@router.get("/{feed_id}/runs", response_model=list[FeedRunResponse])
def get_feed_runs(
    feed_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return FeedService.get_feed_runs(db, feed_id, skip=skip, limit=limit)
