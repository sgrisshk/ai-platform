# Current Project State

**Last updated:** 2026-08-17

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
On 2026-08-16 the human coordinator reported the final digest passed the same rehearsal; HANDOFF-041
is resolved. `task-015-official-20260815-014` is issued and `VERIFIED` with signed model
`openai/gpt-oss-120b`; TASK-015 now awaits fresh actor execution and output acceptance.
`HANDOFF-042` supersedes that provider launch path. The official actor is now deterministic,
networkless, and has a hard provider ceiling of zero requests, tokens, and cost. It consumes the
signed manifest contract directly and no longer depends on an unissued dataset `manifest.json` or
a hard-coded v1.0.0 outcome contract. Image
`policy-blind-agent@sha256:5632ca11139272623e95a82a9fa24c52f19c16d8edc236dfa500e02cbc9570c0`
passed truth-free production-isolated rehearsal and normal freeze validation on 2026-08-16.
Provider run `…-014` is audit-only after source/runtime drift. A genuinely blind-compliant run,
`task-015-official-20260816-015`, was then issued/launched/frozen end to end (agent
`deterministic`, null model): `status=PERSISTED`, 15 candidates from 6,945 evaluated hypotheses.
Committed (`scripts/commit_blind_candidates.py`, signed receipt) before evaluation opened
`hidden_ground_truth.json`; commitment verified, `ground_truth_pattern_count=9`. Precision/recall/
direction/impact-error scoring is `TASK-028` (still `BLOCKED`), not computed here. Frozen artifacts
archived in `artifacts/blind/task-015-official-20260816-015.*`. TASK-015 is `DONE`.
The earlier full-checkout artifact was graded once as a dry run under contract v1.0.0 (all 15
DOWNGRADE, none PASS) purely to exercise the validation machinery; that frozen result
(`artifacts/validation/task-019-validation-report.json`) is untouched and historical. The G05
multiple-comparison defect found during that dry run (`ADR-014`) was fixed the same day: contract
**v1.1.0** (`ADR-015`) replaces G05's p-value source with a normal approximation on the bootstrap
standard error, proven mathematically sufficient and covered by synthetic-only regression tests.

**The full chain then closed for real, end to end, on 2026-08-16:** `task-015-official-20260816-015`
(genuinely `TASK-017`-compliant, committed via signed receipt before ground truth was opened) was
validated under contract v1.1.0 (`TASK-019`, now `DONE`) — **6 of 15 candidates PASS at
`adjusted_observational_association`/`SHADOW_POLICY`; 9 DOWNGRADE; none REJECT — the first genuine
positive result in the project.** `TASK-003` closed (`HANDOFF-030` accepted, independently
re-verified). `TASK-020`/`TASK-021`/`TASK-022`/`TASK-023` are all `DONE` (produced by the same
validation engine, not separate implementations). `TASK-028` (`scripts/evaluate_benchmark.py`)
scored the run against `hidden_ground_truth.json`, opened only after both discovery and validation
were already frozen: Top-10 precision 90%, economic-weighted recall 45.2% (only P01/P06 of 7
scoreable patterns recovered), 0/5 confounding traps promoted (though never proposed as
candidates either — a weaker claim than active rejection, see `TASK-022`), 0 leakage violations,
100% effect-direction accuracy, and **median economic impact estimation error 204%** — diagnosed
cause: validated candidates' exposed populations are ~15–16× larger than the true patterns they
partially recover (`docs/benchmark/task-029-benchmark-report-v1.md` §3.6). `TASK-029`'s report is
frozen; `docs/benchmark/decision-gate.md`'s "Post-benchmark comparison" is filled in.

**Overall decision-gate verdict: FAILED** (driven entirely by the impact-error metric; no hard
disqualifier fired — `ADR-019`). Per the gate's own action table, real customer data does not
proceed on this result. Statistics attributes the failure to a fixable economic-impact-granularity
defect, not a limitation of the discovery mechanism itself (direction and precision are both
strong) — `HANDOFF-043` requests ML_DISCOVERY/FOUNDER_STRATEGY concurrence before a remediation
rerun is authorized.

**`TASK-016` (candidate ranking v0) landed the same day (2026-08-16, ML Discovery, ADR-020):** a
pure, deterministic ranker (`packages/analytics/src/policy_analytics/discovery/ranking.py`) scores
economic impact, support, temporal stability, actionability, and novelty — not search importance
alone, per the task's own goal text — with weights that are v0 defaults from generic business
reasoning, not tuned against results or hidden ground truth. Actionability logic was factored out
of `discovery.engine` into a shared `discovery.actionability` module so the two never diverge. Ran
for real against all 15 `task-015-official-20260816-015` candidates
(`artifacts/discovery/task-016-candidate-ranking-task-015-official-20260816-015.json`);
methodology in `docs/analytics/candidate-ranking-v0.md`. `TASK-016` is `DONE`. `TASK-017`'s two
listed dependencies (`TASK-003`, `TASK-016`) are both now satisfied; its closure is an
Architect/Code-Reviewer wiring confirmation, requested in `HANDOFF-045` along with a
Product/Statistics review of the v0 ranking weights.

**`HANDOFF-025` (economic-impact result contract for `TASK-024`) resolved 2026-08-17 (`ADR-021`):**
`packages/analytics/src/policy_analytics/validation/economic_impact.py`
(`EconomicImpactResult`/`build_economic_impact_result`, `ECONOMIC_IMPACT_CONTRACT_VERSION =
"1.0.0"`), wired into gate G15 in `validation/apply.py`, replaces Architect's stopgap hand-mapping
of `EconomicImpactPersistence` with the real, tested computation
(`docs/analytics/economic-impact-contract.md`; `tests/analytics/test_economic_impact.py`, 7 tests;
177 tests total pass). `affected_records` is the full combined-window exposure (development +
validation + future_holdout), not `exposed_records` (development-only, used for grading) —
correcting a wrong assumption in `docs/product/finding-product-contract.md` that treated the two as
the same population, flagged back to Product as `HANDOFF-046` (not blocking — a documentation
correction, not an implementation dependency). Annualization remains hard-gated off
(`annualization_justified=False`, always) pending a stability check not yet implemented. `TASK-024`
is now `READY` (Architect, 2026-08-17) — implementation not yet started. The `v1.0.0` dry-run
artifact is untouched; the closing-run official artifact
(`artifacts/validation/task-019-official-20260816-015.json`) *was* subsequently regenerated with
`--force` (Architect, same day) so `TASK-024` has a real `economic_impact` field — verdicts and
point estimates identical, only bootstrap CI bounds/p-value shifted (see `HANDOFF-047`, a newly
found Statistics-owned reproducibility gap in `apply.py`'s cluster bootstrap, not fixed here).
`artifacts/evaluation/task-028-benchmark-evaluation.json` was regenerated in lockstep for
consistency with its changed input; every metric held except the already-diagnostic-only
impact-error median.
**`HANDOFF-043` (ML_DISCOVERY/FOUNDER_STRATEGY concurrence on the FAILED-verdict attribution)
remains OPEN and untouched — no remediation scope has been started pending that answer.**

**Ingestion pipeline landed the same day, independently of the above result (2026-08-16, Data
Engineer + Architect):** `TASK-005`/`TASK-006` are `DONE`. `docs/architecture/ingestion-contract.md`
fixes the contract; `POST /api/v1/datasets` now takes a real multipart upload, validates
size/extension/content/encoding, content-addresses and immutably persists raw bytes
(`app/ingestion/`), and enforces `name`+`version` identity with duplicate rejection. Verified
against a real ephemeral PostgreSQL instance, not just unit-level: 163 tests pass, `ruff`/`pyright`
clean. `TASK-007` (schema profiler) is unblocked. This does not touch or lift the `TASK-038`
real-data block below — that remains gated on the decision-gate `FAILED` verdict and
`TASK-057`/`TASK-037` regardless of ingestion readiness.

## Current hypothesis

Historical decision/outcome data may contain actionable interaction patterns the business does not currently recognize. This remains a hypothesis, not a validated finding.

## Current product scope

CSV/Excel export → immutable ingestion → data quality and canonical schema → leakage-safe analytical dataset → interpretable candidate discovery → statistical validation → finding report → policy candidate.

The repository currently implements the platform foundation, metadata APIs, persistence,
migrations, frontend shell, synthetic fixture, a 10,000-row hidden-ground-truth benchmark, the
versioned leakage-safe synthetic analytical dataset `travel-bookings-analytical-v1.0.0` using
canonical schema `travel-booking-canonical-v1.0.0`, and its outcome contract. It does not yet
implement discovery, validation application, or the production
analytical pipeline. Raw customer-data ingestion (`TASK-005`/`TASK-006`) is implemented; schema
profiling, feature-timing classification, the data-quality report, and the production
canonicalization pipeline (`TASK-007` onward) remain unimplemented.

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

The immutable ingestion contract now exists and is implemented (`TASK-005`/`TASK-006`, `DONE`), but
no canonical travel-booking mapping (`TASK-010`) or customer-facing Data Quality Report (`TASK-009`)
exists yet. Real customer data must additionally clear `TASK-057` (secured pilot customer),
`TASK-037` (adversarial security review of this ingestion path), and the current decision-gate
`FAILED` verdict (`HANDOFF-043`) before it is accepted — deletion boundaries (`TASK-055`) also
remain undefined.

## Next milestone

**14-day window (2026-08-14 → 2026-08-28), two tracked milestones, set by Founder Strategy 2026-08-14:**

- **Technical milestone — first compliant blind benchmark result. ACHIEVED 2026-08-16 (day 3 of
  14).** `task-015-official-20260816-015` validated under contract v1.1.0, scored end to end
  through `TASK-020`→`TASK-023`→`TASK-028`→`TASK-029`, graded against
  `docs/benchmark/decision-gate.md`: **overall verdict FAILED** (driven by economic impact
  estimation error alone, median 204%; no hard disqualifier fired — 90% Top-10 precision, 100%
  direction accuracy, 0 leakage, 0/5 traps promoted). Per the milestone's own success condition
  ("a graded verdict exists, whatever it is — a FAILED verdict honestly reported still meets this
  milestone"), **this milestone is met.** Full detail: `docs/benchmark/task-029-benchmark-report-v1.md`,
  `ADR-019`. Open follow-up: `HANDOFF-043` (ML_DISCOVERY/FOUNDER_STRATEGY concurrence on Statistics'
  fixable-defect attribution, before any remediation rerun).
- **Commercial milestone — first documented customer/data-sharing conversation.** Still pending;
  unaffected by the technical result above. At least one real, logged serious conversation in
  `docs/customer/pipeline.md` (per its existing bar: `CALL SCHEDULED`/`CALL DONE` or an equivalent
  real exchange about actual data), from the 7-day acquisition sprint (`ADR-017`,
  `docs/customer/acquisition-sprint-7day.md`) and its continuation through day 14. Owner:
  FOUNDER_STRATEGY (sends/authorizes outreach), CUSTOMER_DISCOVERY (sources, drafts, logs).

**14-day go/no-go — technical half now resolved as FAILED without a hard disqualifier:**
- Per the pre-registered logic: *"Conversation secured but mechanism grades WEAK/FAILED → do not
  accelerate toward `TASK-038` real-data ingestion on the strength of enthusiasm alone; the
  decision-gate still governs that decision regardless of commercial progress."* **This is the
  applicable branch now, regardless of how the commercial milestone resolves.** Real customer data
  ingestion does not proceed until a remediation run re-grades at STRONG or PROMISING.
- The **escalate** branch ("technical FAILED with a hard disqualifier → trigger core-discovery-
  approach review") does **not** apply — no hard disqualifier fired. This is a single diagnosed,
  plausibly fixable failure, not (yet) grounds for the two-strikes core-approach review.
- The commercial-track go/no-go logic (GO / adjust-if-one-lands / escalate-on-zero-conversations)
  is unaffected by the technical result and still applies on its own terms through day 14.

See `30_DAY_VALIDATION_PLAN` framing in `docs/strategy/30-day-validation-plan.md`.

## Success criterion

The later pilot succeeds only if at least one validated finding is new, economically material, and actionable to the customer. The immediate milestone succeeds when a synthetic upload can be transformed reproducibly with complete data-quality and time-availability reporting.

## Kill signal

Across multiple suitable datasets, the system repeatedly produces only obvious, unstable, economically immaterial, or non-actionable relationships.
