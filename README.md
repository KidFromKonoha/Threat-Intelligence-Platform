# Threat Intelligence Platform (TIP)

## Overview

Threat Intelligence Platform (TIP) is a modern, modular, and scalable platform designed to collect, normalize, correlate, enrich, search, and visualize cyber threat intelligence.

The first implementation targets an **Automotive OEM**, but the architecture must remain generic enough to support other industries in the future.

The platform is intended to assist:

* Security Operations Center (SOC)
* Threat Hunting
* Incident Response
* Cyber Threat Intelligence (CTI)
* Vulnerability Management
* Product Security
* Security Leadership

The objective is to help analysts answer one question quickly:

> **"Is this threat relevant to our organization, and what do we know about it?"**

---

# Project Goals

The platform must:

* Aggregate intelligence from multiple external sources.
* Normalize data into a common internal model.
* Remove duplicate intelligence.
* Correlate related indicators automatically.
* Enrich intelligence whenever possible.
* Provide fast global search.
* Present analyst-friendly visualizations.
* Support investigations.
* Scale to millions of indicators.
* Remain modular and easy to extend.

---

# Non-Goals

This project is **not** intended to become:

* SIEM
* SOAR
* EDR
* Case Management Platform
* Ticketing System
* Vulnerability Scanner
* Network Monitoring Platform
* Malware Sandbox
* Packet Capture Platform

Future integrations with these systems are allowed, but replacing them is outside the scope of this project.

---

# Architecture Philosophy

The project follows these principles:

* Documentation is the source of truth.
* Architecture comes before implementation.
* Prefer maintainability over clever code.
* Build incrementally.
* Keep modules independent.
* Avoid unnecessary abstractions.
* Design for future expansion.
* Never overengineer.

---

# Development Workflow

Every feature follows the same lifecycle:

1. Update documentation if requirements change.
2. Review the implementation task.
3. Implement one feature.
4. Verify functionality.
5. Keep the application runnable.
6. Commit the completed feature.

Implementation must follow documentation.

Documentation should never be silently ignored.

---

# Project Structure

```
backend/
frontend/
infrastructure/

README.md
SPEC.md
TASK.md
```

Additional folders may be introduced when necessary.

---

# Technology Stack

## Backend

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Redis
* Celery
* Pydantic

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* shadcn/ui
* TanStack Query
* React Router
* Recharts
* React Flow

---

# Coding Principles

* Write readable code.
* Use descriptive names.
* Prefer composition over inheritance.
* Avoid duplicated logic.
* Keep functions focused.
* Keep files reasonably small.
* Use strong typing whenever possible.
* Never hardcode secrets.
* Validate all external input.
* Log important events.
* Keep APIs consistent.

---

# AI Collaboration Rules

When implementing this project:

* Read this README before starting work.
* Treat `SPEC.md` as the canonical functional specification.
* Treat `TASK.md` as the current implementation objective.
* Do not invent new architecture unless explicitly requested.
* Do not contradict existing documentation.
* If documentation is unclear, ask for clarification instead of making assumptions.
* Reuse existing code whenever practical.
* Do not rewrite unrelated modules.
* Leave the project in a working state after every completed task.

---

# Success Criteria

The finished platform should:

* Collect threat intelligence from multiple feeds.
* Normalize and correlate intelligence automatically.
* Enable fast analyst investigations.
* Highlight threats relevant to organizational assets.
* Provide modern dashboards and visualizations.
* Be production-ready, maintainable, and easily extensible.

This repository represents a long-term engineering project. Every implementation decision should prioritize correctness, maintainability, scalability, and a high-quality analyst experience over short-term convenience.
