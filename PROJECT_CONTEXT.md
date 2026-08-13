# Project context

## Vision

Help businesses discover previously unknown decision patterns that create downstream economic harm, validate the strength of the evidence, and turn credible findings into human-controlled interventions and policy candidates.

## Product thesis

Historical business decisions and downstream economic outcomes can reveal harmful decision patterns. This product turns reproducible evidence into explainable policy candidates while keeping numerical truth in deterministic code.

## Current MVP

The initial travel-agency workflow ingests booking exports, validates and normalizes them, prepares leakage-safe analytical datasets, and will later discover and validate findings. The current repository is the production-oriented foundation: dataset metadata, analysis-run tracking, findings, API, web shell, database, tests, and delivery controls.

## Current customer context

The initial wedge is a travel-agency pilot and historical bookings. A real customer dataset has not yet been profiled by the implemented pipeline. Treat customer availability, pilot commitment, and willingness to pay as unvalidated until recorded through Customer Discovery evidence.

## Current scope

- One FastAPI backend, one Next.js frontend, and PostgreSQL.
- Dataset metadata registration and run/finding read surfaces.
- Reproducible migrations, typed configuration, structured logs, and synthetic test data.
- Deterministic analytics package boundaries without a discovery implementation.
- Repository-native role contracts, decision history, task registry, and durable project memory for specialized-agent collaboration.

For operational status, blockers, and the next milestone, read `memory/CURRENT_STATE.md`. This file describes stable product context and should not be used as a task log.

## Expected dataset schema

The expected export may contain booking identifiers and dates, destination, supplier, product/hotel category, price, cost, gross margin, discount, manager, acquisition channel, customer type, party size, duration, booking lead time, payment method/installments, manual exceptions, cancellations/refunds, booking changes, support cases, additional cost, and repeat purchase.

This list is an expected input vocabulary, not an approved canonical schema. Data Engineer must classify each supplied field as decision-time, post-decision, outcome, identifier, metadata, or unknown before analytical use.

## Architecture summary

The MVP is a modular monolith: Next.js → FastAPI → application services → SQLAlchemy/PostgreSQL, with deterministic analytical modules kept outside API routes. Raw data is immutable, analysis runs are reproducible, findings are traceable, and LLM output cannot be numerical truth. Full boundaries live in `ARCHITECTURE.md`; durable choices live in `DECISIONS.md`.

## Market and differentiation boundary

The core is discovery of previously unknown, actionable, policy-worthy interaction patterns. The product should not drift into a generic BI dashboard, process-mining suite, pricing optimizer, policy-management platform, or undifferentiated causal-analytics toolkit. Competitor claims and named market comparisons require current research before being recorded as facts.

## Non-goals

No production discovery or causal engine, LLM integration, CRM integrations, agent runtime, policy enforcement, complex auth, billing, multi-tenancy, SSO, Kubernetes, Kafka, or full dashboard.

## Validated assumptions

- The repository foundation can build and run as Next.js + FastAPI + PostgreSQL.
- Migrations, API health/readiness, type checks, tests, production builds, and dependency audits have been executed successfully during bootstrap.
- A synthetic fixture can support development without committing customer data.

These validate engineering readiness only; they do not validate product demand or analytical value.

## Unvalidated assumptions

- A suitable customer export contains enough reliable decision-time and outcome data.
- Previously unknown material interaction patterns exist in that data.
- A customer will consider at least one validated finding new and actionable.
- The customer will change behavior or pay for continued use.
- Available observational data can support evidence stronger than descriptive/predictive association.

## Current metrics and experiments

There are no customer traction metrics or active product/ML experiments recorded. Do not infer traction from repository activity or synthetic data. Experiment history belongs in `memory/EXPERIMENTS.md`; validated durable results belong in `memory/FINDINGS.md`.

## Decision and task references

- Current durable decisions: `DECISIONS.md`
- Current work and ownership: `TASKS.md`
- Current milestone and blocker: `memory/CURRENT_STATE.md`
- Cross-role work: `memory/HANDOFFS.md`
- Material unresolved questions: `memory/OPEN_QUESTIONS.md`

## Terminology

- **Dataset:** immutable source identity plus processing status and schema metadata.
- **Analysis run:** reproducible execution envelope: dataset version, code version, configuration, seed, and timestamps.
- **Finding:** traceable evidence object with an explicit evidence level; not automatically causal.
- **Policy candidate:** human-reviewable proposal derived from validated evidence.
- **Decision-time feature:** known at the decision timestamp.
- **Post-decision event:** happens after the decision and is excluded from explanatory features by default.
- **Outcome:** downstream value used to assess consequences.
