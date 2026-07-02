"""Graph API router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.graph.schemas import GraphResponse
from app.features.graph.service import GraphService

router = APIRouter(prefix="/graph", tags=["Graph API"])


@router.get("/indicator/{indicator_id}", response_model=GraphResponse)
def get_indicator_graph(
    indicator_id: str,
    depth: int = Query(1, ge=1, le=3, description="Traversal depth (1-3)"),
    db: Session = Depends(get_db)
):
    """Retrieve relationship graph for an Indicator."""
    return GraphService.build_graph(db, "indicator", indicator_id, depth)


@router.get("/threat-actor/{id}", response_model=GraphResponse)
def get_threat_actor_graph(
    id: str,
    depth: int = Query(1, ge=1, le=3, description="Traversal depth (1-3)"),
    db: Session = Depends(get_db)
):
    """Retrieve relationship graph for a Threat Actor."""
    return GraphService.build_graph(db, "threat-actor", id, depth)


@router.get("/malware/{id}", response_model=GraphResponse)
def get_malware_graph(
    id: str,
    depth: int = Query(1, ge=1, le=3, description="Traversal depth (1-3)"),
    db: Session = Depends(get_db)
):
    """Retrieve relationship graph for a Malware family."""
    return GraphService.build_graph(db, "malware", id, depth)


@router.get("/campaign/{id}", response_model=GraphResponse)
def get_campaign_graph(
    id: str,
    depth: int = Query(1, ge=1, le=3, description="Traversal depth (1-3)"),
    db: Session = Depends(get_db)
):
    """Retrieve relationship graph for a Campaign."""
    return GraphService.build_graph(db, "campaign", id, depth)


@router.get("/investigation/{id}", response_model=GraphResponse)
def get_investigation_graph(
    id: str,
    depth: int = Query(1, ge=1, le=3, description="Traversal depth (1-3)"),
    db: Session = Depends(get_db)
):
    """Retrieve relationship graph for an Investigation."""
    return GraphService.build_graph(db, "investigation", id, depth)
