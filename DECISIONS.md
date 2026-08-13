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

## ADR-007 — Preregistered validation and evidence contract

**Date:** 2026-08-13
**Status:** Accepted

**Decision:** Fix the validation methodology before any candidate pattern exists. Contract v1.0.0 defines sixteen ordered gates, their thresholds, cumulative requirements per evidence level, permitted language per level, and the policy-readiness matrix, in `docs/validation_contract.md` and `packages/analytics/src/policy_analytics/validation/`. Changing a threshold requires a new contract version and re-grading of every finding produced under the old one.

**Context:** A validation standard chosen after seeing results is not a standard. Candidate patterns are search results whose default explanation is leakage, confounding, selection, or the size of the search, and the rules that reject them must be fixed in advance.

**Alternatives:** Case-by-case statistical judgment; thresholds tuned per finding; a binary validated/unvalidated flag.

**Consequences:** A finding cannot claim an evidence level its gate results do not support — `ValidationReport` re-derives the level and refuses inconsistent reports. Unevaluated checks count as failures, so missing upstream inputs cap evidence rather than being waived. Observational data caps this product at `adjusted_observational_association`; levels 4 and 5 require a design, and `HIGH_CONFIDENCE` readiness is unreachable until policy backtesting exists. False-discovery control uses the number of hypotheses discovery evaluated, not the number it reported, which makes the discovery run manifest a hard dependency of evidence grading.

## ADR-008 — Allowlist workspace and signed commitment for blind discovery

**Date:** 2026-08-13
**Status:** Accepted

**Decision:** Run synthetic blind discovery under a separate execution identity in a generated,
allowlist-only workspace. Before hidden truth is opened, an evaluation identity commits the exact
candidate bytes with an HMAC-signed receipt containing their SHA-256 and blind bundle ID.

**Context:** Restricted and public benchmark artifacts coexist in the main checkout. Directory
conventions and Discovery-controlled persistence metadata do not enforce blindness or temporal
commitment.

**Alternatives:** Documentation-only separation; caller-supplied timestamps; a database audit
table; separate repositories/object storage/CI environments.

**Reason:** A generated workspace plus evaluator-owned signature creates the required access and
commitment boundaries using only local files and standard cryptography, without premature
infrastructure.

**Consequences:** A credible blind run must never give Discovery the full checkout or signing key.
Candidate evaluation requires a valid receipt and fails after any candidate modification. The
protocol can later use CI artifacts or external storage without changing its file contracts.

## ADR-009 — Preregistered outcome definition contract

**Date:** 2026-08-13  
**Status:** Accepted

**Decision:** Fix, before any discovery run, which outcome is primary for the first blind benchmark, its harm direction, unit, missing-data policy, and eligible cohort. Primary outcome is `contribution_margin_eur` (EUR per booking; a decrease relative to the comparison group is harmful); six secondary/decomposition outcomes are defined; `repeat_purchase_180d` is exploratory-only and MNAR-bounded. Contract v1.0.0 is pinned to the delivered analytical dataset `travel-bookings-analytical-v1.0.0` by its identity hash, in `docs/outcome_contract.md` and `packages/analytics/src/policy_analytics/outcomes/`.

**Context:** `TASK-015`/`TASK-016` (ML Discovery) require a single, unambiguous target to rank candidates against. Choosing or reweighting the outcome is a business-semantics decision Discovery is not authorized to make (`agents/ML_DISCOVERY.md`), and doing it after seeing candidates would let the target be chosen to fit a result.

**Alternatives:** Let Discovery choose or infer an outcome per run; use multiple co-primary outcomes without a sign convention; use `repeat_purchase_180d` or `gross_profit_eur` as primary.

**Reason:** `contribution_margin_eur` is the only outcome in the schema netting out every downstream cost component present in the data and the only one with verified zero missingness, removing an entire bias family (outcome-dependent missingness) from the primary analysis. `repeat_purchase_180d` has empirically confirmed missing-not-at-random structure (9.72% overall, 45.7% among cancelled bookings vs. 7.2% otherwise) and cannot serve as a primary target without inventing a customer-lifetime-value model this repository does not have.

**Consequences:** ML Discovery ranks candidates using the fixed harm-score sign convention (`harm_multiplier`) and the deterministic, unadjusted `historical_exposure` formula in `aggregation.py`; it may not invent a different target or sign. Findings built on secondary/mechanism outcomes are reported as explanatory, never summed with primary-outcome impact. This is a benchmark-scoped decision only — `OQ-002` (the real-customer outcome) remains open and requires its own Product/Customer Discovery input plus a right-censoring/maturation design this closed 24-month benchmark did not need.

## ADR-010 — First-pilot customer acquisition is tracked, top-priority active work

**Date:** 2026-08-13
**Status:** Accepted

**Decision:** Add `TASK-057` (Secure first real pilot customer) to the registry as explicit `P0` work, owned by Customer Discovery with Founder Strategy support, tracked in parallel with and equally urgent to the ingestion-contract critical path (`HANDOFF-001`). `TASK-037`'s dependency is corrected from the informal "Real customer agreement" to `TASK-057`.

**Context:** A repeatability assessment was requested under the label "TASK-044"; the registry's actual repeatability task is `TASK-045`, gated by `MILESTONE-M3`. Investigation (`HANDOFF-014`, Founder Strategy → Customer Discovery) found zero real customer evidence anywhere in this repository — no agreement, dataset, interview, or finding — because Phase 14 (`TASK-037` onward) treated "real customer agreement" as an unowned precondition rather than active tracked work with an owner and a done condition.

**Alternatives:** Continue treating customer acquisition as an implicit precondition outside the task registry; keep sequencing downstream build work (validation, findings UI, policy backtesting) while acquisition happens informally, untracked.

**Reason:** The core hypothesis can only be tested against real customer data. Build work beyond what a credible first pilot requires has no evidence value until at least one real dataset exists. Making acquisition an owned, done-conditioned `P0` task prevents it from being silently deprioritized in favor of engineering work that produces easier, more visible progress.

**Consequences:** `TASK-037` now formally depends on `TASK-057`. `TASK-045` (repeatability assessment, i.e. the requested "TASK-044") stays `BLOCKED`, and no go/no-go verdict on repeatability, pricing, or fundraising traction will be produced before `MILESTONE-M3` succeeds. Founder Strategy tracks `TASK-057` alongside the ingestion-contract critical path as a joint top priority.
