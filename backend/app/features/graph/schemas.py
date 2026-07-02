"""Schemas for Graph API."""

from pydantic import BaseModel, Field
from typing import Any


class GraphNode(BaseModel):
    id: str
    entity_type: str
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    root_id: str
    depth: int
