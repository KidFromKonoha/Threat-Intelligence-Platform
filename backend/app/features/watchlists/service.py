"""WatchlistService.

Handles CRUD for watchlists and matches entities against rules.
"""

from __future__ import annotations

from typing import Any
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.features.watchlists.models import Watchlist, WatchlistMatch
from app.features.watchlists.schemas import WatchlistCreate, WatchlistUpdate
from app.features.indicators.models import Indicator

def _coerce(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class WatchlistService:
    @staticmethod
    def get_all(db: Session) -> list[Watchlist]:
        return db.query(Watchlist).all()

    @staticmethod
    def get_by_id(db: Session, watchlist_id: str) -> Watchlist:
        w = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
        if not w:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        return w

    @staticmethod
    def create(db: Session, data: WatchlistCreate) -> Watchlist:
        w = Watchlist(**data.model_dump())
        db.add(w)
        db.commit()
        db.refresh(w)
        return w

    @staticmethod
    def update(db: Session, watchlist_id: str, data: WatchlistUpdate) -> Watchlist:
        w = WatchlistService.get_by_id(db, watchlist_id)
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(w, k, v)
        db.commit()
        db.refresh(w)
        return w

    @staticmethod
    def delete(db: Session, watchlist_id: str) -> None:
        w = WatchlistService.get_by_id(db, watchlist_id)
        db.delete(w)
        db.commit()

    @staticmethod
    def evaluate_indicator(db: Session, indicator_id: str) -> list[WatchlistMatch]:
        """Evaluates an indicator against all active watchlists."""
        indicator = (
            db.query(Indicator)
            .options(
                selectinload(Indicator.threat_actors),
                selectinload(Indicator.malware),
                selectinload(Indicator.campaigns),
            )
            .filter(Indicator.id == indicator_id)
            .first()
        )
        if not indicator:
            return []

        matches_to_create = []

        # 1. Match indicator value itself
        val_matches = db.query(Watchlist).filter(
            Watchlist.enabled == True,
            Watchlist.watchlist_type.in_([indicator.type, "indicator"]),
            Watchlist.values.any(indicator.value)
        ).all()
        for w in val_matches:
            matches_to_create.append((w.id, "indicator", indicator.id, f"Matched indicator value: {indicator.value}"))

        # 2. Match threat actors
        ta_names = [ta.name for ta in _coerce(indicator.threat_actors)]
        if ta_names:
            ta_matches = db.query(Watchlist).filter(
                Watchlist.enabled == True,
                Watchlist.watchlist_type == "threat_actor",
                or_(*[Watchlist.values.any(name) for name in ta_names])
            ).all()
            for w in ta_matches:
                matched = set(ta_names) & set(w.values)
                matches_to_create.append((w.id, "indicator", indicator.id, f"Matched threat actor: {', '.join(matched)}"))

        # 3. Match malware
        mal_names = [m.name for m in _coerce(indicator.malware)]
        if mal_names:
            m_matches = db.query(Watchlist).filter(
                Watchlist.enabled == True,
                Watchlist.watchlist_type == "malware",
                or_(*[Watchlist.values.any(name) for name in mal_names])
            ).all()
            for w in m_matches:
                matched = set(mal_names) & set(w.values)
                matches_to_create.append((w.id, "indicator", indicator.id, f"Matched malware: {', '.join(matched)}"))

        # 4. Match campaigns
        cam_names = [c.name for c in _coerce(indicator.campaigns)]
        if cam_names:
            c_matches = db.query(Watchlist).filter(
                Watchlist.enabled == True,
                Watchlist.watchlist_type == "campaign",
                or_(*[Watchlist.values.any(name) for name in cam_names])
            ).all()
            for w in c_matches:
                matched = set(cam_names) & set(w.values)
                matches_to_create.append((w.id, "indicator", indicator.id, f"Matched campaign: {', '.join(matched)}"))

        created_matches = WatchlistService.process_matches(db, matches_to_create)
        return created_matches

    @staticmethod
    def process_matches(db: Session, matches: list[tuple[str, str, str, str]]) -> list[WatchlistMatch]:
        """Creates match records, ignoring duplicates."""
        new_matches = []
        for wid, ent_type, ent_id, reason in matches:
            # Check if match already exists
            exists = db.query(WatchlistMatch).filter_by(
                watchlist_id=wid, entity_type=ent_type, entity_id=ent_id
            ).first()
            if not exists:
                wm = WatchlistMatch(
                    watchlist_id=wid,
                    entity_type=ent_type,
                    entity_id=ent_id,
                    match_reason=reason
                )
                db.add(wm)
                new_matches.append(wm)
        
        db.commit()
        for wm in new_matches:
            db.refresh(wm)
        return new_matches

    @staticmethod
    def get_matches(db: Session) -> list[WatchlistMatch]:
        return db.query(WatchlistMatch).all()

    @staticmethod
    def get_match_by_id(db: Session, match_id: str) -> WatchlistMatch:
        m = db.query(WatchlistMatch).filter(WatchlistMatch.id == match_id).first()
        if not m:
            raise HTTPException(status_code=404, detail="Watchlist match not found")
        return m
