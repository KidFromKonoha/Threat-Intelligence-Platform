"""WatchlistService.

Handles CRUD for watchlists, rules, and alerts.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime

from app.features.watchlists.models import Watchlist, WatchlistRule, WatchlistAlert
from app.features.watchlists.schemas import WatchlistCreate, WatchlistUpdate, WatchlistMetricsResponse


class WatchlistService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Watchlist]:
        return db.query(Watchlist).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, watchlist_id: str) -> Watchlist:
        w = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
        if not w:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        return w

    @staticmethod
    def create(db: Session, data: WatchlistCreate) -> Watchlist:
        w = Watchlist(name=data.name, description=data.description, enabled=data.enabled)
        for r_data in data.rules:
            rule = WatchlistRule(
                rule_type=r_data.rule_type,
                operator=r_data.operator.value,
                value=r_data.value
            )
            w.rules.append(rule)
        
        db.add(w)
        db.commit()
        db.refresh(w)
        return w

    @staticmethod
    def update(db: Session, watchlist_id: str, data: WatchlistUpdate) -> Watchlist:
        w = WatchlistService.get_by_id(db, watchlist_id)
        
        if data.name is not None:
            w.name = data.name
        if data.description is not None:
            w.description = data.description
        if data.enabled is not None:
            w.enabled = data.enabled
            
        if data.rules is not None:
            # Replace all rules
            db.query(WatchlistRule).filter(WatchlistRule.watchlist_id == watchlist_id).delete()
            for r_data in data.rules:
                rule = WatchlistRule(
                    rule_type=r_data.rule_type,
                    operator=r_data.operator.value,
                    value=r_data.value
                )
                w.rules.append(rule)
                
        db.commit()
        db.refresh(w)
        return w

    @staticmethod
    def delete(db: Session, watchlist_id: str) -> None:
        w = WatchlistService.get_by_id(db, watchlist_id)
        db.delete(w)
        db.commit()


class WatchlistAlertService:
    @staticmethod
    def get_all(db: Session, indicator_id: str | None = None, status: str | None = None, skip: int = 0, limit: int = 100) -> list[WatchlistAlert]:
        query = db.query(WatchlistAlert)
        if indicator_id:
            query = query.filter(WatchlistAlert.indicator_id == indicator_id)
        if status:
            query = query.filter(WatchlistAlert.status == status)
            
        return query.order_by(WatchlistAlert.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, alert_id: str) -> WatchlistAlert:
        a = db.query(WatchlistAlert).filter(WatchlistAlert.id == alert_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Alert not found")
        return a

    @staticmethod
    def acknowledge(db: Session, alert_id: str, user_id: str) -> WatchlistAlert:
        a = WatchlistAlertService.get_by_id(db, alert_id)
        if a.status != "NEW":
            raise HTTPException(status_code=400, detail="Alert is not in NEW status")
            
        a.status = "ACKNOWLEDGED"
        a.acknowledged_at = datetime.datetime.now(datetime.timezone.utc)
        a.acknowledged_by = user_id
        
        db.commit()
        db.refresh(a)
        return a

    @staticmethod
    def get_metrics(db: Session) -> WatchlistMetricsResponse:
        total_watchlists = db.query(func.count(Watchlist.id)).scalar() or 0
        active_watchlists = db.query(func.count(Watchlist.id)).filter(Watchlist.enabled == True).scalar() or 0
        
        total_alerts = db.query(func.count(WatchlistAlert.id)).scalar() or 0
        new_alerts = db.query(func.count(WatchlistAlert.id)).filter(WatchlistAlert.status == "NEW").scalar() or 0
        ack_alerts = db.query(func.count(WatchlistAlert.id)).filter(WatchlistAlert.status == "ACKNOWLEDGED").scalar() or 0
        closed_alerts = db.query(func.count(WatchlistAlert.id)).filter(WatchlistAlert.status == "CLOSED").scalar() or 0
        
        return WatchlistMetricsResponse(
            total_watchlists=total_watchlists,
            active_watchlists=active_watchlists,
            total_alerts=total_alerts,
            new_alerts=new_alerts,
            acknowledged_alerts=ack_alerts,
            closed_alerts=closed_alerts
        )
