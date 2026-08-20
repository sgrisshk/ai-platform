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
`policy-blind-agent@sha256:9ad6e1a78ca41a7c04895d1d99c7775e77fc2c8fbb4f23cee268ed04534c7c9b`
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
strong) — `HANDOFF-043` requested ML_DISCOVERY/FOUNDER_STRATEGY concurrence before a remediation
rerun is authorized; see the `HANDOFF-043` update below for ML Discovery's answer.

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
**`TASK-024`/`TASK-025` (real Finding persistence + API) `DONE` 2026-08-17 (Architect).** Migration
`20260817_0003`; `app/findings/persistence.py` (candidate/report/promotion services, enforcing
"no evidence_level → cannot promote"); `app/findings/summary.py` (product contract §12.2's exact
mechanical title/summary template). `scripts/promote_findings.py` ran the real closing-run
artifacts through the full pipeline against a live ephemeral Postgres: 1 `AnalysisRun`, 15
`CandidatePattern`/`ValidationReport` rows, and — per `docs/product/finding-product-contract.md`
§0, "a Finding is any graded candidate output," not only a `PASS`-verdict one — **all 15**
candidates promoted to `Finding` (none `REJECT`): 6 at `adjusted_observational_association`/
`shadow_policy`, 9 at `descriptive_observation`/`experiment_only`. (A draft of this work initially
assumed only the 6 `PASS` candidates should promote and wrote a test expecting exactly that; the
real run caught the wrong assumption, and the test was corrected, not the code.)
`GET /api/v1/findings`/`GET /api/v1/findings/{id}` serve this real data — verified live via
`uvicorn`+`curl`, not just `TestClient` — matching product contract §1's exact required field list
(nothing from §2 "Optional later"), `affected_records` for money-at-stake per `HANDOFF-046`'s
recommendation, and `materiality_pass` shown without its threshold (§3).
**`TASK-026`/`TASK-027` (findings list + detail screens) `DONE` 2026-08-17 (Architect).** Both
UX specs (`docs/product/findings-list-screen.md`/`finding-detail-screen.md`) implemented as
written, extending the existing "Signal Foundry" design system rather than introducing a new one.
Shared `EvidencePill`/`ReadinessPill` components (`apps/web/lib/copy/findingLanguage.ts` as the
single wording source) keep both screens' vocabulary identical, per both specs' explicit
requirement. Sort/filter/pagination resolved server-side from URL search params, no new backend
surface. New `apps/web/lib/api/analysisRuns.ts` (`getAnalysisRun`) added for the detail screen's
provenance strip — the only backend-adjacent addition, wrapping an already-existing route.
Verified live against real data (ephemeral Postgres + `scripts/promote_findings.py` + `uvicorn` +
`pnpm dev`, not just component tests): all 15 real findings render, a `?sort=readiness&
readiness=shadow_policy` filter correctly narrows to the real 6, and a real
`descriptive_observation`-level finding correctly still shows its `adjusted_effect` (consistent
with the TASK-024 finding that adjustment is computed independently of which gate capped the
evidence ceiling). One documented, not fabricated, gap: the "near G03 power floor" small-sample
qualifier both specs call for cannot be built — `FindingRead` doesn't expose the needed MDE/power
diagnostic, and inventing a threshold client-side would violate `ADR-004`. `TASK-035` (finding
feedback model) is now unblocked (`TASK-027`'s detail screen already reserves its UI slot) but
not started — real persistence needs `TASK-053` (auth) first.
**`TASK-053` (basic authentication) and `TASK-035` (finding feedback) `DONE` 2026-08-18
(Architect, `ADR-027`).** Real internal-staff login (bcrypt, DB-backed opaque session cookie, no
JWT, no self-serve signup — `scripts/create_user.py` only) and a real append-only feedback record
attached to it, replacing `TASK-027`'s disabled chip-row placeholder with a working form
(`FeedbackForm.tsx`: novelty/actionability toggles, tag checkboxes, a comment box required exactly
when `WRONG` is set, an optional-field disclosure, a login prompt when anonymous, and a rendered
history). **Protected surface is deliberately narrow**: only the feedback-write endpoint requires
auth — every other route, including dataset upload, stays open by design, not oversight;
`SECURITY.md` updated to say so explicitly. Login rate-limiting/bot protection are not
implemented (real, tracked gap, not silently skipped). Verified against a real ephemeral Postgres
(349 backend + 46 frontend tests, twice each) and a real end-to-end run: a user created via the
CLI, logged in through the real `/login` page, submitted `WRONG`+comment feedback on one of the 15
real closing-run findings, confirmed it persisted and the finding's own `evidence_level`/
`policy_readiness` were unchanged, confirmed logout actually 401s a subsequent request. `TASK-036`
(customer review workflow — Product's UX spec already complete,
`docs/product/customer-review-workflow.md`) is now `READY`, not `BLOCKED`: both blockers it named
are `DONE`, but its own scope (the dedicated one-at-a-time review queue) is separate, un-started
work, not delivered by this pass.

**Fixed 2026-08-18 (Architect): `scripts/promote_findings.py` was hardcoded to the superseded
`task-015-official-20260816-015` run (`ADR-019`, graded FAILED overall) instead of the current
PROMISING-verdict `task-058-remediation-20260817-001` (`ADR-025`)** — any database seeded from its
default held findings from the wrong-era run. Parametrized like `evaluate_benchmark.py`/
`rank_candidates.py`; the remediation run's missing `TASK-016` ranking artifact was generated for
real. Re-verified end to end against a live database: 15/15 promote, 6 `shadow_policy`/9
`experiment_only` as expected. See `TASK-024`'s evidence for the exact numbers.

**`TASK-030` (Policy Candidate domain model) `DONE` 2026-08-18 (Architect, `ADR-029`, resolves
`HANDOFF-049`).** `policy_candidates` extended to the real shape
`docs/product/policy-candidate-domain-model.md` §0–§12 defines (migration `20260818_0007`,
drop/recreate — table confirmed empty). §6's block/auto-retire-on-Finding-lifecycle-change rule is
a service-layer check (`app.policies.service.cascade_finding_lifecycle_change`), not a DB trigger —
**a real, disclosed gap: nothing in this codebase yet transitions a Finding's `lifecycle_status`
away from `ACTIVE`**, so this function isn't wired to any live trigger point today, only built and
verified directly. §3's confounder-scope guardrail (a real gap Statistics' own `HANDOFF-049`
resolution flagged) is closed one task early via a new `scope_narrowing_features` field. `mode` is
contract-locked to `SHADOW` (§1's "unreachable today" is now an enforced invariant). No new API
routes — internal persistence only, matching `app.findings.persistence`'s own precedent. Verified:
13 new integration tests against a real ephemeral Postgres, plus a live run against one of the 15
real closing-run Findings — created, transitioned all the way to `APPROVED_SHADOW`, then the source
Finding was manually superseded and the cascade correctly auto-retired it. Full suite (375 tests)
green twice against a live database. `TASK-031` (the generator — not built here) is now `READY`.

**`TASK-031` (Policy Candidate generator) `DONE` 2026-08-18 (Architect).** Implements
`docs/product/policy-candidate-domain-model.md` §12 exactly, as
`scripts/generate_policy_candidates.py` over a tested orchestration function
(`apps/api/app/policies/generation.py`) — delegates every rule (eligibility, the §3 guardrail,
idempotency) to `create_draft_policy_candidate` (`TASK-030`), adding none of its own. Batch (every
`ACTIVE` Finding) or `--finding-id`; `--force` only alongside `--finding-id`, never in batch mode
(§12: "never automatic proliferation"). `title`/`rationale` reuse the Finding's own mechanical
`title`/`summary` verbatim. Verified against a real ephemeral Postgres (6 new tests) and live,
non-test runs against the 15 real closing-run Findings: 6 created (the `shadow_policy` ones), 9
correctly skipped with the real reason; a rerun was a clean no-op. Full suite (381 tests) green
twice on a fresh database. `MILESTONE-M2` (policy discovery demo) now only needs `TASK-034` (the
backtest UI, `READY`, not started) to close.

**`TASK-034` (policy backtest UI) `DONE` 2026-08-19 (Architect, `ADR-033`).** Two real gaps closed:
nothing computed/persisted a backtest *run* yet (only the pure engine existed), and no screen
anywhere reached a Policy Candidate (`TASK-030`/`031` had no routes/UI) — per explicit user
direction, a minimal Policy Candidate detail screen was built alongside the backtest screen, not
worked around. `PolicyBacktestRunModel` reuses `ResourceStatus` exactly as `HANDOFF-050`
recommended, computed synchronously inside the request (no async/worker infrastructure exists
anywhere in this codebase). First public routes for `app.policies` — no auth, matching `ADR-027`'s
narrow protected surface. **Built against `apps/web`'s new static-export architecture (`ADR-032`,
landed the same day)** — both screens are flat `?id=`-reading routes under `Suspense`, Client
Components fetching in `useEffect`, mirroring `findings/detail`'s established pattern, not the
server-component pattern this repo used before that day. Verified: a live backtest trigger matched
byte-for-byte against a direct, independent `run_backtest()` call
(`affected_decisions=570`/`avoided_bad_outcomes=108`/`suppressed_good_outcomes=462`); 19 new
backend + 9 new frontend tests; `next build` producing both new static routes cleanly; full suite
(391 backend, 55 frontend) green twice. `MILESTONE-M2` is `READY` — "create a policy candidate" is
real but script-mediated (§12's own design), not yet a UI button, so whether that satisfies the
milestone's literal success criterion is a Product call, not made here. `TASK-036` (customer review
workflow) was deliberately not bundled into this pass.

**`TASK-036` (customer review workflow) `DONE` 2026-08-19 (Architect, `ADR-034`).** A queue
sequencing the already-real `FindingFeedback` API (`TASK-035`) — never a duplicate of it;
`FeedbackForm.tsx` on the finding detail page is unchanged. `FindingCoreContent.tsx` extracted
from `FindingDetailView.tsx` so both views render the literal same finding content, not two copies
that can drift. New `ReviewQueueForm.tsx` (Save-and-next/Skip/Back over the same field set/
`WRONG ⇒ comment` rule as `FeedbackForm`), session-scoped `localStorage` resume (no backend
`review_session` object — explicitly out of scope), real `captured_by` attribution via `TASK-053`
auth. **A real bug was caught and fixed before shipping**: the first draft re-filtered the visible
queue reactively as progress updated, which shifted the array under the current index and silently
skipped the next finding on every advance — fixed by freezing the filter against a session-start
snapshot. Known, disclosed simplification: no mid-session supersede detection (no polling
infrastructure exists anywhere in this codebase). Verified: 12 new frontend tests (63 total)
including a full simulated session and a resume-with-prior-progress case; `next build` clean; a
live `uvicorn`/`pnpm dev` pair confirming the real login → list findings → submit feedback path.

**`TASK-007` (schema profiler) `DONE` 2026-08-17 (Architect).** New `dataset_column_profiles`
table (migration `20260817_0004`), deliberately separate from `DatasetColumn`/`DatasetModel.columns`
(that stays `TASK-008`'s eventual feature-timing output). Pure, deterministic, no-ML majority-vote
type inference (`packages/analytics/.../profiling/schema_profiler.py`, `ADR-004`); "semantic type"
and "safe examples" are explicit disclosed heuristics, not validated facts or a real PII detector.
Runs synchronously on upload; a profiling failure logs and leaves the dataset unprofiled rather
than failing the already-immutable upload. **Real bug caught by live verification, not unit
tests:** raw-substring name-hint matching misclassified `trip_duration` as `percentage_rate`
("duration" contains "ratio") — found by uploading the real
`tests/fixtures/synthetic_travel_bookings.csv` fixture through a live `uvicorn`, fixed with
whole-token matching, regression-tested. Verified against a real ephemeral Postgres: migration
round-trips, full suite green twice (230 passed), and the real 24-column fixture profiles
correctly end to end (e.g. `booking_changes` correctly identified as a real 0-3 integer count, not
the boolean its name suggests). `TASK-008` (feature-timing classification) is now unblocked but
not started — a genuinely separate design task, not folded into this one.
**Second real bug found the same day, by deliberate manual repro, not by trusting the passing
suite:** `_min_max` filtered a numeric column's range with the broader `_matches_float` (also
accepts plain integers) instead of the winning type's own predicate, so a value already flagged as
suspicious could still be reported as the column's own `min_value`/`max_value` — a suspicious
`"999999.5"` outlier in an otherwise-clean 1..99 integer column was silently laundered into
`max_value`. Did not reproduce on the clean synthetic fixture, which is why it needed a deliberate
repro rather than rerunning the existing suite — exactly the messy-real-data risk this task exists
to catch. Fixed (min/max now computed only from type-conforming values) with 2 regression tests;
re-verified against a live ephemeral Postgres (237 passed), `ruff`/`pyright` clean.
**Remediation rerun re-grades the decision gate to PROMISING (2026-08-17, Statistics/Architect,
`ADR-025`), resolving `HANDOFF-048`, closing `TASK-058`/`TASK-059`.** `TASK-019`/`TASK-028` ran for
real against `task-058-remediation-20260817-001` (new files; the original frozen `…-015` artifacts
were not touched). Governing metric — economic impact estimation error — dropped from median 204%
to **37.5%** (FAILED band → PROMISING band); Top-K precision (90%), leakage (0), and direction
accuracy (100%, now 7/7 matched candidates) held or improved; economic-weighted recall unchanged
(45.2%). One disclosed wrinkle: `CAND-014`, a genuine `P06` recovery, also trips the evaluator's
literal `T04` trap-condition check because it contains `payment_method==bank_transfer` — does not
change the graded band, recorded as a `_matches_trap()` precision gap, not smoothed over. **Overall
decision-gate verdict is now PROMISING, up from FAILED (`ADR-019`).** Per `ADR-022`'s own stated
reopening condition, `TASK-057` (customer outreach) is back to `TODO` — the founder's pause was
explicitly conditioned on exactly this re-grade. `TASK-038` (real customer data ingestion) is
**not** unblocked by this alone: `docs/benchmark/decision-gate.md`'s PROMISING action-row wording is
genuinely ambiguous on a first-time FAILED→PROMISING transition, flagged to Founder in `ADR-025`
rather than resolved unilaterally — moot for now since `TASK-038` also still needs `TASK-057`
(reopened today, zero conversations so far) and `TASK-037` (security review).

**`HANDOFF-043` — ML_DISCOVERY answered 2026-08-17: partial concurrence, with a dissent.** Agrees
this is a fixable defect, not a core-approach limitation (single-remediation path, not the
two-strikes trigger). Dissents that the fix is estimation-layer-only: `supplier`/`destination`
were both eligible search features yet zero of the 15 candidates use any categorical condition,
pointing to a search-selection artifact (`discovery.engine`'s beam-survival score maximizes raw
population × effect with no precision term) as a real contributing cause, not only `TASK-021`/
`TASK-023`'s reporting arithmetic. Also flags that Statistics' proposed ground-truth-matched
attribution-narrowing is only computable inside the benchmark harness and cannot generalize to
real customer findings, which have no true pattern to narrow against. Recommended a two-part
remediation: (1) an explicitly benchmark-evaluation-only attribution-narrowed diagnostic for
`TASK-028`'s metric 6, and (2) a small additive precision term at `TASK-015`'s search-selection
layer, so future candidates are inherently tighter, not just differently reported. **Resolved
2026-08-17 (Founder Strategy):** single-remediation path confirmed; both parts authorized, numbered
`TASK-059` (part 1, Statistics) and `TASK-058` (part 2, ML Discovery), both `READY`.

**`TASK-058` implemented same day (2026-08-17, ML Discovery, `ADR-023`):**
`DiscoveryConfig.population_score_exponent` (default `0.5`) changes the beam-survival score from
linear `historical_exposure` to `harm_per_booking × n_exposed^0.5` — sub-linear in population, so a
rule can no longer inflate its score just by absorbing more diluting bookings; `exponent=1.0`
exactly reproduces the old ranking (regression-tested). `DISCOVERY_METHOD_VERSION` is now
`discovery-engine-v0.2.0`. A new official blind run under the existing `ADR-008` protocol,
`task-058-remediation-20260817-001` (`status=PERSISTED`, 15 candidates), was issued, verified,
launched (deterministic, network `none`, no image rebuild needed), frozen, and **committed via
signed receipt before any evaluation opened `hidden_ground_truth.json`**. Public, no-ground-truth
evidence the fix changed candidate composition: 2 candidates now use a categorical condition absent
from every one of the original 15 — `supplier == BlueWing`, `destination == Tokyo AND
payment_method == bank_transfer` — matching pattern identities already disclosed in the frozen
benchmark report. `TASK-058` is `IN_PROGRESS`, not `DONE`: its done condition needs `TASK-019`/
`TASK-028` run against this new artifact to confirm materially narrower exposed populations versus
matched true patterns, handed to Statistics/Architect in `HANDOFF-048`.

**`HANDOFF-047` (cluster-bootstrap reproducibility) and `TASK-059` (attribution-narrowed
diagnostic) landed together the same day (2026-08-17, Statistics, `ADR-024`):**
`cluster_bootstrap_replicates()` now resamples a sorted-key population, not raw dict order, fixing
the gap Architect found (identical point estimates, drifting CIs/p-values across reruns) at its
root — 4 new regression tests prove the pre-fix call shape *did* diverge under dict-reorder and the
fixed one doesn't. `scripts/evaluate_benchmark.py` gains
`economic_impact_estimation_error_attribution_narrowed_diagnostic`, a clearly-labeled
benchmark-evaluation-only sibling of the governing metric 6 (untouched), scaling each candidate's
reported per-record effect by its overlap with the matched pattern's true affected bookings — 4
new unit tests on synthetic fixtures. Dry-run against the frozen run's real inputs (scratch output
only): attribution-narrowed median error 79% vs. the governing 199%, and zero verdict flips when
rerunning validation under the bootstrap fix against the same inputs as the currently-frozen
report. **Neither frozen artifact
(`task-019-official-20260816-015.json`/`task-028-benchmark-evaluation.json`) has been regenerated
yet** — overwriting them was blocked by the session's own permission guard on hard-to-reverse
actions and left for explicit authorization rather than pushed past; `TASK-059` is `IN_PROGRESS`,
not `DONE`, until that happens. This is separate from `HANDOFF-048` (re-running `TASK-019`/
`TASK-028` against the *new* `task-058-remediation-20260817-001` candidate set) — not started.

**Ingestion pipeline landed 2026-08-16→17, independently of the above result (Data Engineer +
Architect):** `TASK-005` through `TASK-009` are now all `DONE` — the full raw-ingestion half of
Phase 2 is complete. `docs/architecture/ingestion-contract.md` fixes the contract; `POST
/api/v1/datasets` takes a real multipart upload, validates size/extension/content/encoding,
content-addresses and immutably persists raw bytes (`app/ingestion/`), and enforces `name`+`version`
identity with duplicate rejection (`TASK-005`/`TASK-006`). Each upload is then profiled column-by-
column (`TASK-007`, `dataset_column_profiles`), classified into `DECISION_TIME`/`POST_DECISION`/
`OUTCOME`/`IDENTIFIER`/`METADATA`/`UNKNOWN` by a deterministic, disclosed rule-based classifier that
defaults unmatched columns to `UNKNOWN`, never silently to `DECISION_TIME` (`TASK-008`,
`FeatureTiming.UNKNOWN` added), and rolled up into a single Data Quality Report with a disclosed
`READY`/`READY_WITH_LIMITATIONS`/`NOT_READY` rating (`TASK-009`, `datasets.quality_report`). The
feature-timing classifier was checked against the real benchmark's public
`feature_timing.json` (32/32 exact match) plus an independent, stronger safety test that no
non-decision-time column is ever misclassified `DECISION_TIME`, regardless of exact bucket. All of
`TASK-005`–`TASK-009` verified against a real ephemeral PostgreSQL instance, not just unit-level:
299 tests pass, `ruff`/`pyright` clean, alembic up/down/up round-trips clean. `TASK-010` (canonical
schema) is unblocked but not started — it raises a real design question `TASK-011`'s existing
`travel-booking-canonical-v1.0.0` synthetic-shortcut label doesn't resolve, and no real customer
export exists yet to design a general normalizer against. This does not touch or lift the
`TASK-038` real-data block below — that remains gated on the decision-gate `FAILED` verdict and
`TASK-057`/`TASK-037` regardless of ingestion readiness.

**`TASK-014` (baseline business statistics) `DONE` 2026-08-17 (Statistics), the first pass over
this task — never picked up before now, run independently of and after `TASK-015` already
completed.** `scripts/baseline_statistics.py` (reuses `load_analytical_frame`/`summarize_group`/
`mnar_bounds`, no new outcome-handling logic), frozen at
`artifacts/baseline/task-014-baseline-statistics.json`
(`docs/analytics/baseline-statistics-v1.md`): confirms `TASK-012`'s split date boundaries hold
exactly (no gap/overlap), reconfirms `TASK-013`'s 0%/9.7% missingness independently across all 7
outcomes, and reports overall feature distributions plus time/segment/supplier/manager trend
against the primary outcome — purely `descriptive_observation`-level, no interval or p-value
attached to anything, no `hidden_ground_truth.json` access. No data-quality flag found. 8 new
tests.

**`TASK-032`/`TASK-033` (policy backtest engine + synthetic validation) `DONE` 2026-08-18
(Statistics, `ADR-028`)** — built ahead of `TASK-031` (persistence/generator), which the engine
does not depend on: it operates directly on a Finding's frozen `pattern.conditions`, same
relationship `TASK-021`/`TASK-023` had to `TASK-024`. `packages/analytics/src/policy_analytics/
backtest/` implements `docs/analytics/validation-contract.md` §9 exactly: `future_holdout`-only
(hard constant), raw/unadjusted `benefit` (an honest disclosed upper bound, not the smaller
adjusted figure), both-sides-always avoided/suppressed counts (enforced in code), never-invented
operational cost. Run for real against the 6 `shadow_policy`-eligible candidates in
`task-019-official-20260817-task-058-remediation-001.json`: all 6 show a measurable positive net
effect in `future_holdout` (`artifacts/backtest/task-032-backtest-task-058-remediation-001.json`).
`TASK-033` (`scripts/validate_backtest_synthetic.py`, run only after methodology was frozen)
isolates engine correctness from `TASK-028`'s already-diagnosed candidate-matching dilution by
backtesting each of the 9 hidden patterns' own true `affected_booking_ids` directly: **9/9 correct
direction, median 31.0% relative error** against an explicitly-approximated true value (disclosed
approximation, not exact — ground truth has no `future_holdout`-only breakdown). Confounding-trap
check confirms the "not causal, unadjusted" disclosure is necessary: every trap shows a nonzero
raw benefit despite a known-zero true direct effect. `HANDOFF-049`/`HANDOFF-050`'s Statistics
halves answered (backtest_result shape confirmed and extended with disclosure fields; the §3
confounder-scope guardrail is *not* enforced inside the engine and must be enforced by `TASK-031`
before a narrowed condition set reaches it — flagged explicitly, not assumed). Full methodology:
`docs/analytics/policy-backtest-contract.md`; validation report:
`docs/benchmark/task-033-backtest-validation-v1.md`. 13 new tests, synthetic fixtures only. **Still
correctly blocked:** wiring `backtest_result` into a real persisted `PolicyCandidate` row is
`TASK-031`'s job, not done here.

**`TASK-060` (diversity-aware selection) reviewed 2026-08-20 (Statistics, `ADR-036`,
`HANDOFF-052`): done condition NOT met, on all three parts — stays `IN_PROGRESS`, iterates.**
Unique true-pattern recovery unchanged (2); Top-10 precision fell 90%→40%; confounding trap **T03**
was promoted (`CAND-012` reached `PASS`/`shadow_policy` despite clearing G06, whose fixed
`manager`/`supplier` adjustment set doesn't cover T03's actual confounders — a real, previously-
latent gap, first triggered now that diversity search explores more of the feature space).
Corrected a `T02`/`T03` mislabeling in `TASK-060`'s own tracking bullet and `HANDOFF-052`.
Explicitly declined to recommend expanding G06's adjustment set to the now-known confounders — would
be exactly the post-hoc, ground-truth-informed tuning `ADR-007` forbids. **Does not affect the
standing PROMISING decision-gate verdict** (`ADR-025`, anchored to `task-058-remediation`, untouched).

**`TASK-060` iterated same day (ML Discovery, `ADR-037`):** `ADR-036` left open whether the
diversity *search* mechanism itself (as opposed to the G06 gap it declined to patch) had a fixable,
generic defect — it does: pure overlap-based marginal gain lets a weak, merely-disjoint rule win a
round purely by being untouched, the standard failure mode of diversity selection without a
relevance floor. Fixed with no reference to `T03`/`acquisition_channel`/any specific feature:
`diversity_discount_weight` default `1.0`→`0.5`; new `min_diversity_relevance_ratio` (default `0.5`)
requires a rule to reach half its own phase's strongest raw score before being considered at all.
`DISCOVERY_METHOD_VERSION` → `v0.3.1`. New official blind run `task-060-iteration-20260820-002`
(`status=PERSISTED`, 15 candidates, committed via signed receipt before any evaluation opened
ground truth) contains **no `acquisition_channel` condition at all** (emergent, not targeted);
distinct categorical pairs land at 4, between the redundant baseline (3) and the trap-contaminated
run (5). One new condition, `customer_type == 'new'`, is flagged for scrutiny (a known `T03`
confounder) without prejudging it. `TASK-019`/`TASK-028` against this run requested in
`HANDOFF-054`, not yet scored. `TASK-060` remains `IN_PROGRESS`.
`TASK-061` (multi-domain benchmark suite) reviewed the same day: domain 1/6 (e-commerce)
independently re-verified — RNG-draw-parity for counterfactual replay confirmed by direct grep (no
`rng.*()` call gated by pattern-active status), leakage/checksum tests re-run and real; engine
mechanics have no defect. **A deeper empirical pass on the 5 traps' actual behavior (not just the
engine) found a real content gap** (`HANDOFF-053`): 4 of 5 traps' declared `confounded_by`
metadata doesn't match their real generative mechanism (raw group-mean check on real 10k-row
output) — two traps' genuine spurious signal actually comes from an undeclared shared pathway
(`discount_pct`), one looks like contamination from an adjacent real pattern rather than
independent confounding, two carry unwired/misattributed variables. Recommended fixing domain 1's
declarations plus an automated live-trap empirical test before domain 2/6 starts, so the gap isn't
silently templated five more times — not blocking, `DATA_ENGINEER`'s call.

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
exists yet. The decision-gate re-grade that used to block real customer data is cleared — the
`TASK-058`/`TASK-059` remediation rerun graded **PROMISING** (`ADR-025`, 2026-08-17) — but real
customer data still requires `TASK-057` (reopened `TODO` today, zero conversations so far),
`TASK-037` (adversarial security review of the ingestion path), and a Founder reading of
`docs/benchmark/decision-gate.md`'s ambiguous PROMISING action-row wording (`ADR-025` consequence
2) before it is accepted — deletion boundaries (`TASK-055`) also remain undefined.

**TASKS.md reconciled 2026-08-17 (Architect)** now that the PROMISING re-grade is real and
recorded: `MILESTONE-M1` marked `DONE` for its stated synthetic-benchmark scope (real-ingestion
canonicalization, `TASK-010`, stays a separate, still-`BLOCKED` piece, explicitly not implied done
by this); `TASK-029`'s own stale `FAILED`-verdict evidence text annotated as superseded rather than
left to silently contradict `ADR-025` elsewhere. `TASK-030` (policy candidate domain model)
unblocked to `READY` — a real, persisted, UI-visible Finding now exists to attach one to;
`TASK-031` correctly stays `BLOCKED` on `TASK-030` itself. `TASK-053` (basic auth) reprioritized
P2→P1, `BLOCKED`→`READY`: no longer just "wait for real external users" — `TASK-035` (finding
feedback) is real and `READY` but cannot attribute *who* gave feedback without some identity
concept. Not implemented, a genuinely separate security-sensitive design task.

**`TASK-060` (diversity-aware candidate selection) implemented 2026-08-18 (ML Discovery, `ADR-035`):**
live-verified against `artifacts/evaluation/task-028-task-058-remediation-001.json`, only 2 unique
patterns (`P01`, `P06`) were represented across `task-058-remediation-20260817-001`'s 15
candidates — 13 were near-duplicate rescalings of `P01`, individually under the 0.85
`max_candidate_jaccard` ceiling but collectively redundant, so economic-weighted recall (45.2%) had
not moved. `discovery.engine._greedy_diverse_select` replaces single-pass score-sorted top-K
selection with a two-phase greedy loop scored by marginal gain (score discounted by overlap with
already-selected candidates; `diversity_discount_weight=0.0` exactly reproduces the old sequence).
`_development_score` itself untouched — out of scope per the task. `DISCOVERY_METHOD_VERSION` is
now `discovery-engine-v0.3.0`. A new official blind run, `task-060-remediation-20260818-001`
(`status=PERSISTED`, 15 candidates), was issued/verified/launched/frozen/**committed via signed
receipt before any evaluation opened ground truth**. Public comparison: distinct categorical
`(feature, value)` pairs used rose 3→5, `destination == Zanzibar` is new (matches disclosed "P02
Zanzibar family summer"), mean support and total exposure both fell a further ~33-36%. **One
caution flagged, not resolved:** `CAND-012` uses `acquisition_channel == paid_search`, associated
with confounding trap `T02` in the validation contract's own taxonomy — needs real G06 scrutiny,
not assumed genuine. `TASK-060` is `IN_PROGRESS`, not `DONE`: its three-part done condition
(unique-pattern recovery, no precision/direction degradation, no trap-rejection degradation) needs
`TASK-019`/`TASK-028` against this new run, handed to Statistics/Architect in `HANDOFF-052`.

## Next milestone

**14-day window (2026-08-14 → 2026-08-28), two tracked milestones, set by Founder Strategy 2026-08-14:**

- **Technical milestone — first compliant blind benchmark result. ACHIEVED 2026-08-16 (day 3 of
  14); re-graded 2026-08-17 (day 4).** `task-015-official-20260816-015` first graded **FAILED**
  (median impact error 204%, `ADR-019`). Founder-authorized two-part remediation (`HANDOFF-043`) —
  `TASK-058` (search-selection precision term, `ADR-023`) and `TASK-059` (benchmark-only diagnostic,
  `ADR-024`) — produced a new blind run, `task-058-remediation-20260817-001`, scored the same day:
  **overall verdict PROMISING** (`ADR-025`; median impact error 37.5%, Top-10 precision 90%, 100%
  direction accuracy, 0 leakage, 0/5 traps promoted). `TASK-058`/`TASK-059` both `DONE`; `HANDOFF-048`
  resolved. Full detail: `docs/benchmark/decision-gate.md` "Post-benchmark comparison" (both
  entries), `docs/benchmark/task-029-benchmark-report-v1.md`.
- **Commercial milestone — first documented customer/data-sharing conversation. Paused
  2026-08-17→2026-08-17 (`ADR-022`, same day), reopened same day on the PROMISING re-grade
  (`ADR-025`).** `ADR-010`, `ADR-017`, and `docs/strategy/30-day-validation-plan.md` originally
  recorded acquisition as parallel and non-blocking; the founder paused it as a focus choice, then
  the pause's own stated reopening condition (STRONG/PROMISING re-grade) was met within the day.
  `TASK-057` is `TODO`. Zero real conversations logged yet — the pause did not cost calendar time,
  only same-day sequencing.

**14-day go/no-go — technical half now PROMISING, not FAILED:**
- Per the pre-registered logic: **GO requires both** the technical milestone at PROMISING/STRONG
  *and* ≥1 real serious conversation logged. The technical half of that condition is now met; the
  commercial half is not yet — `TASK-057` just reopened with zero conversations.
- `docs/benchmark/decision-gate.md`'s own PROMISING action-row text ("do not advance to real
  customer data until re-graded at STRONG or PROMISING-with-the-same-metric-improved") is
  ambiguous on whether this first-time FAILED→PROMISING transition already satisfies it —
  unresolved, flagged to Founder in `ADR-025`, not needed urgently since `TASK-038` also still
  needs `TASK-057`/`TASK-037`.
- The **escalate** branch (hard disqualifier, or two runs both WEAK-or-worse) does **not** apply —
  no hard disqualifier ever fired, and the one remediation attempt succeeded.

See `30_DAY_VALIDATION_PLAN` framing in `docs/strategy/30-day-validation-plan.md`.

## Success criterion

The later pilot succeeds only if at least one validated finding is new, economically material, and actionable to the customer. The immediate milestone succeeds when a synthetic upload can be transformed reproducibly with complete data-quality and time-availability reporting.

## Kill signal

Across multiple suitable datasets, the system repeatedly produces only obvious, unstable, economically immaterial, or non-actionable relationships.
