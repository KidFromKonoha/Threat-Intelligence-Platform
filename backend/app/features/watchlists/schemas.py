"""Schemas for Watchlists."""

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any
from enum import Enum


class RuleOperator(str, Enum):
    EQ = "=="
    NE = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "in"
    CONTAINS = "contains"


class WatchlistRuleBase(BaseModel):
    rule_type: str
    operator: RuleOperator
    value: Any


class WatchlistRuleCreate(WatchlistRuleBase):
    pass


class WatchlistRuleResponse(WatchlistRuleBase):
    id: str
    watchlist_id: str

    model_config = ConfigDict(from_attributes=True)


class WatchlistBase(BaseModel):
    name: str
    description: str | None = None
    enabled: bool = True


class WatchlistCreate(WatchlistBase):
    rules: list[WatchlistRuleCreate]


class WatchlistUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
    rules: list[WatchlistRuleCreate] | None = None


class WatchlistResponse(WatchlistBase):
    id: str
    created_at: datetime
    rules: list[WatchlistRuleResponse] = []

    model_config = ConfigDict(from_attributes=True)


class WatchlistAlertResponse(BaseModel):
    id: str
    watchlist_id: str
    indicator_id: str
    severity: str
    status: str
    risk_score_snapshot: float | None = None
    matched_rule: str | None = None
    matched_value: str | None = None
    created_at: datetime
    updated_at: datetime
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None

    model_config = ConfigDict(from_attributes=True)


class WatchlistMetricsResponse(BaseModel):
    total_watchlists: int
    active_watchlists: int
    total_alerts: int
    new_alerts: int
    acknowledged_alerts: int
    closed_alerts: int
