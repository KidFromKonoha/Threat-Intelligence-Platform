from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.investigation.schemas import (
    InvestigationIndicatorBundle,
    InvestigationThreatActorBundle,
    InvestigationCampaignBundle,
    UnifiedSearchResponse,
    EntityEventSchema
)
from app.features.investigation.service import (
    IndicatorBundleBuilder,
    ThreatActorBundleBuilder,
    CampaignBundleBuilder,
    TimelineService,
    SearchService
)

router = APIRouter(prefix="/investigation", tags=["Investigation"])

@router.get("/indicator/{id}", response_model=InvestigationIndicatorBundle)
def get_indicator_bundle(id: str, db: Session = Depends(get_db)):
    bundle = IndicatorBundleBuilder.build(db, id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return bundle

@router.get("/threat-actor/{id}", response_model=InvestigationThreatActorBundle)
def get_threat_actor_bundle(id: str, db: Session = Depends(get_db)):
    bundle = ThreatActorBundleBuilder.build(db, id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Threat Actor not found")
    return bundle

@router.get("/campaign/{id}", response_model=InvestigationCampaignBundle)
def get_campaign_bundle(id: str, db: Session = Depends(get_db)):
    bundle = CampaignBundleBuilder.build(db, id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return bundle

@router.get("/search", response_model=UnifiedSearchResponse)
def search_investigation(q: str, db: Session = Depends(get_db)):
    if not q or len(q) < 2:
        return UnifiedSearchResponse()
    return SearchService.search(db, q)

@router.get("/timeline/{entity_id}", response_model=list[EntityEventSchema])
def get_timeline(entity_id: str, entity_type: str = "indicator", db: Session = Depends(get_db)):
    return TimelineService.get_timeline(db, entity_type, entity_id)
