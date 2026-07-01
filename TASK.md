# Current Task

## Phase 3A – Feed Collection Framework

Objective

Build the feed ingestion framework.

Do not implement real threat feeds yet.

Requirements

- Feed Manager
- Base Collector class
- Collector Registry
- Scheduler abstraction
- Validation pipeline
- Normalization pipeline
- Storage pipeline
- Retry support
- Timeout support
- Logging
- Metrics
- Feed configuration

Architecture

Every collector must implement:

- fetch()
- validate()
- normalize()
- store()

Collectors must be automatically discoverable.

The framework must allow adding a new feed by creating a single new collector class.

Do not implement APIs.

Do not implement UI.

Do not implement enrichment.

Do not implement correlation.

Deliverables

- Working feed framework
- Example dummy collector
- Updated IMPLEMENTATION_CONTEXT.md