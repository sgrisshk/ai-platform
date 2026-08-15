# Current Project State

**Last updated:** 2026-08-13

## Current objective

Build the trustworthy ingestion and evidence contracts required to test whether historical travel-booking decisions contain previously unknown, economically material, actionable patterns.

## Current customer context

Initial use case: travel agency pilot. No real customer dataset is stored in this repository, and no customer dataset has yet been profiled by the implemented pipeline. Customer Discovery confirmed (2026-08-13, see the Founder Strategy → Customer Discovery `HANDOFF-007` resolution in `memory/HANDOFFS.md`) that no real customer agreement, real dataset commitment, or customer interview is recorded anywhere in this repository — `DECISIONS.md` contains no such decision. Securing the first real pilot customer has not started and is currently the actual bottleneck ahead of `TASK-037`/`MILESTONE-M3`, independent of the ingestion-contract blocker below. `TASK-042` (customer findings review) stays correctly `BLOCKED`; its review protocol was prepared in advance in `docs/customer/findings-review-protocol.md`.

## Current stage

Repository bootstrap is complete. The validation and evidence contract (ADR-007,
`docs/analytics/validation-contract.md`) and the outcome definition contract, now v1.1.0
(`docs/analytics/outcome-contract.md`, closing `TASK-013`, ADR-009/ADR-011), are both preregistered: together
they fix how any future candidate will be graded and what "harm" means on the benchmark. Primary
outcome is `contribution_margin_eur` (EUR/booking, decrease = harm, verified 0% missing);
`repeat_purchase_180d` is MNAR-bounded exploratory only. v1.1.0 added a machine-readable
discovery-time statistical contract (search-split rule, support floor, excluded-feature list,
missing-outcome handling) without reopening the primary-outcome decision. The synthetic benchmark
was reviewed by Statistics and approved in substance. Its last required artifact change is now
implemented: private per-pattern true-effect records include configured and realized effect,
direction, support, economic impact, validity interval, outcome, and units; final acceptance is
pending Statistics review in `HANDOFF-030` (the customer-identifier item is also delivered). The blind-discovery access and
commitment boundary is implemented under ADR-008: Discovery receives only an allowlisted analytical
workspace, and post-hoc evaluation requires an evaluator-signed candidate receipt
(`docs/benchmark/blind-benchmark-protocol.md`). The local runner adds an external run root, manifest,
provenance and audit records, strict verification, fresh container launch, output schemas, state
transitions, and result freezing (`blind/README.md`). One command rebuilds the public artifact, which contains only
the approved analytical partitions and sanitized public metadata, with no private source or
evaluation artifacts. The blind runner infrastructure is technically ready, but no reusable
verified run currently exists. The runner now uses a minimal Groq tool-calling actor and immutable image
`policy-blind-agent@sha256:0d64b3acd49008577216fd79e14c9c242e6c99b52712931ee7ef2392ecae98a2`;
issuance signs the runtime agent and explicit Groq model alongside output schema v1.1.0.
Run `task-015-official-20260814-006` used the superseded Codex runtime;
manifest SHA-256 is `f2981fbc8ff55ba31ba4f4124d3a7bab38d0c844b0024832bdc1e024700d6a10`.
Source drift and runtime substitution now fail closed, and freeze enforces the signed acceptance
contract. The evaluator key remains external and is not mounted or passed to Discovery. Run
`…-002` is unchanged audit-only evidence; `…-003`/`…-004` are failed issuance attempts. Discovery
did not execute: `…-006` attempted provider launch without usable bearer authentication, received
HTTP 401, and is now irreversibly `FAILED`. TASK-015 remains `BLOCKED` pending successful official
execution and freeze. `HANDOFF-036`, `HANDOFF-037`, and `HANDOFF-038` are resolved: exposed
historical credentials were revoked, and the secret-safe pinned-container Groq preflight passed
with `openai/gpt-oss-120b` and a
required function tool call. Runs `…-007` and `…-008` also
failed with HTTP 401 before Discovery work. Presence-
only credential checks are no longer sufficient. The Groq `blind-provider-preflight` performs
an authenticated model request in the pinned container without mounting a workspace; no new
official run is issued until it succeeds. Failed runs cannot be retried. Run `…-005` failed before agent execution
because its launcher used a removed Codex CLI flag; the replacement Groq actor uses explicit
read/list/Python tools. The replacement actor is no longer Aider: it mounts public
inputs read-only, mounts only `output/` writable, and permits exactly the three required artifact
names. Freeze acceptance failures now atomically close `RUNNING`/`COMPLETED` runs as `FAILED`.
Run `task-015-official-20260814-011` failed before discovery on the account's 8,000 TPM limit and
is irreversibly `FAILED` with no outputs. `HANDOFF-039` is resolved on the repinned image: requests
have bounded completion/context/tool outputs and capped 429 retries. Official `…-012` later failed
on a GPT-OSS paginated read rejected by the old schema and is irreversibly `FAILED` with no
outputs. `HANDOFF-040` is resolved: bounded 1-based inclusive pagination and an authenticated
two-page preflight passed. Official `…-013` then failed without outputs after GPT-OSS requested an
undeclared `search(path, query)`. `HANDOFF-041` is now resolved on the repinned image: bounded
literal search and capped `tool_use_failed` recovery are implemented, and a full authenticated
production-isolated rehearsal with `openai/gpt-oss-120b` passed listing, paginated reads, search,
Python execution, controlled recovery, and validation of exactly three schema-v1.1.0 dummy
outputs on intermediate digest `5503b6d0…`. The final type-safe digest is `0d64b3ac…`; two
authenticated repetitions failed closed before completion on Groq's 200,000 TPD quota. No official
`…-014` was issued. HANDOFF-041 and TASK-015 issuance remain blocked until the final digest passes
the same rehearsal after quota replenishment.
The earlier persisted artifact
(15 candidates, 6,945 evaluated hypotheses, fit on `development` only) came from a full-checkout
run that does not satisfy ADR-008. Statistics ran the full
`TASK-018` validation contract against that artifact anyway, as a dry run of the validation
machinery (`TASK-019`, `IN_PROGRESS`, not `DONE`): **all 15 candidates DOWNGRADE to
`LEVEL_1_DESCRIPTIVE`**, none PASS. At dry-run time this reflected three independent issues rather
than weak candidates: the now-resolved issuance gap, the still-unexecuted fresh blind run, and a
defect in the validation contract's own multiple-comparison gate (`ADR-014`: its bootstrap
p-value floor could not pass BH correction at this system's typical family sizes regardless of
true effect size). **That defect is now fixed:** validation contract **v1.1.0** (`ADR-015`)
replaces G05's p-value source with a normal approximation on the bootstrap standard error, proven
mathematically sufficient and covered by synthetic-only regression tests
(`tests/analytics/test_g05_multiplicity_fix.py`); the frozen v1.0.0 dry-run artifact was left
untouched and the CLI now refuses to overwrite a frozen result without `--force`. No candidate was
handed to Architect/Product as a validated finding, and the fix alone does not change that — a
genuinely blind `TASK-015`/`TASK-017` artifact is still required before `TASK-019` can close.
Tooling is now checked and ready for that artifact specifically (`ADR-018`): the blind-agent
output schema (`tools/blind_agent/models.py`) differs from what the dry run used, and the
validation engine/CLI now handle both shapes and require explicit blind-compliance flags rather
than inferring them. The remaining gap is entirely on the `TASK-015` execution side
(`HANDOFF-036`/`HANDOFF-037`). Ingestion-contract design is the next data-pipeline boundary for
real customer data.

## Current hypothesis

Historical decision/outcome data may contain actionable interaction patterns the business does not currently recognize. This remains a hypothesis, not a validated finding.

## Current product scope

CSV/Excel export → immutable ingestion → data quality and canonical schema → leakage-safe analytical dataset → interpretable candidate discovery → statistical validation → finding report → policy candidate.

The repository currently implements the platform foundation, metadata APIs, persistence,
migrations, frontend shell, synthetic fixture, a 10,000-row hidden-ground-truth benchmark, the
versioned leakage-safe synthetic analytical dataset `travel-bookings-analytical-v1.0.0` using
canonical schema `travel-booking-canonical-v1.0.0`, and its outcome contract. It does not yet
implement discovery, validation application, or the production
analytical pipeline. Customer-data ingestion and the production canonicalization pipeline remain
unimplemented.

TASK-012 adds split contract `travel-bookings-temporal-split-v1.0.0`: development is calendar
2024, validation is H1 2025, and future holdout is H2 2025. Search/selection is allowed only on
development; later splits remain diagnostic-only during discovery.

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

**14-day window (2026-08-14 → 2026-08-28), two tracked milestones, set by Founder Strategy 2026-08-14:**

- **Technical milestone — first compliant blind benchmark result.** A genuine blind `TASK-015` rerun (workspace `task-015-official-20260814-002`, already issued and verified, awaiting a launched Discovery actor per `HANDOFF-032`), re-validated under validation contract v1.1.0 (`ADR-015`, G05 fixed), scored through the remaining `TASK-020`→`TASK-023`→`TASK-028`→`TASK-029` chain, and graded against `docs/benchmark/decision-gate.md`'s STRONG/PROMISING/WEAK/FAILED bands. Success condition: a graded verdict exists, whatever it is — a FAILED verdict honestly reported still meets this milestone; a verdict that doesn't exist by day 14 does not. Owner: ML_DISCOVERY (execute `HANDOFF-032`), STATISTICS (run `TASK-020`–`TASK-023`, `TASK-028`–`TASK-029` under v1.1.0), ARCHITECT (coordinator support). Risk: this is a long chain even with both major blockers (workspace issuance, G05 defect) already cleared — an aggressive but not certain 14-day timeline.
- **Commercial milestone — first documented customer/data-sharing conversation.** At least one real, logged serious conversation in `docs/customer/pipeline.md` (per its existing bar: `CALL SCHEDULED`/`CALL DONE` or an equivalent real exchange about actual data), from the 7-day acquisition sprint (`ADR-017`, `docs/customer/acquisition-sprint-7day.md`) and its continuation through day 14. Owner: FOUNDER_STRATEGY (sends/authorizes outreach), CUSTOMER_DISCOVERY (sources, drafts, logs).

**14-day go/no-go:**
- **GO (continue unchanged):** technical milestone grades PROMISING or STRONG, and ≥1 real serious conversation logged.
- **Adjust, don't kill, if exactly one lands:** mechanism grades PROMISING/STRONG but zero conversations after a real 14-day founder-executed effort → GTM/channel/positioning problem, not a thesis problem; revisit outreach approach before touching `ADR-016`'s travel-only scope. Conversation secured but mechanism grades WEAK/FAILED → do not accelerate toward `TASK-038` real-data ingestion on the strength of enthusiasm alone; the `docs/benchmark/decision-gate.md` gate still governs that decision regardless of commercial progress.
- **Escalate:** technical FAILED with a hard disqualifier (leakage or promoted confounding trap) → trigger the core-discovery-approach review process already defined in `docs/benchmark/decision-gate.md`. Zero real conversations despite a genuinely executed 14-day effort (not just an unauthenticated channel) → this stops being a tooling excuse and becomes a real ICP/positioning signal; reopen `ADR-016` at that point, not before.

Both milestones proceed in parallel — neither is sequenced after the other; see `30_DAY_VALIDATION_PLAN` framing in `docs/strategy/30-day-validation-plan.md`.

## Success criterion

The later pilot succeeds only if at least one validated finding is new, economically material, and actionable to the customer. The immediate milestone succeeds when a synthetic upload can be transformed reproducibly with complete data-quality and time-availability reporting.

## Kill signal

Across multiple suitable datasets, the system repeatedly produces only obvious, unstable, economically immaterial, or non-actionable relationships.
