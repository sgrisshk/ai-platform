# MVP Task Registry

## Project goal

Build and validate an MVP that can ingest historical business decisions, separate decision-time variables from downstream outcomes, discover non-obvious harmful patterns, validate them statistically, estimate economic impact, present evidence, create policy candidates, backtest policies, and later repeat the workflow on real customer data.

- **Domain:** Travel agency / tour operator
- **Strategy:** synthetic benchmark → blind evaluation → real customer data
- **Current priority:** prove that discovery can recover hidden economically harmful patterns without access to ground truth.

Do not optimize for feature count. Optimize for evidence that the core mechanism works.

## Operating rules

Every task has exactly one primary owner. If work falls outside that role, create a task-referenced handoff in `memory/HANDOFFS.md`; do not silently assume specialist authority.

Before work, read `PROJECT_CONTEXT.md`, `ARCHITECTURE.md`, `AGENTS.md`, `agents/README.md`, the applicable role file, relevant `DECISIONS.md` entries, this registry, and `memory/CURRENT_STATE.md`.

Use only these statuses: `TODO`, `READY`, `IN_PROGRESS`, `BLOCKED`, `IN_REVIEW`, `DONE`, `REJECTED`.

Priorities:

- `P0` — blocks the MVP
- `P1` — required for the first usable product
- `P2` — important after core validation
- `P3` — later

Do not mark work `DONE` without executing its required checks and completion protocol from `AGENTS.md`.

## Phase 0 — Repository foundation

### TASK-001 — Repository bootstrap

- **Owner:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** none
- **Goal:** Production-capable FastAPI, Next.js, PostgreSQL, SQLAlchemy/Alembic, Docker Compose, uv/pnpm, quality tooling, CI, `/health`, and real `/ready` foundation.
- **Evidence:** Bootstrap commands, tests, PostgreSQL migrations, frontend build, Compose smoke test, Docker images, and dependency audits were executed on 2026-08-13.

### TASK-002 — Core domain models

- **Owner:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-001
- **Goal:** Separate API and persistence primitives for Dataset, DatasetColumn, AnalysisRun, Finding, and PolicyCandidate using UUIDs and timezone-aware timestamps.
- **Remaining evolution:** Full validated-finding fields are tracked by TASK-023; current objects intentionally form a minimal skeleton.

## Phase 1 — Synthetic benchmark

### TASK-003 — Synthetic travel-agency benchmark generator

- **Owner:** DATA_ENGINEER
- **Reviewer:** STATISTICS
- **Priority:** P0
- **Status:** READY
- **Depends on:** TASK-001
- **Goal:** Generate 10,000 bookings across 24 months with a fixed seed and hidden ground truth.
- **Scope:** Seasonality, managers, suppliers, customer segments, discounts, payments, cancellations, refunds, support costs, gross profit, and contribution margin; at least 8 harmful patterns, 5 confounding traps, drift, heterogeneous effects, selection bias, leakage fields, missingness, and a dirty-data variant.
- **Outputs:** `synthetic_data/{raw,reference,metadata,evaluation}/`, clean/dirty CSVs, schema and feature-timing metadata, hidden ground truth, corruption/config manifests, evaluator, and `SIMULATION_REPORT.md`.
- **Critical rule:** ML Discovery must never receive hidden ground truth before candidates are persisted.
- **Done when:** Generation is reproducible, configured patterns/traps exist, time splits work, public inputs contain no answer leakage, and tests pass.

### TASK-004 — Benchmark difficulty presets

- **Owner:** DATA_ENGINEER
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-003
- **Goal:** Add `EASY`, `MEDIUM`, `HARD`, and `BRUTAL` presets varying noise, effects, missingness, confounding, rarity, and temporal instability.

## Phase 2 — Data ingestion

### TASK-005 — Immutable ingestion contract

- **Owner:** DATA_ENGINEER
- **Reviewer:** ARCHITECT
- **Priority:** P0
- **Status:** READY
- **Depends on:** TASK-002
- **Goal:** Specify checksums, file validation, size/type limits, safe names, retention, versioning, immutable storage, logging/privacy boundaries, and typed ingestion manifest.
- **Handoff:** `HANDOFF-001`.

### TASK-006 — Dataset upload API and raw storage

- **Owner:** ARCHITECT
- **Data contract:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-005
- **Goal:** Accept CSV through `POST /api/v1/datasets`, preserve raw bytes immutably, and persist filename, checksum, timestamp, size, version, and source type without logging contents.
- **Done when:** A synthetic CSV can be uploaded and every version is traceable; identical identity rules prevent silent overwrite.

### TASK-007 — Schema profiler

- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-006
- **Goal:** Persist inferred type, missingness, distinct count, relevant min/max, safe examples, suspicious values, and likely semantic type per column.

### TASK-008 — Feature-timing classification

- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-007
- **Goal:** Classify every field as `DECISION_TIME`, `POST_DECISION`, `OUTCOME`, `IDENTIFIER`, `METADATA`, or `UNKNOWN`.
- **Invariant:** Post-decision, outcome, and unknown fields cannot enter discovery features.
- **Done when:** Benchmark classification matches expected metadata and leakage tests pass.

### TASK-009 — Data-quality report

- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-007, TASK-008
- **Goal:** Produce machine- and customer-readable rows, columns, coverage, duplicates, missingness, invalid/suspicious records, currencies, leakage risks, outcomes, and usable variables.
- **Rating:** Exactly one of `READY`, `READY_WITH_LIMITATIONS`, or `NOT_READY`.

## Phase 3 — Canonical analytical dataset

### TASK-010 — Travel-booking canonical schema

- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-009
- **Goal:** Reproducibly normalize travel-agency inputs into a typed canonical representation.

### TASK-011 — Analytical dataset builder

- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-010
- **Goal:** Build versioned analytical datasets with separate features, outcomes, identifiers, and metadata plus transformation configuration and lineage.

### TASK-012 — Temporal split builder

- **Owner:** DATA_ENGINEER
- **Reviewer:** STATISTICS
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-011
- **Goal:** Deterministically create development, validation, and future holdout splits without random time shuffling.

## Phase 4 — Outcome analytics

### TASK-013 — Outcome definition layer

- **Owner:** STATISTICS
- **Implementation support:** ARCHITECT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-011
- **Goal:** Version explicit definitions for actual gross profit, contribution margin/value percentage, cancellation, refund, support cost, and repeat purchase.

### TASK-014 — Baseline business statistics

- **Owner:** STATISTICS
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-013
- **Goal:** Sanity-check overall distributions, time/segment/supplier/manager trends, and outcome prevalence before discovery.

## Phase 5 — Pattern discovery

### TASK-015 — Discovery engine v0

- **Owner:** ML_DISCOVERY
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-011, TASK-013
- **Goal:** Use simple interpretable methods first—shallow trees, boosting with rule extraction, and subgroup discovery—to return 10–20 harmful candidate patterns.
- **Candidate contract:** Conditions, support, N, raw difference, deterministic economic exposure, stability indicators, and warnings.

### TASK-016 — Candidate ranking v0

- **Owner:** ML_DISCOVERY
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-015
- **Goal:** Rank candidates by economic impact, support, stability, actionability, and novelty—not model importance alone.

### TASK-017 — Blind discovery test

- **Owner:** ML_DISCOVERY
- **Reviewer:** CODE_REVIEWER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-003, TASK-016
- **Goal:** Run without hidden ground truth and persist candidates before evaluation files are opened.

## Phase 6 — Statistical validation

### TASK-018 — Validation and evidence contract

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** READY
- **Depends on:** none
- **Goal:** Predefine sample-size, uncertainty, temporal/segment stability, multiple testing, confounding, leakage, selection, seasonality, evidence grades, and policy-readiness rules.

### TASK-019 — Validation framework implementation

- **Owner:** STATISTICS
- **Implementation support:** ARCHITECT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-017, TASK-018
- **Goal:** Apply the standardized validation contract to persisted candidates.

### TASK-020 — Evidence classification

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-019
- **Goal:** Assign exactly one level: descriptive, predictive association, adjusted observational, quasi-causal, or experimental.

### TASK-021 — Adjusted effect estimation v0

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-019
- **Goal:** Estimate adjusted effects with the simplest defensible method, uncertainty, controls, and explicit non-identifiability/limitations.

### TASK-022 — Confounding-trap evaluation

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-003, TASK-021
- **Goal:** Verify that known manager/supplier and other synthetic traps are rejected or conservatively downgraded.

## Phase 7 — Economic impact

### TASK-023 — Economic impact engine v0

- **Owner:** STATISTICS
- **Implementation support:** ARCHITECT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-021
- **Goal:** Deterministically report affected records, average effect, historical impact, justified annualization, and uncertainty range.

## Phase 8 — Validated findings

### TASK-024 — Full finding persistence model

- **Owner:** ARCHITECT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-020, TASK-023
- **Goal:** Extend the current skeleton with pattern, support, raw/adjusted effects, uncertainty, impact, evidence, warnings, stability, status, and lineage.

### TASK-025 — Findings API completion

- **Owner:** ARCHITECT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-024
- **Goal:** Make existing list/detail endpoints serve real persisted validated findings with safe evidence-aligned schemas.

## Phase 9 — First product UI

### TASK-026 — Findings list screen

- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-025
- **Goal:** Show ranked findings without becoming a generic dashboard.

### TASK-027 — Finding detail screen

- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-025
- **Goal:** Explain what was found, population, impact, raw/adjusted effect, evidence, stability, alternatives, warnings, and next step in business language.

## Phase 10 — Blind benchmark evaluation

### TASK-028 — Ground-truth evaluator

- **Owner:** STATISTICS
- **Implementation support:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-022, TASK-023
- **Goal:** Compute precision, recall, Top-K/economic-weighted recall, false-positive and confounder-rejection rates, direction accuracy, impact error, and leakage violations.

### TASK-029 — Benchmark report v1

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-028
- **Goal:** Document recovered/missed patterns, false positives, confounding failures, expensive misses, and the largest methodological weakness.

## MILESTONE-M1 — Synthetic end-to-end MVP

- **Status:** BLOCKED
- **Depends on:** TASK-029

Complete when synthetic CSV → ingestion → profiling → canonical dataset → discovery → validation → impact → persisted finding → UI → blind evaluation works end to end. Several true patterns must be recovered, high-impact patterns rank near the top, major traps are rejected/downgraded, no post-treatment leakage occurs, and findings are understandable.

## Phase 11 — Policy candidates (after M1)

### TASK-030 — Policy candidate domain model
- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** MILESTONE-M1
- **Goal:** Define trigger, scope, action, expected benefit, evidence, exceptions, and status.

### TASK-031 — Policy candidate generator
- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Reviewer:** STATISTICS
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-030
- **Goal:** Deterministically translate validated findings into reviewable interventions; an LLM may later explain but never invent numerical thresholds.

## Phase 12 — Historical policy backtesting

### TASK-032 — Policy backtest engine v0
- **Owner:** STATISTICS
- **Implementation support:** ARCHITECT
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-031
- **Goal:** Estimate affected decisions, avoided bad outcomes, affected good outcomes, benefit, opportunity/operational costs, net effect, and uncertainty.

### TASK-033 — Synthetic backtest validation
- **Owner:** STATISTICS
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-003, TASK-032
- **Goal:** Compare backtest estimates with synthetic policy ground truth.

### TASK-034 — Policy backtest UI
- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-032
- **Goal:** Present rule, affected records, upside/downside, uncertainty, evidence, and next action.

## MILESTONE-M2 — Policy discovery demo

- **Status:** BLOCKED
- **Depends on:** TASK-034
- **Success:** A user can upload data, run analysis, open evidence, create a policy candidate, and run a historical backtest.

## Phase 13 — Customer feedback

### TASK-035 — Finding feedback model
- **Owner:** PRODUCT
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-027
- **Values:** `KNOWN_ALREADY`, `NEW`, `WRONG`, `NOT_ACTIONABLE`, `INTERESTING`, `ACTIONABLE`.

### TASK-036 — Customer review workflow
- **Owner:** PRODUCT
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-035
- **Goal:** Structured one-by-one finding review.

## Phase 14 — First real customer data

### TASK-037 — Real-dataset security review
- **Owner:** CODE_REVIEWER
- **Support:** ARCHITECT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** Real customer agreement
- **Goal:** Review storage, logs, access, backups, local copies, secrets, and deletion before any real data enters the system.

### TASK-038 — Customer dataset ingestion
- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-037
- **Goal:** Ingest the first real dataset without modifying source data.

### TASK-039 — Customer data-quality review
- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-038
- **Goal:** Produce a customer-specific Data Quality Report.

### TASK-040 — Customer blind discovery run
- **Owner:** ML_DISCOVERY
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-039

### TASK-041 — Customer statistical validation
- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-040
- **Goal:** Conservatively validate top candidates.

### TASK-042 — Customer findings review
- **Owner:** CUSTOMER_DISCOVERY
- **Support:** PRODUCT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-041
- **Goal:** Capture known/new, actionability, relevance, trust objections, and desired follow-up.

## MILESTONE-M3 — First real discovery

- **Status:** BLOCKED
- **Depends on:** TASK-042
- **Success:** At least one customer response equivalent to “new + economically material + actionable.” If findings are obvious or non-actionable, reassess methodology, ICP, outcomes, and available variables.

## Phase 15 — Repeatability and commercial validation

### TASK-043 — Second independent dataset pilot
- **Owner:** CUSTOMER_DISCOVERY
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** MILESTONE-M3

### TASK-044 — Third independent dataset pilot
- **Owner:** CUSTOMER_DISCOVERY
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** MILESTONE-M3

### TASK-045 — Repeatability assessment
- **Owner:** FOUNDER_STRATEGY
- **Support:** STATISTICS
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-043, TASK-044
- **Goal:** Evaluate new-finding rate, materiality, actionability, policy-change willingness, data requirements, and time-to-value across companies.

### TASK-046 — Paid pilot offer
- **Owner:** CUSTOMER_DISCOVERY
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** MILESTONE-M3
- **Goal:** Ask a customer to pay; stated willingness alone is not validation.

### TASK-047 — Pilot pricing test
- **Owner:** FOUNDER_STRATEGY
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-046
- **Goal:** Test fixed analysis, monthly pilot, or fixed 6–8 week engagement before complex performance pricing.

## Phase 16 — Accelerator and fundraising

Fundraising must not block product validation.

### TASK-048 — Company one-liner
- **Owner:** FOUNDER_STRATEGY
- **Priority:** P1
- **Status:** READY
- **Goal:** Maintain one simple, evidence-aligned sentence without broad positioning.

### TASK-049 — Founder story
- **Owner:** FOUNDER_STRATEGY
- **Priority:** P2
- **Status:** TODO

### TASK-050 — Application metrics snapshot
- **Owner:** FUNDRAISING
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** First usable traction
- **Metrics:** Customer datasets, analyzed transactions, generated/confirmed-new findings, policies changed, verified impact, and paid pilots.

### TASK-051 — YC application draft
- **Owner:** FUNDRAISING
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** Meaningful evidence
- **Goal:** Factual application with no synthetic-data traction or unsupported causal claims.

### TASK-052 — Accelerator application pack
- **Owner:** FUNDRAISING
- **Priority:** P2
- **Status:** BLOCKED
- **Depends on:** TASK-048
- **Outputs:** One-liner, 100-word description, problem, solution, why now, market, competitors, traction, founder story, demo link, and short product video.

## Phase 17 — Security and enterprise readiness

Do not overbuild before demand.

### TASK-053 — Basic authentication
- **Owner:** ARCHITECT
- **Priority:** P2
- **Status:** BLOCKED
- **Depends on:** Real external users

### TASK-054 — Tenant-isolation design
- **Owner:** ARCHITECT
- **Reviewer:** CODE_REVIEWER
- **Priority:** P2
- **Status:** BLOCKED
- **Depends on:** Multiple customer accounts

### TASK-055 — Data-deletion workflow
- **Owner:** ARCHITECT
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** First real customer dataset

### TASK-056 — Audit trail
- **Owner:** ARCHITECT
- **Priority:** P2
- **Status:** BLOCKED
- **Depends on:** Real customer usage

## Explicitly deferred

Do not create implementation tasks without customer-backed justification for Salesforce, HubSpot, SAP, Slack/Gmail integrations, streaming, Kafka, Kubernetes, autonomous enforcement, agent runtime, universal Business Graph, SSO/SAML, billing automation, complex RBAC, mobile apps, vector databases, generic workflow builders, or AI-agent organization governance.

## Immediate execution order

```text
TASK-003 + TASK-005 + TASK-018
→ TASK-006 → TASK-007 → TASK-008 → TASK-009
→ TASK-010 → TASK-011 → TASK-012 → TASK-013
→ TASK-015 → TASK-016 → TASK-017
→ TASK-019 → TASK-020 → TASK-021 → TASK-022 → TASK-023
→ TASK-024 → TASK-025 → TASK-027
→ TASK-028 → TASK-029 → MILESTONE-M1
```

TASK-003, TASK-005, and TASK-018 may proceed independently, but their owners must respect handoffs and hidden-ground-truth separation.

## Sprint plan

### Sprint 1 — Benchmark and ingestion foundation

- **Tasks:** TASK-003, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009, TASK-018
- **Exit:** Reproducible hidden-ground-truth benchmark exists; synthetic CSV is immutably uploaded, profiled, timing-classified, and receives a Data Quality Report; CI is green.

### Sprint 2 — First blind candidate discovery

- **Tasks:** TASK-010 through TASK-013, TASK-015 through TASK-017
- **Exit:** Ranked candidates are persisted without Discovery access to hidden ground truth.

### Sprint 3 — Defensibility and evaluation

- **Tasks:** TASK-019 through TASK-025, TASK-027 through TASK-029
- **Exit:** The team knows what was recovered/missed, false positives, confounding failures, leakage violations, and whether costly harmful patterns rank near the top.
