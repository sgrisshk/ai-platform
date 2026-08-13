# Architecture and Product Decision Log

Only deliberate, durable decisions belong here. New entries are append-only; supersede an old decision with a new entry instead of rewriting history.

## ADR-001 — Modular monolith for the MVP

**Date:** 2026-08-13  
**Status:** Accepted

**Decision:** Deploy one Next.js frontend, one FastAPI backend, and PostgreSQL.

**Context:** The early MVP needs rapid iteration, reproducibility, and clear module boundaries without distributed-system overhead.

**Alternatives:** Microservices; event-driven services; serverless functions.

**Reason:** A modular monolith meets current scale and team needs with lower operational and coordination cost.

**Consequences:** Boundaries are enforced in code and documentation rather than network calls. New services require a demonstrated need and a new decision entry.

## ADR-002 — PostgreSQL is the default production database

**Date:** 2026-08-13  
**Status:** Accepted

**Decision:** Use PostgreSQL with SQLAlchemy 2.x and Alembic. Do not use SQLite as the production/default database.

**Context:** The system needs robust relational integrity, JSON metadata, UUIDs, timezone-aware timestamps, and migration support.

**Alternatives:** SQLite; document database.

**Reason:** PostgreSQL covers current relational and metadata requirements without another datastore.

**Consequences:** Integration and migration tests require PostgreSQL. Schema changes must use committed Alembic migrations.

## ADR-003 — Polars is the primary dataframe engine

**Date:** 2026-08-13  
**Status:** Accepted

**Decision:** Use Polars for deterministic data transformations; pandas is allowed only for necessary compatibility.

**Context:** Analytical transformations should be typed, efficient, and reproducible.

**Alternatives:** pandas as the default; Spark.

**Reason:** Polars is sufficient for MVP-scale analytical workloads without distributed infrastructure.

**Consequences:** New analytics dependencies require justification. Dataframe logic remains outside API routes.

## ADR-004 — Numerical truth is deterministic

**Date:** 2026-08-13  
**Status:** Accepted

**Decision:** LLMs may assist semantic mapping, hypotheses, interpretation, and prose, but cannot be the source of numerical or statistical truth.

**Context:** Business policies must be reproducible and auditable.

**Alternatives:** LLM-generated calculations or unverified estimates.

**Reason:** Arithmetic, statistics, causal estimates, financial impact, eligibility, and backtests require executable deterministic code.

**Consequences:** Every reported number must have code, inputs, configuration, and lineage.

## ADR-005 — Explicit evidence taxonomy

**Date:** 2026-08-13  
**Status:** Accepted

**Decision:** Findings use five levels: descriptive observation, predictive association, adjusted observational association, quasi-causal evidence, and experimental evidence.

**Context:** Pattern discovery alone cannot support causal claims.

**Alternatives:** Binary validated/unvalidated labels; unrestricted prose.

**Reason:** Evidence-aligned language prevents harmful overclaiming.

**Consequences:** API and UI language cannot exceed the assigned evidence level. Serious candidates require Statistics review.

## ADR-006 — Durable file-based project memory

**Date:** 2026-08-13  
**Status:** Accepted

**Decision:** Maintain small, structured project memory under `memory/`, role contracts under `agents/`, and cross-role handoffs in `memory/HANDOFFS.md`.

**Context:** Multiple specialized agents need continuity without storing chat transcripts or speculative summaries.

**Alternatives:** Conversation-only context; unstructured notes; external knowledge base.

**Reason:** Repository-native memory is versioned, reviewable, portable, and close to code.

**Consequences:** Agents update memory only when information changes future decisions and follow the protocol in `memory/README.md`.

