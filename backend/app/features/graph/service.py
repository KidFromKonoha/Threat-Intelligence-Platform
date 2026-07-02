"""GraphService.

Builds relationship graphs from existing SQL database relationships.
Uses selectinload('*') for dynamic BFS traversal to prevent N+1 queries.
Reuses CorrelationService for Indicator anchors to retrieve specialized virtual relationships.
"""

from __future__ import annotations
import time
import logging
from typing import Any
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.inspection import inspect

from app.features.graph.schemas import GraphResponse, GraphNode, GraphEdge
from app.features.indicators.models import Indicator
from app.features.threat_actors.models import ThreatActor
from app.features.malware.models import Malware
from app.features.campaigns.models import Campaign
from app.features.investigations.models import Investigation
from app.features.mitre.models import MITRETechnique
from app.features.vulnerabilities.models import Vulnerability
from app.features.reports.models import Report
from app.features.feeds.models import Feed
from app.features.assets.models import Asset
from app.features.correlation.service import CorrelationService

logger = logging.getLogger(__name__)

ENTITY_MAP = {
    "indicator": Indicator,
    "threat-actor": ThreatActor,
    "malware": Malware,
    "campaign": Campaign,
    "investigation": Investigation,
    "mitre-technique": MITRETechnique,
    "vulnerability": Vulnerability,
    "report": Report,
    "feed": Feed,
    "asset": Asset,
}

MODEL_TO_TYPE = {v: k for k, v in ENTITY_MAP.items()}


def _get_entity_label(instance: Any) -> str:
    if isinstance(instance, Indicator):
        return instance.value
    if isinstance(instance, Vulnerability):
        return instance.cve
    if isinstance(instance, (Investigation, Report)):
        return instance.title
    if hasattr(instance, "name"):
        return instance.name
    return str(instance.id)


class GraphService:
    @staticmethod
    def build_graph(db: Session, root_type: str, root_id: str, max_depth: int) -> GraphResponse:
        t0 = time.monotonic()
        nodes: dict[str, GraphNode] = {}
        edges: dict[tuple[str, str, str], GraphEdge] = {}
        
        visited_nodes = set()
        
        def add_node(e_type: str, e_id: str, label: str):
            if e_id not in nodes:
                nodes[e_id] = GraphNode(id=e_id, entity_type=e_type, label=label)
                
        def add_edge(src_id: str, tgt_id: str, rel: str):
            # deduplicate bidirectional edges
            canon = tuple(sorted([src_id, tgt_id])) + (rel,)
            if canon not in edges:
                edges[canon] = GraphEdge(source=src_id, target=tgt_id, relationship=rel)

        current_level = {(root_type, root_id)}
        
        for current_depth in range(max_depth + 1):
            if not current_level:
                break
                
            next_level = set()
            by_type: dict[str, set[str]] = {}
            for t, i in current_level:
                by_type.setdefault(t, set()).add(i)
                
            for e_type, e_ids in by_type.items():
                if not e_ids:
                    continue
                    
                # Reuse CorrelationService specifically for Indicator anchors at root depth
                if e_type == "indicator" and current_depth == 0 and len(e_ids) == 1:
                    ind_id = list(e_ids)[0]
                    try:
                        rels = CorrelationService.get_relationships(db, ind_id)
                        add_node("indicator", ind_id, rels.indicator.value)
                        visited_nodes.add(("indicator", ind_id))
                        
                        if current_depth < max_depth:
                            def _proc(refs, ref_type, rel_name):
                                for r in refs:
                                    lbl = getattr(r, "value", getattr(r, "name", getattr(r, "title", getattr(r, "cve", r.id))))
                                    add_node(ref_type, r.id, lbl)
                                    add_edge(ind_id, r.id, rel_name)
                                    if (ref_type, r.id) not in visited_nodes:
                                        next_level.add((ref_type, r.id))
                                        
                            _proc(rels.feeds, "feed", "feeds")
                            _proc(rels.malware, "malware", "malware")
                            _proc(rels.campaigns, "campaign", "campaigns")
                            _proc(rels.threat_actors, "threat-actor", "threat_actors")
                            _proc(rels.mitre_techniques, "mitre-technique", "techniques")
                            _proc(rels.reports, "report", "reports")
                            _proc(rels.vulnerabilities, "vulnerability", "vulnerabilities")
                        continue
                    except HTTPException:
                        if current_depth == 0:
                            raise
                
                model = ENTITY_MAP.get(e_type)
                if not model:
                    continue
                
                # Batch load all entities of this type to avoid N+1 queries
                instances = db.query(model).options(selectinload('*')).filter(model.id.in_(e_ids)).all()
                if current_depth == 0 and not instances:
                    raise HTTPException(status_code=404, detail=f"Root {e_type} not found")
                    
                for instance in instances:
                    inst_id = str(instance.id)
                    add_node(e_type, inst_id, _get_entity_label(instance))
                    visited_nodes.add((e_type, inst_id))
                    
                    if current_depth < max_depth:
                        mapper = inspect(type(instance))
                        for rel in mapper.relationships:
                            related_items = getattr(instance, rel.key)
                            if related_items is None:
                                continue
                            if not isinstance(related_items, list):
                                related_items = [related_items]
                                
                            for rel_item in related_items:
                                rel_type = MODEL_TO_TYPE.get(type(rel_item))
                                if not rel_type:
                                    continue
                                    
                                rel_id = str(rel_item.id)
                                add_node(rel_type, rel_id, _get_entity_label(rel_item))
                                add_edge(inst_id, rel_id, rel.key)
                                
                                if (rel_type, rel_id) not in visited_nodes:
                                    next_level.add((rel_type, rel_id))
                                    
            current_level = next_level
            
        duration = time.monotonic() - t0
        logger.info(
            "[graph] generated: root=%s/%s depth=%d nodes=%d edges=%d duration=%.3fs",
            root_type, root_id, max_depth, len(nodes), len(edges), duration
        )

        return GraphResponse(
            nodes=list(nodes.values()),
            edges=list(edges.values()),
            root_id=root_id,
            depth=max_depth
        )
