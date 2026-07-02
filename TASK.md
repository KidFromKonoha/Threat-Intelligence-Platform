# Current Task

## Phase 13 – Graph API

### Objective

Implement a graph API that exposes intelligence relationships for frontend visualization.

The graph must be built entirely from the existing relational database and existing CorrelationService.

Do not introduce graph databases or duplicate relationship logic.

---

## Graph Model

Return a graph consisting of:

### Nodes

Each node must contain:

- id
- entity_type
- label
- metadata

Supported entity types:

- Indicator
- Malware
- ThreatActor
- Campaign
- MITRETechnique
- Vulnerability
- Report
- Asset

---

### Edges

Each edge must contain:

- source
- target
- relationship
- metadata

Relationship names should match existing relationship semantics wherever possible.

---

## Service Layer

Create GraphService.

Responsibilities:

- build graph
- transform existing relationships into graph nodes/edges
- deduplicate nodes
- deduplicate edges

Do not perform business logic already implemented elsewhere.

Reuse CorrelationService.

---

## Traversal

Support configurable traversal depth:

depth=1 (default)

depth=2

depth=3 (maximum)

Prevent infinite recursion.

Do not revisit previously explored entities.

---

## API

Implement:

GET /graph/indicator/{indicator_id}

GET /graph/threat-actor/{id}

GET /graph/malware/{id}

GET /graph/campaign/{id}

GET /graph/investigation/{id}

Query parameters:

depth=1..3

---

## Performance

Avoid recursive ORM loading.

Avoid N+1 queries.

Reuse existing relationship loading.

Deduplicate nodes and edges efficiently.

Graph generation should scale to large datasets.

---

## Error Handling

- 404 for missing entities.
- 422 for invalid depth.
- Empty graph rather than null.

---

## Logging

Log:

- root entity
- graph depth
- node count
- edge count
- generation duration

---

## Non Goals

Do not implement:

- Neo4j
- Cypher
- NetworkX
- GraphQL
- Graph analytics
- Frontend visualization
- Authentication

---

## Deliverables

- Graph schemas
- GraphService
- Router
- CorrelationService reuse
- IMPLEMENTATION_CONTEXT.md update