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

**Decision:** Fix the validation methodology before any candidate pattern exists. Contract v1.0.0 defines sixteen ordered gates, their thresholds, cumulative requirements per evidence level, permitted language per level, and the policy-readiness matrix, in `docs/analytics/validation-contract.md` and `packages/analytics/src/policy_analytics/validation/`. Changing a threshold requires a new contract version and re-grading of every finding produced under the old one.

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

**Decision:** Fix, before any discovery run, which outcome is primary for the first blind benchmark, its harm direction, unit, missing-data policy, and eligible cohort. Primary outcome is `contribution_margin_eur` (EUR per booking; a decrease relative to the comparison group is harmful); six secondary/decomposition outcomes are defined; `repeat_purchase_180d` is exploratory-only and MNAR-bounded. Contract v1.0.0 is pinned to the delivered analytical dataset `travel-bookings-analytical-v1.0.0` by its identity hash, in `docs/analytics/outcome-contract.md` and `packages/analytics/src/policy_analytics/outcomes/`.

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

## ADR-011 — Outcome contract v1.1.0: explicit discovery-time statistical contract

**Date:** 2026-08-13
**Status:** Accepted

**Decision:** Extend the outcome contract (ADR-009) to v1.1.0 without reopening the primary-outcome choice: add an empirically verified `valid_range` per outcome, an explicit no-winsorization/no-transformation-at-discovery rule, an explicit per-outcome aggregation rule, and a machine-readable `DiscoveryStatisticalContract` (`DISCOVERY_CONTRACT` in `packages/analytics/src/policy_analytics/outcomes/contract.py`) fixing the search-fit split, the minimum-support floor, excluded explanatory-variable classifications, and missing-outcome handling for discovery specifically — as distinct from validation's later treatment of the same concerns.

**Context:** The v1.0.0 contract fixed *what* the outcome is but left several discovery-time operating rules implicit or split across the outcome and validation contracts: how to detect an anomalous outcome value, whether transformations are permitted before ranking, which split candidates may be tuned on, and what the minimum support for even proposing a candidate is. `TASK-015` had already run and, by inspection, complied with every one of these rules in practice — but compliance was accidental (a consequence of good engineering judgment), not contractually required, which is not sufficient for a preregistered contract meant to bind future runs and future agents.

**Alternatives:** Leave these rules implicit in code comments and prior conversation; duplicate the validation contract's support floor as a second, independently maintained number; let ML Discovery infer the search-split rule from the split labels without an explicit prohibition on using later splits to select candidates.

**Reason:** A rule that is only true by accident stops being true the next time someone runs discovery without having read this exact history. The support floor is imported from the validation contract's own `ValidationThresholds.min_exposed_records`, not restated, so the two cannot silently drift to different numbers. The search-split rule is stated explicitly because using `validation`/`future_holdout` to select candidates would invalidate the validation contract's own temporal-stability gate (G10) by leaking the exact period that gate is designed to test.

**Consequences:** `TASK-015`'s existing persisted candidates (`artifacts/discovery/task-015-candidates.json`) were checked against every new rule and found compliant: all 15 candidates use only `DECISION_TIME` features, all have `n_exposed >= 50` on development, and conditions were fit on development only. No rerun is required. Any future discovery or ranking run must construct its statistical contract from `DISCOVERY_CONTRACT`, not from local judgment. `valid_range` values are empirical claims about the pinned dataset instance and are re-verified by `tests/analytics/test_outcome_contract.py` against the live artifact; they must be re-derived, not copied, if the dataset is regenerated.

## ADR-012 — Pre-registered benchmark decision gate (STRONG/PROMISING/WEAK/FAILED)

**Date:** 2026-08-13
**Status:** Accepted

**Decision:** Before the first blind discovery run (`TASK-017`) is scored, fix a business decision gate — `docs/benchmark/decision-gate.md` — that converts `TASK-028`'s six metrics (Top-K precision, economic-weighted recall, confounder trap rejection, leakage violations, effect direction accuracy, economic impact estimation error) into one of four verdicts and a bound action: STRONG → proceed toward real customer data; PROMISING → one targeted synthetic iteration, no approach change; WEAK → no real data, iterate; FAILED → no real data, and after two failed independent runs on the same metric with a confirmed non-fixable cause, a mandatory core-discovery-approach review. Any leakage violation, any promoted confounding trap, or any materially-sized wrong-direction finding is a hard disqualifier that forces FAILED regardless of the other five metrics.

**Context:** Ground truth (`synthetic_data/evaluation/hidden_ground_truth.json`) is confirmed unopened as of this commit — `TASK-017`/`TASK-028` are `BLOCKED`, and `TASK-015` was reverted to `BLOCKED` pending a rerun against the current pinned dataset identity and formal `TASK-012` split contract. `docs/analytics/validation-contract.md` §10 already fixes a qualitative acceptance test for the validation methodology, but nothing translates its output into a founder-level go/no-go on spending a real customer relationship on this mechanism. Recording the criteria after seeing results would let success standards move to fit whatever the run produced, which the discipline in `ADR-007` explicitly exists to prevent.

**Alternatives:** Grade the benchmark informally after the fact; let Statistics' per-finding evidence levels alone stand in for a benchmark-level verdict; wait for a real customer dataset before defining what "good enough" means.

**Reason:** The two cheapest, most decision-relevant unknowns for this company are whether the mechanism works and whether a customer exists (`docs/strategy/30-day-validation-plan.md`). This gate makes the first one falsifiable and immune to post-hoc goalpost-moving, at zero customer cost, before any real data is touched.

**Consequences:** No real-customer dataset may be ingested (`TASK-038`) on the strength of a benchmark run graded below STRONG or PROMISING-with-improvement under this gate. The tier thresholds are Founder-set business judgment; `HANDOFF-027` asks Statistics to confirm they don't conflict with `docs/analytics/validation-contract.md` before `TASK-028` runs. `docs/benchmark/decision-gate.md` is append-only after this date — results are added under its "Post-benchmark comparison" section, never substituted into the criteria above it.

## ADR-013 — Domain-grouped documentation layout

**Date:** 2026-08-14
**Status:** Accepted

**Decision:** Reserve the repository root for the eight global entry-point/source-of-truth Markdown files and place all scoped documentation under domain directories in `docs/`: architecture, analytics, benchmark, customer, product, strategy, and operations.

**Context:** Product, benchmark, customer-acquisition, and analytical design documents accumulated in the repository root, making global sources of truth indistinguishable from scoped working contracts and plans.

**Alternatives:** Keep a flat root; keep a flat `docs/`; introduce a documentation generator or external knowledge base.

**Reason:** Domain grouping makes ownership and discovery obvious without adding tooling or moving durable memory out of Git.

**Consequences:** New scoped Markdown files must follow `docs/README.md`. Moves update all references atomically and do not leave compatibility copies. `agents/`, `memory/`, dataset-local, and package-local documentation retain their specialized locations.

## ADR-014 — Bootstrap p-value resolution floor discovered incompatible with large-family BH correction

**Date:** 2026-08-14  
**Status:** Accepted (finding); fix not yet applied

**Decision:** Record, without retroactively changing, a structural defect discovered while running the `TASK-018` validation contract for the first time (`TASK-019` dry run against the `TASK-015` candidates): `bootstrap_two_sided_p`'s resolution floor of `1/(B+1)` (≈0.0005 at the contract's `bootstrap_resamples = 2000`) is mathematically incapable of passing Benjamini-Hochberg correction at `family_size = 6945` for any candidate, regardless of true effect size, because the floor exceeds `alpha·rank/family_size` for every achievable rank once family_size is in the low thousands. This is not a property of the specific candidates tested; it would occur for any candidate set with this family size and this bootstrap replicate count.

**Context:** All 15 `TASK-015` candidates were graded against gate G05 using the exact preregistered method (`docs/analytics/validation-contract.md` §4). Every candidate's raw bootstrap p-value landed at the floor, and every one failed BH correction, capping every candidate at `LEVEL_1_DESCRIPTIVE` regardless of how large or stable its raw effect was. A supplementary diagnostic — a normal approximation using the same cluster-bootstrap standard error (no scipy required: `math.erf`) — put every candidate's p-value below 1e-6, several orders of magnitude past what would be needed to survive correction. This strongly suggests the G05 failures reflect estimator precision, not weak evidence.

**Alternatives considered:** (a) Silently switch the p-value method mid-run to the normal approximation and let candidates pass — rejected: this is exactly the "tune the threshold after seeing the result" behavior `docs/analytics/validation-contract.md` §2 forbids, even though the underlying justification is methodological rather than result-driven; the discipline of not making that judgment call unilaterally, in the same run that revealed the problem, matters more than the inconvenience of a conservative result. (b) Increase `bootstrap_resamples` enough to resolve p-values below `alpha/family_size` empirically — mathematically valid but would require roughly 50,000+ replicates per candidate per split, which is expensive without deeper optimization and does not fix the underlying issue for a larger future family. (c) Leave G05 as specified and accept that every candidate stays capped at `LEVEL_1_DESCRIPTIVE` until a fix ships — chosen for this run.

**Reason:** Preregistration exists to prevent a threshold from being loosened because a result is inconvenient. It does not exist to force silent use of a mathematically degenerate estimator once its precision limit has been proven, in general, to be incompatible with the family sizes this system actually produces (thousands of evaluated hypotheses per discovery run). The correct response is to ship the fix as a new, explicitly versioned contract change applied to the *next* run, not this one.

**Consequences:** `TASK-019` stays `IN_PROGRESS`, not `DONE`; no candidate from this run may be presented as having passed multiplicity correction. Before the next validation run, `docs/analytics/validation-contract.md` and `packages/analytics/src/policy_analytics/validation/` need a versioned fix to G05 — most likely switching its p-value source to the normal approximation on the bootstrap standard error (removing the floor entirely, since it is a moment estimate rather than a tail-count estimate) while keeping the bootstrap itself as the source of the standard error. This is Statistics-owned work, tracked as a prerequisite for `TASK-019`'s next attempt, not a new task number.

## ADR-015 — Validation contract v1.1.0: G05 p-value source fixed to a normal approximation

**Date:** 2026-08-14  
**Status:** Accepted; shipped in code, not applied to any candidate

**Decision:** Fix the defect recorded in ADR-014 by changing gate G05's p-value source, in a new contract version (`CONTRACT_VERSION` bumped `"1.0.0"` → `"1.1.0"`), from the empirical bootstrap tail-count inversion (`bootstrap_two_sided_p`) to a normal approximation on the cluster-bootstrap standard error (`normal_approx_two_sided_p(point_estimate, bootstrap_standard_error(replicates))`, computed via `math.erfc` to avoid catastrophic cancellation). No other gate, threshold, or evidence rule changed. The already-frozen 2026-08-14 `TASK-019` dry-run artifact (`artifacts/validation/task-019-validation-report.json`, `validation_contract_version = "1.0.0"`) is left exactly as written and is not re-graded.

**Context:** ADR-014 established that the old method's resolution floor (`1/(B+1) ≈ 0.0005` at `bootstrap_resamples = 2000`) makes G05 structurally unsatisfiable once `family_size` exceeds roughly 200 — a threshold this system's discovery searches (thousands of evaluated hypotheses) blow past by a wide margin, regardless of true effect size. `scripts/validate_candidates.py` now refuses to overwrite an existing frozen output without an explicit `--force`, so this fix cannot silently rewrite a result that other durable records (TASKS.md, HANDOFF-016) already reference.

**Mathematical verification:** at a generous future `family_size = 100,000`, the strictest BH requirement (`rank = 1`) is `p ≤ 1e-6`, reached at `z ≈ 4.89` standard errors — well within what real cluster-bootstrap effects at this system's typical sample sizes produce (the ADR-014 diagnostic p-values corresponded to `z` in the 8–20+ range). `math.erfc` stays accurate out to roughly `z ≈ 38` before underflowing to exactly `0.0`, which is still the correct comparison result against any positive threshold — leaving on the order of 300 decades of headroom past what any realistic family size requires. Full derivation: `docs/analytics/validation-contract.md` §4a.

**Alternatives considered:** (a) increase `bootstrap_resamples` until the empirical floor clears the requirement — rejected, needing on the order of 50,000+ replicates per candidate per split with no fix for a larger future search, since the crossover just moves; (b) a more sophisticated resampling tail estimate (importance-sampled or Edgeworth-corrected bootstrap, saddlepoint approximation) — rejected as unneeded complexity given this system's sample sizes are squarely in the regime the central limit theorem is built for; (c) the normal approximation, as implemented — chosen as the simplest option proven mathematically sufficient.

**Regression coverage:** `tests/analytics/test_g05_multiplicity_fix.py` is synthetic and mathematical throughout — no real dataset, candidate, `hidden_ground_truth.json`, or `synthetic_benchmark.py` reference. It proves, as general properties of the two estimators rather than as claims about any specific candidate: the old method cannot distinguish a modest synthetic effect from an astronomically larger one once every bootstrap replicate shares a sign; the old method fails BH correction at a realistic family size even at its own most-significant-possible value; the new method has no such floor and resolves far below what any realistic family size requires; a strong synthetic effect (constructed independently of any real candidate) fails under the old method and passes under the new one at the same family size; and a null synthetic effect (mean at zero) still correctly fails under the new method, proving the fix is not a rubber stamp.

## ADR-016 — ICP scope: travel agencies only until first real discovery (resolves HANDOFF-022)

**Date:** 2026-08-14
**Status:** Accepted

**Decision:** Data acquisition, discovery-call effort, and any real analysis stay scoped to travel agencies/tour operators only until `MILESTONE-M3` (first real discovery, customer-confirmed as new/material/actionable) is reached or travel-agency outreach demonstrably dead-ends after a real effort. The two other verticals researched in `docs/customer/prospect-target-list.md` (recruitment/staffing, B2B distribution) are kept as a researched backlog, not contacted, and receive zero further founder or Customer Discovery execution time under this decision. This directly answers `HANDOFF-022`'s four questions: (1) non-travel data is not run through the pipeline and is not collected yet either — the question is deferred, not answered by building three schemas; (2) no per-vertical outcome-definition template is predefined; (3) outreach stays "independent research, no product," unchanged; (4) travel agencies are not merely priority #1 — they are, for now, the only active vertical.

**Context:** `TASK-057` and the entire built pipeline (canonical schema, synthetic benchmark, outcome contract, discovery engine, validation contract) are travel-agency-specific; a recruitment or distribution dataset arriving today would have nowhere approved to go without new schema and outcome-contract work per vertical (`OQ-002`/`OQ-004` would multiply by three). Separately, `HANDOFF-026`'s own outcome — zero of three required conversations after a full day, blocked purely on the founder being the sole available execution channel — demonstrates that founder bandwidth, not idea generation, is the binding constraint right now.

**Alternatives:** Option B — run travel primary with recruitment/distribution in parallel as a generality check, per the acquisition plan's original three-vertical draft.

**Reason, against the four stated criteria:**
- **Learning speed:** the biggest open uncertainty (does discovery find real, material, actionable patterns at all) can only be tested today against travel data — the only vertical with a working canonical schema and outcome contract. A non-travel dataset would sit unanalyzed and teach nothing about that uncertainty; it would only teach willingness-to-share norms, which is a smaller, later question.
- **Domain-specific overfitting risk:** real, but premature. Whether the discovery *methodology* generalizes across verticals is only worth testing after it has been shown to work on the one vertical fully built for it. Testing generality before testing validity inverts the priority `agents/FOUNDER_STRATEGY.md` sets — proving the core hypothesis before expanding scope.
- **Founder bandwidth:** the scarcest resource in the company right now, proven by `HANDOFF-026`'s literal result. A solo founder is the only entity that can authorize a send channel, supply warm contacts, or personally send outreach in this environment. Three parallel verticals means three parallel positioning conversations, three sets of objections, and three qualification bars, run by the same one person who has not yet cleared the first.
- **Clarity of positioning:** "we analyze historical decisions for a travel agency" is a concrete, checkable pitch. "We analyze historical decisions for travel agencies, staffing firms, or wholesale distributors" reads as a horizontal analytics platform — exactly the "generic AI platform" positioning `agents/FOUNDER_STRATEGY.md`'s differentiation guardrails warn against, before a single real finding exists to prove the horizontal claim.

**Consequences:** `TASK-057`'s goal text (travel-agency-specific) is confirmed correct as written, not widened. `docs/customer/prospect-target-list.md`'s recruitment/distribution rows (R1–R7, D1–D7) are retained as a sourced backlog and may be reactivated by a future Founder Strategy decision if travel-agency outreach dead-ends after a real attempt (see the 14-day go/no-go in `memory/CURRENT_STATE.md`) — this is a paused door, not a closed one. `HANDOFF-022` is resolved.

## ADR-017 — Customer acquisition execution channel and 7-day outreach commitment (resolves HANDOFF-026)

**Date:** 2026-08-14
**Status:** Accepted

**Decision:** All three non-exclusive execution paths `HANDOFF-026` raised are authorized, combined, and time-boxed to a 7-day sprint, scoped to travel-agency prospects only per `ADR-016`: (1) the founder personally sends outreach — via their own warm contacts first, then via LinkedIn/email for the researched cold list — and reports real responses back for Customer Discovery to log; (2) the founder authorizes the Gmail connector via claude.ai connector settings so Customer Discovery can send and track email directly once live; (3) Customer Discovery's named-prospect research continues to fill out decision-maker contacts for the existing travel rows. Numeric target for the 7 days, detailed in `docs/customer/acquisition-sprint-7day.md`: **15 outbound touches → 4 real replies/exchanges → 1 serious conversation** logged in `docs/customer/pipeline.md` under its existing bar.

**Context:** As of this decision, `TASK-057` is at 0 of 3 required serious conversations. `docs/customer/prospect-target-list.md` supplies 8 researched (uncontacted, unqualified) travel-agency candidates. The Gmail connector remains unauthenticated — that step requires the founder's own action in claude.ai connector settings and cannot be completed by an agent. No warm contacts have been supplied yet. Real reply cycles take real-world days regardless of channel, so a 7-day window is the minimum meaningful measurement period, not an arbitrary sprint length.

**Alternatives:** Wait for Gmail authorization before sending anything (rejected — warm contacts and LinkedIn do not depend on it, and waiting wastes the days); pursue only warm intros (rejected — insufficient volume from a solo founder's network alone to reach a meaningful touch count); pursue only cold outreach (rejected — foregoes the fastest, highest-reply-rate channel available).

**Reason:** Combining paths removes the single point of failure `HANDOFF-026` exposed (an unauthenticated connector fully blocking progress) while keeping the founder's limited time focused on sending and replying, not on tooling. The numeric target is deliberately smaller than the full acquisition plan's 20-prospect funnel (`docs/customer/data-acquisition-plan.md` §10: 12–14 calls, ≥3 conversations, 3–5 datasets) — this is a 7-day checkpoint inside that funnel, not a replacement for it.

**Consequences:** `HANDOFF-026` is resolved as "combination of all three paths, time-boxed, with an explicit numeric target" — it does not close `TASK-057` itself, which still requires real conversations to happen. If Gmail authorization has not happened by day 2 of the sprint, outreach proceeds via founder-sent LinkedIn/email regardless, so the sprint does not silently stall on it a second time. Progress (or its absence) against the 15→4→1 target is the primary input to the 14-day commercial milestone and go/no-go in `memory/CURRENT_STATE.md`.

**Consequences:** `TASK-019` remains `IN_PROGRESS`. The fix is live in code and verified against real `TASK-015` candidate data as a code-behavior check only (not persisted, not treated as evidence) — several candidates' G05 gate would now pass at realistic effect sizes, confirming the estimator works, but this changes nothing about whether those candidates are usable: `TASK-017`/ADR-008 blind-protocol compliance and the founder readiness block on `TASK-015`/`TASK-016` are independent, unresolved prerequisites. `TASK-019` will next apply `CONTRACT_VERSION = "1.1.0"` to a genuinely compliant `TASK-017` artifact once one exists; that will be a new, separately frozen run.

## ADR-018 — TASK-019 closing-run readiness: blind-agent schema compatibility and explicit compliance recording

**Date:** 2026-08-14  
**Status:** Accepted

**Decision:** Make `run_validation`/`scripts/validate_candidates.py` accept either candidate-document shape currently in use — the original discovery engine's inline shape and the blind-agent output schema (`tools/blind_agent/models.py`, `OUTPUT_SCHEMA_VERSION = "1.1.0"`) — and require the CLI operator to state `--blind-compliant`/`--founder-block-lifted` explicitly whenever grading anything other than the historical dry-run artifact, recording both into the frozen output. The CLI now takes `--candidates`/`--metrics`/`--dataset-root`/`--output`/`--analysis-run-id` instead of hardcoded module constants.

**Context:** Comparing `tools/blind_agent/models.py`'s `CandidatesDocument`/`Candidate`/`MetricsDocument` against what `apply.py` was written to parse (the original `policy_analytics.discovery.engine` output) found two incompatibilities that would have surfaced only when a real blind run finally succeeded: (1) `evaluated_hypotheses` is not present in `candidates.json` at all under the new schema — it lives in a sibling `discovery_metrics.json`; (2) candidates carry a single `sample_size`/`support`/`raw_effect`/`economic_exposure`, not the old per-split (`development`/`validation`/`future_holdout`) breakdown. Item (2) turned out not to require a code change: `_validate_one` already recomputes every quantity from the analytical dataset via each candidate's `conditions`, and never trusted the old schema's precomputed split stats either — it only ever read `candidate_id` and `conditions`, which both schemas share. Item (1) required `_evaluated_hypotheses()`, a small adapter checked by dedicated tests.

Separately, `scripts/validate_candidates.py`'s `process_compliance` block (blind-protocol satisfaction, founder-readiness-block status) was hardcoded `False`/`False` — correct for the one artifact that existed, but silently wrong for any future one. Given the CLI can now point at any artifact, hardcoding is no longer safe in either direction: defaulting to `False` would misrepresent a genuinely compliant future artifact as unusable, and defaulting to `True` would risk exactly the kind of silent overclaiming this whole validation framework exists to prevent.

**Alternatives considered:** (a) have the script parse `TASKS.md`/`HANDOFF-*` to auto-detect compliance — rejected as fragile (prose, not a stable machine interface) and as delegating a judgment call to text-matching; (b) default compliance flags to `False` (conservative) — rejected because it would need to be silently overridden for every future real run, training operators to reach for an override reflexively; (c) require explicit flags with no default, frozen into the record — chosen, matching the existing `--force` precedent for overwrite protection.

**Consequences:** `run_validation` gained an optional `metrics_path` parameter and pre-flight checks (candidate/payload outcome-ID consistency, explicit `INSUFFICIENT_CANDIDATES` handling) that run before the analytical dataset is loaded. `tests/analytics/test_validation_apply.py` gained schema-compatibility tests built from the real `tools.blind_agent.models` classes (not a hand-typed guess at the shape), proving a schema-valid blind-agent document parses and grades correctly end-to-end through the actual CLI, verified by direct invocation. No gate, threshold, or evidence rule changed — this is tooling readiness for `TASK-019`, not a new methodology decision. `TASK-019` remains `IN_PROGRESS`; this ADR does not claim a compliant artifact exists yet, only that the code is now ready to grade one correctly when it does.

## ADR-019 — First compliant blind benchmark run scored FAILED; real customer data blocked pending remediation

**Date:** 2026-08-16  
**Status:** Accepted

**Decision:** The first `TASK-017`-compliant blind discovery run (`task-015-official-20260816-015`), validated under contract v1.1.0 and scored by `TASK-028`, grades **FAILED** overall under the pre-registered `docs/benchmark/decision-gate.md`. Per that document's binding action table, real customer data ingestion (`TASK-037`→`TASK-038`) does not proceed on the strength of this benchmark result. Full detail: `docs/benchmark/task-029-benchmark-report-v1.md`; live comparison against pre-registered bands: `docs/benchmark/decision-gate.md` "Post-benchmark comparison".

**Context:** No hard disqualifier fired (0 leakage violations; no confounding trap promoted; 100% effect-direction accuracy on validated findings). The verdict is driven entirely by one metric — economic impact estimation error, median 204% relative error — while Top-10 precision (90%) and direction accuracy (100%) are strong. The other three metrics: economic-weighted recall 45.2% (PROMISING), confounder trap rejection PROMISING (no trap was ever proposed as a candidate, which is a weaker claim than demonstrated active rejection), leakage 0 (passes).

**Reason for FAILED rather than WEAK/PROMISING:** `docs/benchmark/decision-gate.md` takes the weakest graded band as the overall verdict; metric 6's own band table puts anything over 100% relative error at FAILED, and this run's error is documented and diagnosed (`task-029-benchmark-report-v1.md` §3.6): the validated candidates' rules (e.g. `discount_rate >= 0.12 AND customer_price_eur < 3818`) expose ~15–16× more bookings than the true injected pattern they partially recover, which dilutes per-booking effect while inflating total reported exposure through the larger population.

**Attribution and next step:** Statistics attributes this to a fixable estimation-granularity gap (no current step isolates a rule's exposure attributable to its overlap with a specific known-recovered pattern from its whole-population exposure) rather than a limitation of the discovery search itself, given the same run's strong precision and perfect direction accuracy. This attribution requires ML_DISCOVERY's concurrence before decision-gate.md's FAILED action authorizes a single remediation rerun rather than counting as the first of two strikes toward a mandatory core-discovery-approach review — tracked as `HANDOFF-043`, not yet resolved as of this entry.

**Consequences:** `MILESTONE-M1` ("Synthetic end-to-end MVP") is technically demonstrated end-to-end (ingestion through blind discovery through validation through ground-truth scoring all ran, deterministically, without a hidden-ground-truth boundary violation) but does not meet its own quality bar ("several true patterns must be recovered... major traps are rejected/downgraded" — recovery and trap-avoidance both hold, but impact accuracy does not). `TASK-057`/real-customer-data work is unaffected procedurally (it was already gated on customer acquisition, not on this benchmark) but this benchmark's FAILED verdict is now the standing reason `TASK-037`/`TASK-038` may not proceed even once a customer exists, until re-graded at STRONG or PROMISING.

## ADR-020 — Candidate ranking v0: five-component weighted score, not search importance alone

**Date:** 2026-08-16
**Status:** Accepted

**Decision:** Implement `TASK-016` as `packages/analytics/src/policy_analytics/discovery/ranking.py`: a pure, deterministic function combining five components — economic impact, support, temporal stability, actionability, and novelty (non-redundancy against other candidates in the same batch) — into one transparent `rank_score`, with every component exposed per candidate. Weights (`economic_impact=0.35, support=0.15, stability=0.20, actionability=0.15, novelty=0.15`) are ML_DISCOVERY-authored v0 defaults from generic business reasoning, versioned as `candidate-ranking-v0.1.0`, and were fixed and this module written without opening `hidden_ground_truth.json` or `synthetic_benchmark.py`. A missing stability signal (no later split had exposure) scores `0.0`, never `1.0` or an omitted term. Ranking never edits, drops, reorders within, or adds to a persisted candidate list, and never recomputes a candidate's own frozen `economic_exposure`/`support`/`raw_effect` — only stability (no per-split breakdown in the frozen blind-agent schema) and novelty (exposure-membership overlap) are recomputed from the analytical dataset, reusing `validation.apply`'s already-tested split/condition-evaluation functions rather than a third duplicate implementation. Full methodology: `docs/analytics/candidate-ranking-v0.md`. Ran for real against `task-015-official-20260816-015`'s 15 frozen candidates, frozen at `artifacts/discovery/task-016-candidate-ranking-task-015-official-20260816-015.json`.

**Context:** `docs/analytics/discovery-engine-v0.md` fixed the search's own preliminary order as a single number (development historical exposure with a mild complexity penalty) explicitly for selection only, stating "Full multi-factor ranking is TASK-016." `TASK-016`'s goal text is explicit that this must not be "model importance alone." The frozen official candidate artifact (blind-agent schema, `OUTPUT_SCHEMA_VERSION = "1.1.0"`) does not carry actionability, temporal stability, or exposure membership, so a ranking module operating on it must recompute exactly those and no more.

**Alternatives:** (a) Rank by the search's own `rank_score`/economic exposure alone — rejected, contradicts the task's own goal text and reduces to the thing ADR-011/docs already said ranking must not be. (b) Wait for a Product/Statistics-approved weight contract before implementing anything — rejected as blocking `TASK-017`'s only remaining dependency indefinitely; ship versioned v0 defaults now, request review in parallel (`HANDOFF-045`), and let a future contract change be a visible version bump rather than a precondition to starting. (c) Fit or tune weights by checking which weighting best matches `hidden_ground_truth.json` (already opened by `TASK-028` at the time this was implemented) — rejected outright as exactly the after-the-fact goalpost-moving `ADR-007`'s discipline exists to prevent; this module was designed and documented before it was ever run, using only generic business reasoning, the same discipline Statistics used for its confounder set.

**Reason:** A five-component transparent score with every weight and value exposed is falsifiable and auditable in a way a single opaque importance number is not, and it directly answers the task's own stated requirement. Reusing `validation.apply`'s public `Condition`/`rule_expr`/`split_stats`/`load_analytical_frame` avoids a third duplicate condition-evaluation implementation (engine.py already has one, validation/apply.py has another) while keeping the two modules decoupled from `discovery.ranking`'s own pure scoring function, which remains testable with zero I/O.

**Consequences:** `docs/analytics/discovery-engine-v0.md`'s "actionability" logic was extracted from `discovery.engine` into a new shared `discovery.actionability` module so the search-time label and the ranking component can never silently diverge; `engine.py`'s own candidate output and existing tests are unchanged. `TASK-016` is `DONE`; per its own prior status note, `TASK-017`'s two listed dependencies (`TASK-003`, `TASK-016`) are now both satisfied — closing `TASK-017` is Architect/Code-Reviewer confirmation, not new implementation (`HANDOFF-045`). The weights are provisional pending Product/Statistics review and must not be treated as a final business-approved contract until that review lands.

## ADR-021 — Economic impact result contract v1.0.0 (resolves HANDOFF-025)

**Date:** 2026-08-17
**Status:** Accepted

**Decision:** `TASK-023`'s economic-impact output is a new, independently-versioned contract —
`packages/analytics/src/policy_analytics/validation/economic_impact.py`
(`EconomicImpactResult`, `build_economic_impact_result`, `ECONOMIC_IMPACT_CONTRACT_VERSION =
"1.0.0"`) — wired into gate G15 inside `validation/apply.py`, in exact field-for-field
correspondence with Architect's storage envelope (`EconomicImpactPersistence`,
`apps/api/app/findings/contracts.py`) so `TASK-024` can persist it without recomputing or
reinterpreting any statistical meaning. Full semantics: `docs/analytics/economic-impact-contract.md`.

**Key choices, each made without opening `hidden_ground_truth.json`:**
1. `affected_records` is the candidate's exposed count over the **full combined window**
   (development + validation + future_holdout), not `ValidationMetadataPersistence.exposed_records`
   (development-split-only). These answer different questions and are not generally equal — this
   corrects a wrong assumption in `docs/product/finding-product-contract.md` that treated them as
   the same population (`HANDOFF-046`, sent to Product).
2. The point estimate (`per_record_effect.value`) is the real, unresampled combined-window sample
   statistic (`split_stats`), not the bootstrap replicates' own mean — G15 previously used the
   latter, sufficient for a pass/fail gate but not a persistence-ready point estimate. This is a
   precision correction (≤0.2% numeric difference on the closing `TASK-019` run), not a
   re-estimation; it does not alter any frozen verdict.
3. `historical_impact`'s interval is `per_record_effect`'s interval scaled by `affected_records`
   from the *same* cluster-bootstrap replicate set (`customer_id`, combined window) — kept
   internally consistent, and explicitly distinct from `ValidationMetadataPersistence.raw_effect`'s
   development-only bootstrap, which grades evidence rather than sizes impact.
4. `annualization_justified`/`annualized_impact` are hard-gated to `False`/`None` by
   `EconomicImpactResult.__post_init__` — v1.0.0 does not implement the exposure-rate-stability
   check `docs/analytics/validation-contract.md` §8 requires before annualizing, so it can never
   silently claim it did.
5. Exposure is **not** narrowed to a ground-truth-matched subpopulation — that is `HANDOFF-043`'s
   pending remediation question, explicitly forbidden by this module's own docstring until
   ML_DISCOVERY concurs; this contract reports each candidate's own whole-rule exposure, unchanged.

**Alternatives:** (a) Leave `EconomicImpactPersistence` populated by Architect's stopgap hand-mapping
of existing G15 diagnostics — rejected; it borrowed `validation_contract_version` for
`impact_contract_version` (wrong — impact evolves on its own schedule) and used
`validation_report.adjusted_effect` (development-split grading estimate) as `per_record_effect`
(wrong population for sizing impact). (b) Attribution-narrow exposure now, folding
`HANDOFF-043`'s remediation into this contract — rejected; that is a design decision pending
ML_DISCOVERY's concurrence, not something a persistence-contract resolution should pre-empt.

**Consequences:** `HANDOFF-025` is resolved; `TASK-024` moves from `BLOCKED` to `READY` (Architect,
2026-08-17). `HANDOFF-046` asks Product to correct `finding-product-contract.md`'s
`affected_records`/`exposed_records` row and choose which count is customer-facing — not blocking
implementation, since Statistics' contract already states the correct semantics regardless of
Product's display choice. 177 tests pass (7 new in `tests/analytics/test_economic_impact.py`); both
prior frozen validation artifacts remained untouched by this ADR itself (only future runs use the
corrected point estimate) — **superseded immediately after, 2026-08-17, Architect:** the
`v1.0.0` dry-run artifact is still untouched, but the closing-run official artifact
(`artifacts/validation/task-019-official-20260816-015.json`) *was* subsequently regenerated with
`--force` so `TASK-024` persistence has a real `economic_impact` field to read, since nothing short
of re-running `apply.py`'s current code can add a field it didn't compute before. Verified before
doing so: every verdict (`PASS`/`DOWNGRADE`) and point estimate identical between the two runs; only
bootstrap CI bounds and the derived p-value shifted (`HANDOFF-047` — traced to a `Polars`
`group_by`-order/seeded-resampling interaction, not fixed here). `artifacts/evaluation/`
`task-028-benchmark-evaluation.json` was regenerated in lockstep for the same reason (its input
changed); every metric except the diagnostic-only impact-error median was byte-identical
(`2.038` → `1.995`), and no prose in `docs/benchmark/` cites the old value.

## ADR-022 — Customer acquisition sequenced after MVP technical validation (supersedes the parallel-track design in ADR-010/ADR-017/30-day-validation-plan)

**Date:** 2026-08-17
**Status:** Accepted

**Decision:** Active `TASK-057` outreach (sending new touches, opening new conversations, continuing the `ADR-017` 7-day sprint) is paused until the technical track (`docs/benchmark/decision-gate.md`) re-grades at STRONG or PROMISING. This explicitly overrides the "parallel, neither blocks the other" design recorded in `ADR-010`, `ADR-017`, and `docs/strategy/30-day-validation-plan.md`'s governing principle ("Both run in parallel starting day 1... everything downstream... is explicitly de-prioritized for this window" — that "everything downstream" framing did not itself contemplate pausing Track 3, which this ADR now does). This is a founder prioritization call, not a correction of those documents' reasoning, which this ADR does not dispute.

**Context:** Founder Strategy's own audit (2026-08-17) of `DECISIONS.md` correctly found no prior ADR recording a sequential design — the repository's actual prior record is genuinely and intentionally parallel, three times over (ADR-010, ADR-017, 30-day-validation-plan.md). The founder holds a sequencing preference that predates this repository's task-tracking discipline and was communicated directly, outside any prior ADR; it surfaces here, formally, only now that Founder Strategy's audit exposed the conflict. Founder does not dispute Founder Strategy's counter-argument on its merits: the `ADR-019` FAILED verdict is narrow (economic-impact estimation only; 90% Top-10 precision, 100% direction accuracy, no hard disqualifier), `HANDOFF-043` (ML Discovery, 2026-08-17) confirms it is a fixable defect rather than a core-method limitation, the sales cycle has no code dependency on the engine, and the approved offer text in `docs/customer/pipeline.md` makes no delivery-timeline promise. The override is a bandwidth/focus choice, not a rebuttal.

**Alternatives:** (a) Keep the parallel track as designed — rejected; founder wants undivided engineering/product focus while the mechanism's headline metric is still failing its own pre-registered bar and remediation scope (`HANDOFF-043` part 2) is still being decided, and does not want to be personally holding customer conversations about a product whose core result just failed, even on a narrow, likely-fixable metric. (b) Partial parallelism — continue only already-warm conversations without opening new outbound — considered, rejected for simplicity; a full pause is easier to reason about and cleanly re-open. (c) Defer the decision until a remediation rerun exists — rejected; the founder decision is available now and does not need to wait on engineering output.

**Reason:** The founder's own time is the scarce resource `ADR-017` explicitly routes outreach through ("founder personally sends outreach... reports real responses back"); spending it on new prospect conversations while the product's headline validated-mechanism result is FAILED (even if narrowly and plausibly fixably so) is a use of that scarce resource the founder does not want to make right now. This is a deliberate, named risk: per `ADR-010`'s own reasoning ("build work beyond what a credible first pilot requires has no evidence value until at least one real dataset exists"), delaying acquisition start delays discovering whether the ICP/channel itself works — that risk is accepted, not overlooked.

**Consequences:** `TASK-057` moves from `TODO` to `BLOCKED`, reason: this ADR, not a technical dependency — re-opens without a further ADR once `docs/benchmark/decision-gate.md` re-grades at STRONG or PROMISING. `TASK-046`/`TASK-047` remain `BLOCKED` as before (downstream of `TASK-057`/`MILESTONE-M3`), now additionally blocked by this ADR while it is in effect. `TASK-048`/`TASK-049` (one-liner, founder story) are unaffected and may continue — neither involves contacting a customer. `docs/strategy/30-day-validation-plan.md` Track 3/4 week-by-week objectives are superseded for as long as this ADR is in effect; the document itself is not rewritten (append-only respected) — this ADR is the binding sequencing rule until superseded. `memory/CURRENT_STATE.md`'s "Next milestone" section is updated in the same change to state the commercial milestone is paused, not "unaffected," under this ADR. Already-completed groundwork (Gmail connector authorization, `docs/customer/prospect-target-list.md` research) is not undone, only not acted on further until re-opened.

## ADR-023 — Discovery engine v0.2.0: population-dampened beam-survival score (`TASK-058`, `HANDOFF-043` remediation part 2)

**Date:** 2026-08-17
**Status:** Accepted

**Decision:** Change `discovery.engine`'s beam-survival score from linear
`historical_exposure = harm_per_booking × n_exposed` to `harm_per_booking ×
n_exposed^population_score_exponent` (default `population_score_exponent = 0.5`, a new
`DiscoveryConfig` field validated to `(0.0, 1.0]`). `population_score_exponent = 1.0` reproduces
the old ranking exactly and is regression-tested. `DISCOVERY_METHOD_VERSION` bumps
`"discovery-engine-v0.1.0"` → `"discovery-engine-v0.2.0"`. Full mechanism and rationale:
`docs/analytics/discovery-engine-v0.md` §"Precision term".

**Context:** `HANDOFF-043` (2026-08-17, ML Discovery) diagnosed that linear-in-population scoring
structurally favors broad rules over precise ones: on `task-015-official-20260816-015`,
`supplier`/`destination` were both eligible `DECISION_TIME` search features, yet zero of the 15
reported candidates used any categorical condition, despite disclosed pattern names ("BlueWing",
"Tokyo") implying those features would have narrowed a candidate toward the true population. This
is a search-selection artifact — a beam-search step adding a narrowing condition loses to one that
stays broad before any candidate is even reported — not fixable by `TASK-016`'s downstream
re-ranking of an already-selected top-K, and not fixable by `TASK-021`/`TASK-023`'s reporting layer
alone (`ADR-021` explicitly deferred attribution-narrowing to this decision). Founder authorized
both `HANDOFF-043` remediation parts the same day.

**Alternatives:** (a) A lightweight post-search "tightening" pass that tries adding one narrowing
categorical condition to an already-found broad rule — considered, not chosen for v0.2.0: it would
only patch the specific top-K the old objective already selected, rather than changing which rules
survive the beam at every depth, and is more implementation surface for a similar effect. (b) A
hard cap on `n_exposed` (reject any rule above some population ceiling) — rejected: an arbitrary
cliff, harder to justify from generic reasoning, and would wrongly penalize a genuinely broad true
effect. (c) The chosen exponent-dampening — a single, continuous, generically-motivated parameter
(geometric mean between total exposure and per-booking purity), with `1.0` as an exact escape hatch
back to the old behavior for comparison.

**Reason:** `n_exposed^0.5` is the minimal change that directly targets the diagnosed mechanism —
sub-linear population scaling means a rule can no longer inflate its score just by absorbing more
diluting bookings — while remaining a symmetric, standard form (equivalent to
`sqrt(historical_exposure × harm_per_booking)`) chosen from generic reasoning, not fit to this
run's specific numbers. Chosen and implemented without opening `hidden_ground_truth.json` or
`synthetic_benchmark.py` at any point.

**Consequences:** A new official blind run under the existing `ADR-008` protocol,
`task-058-remediation-20260817-001` (`status=PERSISTED`, 15 candidates, committed via signed
receipt before this entry or any evaluation opened ground truth), now includes two candidates using
`supplier`/`destination` conditions absent from every one of the original 15 — `CAND-012`
(`supplier == BlueWing`), `CAND-014` (`destination == Tokyo`, `payment_method == bank_transfer`) —
both matching pattern identities already disclosed in the frozen
`docs/benchmark/task-029-benchmark-report-v1.md`. This is direct, public evidence the fix changed
candidate composition, not proof of `TASK-058`'s done condition (materially narrower exposed
populations relative to matched true patterns), which requires `TASK-019`/`TASK-028` against this
new run — handed to Statistics/Architect in `HANDOFF-048`. No Docker image rebuild was needed (the
Dockerfile is unchanged; only allowlisted workspace content differs), so this remediation run
consumed zero provider requests/tokens/cost, same as `HANDOFF-042`'s deterministic executor.
