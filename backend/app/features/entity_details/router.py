"""Entity Detail APIs Router.

Provides rich detail endpoints for indicators, threat actors, malware,
campaigns, and vulnerabilities.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.entity_details.service import EntityDetailService
from app.features.entity_details.schemas import (
    IndicatorFullDetailResponse,
    ThreatActorDetailResponse,
    MalwareDetailResponse,
    CampaignDetailResponse,
    VulnerabilityDetailResponse,
)

router = APIRouter(tags=["Entity Details"])

@router.get("/indicators/{id}", response_model=IndicatorFullDetailResponse)
def get_indicator_detail(id: str, db: Session = Depends(get_db)):
    return EntityDetailService.get_indicator(db, id)

@router.get("/threat-actors/{id}", response_model=ThreatActorDetailResponse)
def get_threat_actor_detail(id: str, db: Session = Depends(get_db)):
    return EntityDetailService.get_threat_actor(db, id)

@router.get("/malware/{id}", response_model=MalwareDetailResponse)
def get_malware_detail(id: str, db: Session = Depends(get_db)):
    return EntityDetailService.get_malware(db, id)

@router.get("/campaigns/{id}", response_model=CampaignDetailResponse)
def get_campaign_detail(id: str, db: Session = Depends(get_db)):
    return EntityDetailService.get_campaign(db, id)

@router.get("/vulnerabilities/{id}", response_model=VulnerabilityDetailResponse)
def get_vulnerability_detail(id: str, db: Session = Depends(get_db)):
    return EntityDetailService.get_vulnerability(db, id)
