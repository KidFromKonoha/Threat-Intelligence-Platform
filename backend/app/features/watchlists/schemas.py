"""Schemas for Watchlists."""

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any


class WatchlistCreate(BaseModel):
    name: str
    description: str | None = None
    enabled: bool = True
    watchlist_type: str
    matching_rule: str = "exact"
    values: list[str]


class WatchlistUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
    watchlist_type: str | None = None
    matching_rule: str | None = None
    values: list[str] | None = None


class WatchlistResponse(WatchlistCreate):
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WatchlistMatchResponse(BaseModel):
    id: str
    watchlist_id: str
    entity_type: str
    entity_id: str
    match_reason: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
