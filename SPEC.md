# Threat Intelligence Platform (TIP) Specification

Version: 1.0

Status: Draft

---

# 1. Purpose

This document is the canonical functional specification for the Threat Intelligence Platform (TIP).

It defines what the platform must do, how information is organized, and the expected behavior of every major module.

Implementation must follow this specification.

If implementation and specification conflict, the specification takes precedence until intentionally updated.

---

# 2. Vision

The Threat Intelligence Platform is a centralized intelligence portal designed to aggregate, normalize, correlate, enrich, search, and visualize cyber threat intelligence from multiple sources.

The first deployment targets an Automotive OEM, helping security teams understand threats relevant to the organization's infrastructure, suppliers, products, and manufacturing ecosystem.

The platform should reduce investigation time by presenting all relevant intelligence in a single location instead of requiring analysts to search multiple external services.

---

# 3. Objectives

The platform shall:

* Collect intelligence from multiple external feeds.
* Normalize data into a unified internal format.
* Deduplicate repeated intelligence.
* Correlate related entities automatically.
* Enrich intelligence where possible.
* Provide fast global search.
* Visualize relationships between entities.
* Support analyst investigations.
* Prioritize threats relevant to organizational assets.
* Scale efficiently to millions of records.

---

# 4. Target Users

## Security Operations Center (SOC)

Validate suspicious indicators.

Investigate alerts.

Review intelligence.

---

## Threat Hunters

Discover emerging threats.

Identify infrastructure reuse.

Analyze attacker behavior.

---

## Incident Responders

Understand incidents quickly.

Collect related intelligence.

Identify attacker infrastructure.

---

## Cyber Threat Intelligence Team

Track campaigns.

Track malware.

Track threat actors.

Publish intelligence.

---

## Vulnerability Management

Monitor exploited CVEs.

Track KEV entries.

Identify affected assets.

---

## Product Security

Track threats affecting:

* Connected Vehicles
* ECUs
* OTA Infrastructure
* CAN Networks
* Manufacturing Systems

---

## Security Leadership

View dashboards.

Review trends.

Measure threat activity.

---

# 5. Platform Scope

The platform is responsible for:

* Threat Intelligence Collection
* Threat Intelligence Storage
* Threat Intelligence Correlation
* Threat Intelligence Enrichment
* Search
* Dashboards
* Investigations
* Reporting
* Visualizations

---

# 6. Out of Scope

The platform is not intended to function as:

* SIEM
* SOAR
* EDR
* Antivirus
* Ticketing System
* Vulnerability Scanner
* Packet Capture Platform
* Malware Sandbox
* Endpoint Management Platform

Integration with these systems may be added in the future.

---

# 7. Core Domain Model

The platform consists of four primary domains.

## Threat Intelligence

Contains intelligence about attackers and malicious activity.

Includes:

* Indicators
* Threat Actors
* Malware
* Campaigns
* MITRE ATT&CK Techniques
* Reports

---

## Threat Collection

Responsible for gathering intelligence.

Includes:

* Threat Feeds
* Feed Collectors
* Feed Runs
* Feed Health
* Enrichment Services

---

## Organization Context

Represents the organization being protected.

Includes:

* Assets
* Asset Groups
* Suppliers
* Products
* Vehicle Platforms
* Domains
* Public IPs
* Watchlists

---

## Security Operations

Supports analysts.

Includes:

* Investigations
* Saved Searches
* Dashboards
* Comments
* Reports
* Users

---

# 8. Core Entity Principles

Every major entity shall:

* Have a globally unique identifier.
* Track creation and update timestamps.
* Support relationships with other entities.
* Store references to original intelligence sources.
* Maintain historical information whenever practical.
* Support future schema expansion without redesign.

---

# 9. Canonical Entities

The following entities form the core of the platform.

## Indicator

Represents an observable used during investigations.

Supported indicator types include:

* IPv4
* IPv6
* Domain
* URL
* File Hash
* Email Address
* ASN
* Process Name
* File Name
* Registry Key
* Mutex
* Certificate
* User Agent

Indicators are the primary searchable objects within the platform.

---

## Threat Actor

Represents an adversary or adversary group.

Examples:

* Nation-state groups
* Ransomware groups
* Criminal organizations
* Unknown clusters

Threat Actors may own campaigns, malware, infrastructure, and indicators.

---

## Malware

Represents malicious software.

Malware may be linked to:

* Threat Actors
* Campaigns
* Hashes
* Infrastructure
* MITRE Techniques

---

## Campaign

Represents a coordinated malicious operation.

Campaigns connect:

* Threat Actors
* Malware
* Indicators
* Victims
* Infrastructure

---

## Vulnerability

Represents publicly disclosed vulnerabilities.

Typically identified using CVE identifiers.

May include:

* CVSS
* EPSS
* KEV status
* Exploitation information

---

## MITRE Technique

Represents attacker behavior using the MITRE ATT&CK framework.

Multiple entities may reference one or more techniques.

---

## Threat Feed

Represents an external intelligence provider.

Examples include:

* ThreatFox
* MalwareBazaar
* AbuseIPDB
* URLHaus
* AlienVault OTX
* OpenPhish
* PhishTank
* CISA KEV

Each feed is independent.

---

## Asset

Represents an organizational asset.

Examples:

* Domain
* Public IP
* Cloud Account
* Supplier
* Product
* Manufacturing Plant
* VPN Gateway

Assets enable relevance scoring.

---

## Investigation

Represents an analyst investigation.

May contain:

* Indicators
* Threat Actors
* Malware
* Campaigns
* Notes
* Timeline
* Graphs

Investigations should be persistent and shareable.

---

## Watchlist

Represents user-defined monitoring criteria.

Examples:

* Threat Actor
* Domain
* CVE
* Country
* Malware
* Tag

Matching intelligence should automatically generate notifications.

---

# 10. Fundamental Design Principles

The platform should always:

* Prefer correlation over isolated data.
* Preserve source attribution.
* Avoid duplicate intelligence.
* Remain modular.
* Support future integrations.
* Minimize analyst effort.
* Prioritize organizational relevance over intelligence volume.

# 11. Entity Specifications

---

## 11.1 Indicator

### Description

Represents an observable that may indicate malicious activity.

### Supported Types

* IPv4
* IPv6
* Domain
* URL
* Email
* MD5
* SHA1
* SHA256
* ASN
* File Name
* Process Name
* Registry Key
* Mutex
* Certificate
* User Agent

### Fields

| Field            | Type            | Required |
| ---------------- | --------------- | -------- |
| id               | UUID            | Yes      |
| type             | Enum            | Yes      |
| value            | String          | Yes      |
| normalized_value | String          | Yes      |
| confidence       | Integer (0-100) | Yes      |
| severity         | Enum            | Yes      |
| risk_score       | Integer (0-100) | Yes      |
| status           | Enum            | Yes      |
| first_seen       | Timestamp       | Yes      |
| last_seen        | Timestamp       | Yes      |
| country          | String          | No       |
| asn              | String          | No       |
| whois            | JSON            | No       |
| passive_dns      | JSON            | No       |
| reputation       | JSON            | No       |
| tags             | Array           | No       |
| source_count     | Integer         | Yes      |
| created_at       | Timestamp       | Yes      |
| updated_at       | Timestamp       | Yes      |

### Relationships

Indicator ↔ Threat Actor

Indicator ↔ Malware

Indicator ↔ Campaign

Indicator ↔ Feed

Indicator ↔ Investigation

Indicator ↔ Asset

Indicator ↔ MITRE Technique

Indicator ↔ Report

Indicator ↔ Indicator

### Pages

Search

Details

Timeline

Graph

History

---

## 11.2 Threat Actor

### Fields

* id
* name
* aliases
* description
* country
* motivation
* sophistication
* first_seen
* last_seen
* active
* references
* created_at
* updated_at

### Relationships

Threat Actor

↓

Campaigns

↓

Malware

↓

Indicators

↓

Reports

↓

MITRE Techniques

---

## 11.3 Malware

### Fields

* id
* name
* aliases
* family
* category
* description
* capabilities
* persistence
* communication
* references
* created_at
* updated_at

### Relationships

Malware

↓

Hashes

↓

Campaigns

↓

Threat Actors

↓

Indicators

↓

MITRE Techniques

---

## 11.4 Campaign

### Fields

* id
* name
* description
* first_seen
* last_seen
* target_sector
* target_country
* references
* created_at
* updated_at

### Relationships

Campaign

↓

Threat Actor

↓

Malware

↓

Indicators

↓

Reports

↓

Victims

---

## 11.5 Vulnerability

### Fields

* id
* cve
* description
* cvss
* epss
* kev
* exploited
* patch_available
* references
* created_at
* updated_at

### Relationships

Vulnerability

↓

Threat Actors

↓

Malware

↓

Campaigns

↓

Products

↓

Assets

---

## 11.6 MITRE Technique

### Fields

* id
* technique_id
* tactic
* name
* description
* url

### Relationships

Technique

↓

Indicators

↓

Threat Actors

↓

Malware

↓

Campaigns

---

## 11.7 Feed

### Fields

* id
* name
* description
* type
* enabled
* schedule
* authentication
* rate_limit
* priority
* last_success
* last_failure
* records_imported
* status

### Relationships

Feed

↓

Collectors

↓

Indicators

↓

Feed Runs

---

## 11.8 Feed Run

Represents one execution of a collector.

Fields

* id
* feed
* start_time
* end_time
* duration
* status
* records_received
* records_added
* records_updated
* records_skipped
* errors

---

## 11.9 Asset

Represents an organization-owned resource.

Supported Types

* Public IP
* Domain
* Email Domain
* Cloud Account
* Supplier
* VPN Gateway
* Product
* Manufacturing Plant
* Vehicle Platform
* Repository

Fields

* id
* type
* name
* value
* owner
* criticality
* tags
* created_at

Relationships

Asset

↓

Indicators

↓

Investigations

↓

Watchlists

---

## 11.10 Investigation

Represents an analyst investigation.

Fields

* id
* title
* description
* owner
* status
* priority
* created_at
* updated_at
* closed_at

Relationships

Investigation

↓

Indicators

↓

Threat Actors

↓

Malware

↓

Campaigns

↓

Assets

↓

Comments

---

## 11.11 Watchlist

Fields

* id
* name
* description
* owner
* enabled
* matching_rule
* created_at

Watchlists generate notifications when new intelligence matches.

---

## 11.12 Report

Fields

* id
* title
* summary
* author
* created_at
* references

Reports may reference any entity.

---

## 11.13 Comment

Fields

* id
* entity
* author
* content
* timestamp

Comments support analyst collaboration.

---

# 12. Correlation Rules

The platform shall automatically correlate intelligence.

Supported correlations include:

Indicator ↔ Indicator

Indicator ↔ Threat Actor

Indicator ↔ Malware

Indicator ↔ Campaign

Indicator ↔ Vulnerability

Indicator ↔ Asset

Threat Actor ↔ Campaign

Threat Actor ↔ Malware

Campaign ↔ Malware

Campaign ↔ Vulnerability

Malware ↔ Hash

Malware ↔ Infrastructure

Relationships shall be stored independently from entities to allow future expansion.

Every relationship shall include:

* source
* confidence
* relationship_type
* discovered_at
* updated_at

---

# 13. Risk Scoring

Every Indicator shall have a calculated Risk Score (0–100).

Suggested inputs:

* Feed confidence
* Number of independent sources
* Recent activity
* Known malware association
* Known threat actor association
* Internal asset match
* Active exploitation
* Analyst verdict

Risk Score shall update automatically whenever new intelligence is received.

# 14. Feed Collection Architecture

## Objectives

* Modular
* Independent
* Fault tolerant
* Easy to extend
* No collector should affect another collector

---

## Supported Feeds (Initial)

Open Source

* ThreatFox
* MalwareBazaar
* AbuseIPDB
* AlienVault OTX
* URLHaus
* OpenPhish
* PhishTank
* Feodo Tracker
* CISA KEV
* Emerging Threats

Optional

* VirusTotal
* GreyNoise
* Shodan

Future feeds must be added without modifying existing collectors.

---

## Collector Lifecycle

Every collector follows:

Fetch

↓

Validate

↓

Normalize

↓

Deduplicate

↓

Enrich

↓

Correlate

↓

Store

↓

Index

↓

Notify

---

## Collector Requirements

Every collector shall support:

* Scheduling
* Retry
* Logging
* Rate limiting
* Timeout
* Error isolation
* Metrics
* Configuration
* Health monitoring

A failed collector must not stop other collectors.

---

# 15. Data Normalization

Every feed returns data in different formats.

All intelligence shall be converted into a common internal schema before storage.

Normalization includes:

* Field mapping
* Timestamp normalization
* Country normalization
* Hash normalization
* URL normalization
* Indicator type detection
* Confidence mapping
* Severity mapping

No raw feed format should be exposed to the application layer.

Raw responses shall still be stored for auditing.

---

# 16. Deduplication

Duplicate intelligence should never create duplicate entities.

Duplicate detection should consider:

* Indicator type
* Indicator value
* Existing relationships
* Feed source

If duplicate:

* Update last_seen
* Merge sources
* Merge tags
* Preserve history

---

# 17. Enrichment Engine

The platform shall enrich intelligence whenever possible.

Examples:

Indicator →

WHOIS

Passive DNS

ASN

GeoIP

Reverse DNS

Threat Actor →

Aliases

Country

Motivation

Known campaigns

Malware →

Family

Capabilities

Persistence

Communication

CVE →

CVSS

EPSS

KEV

Affected products

Enrichment failures must not interrupt ingestion.

---

# 18. Search Engine

Global search is a primary feature.

Supported search objects:

* Indicators
* Threat Actors
* Malware
* Campaigns
* CVEs
* MITRE Techniques
* Assets
* Reports

---

## Search Features

* Exact search
* Partial search
* Fuzzy search
* Type filtering
* Tag filtering
* Feed filtering
* Time filtering
* Confidence filtering
* Severity filtering

---

## Search Requirements

Search must return:

Summary

↓

Risk

↓

Confidence

↓

Sources

↓

Related entities

↓

Timeline

↓

Actions

Target response time:

< 500 ms for common queries.

---

# 19. Organization Context

The platform protects one organization.

Organization context includes:

Domains

Public IPs

VPNs

Cloud accounts

Products

Vehicle platforms

Manufacturing plants

Suppliers

Email domains

Business units

---

## Relevance Detection

Every incoming intelligence object shall be checked against organization assets.

Possible outcomes:

No Match

Low Relevance

Medium Relevance

High Relevance

Critical Relevance

This relevance score contributes to the overall Risk Score.

---

# 20. Watchlists

Users may create watchlists.

Supported watchlist targets:

Indicator

Threat Actor

Campaign

Malware

Country

CVE

MITRE Technique

Tag

Supplier

Asset

---

## Watchlist Actions

When matched:

* Highlight entity
* Generate notification
* Add to dashboard
* Record match history

---

# 21. Investigation Workspace

Investigations shall support:

* Pin Indicators
* Pin Threat Actors
* Pin Malware
* Pin Campaigns
* Pin CVEs
* Pin Assets
* Notes
* Timeline
* Relationship Graph
* Export

Investigations are persistent.

Investigations may be reopened.

---

# 22. Timeline

Every major entity shall expose a timeline.

Example events:

Created

Updated

Seen by new feed

Confidence changed

Relationship added

Relationship removed

Matched asset

Matched watchlist

Analyst comment

Timeline should be chronological.

---

# 23. Graph Visualization

The platform shall visualize relationships.

Supported nodes:

Indicator

Threat Actor

Campaign

Malware

Asset

Feed

MITRE Technique

CVE

Supported actions:

Expand

Collapse

Filter

Highlight

Search

Node Details

Analysts should be able to navigate relationships interactively.

# 24. Dashboard

The dashboard is the primary landing page for analysts.

## Objectives

* Surface the most important intelligence first.
* Minimize clicks during investigations.
* Highlight organization-relevant threats.
* Provide quick navigation to detailed views.

---

## Dashboard Widgets

### Overview

* Total Indicators
* New Indicators (24 Hours)
* Active Threat Feeds
* Feed Health
* Open Investigations

---

### Threat Activity

* Indicators by Day
* Top Threat Actors
* Top Malware Families
* Top Campaigns
* Top Countries
* Top MITRE Techniques

---

### Organization

* High Risk Asset Matches
* Supplier Threats
* Automotive Threats
* Active Watchlist Matches

---

### Feed Status

For every feed display:

* Status
* Last Successful Run
* Last Failed Run
* Records Imported
* Errors
* Average Runtime

---

### Recent Intelligence

Display latest:

* Indicators
* Campaigns
* Malware
* Threat Actors
* CVEs

---

# 25. Entity Detail Pages

Every major entity shall have a dedicated page.

## Common Layout

Summary

↓

Risk Assessment

↓

Timeline

↓

Relationships

↓

References

↓

Raw Data

↓

History

↓

Comments

↓

Export

---

## Indicator Page

Display:

* Value
* Type
* Risk Score
* Confidence
* Severity
* First Seen
* Last Seen
* Sources
* Tags
* Related Indicators
* Related Threat Actors
* Related Malware
* Related Campaigns
* Related CVEs
* Related Assets
* MITRE Techniques
* WHOIS
* Passive DNS
* Timeline
* Comments
* Export

---

## Threat Actor Page

Display:

* Name
* Aliases
* Description
* Motivation
* Country
* Sophistication
* Active Status
* Campaigns
* Malware
* Infrastructure
* Indicators
* MITRE Techniques
* Timeline
* References

---

## Malware Page

Display:

* Name
* Aliases
* Category
* Family
* Description
* Capabilities
* Persistence
* Communication
* Hashes
* Campaigns
* Threat Actors
* Indicators
* MITRE Techniques
* Timeline

---

## Campaign Page

Display:

* Name
* Description
* Threat Actor
* Malware
* Indicators
* Victims
* Countries
* Timeline
* References

---

## Vulnerability Page

Display:

* CVE
* Description
* CVSS
* EPSS
* KEV Status
* Exploited
* Patch Available
* Threat Actors
* Malware
* Campaigns
* Assets
* References

---

# 26. Reporting

Support generation of:

* Daily Report
* Weekly Report
* Monthly Report
* Threat Landscape Report
* Automotive Threat Report
* Executive Summary

Reports may be exported as:

* PDF
* CSV
* JSON
* STIX 2.1

---

# 27. API Requirements

The backend exposes a versioned REST API.

Base path:

/api/v1

---

## General Rules

* RESTful endpoints
* JSON only
* Pagination
* Filtering
* Sorting
* Consistent error responses
* Authentication required unless explicitly public

---

## Standard Operations

Every primary entity should support:

* Create
* Read
* Update
* Delete
* Search
* Filter
* Export

where appropriate.

---

# 28. Security

The platform shall support:

* Role Based Access Control (RBAC)
* Authentication
* Authorization
* Audit Logging
* Input Validation
* Output Sanitization
* Secret Management
* HTTPS
* Secure Password Storage
* Session Management

---

## Initial Roles

Administrator

Threat Intelligence Analyst

SOC Analyst

Threat Hunter

Incident Responder

Read Only User

Roles may be extended later.

---

# 29. Performance Requirements

The platform should:

* Support millions of indicators.
* Support concurrent users.
* Scale horizontally where practical.
* Minimize duplicate storage.
* Optimize database queries.
* Cache frequently accessed data.
* Keep collector execution independent.

Target search latency:

Less than 500 ms for common searches.

---

# 30. Logging

Log:

* Feed Runs
* API Requests
* Authentication Events
* Authorization Failures
* Collector Errors
* Data Processing Errors
* Background Jobs

Logs should be structured and searchable.

---

# 31. Future Enhancements

The architecture should allow future support for:

* STIX/TAXII
* MISP Integration
* Sigma Repository
* YARA Repository
* AI Threat Summaries
* Threat Intel Sharing
* Multi-Tenant Deployment
* SSO
* SAML/OIDC
* Webhooks
* GraphQL
* Plugin Marketplace
* IOC Expiration Policies
* Automated Enrichment Pipelines
* Threat Intelligence Scoring Improvements

These features are outside the scope of Version 1 but should not require architectural redesign.

---

# 32. Definition of Done

A feature is complete only if:

* Requirements are implemented.
* Code follows project standards.
* API documentation is updated if required.
* No existing functionality is broken.
* Error handling is implemented.
* Logging is included where appropriate.
* Feature is testable.
* Code is production-ready.

End of SPEC.md



