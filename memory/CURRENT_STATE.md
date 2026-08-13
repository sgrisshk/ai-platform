# Current Project State

**Last updated:** 2026-08-13

## Current objective

Build the trustworthy ingestion and evidence contracts required to test whether historical travel-booking decisions contain previously unknown, economically material, actionable patterns.

## Current customer context

Initial use case: travel agency pilot. No real customer dataset is stored in this repository, and no customer dataset has yet been profiled by the implemented pipeline. Customer Discovery confirmed (2026-08-13, see the Founder Strategy → Customer Discovery `HANDOFF-007` resolution in `memory/HANDOFFS.md`) that no real customer agreement, real dataset commitment, or customer interview is recorded anywhere in this repository — `DECISIONS.md` contains no such decision. Securing the first real pilot customer has not started and is currently the actual bottleneck ahead of `TASK-037`/`MILESTONE-M3`, independent of the ingestion-contract blocker below. `TASK-042` (customer findings review) stays correctly `BLOCKED`; its review protocol was prepared in advance in `docs/customer_findings_review_protocol.md`.

## Current stage

Repository bootstrap is complete. The validation and evidence contract (ADR-007,
`docs/validation_contract.md`) and the outcome definition contract (`docs/outcome_contract.md`,
closing `TASK-013`) are both preregistered: together they fix how any future candidate will be
graded and what "harm" means on the benchmark. Primary outcome is `contribution_margin_eur`
(EUR/booking, decrease = harm, verified 0% missing); `repeat_purchase_180d` is MNAR-bounded
exploratory only. The synthetic benchmark was reviewed by Statistics and approved in substance,
with one artifact change still open before it closes (per-pattern true effect sizes —
`HANDOFF-010` item 1; the customer-identifier item is delivered). The blind-discovery access and
commitment boundary is implemented under ADR-008: Discovery receives only an allowlisted
analytical workspace, and post-hoc evaluation requires an evaluator-signed candidate receipt
(`docs/blind_benchmark_protocol.md`). `TASK-015`'s dependencies (`TASK-011`, `TASK-013`) are both
`DONE`, so ML Discovery is unblocked pending its own `HANDOFF-011` obligations (search-space
manifest, immutable candidate persistence). Ingestion-contract design is the next data-pipeline
boundary for real customer data.

## Current hypothesis

Historical decision/outcome data may contain actionable interaction patterns the business does not currently recognize. This remains a hypothesis, not a validated finding.

## Current product scope

CSV/Excel export → immutable ingestion → data quality and canonical schema → leakage-safe analytical dataset → interpretable candidate discovery → statistical validation → finding report → policy candidate.

The repository currently implements the platform foundation, metadata APIs, persistence,
migrations, frontend shell, synthetic fixture, a 10,000-row hidden-ground-truth benchmark, the
versioned leakage-safe synthetic analytical dataset `travel-bookings-analytical-v1.0.0`, and its
outcome contract. It does not yet implement discovery, validation application, or the production
analytical pipeline. Customer-data ingestion and the production canonicalization pipeline remain
unimplemented.

## Explicit non-goals

- CRM integration
- autonomous policy enforcement
- agent runtime/governance platform
- universal business graph
- enterprise SSO, billing, or multi-tenancy in the bootstrap
- production causal claims
- distributed infrastructure without demonstrated need

## Current blocker

No immutable ingestion contract or canonical travel-booking mapping exists. Real customer data must not be accepted until security, storage, validation, and deletion boundaries are defined.

## Next milestone

Close the hidden-ground-truth synthetic benchmark (`TASK-003`) against its one remaining required
artifact change (per-pattern true effect sizes, `HANDOFF-010` item 1) and approve the immutable
ingestion contract (`TASK-005`). The evidence contract (`TASK-018`) and outcome contract
(`TASK-013`) are both done. The next hard dependency is on ML Discovery: a discovery run manifest
recording the evaluated search space and immutable candidate persistence (`HANDOFF-011`). Without
it, no finding this system produces can exceed `descriptive_observation`, regardless of how the
outcome or evidence contracts are applied.

Running in parallel, tracked as an equally urgent `P0`: `TASK-057`, securing the first real pilot
customer (see `ADR-010`). This is not sequenced after the synthetic-benchmark/engine work above —
it has no code dependency on it — and is the actual gate on `TASK-037` and `MILESTONE-M3`. Neither
track should be deprioritized in favor of the other.

## Success criterion

The later pilot succeeds only if at least one validated finding is new, economically material, and actionable to the customer. The immediate milestone succeeds when a synthetic upload can be transformed reproducibly with complete data-quality and time-availability reporting.

## Kill signal

Across multiple suitable datasets, the system repeatedly produces only obvious, unstable, economically immaterial, or non-actionable relationships.
