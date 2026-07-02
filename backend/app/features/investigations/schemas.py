"""Pydantic schemas for Investigations."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from app.db.enums import InvestigationPriority, InvestigationStatus
from app.features.search.schemas import EntitySummary, IndicatorSummary


class InvestigationBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: InvestigationStatus = InvestigationStatus.OPEN
    priority: InvestigationPriority = InvestigationPriority.MEDIUM


class InvestigationCreate(InvestigationBase):
    pass


class InvestigationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[InvestigationStatus] = None
    priority: Optional[InvestigationPriority] = None


class InvestigationResponse(InvestigationBase):
    id: str
    owner: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InvestigationSummaryResponse(BaseModel):
    investigation: InvestigationResponse
    indicators: list[IndicatorSummary] = []
    malware: list[EntitySummary] = []
    threat_actors: list[EntitySummary] = []
    campaigns: list[EntitySummary] = []
    reports: list[EntitySummary] = []
    mitre_techniques: list[EntitySummary] = []
    vulnerabilities: list[EntitySummary] = []


class InvestigationTimelineEvent(BaseModel):
    event_type: str
    timestamp: datetime
    description: str
    details: dict = Field(default_factory=dict)
