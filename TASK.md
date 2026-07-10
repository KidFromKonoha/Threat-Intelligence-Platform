# Frontend Phase F4 — Global Search

## Business Objective

Implement the primary search experience for the Threat Intelligence Platform.

Search is the analyst's primary workflow.

The experience should feel fast, precise, keyboard-friendly, and optimized for investigation.

---

# User Story

As a SOC Analyst,

I want to search indicators, malware, campaigns, threat actors and organizations,

so that I can rapidly investigate threats without navigating through multiple pages.

---

# Scope

Implement:

- Global Search page
- Search input
- Search filters
- Search results
- Result cards/table
- Pagination (if supported)
- Loading state
- Empty state
- Error state

---

# Out of Scope

Do NOT implement:

- Entity Detail pages
- Investigation creation
- Watchlists
- Reports
- Graph visualization
- Saved searches
- Search history
- Autocomplete (unless backend explicitly supports it)

---

# APIs

Read ONLY the Search-related endpoints and schemas from openapi.json.

Consume exactly the documented APIs.

Do NOT invent query parameters.

If search requires pagination, sorting or filtering, implement only what is documented.

If functionality is missing, report it.

---

# Search Experience

The page should consist of:

------------------------------------------------

Search Bar

------------------------------------------------

Optional Filters

------------------------------------------------

Search Results

------------------------------------------------

Result Summary

------------------------------------------------

Pagination

------------------------------------------------

The search bar should receive immediate focus when opening the page.

---

# Search Results

Display results in a dense analyst-friendly layout.

Each result should clearly show:

- Primary name/value
- Entity type
- Severity (if available)
- Confidence (if available)
- Source
- Last seen
- Short description

Avoid giant cards.

Prefer compact rows or compact cards.

---

# Filters

Implement only filters supported by the backend.

Examples may include:

- Entity Type
- Severity
- Confidence
- Source

Do not invent filters.

---

# Components

Create reusable components where appropriate.

Examples:

- SearchBar
- SearchFilters
- SearchResultCard
- SearchResultsTable
- SearchSummary
- SearchSkeleton
- SearchEmptyState

Business logic belongs inside:

features/search/api

features/search/hooks

Presentational components remain stateless.

---

# UX Requirements

The search experience should feel:

- Immediate
- Keyboard friendly
- Responsive
- Information dense

Typing a search and understanding the results should require minimal clicks.

---

# Accessibility

Support:

- Keyboard navigation
- Focus management
- Proper labels
- Screen reader compatibility

---

# Performance

Use TanStack Query.

Avoid unnecessary refetches.

Debounce search input if appropriate.

Do not issue excessive API requests while typing.

---

# Architecture

Follow:

- FRONTEND_ARCHITECTURE.md
- IMPLEMENTATION_CONTEXT.md

Maintain feature isolation.

Strong TypeScript.

No any.

---

# Acceptance Criteria

✓ Backend search API consumed

✓ Live search results

✓ Loading state

✓ Empty state

✓ Error state

✓ Responsive

✓ Enterprise appearance

✓ No fake data

---

# Definition of Done

A phase is NOT complete until:

✓ Implementation complete

✓ Phase Review Report generated

✓ tsc -b passes

✓ vite build passes

✓ npm run dev runs

✓ Manual runtime verification completed

✓ Search works against live backend APIs

✓ All documented filters function correctly

---

# Documentation

Append ONLY:

## Frontend Phase F4

to IMPLEMENTATION_CONTEXT.md.

Update FRONTEND_ARCHITECTURE.md only if a genuine architectural convention changes.

---

# Stop Condition

Stop immediately after completing Phase F4.