# Task Registry

This file tracks actionable repository work. Durable state belongs in `memory/`; deliberate decisions belong in `DECISIONS.md`.

## Active

### TASK-001 — Immutable ingestion contract

- **Owner:** DATA_ENGINEER
- **Status:** READY
- **Goal:** Specify raw upload identity, content hashes, validation, size/type limits, retention, and immutable storage interface.
- **Dependencies:** Architect review for persistence/storage boundary.
- **Done when:** Contract, threat cases, tests, and architecture documentation are reviewed; no real customer data is committed.

### TASK-002 — Canonical travel-booking schema

- **Owner:** DATA_ENGINEER
- **Status:** BLOCKED_BY_TASK_001
- **Goal:** Implement typed canonical fields and explicit `DECISION_TIME`, `POST_DECISION`, `OUTCOME`, `IDENTIFIER`, `METADATA`, and `UNKNOWN` classification.
- **Done when:** Mapping and leakage tests cover the synthetic fixture and unknown fields fail safely.

### TASK-003 — Finding evidence contract

- **Owner:** STATISTICS
- **Status:** READY
- **Goal:** Define validation metrics, uncertainty, stability, warnings, evidence grading, and policy-readiness semantics before discovery implementation.
- **Handoff:** Architect must review persistence/API implications after methodology is defined.

## Backlog

### TASK-004 — Reproducible normalization manifests and record lineage
- **Owner:** DATA_ENGINEER

### TASK-005 — Leakage-safe deterministic feature contracts
- **Owner:** DATA_ENGINEER
- **Reviewers:** STATISTICS, CODE_REVIEWER

### TASK-006 — First interpretable discovery baseline
- **Owner:** ML_DISCOVERY
- **Blocked by:** TASK-002, TASK-003, TASK-005

### TASK-007 — Authentication, authorization, and tenant-isolation design
- **Owner:** ARCHITECT
- **Trigger:** Before exposure to untrusted users or real customer data.

### TASK-008 — Select staging provider and deployment adapter
- **Owner:** ARCHITECT

### TASK-009 — Customer pilot and interview plan
- **Owner:** CUSTOMER_DISCOVERY
- **Reviewer:** PRODUCT

### TASK-010 — Finding review workflow
- **Owner:** PRODUCT
- **Blocked by:** TASK-003

## Completed

### TASK-011 — Specialized agent routing and strategy roles

- **Owner:** ARCHITECT
- **Completed:** 2026-08-13
- **Outcome:** Added Founder Strategy and Fundraising role contracts, explicit agent-routing workflow, independence rules, and consolidated stable product context without duplicating operational memory.

### TASK-000 — Production-grade repository bootstrap

- **Owner:** ARCHITECT
- **Completed:** 2026-08-13
- **Outcome:** FastAPI, Next.js, PostgreSQL, migrations, deterministic package boundaries, synthetic fixture, tests, lockfiles, Docker, CI/CD interface, security baseline, and core documentation are in place.
