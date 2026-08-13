# Agent Handoffs

All unresolved cross-role work is recorded here. Status values are `OPEN`, `IN_PROGRESS`, `RESOLVED`, or `CANCELLED`. Resolved entries remain as durable history.

## HANDOFF-001

**Created:** 2026-08-13  
**From:** ARCHITECT  
**To:** DATA_ENGINEER  
**Status:** OPEN

**Task:** Define the immutable ingestion contract for `TASK-005`.

**Context:** The repository foundation, metadata models, PostgreSQL migration, API skeleton, security baseline, and synthetic travel fixture exist. Upload handling and customer-data storage intentionally do not exist. Architecture requires raw → normalized → analytical reproducibility and explicit feature timing.

**Question:** What typed ingestion manifest, validation stages, data-quality output, and lineage identifiers are required before implementing file acceptance?

**Files:**

- `ARCHITECTURE.md`
- `SECURITY.md`
- `TASKS.md`
- `packages/schemas/src/policy_schemas/domain.py`
- `tests/fixtures/synthetic_travel_bookings.csv`

**Expected output:** Reviewed ingestion/data-quality contract and proposed tests; any persistence or infrastructure questions handed back to Architect.

**Blocking:** YES — blocks `TASK-006` and acceptance of real customer data.

**Resolution:** Pending. This blocks `TASK-006` through `TASK-009`.

## HANDOFF-006

**Created:** 2026-08-13
**From:** DATA_ENGINEER
**To:** STATISTICS
**Status:** RESOLVED

**Task:** Independently review TASK-003 benchmark design and hidden ground truth.

**Context:** The deterministic 10,000-booking benchmark contains nine configured harmful patterns,
five confounding traps, temporal drift, heterogeneous effects, outcome-dependent missingness,
selection bias, explicit leakage fields, and a reproducible dirty-data layer. Public inputs are
physically separated from restricted evaluation truth. The generator source is also restricted
from ML Discovery because it necessarily encodes the mechanisms. Data Engineering makes no claim
about causal validity or benchmark difficulty calibration.

**Question:** Are the simulated effect mechanisms, confounding/selection traps, and ground-truth
representation suitable for later statistical validation without overstating identifiability?

**Files:**

- `packages/analytics/src/policy_analytics/synthetic_benchmark.py`
- `synthetic_data/evaluation/hidden_ground_truth.json`
- `synthetic_data/metadata/feature_timing.json`
- `SIMULATION_REPORT.md`

**Expected output:** Approve TASK-003 or request concrete simulation changes; record any constraints
needed by TASK-018, TASK-022, and TASK-028.

**Blocking:** YES — TASK-003 requires Statistics review before `DONE`.

**Resolution (2026-08-13, Statistics):** **Approved in substance, with two artifact changes required
before `DONE`.** The simulated mechanisms, five confounding traps, drift, heterogeneity,
outcome-dependent missingness, and leakage fields are suitable for statistical validation and do
not overstate identifiability. Verified against the generated artifacts:

1. **Ground truth carries no true effect size.** `hidden_ground_truth.json` records
   `affected_booking_ids` but no per-pattern effect in outcome units. `TASK-028` must score
   direction accuracy and impact error, which is impossible from membership alone. The nominal
   `loss` constants in the generator cannot substitute: injection runs through
   `max(0.0, gauss(42 + loss, 55 + 0.08 * loss))`, so truncation at zero and effect-dependent
   variance make the realized mean shift differ from the nominal constant. Required: a
   counterfactual regeneration pass (same seed, same draws, that pattern's effect disabled)
   recording the realized ATE per pattern per outcome. **Blocks `TASK-022` and `TASK-028`.**
2. **No customer identifier exists**, yet `repeat_purchase_180d` is an outcome. Repeat purchase
   presupposes a customer entity; without a stable ID the outcome cannot be linked or verified,
   and customer-level dependence cannot be clustered. Supplier has only 4 levels, below the
   contract's `min_clusters = 5`, so manager (8 levels) is currently the only usable clustering
   key. Required: a stable synthetic `customer_id`. **Blocks reliable interval estimation.**

Non-blocking observations recorded for later tasks: every trap is confounded by *observed*
columns, so correct adjustment recovers the null and the benchmark cannot yet test sensitivity to
*unmeasured* confounding — the core failure mode of gate G06 (request tracked for `TASK-004`
presets). P07 has zero development-split records and P09 zero validation-split records, so both
correctly fail the temporal-stability gate; this is contract-correct but requires a scoring
decision in `TASK-028`, and P07 is undiscoverable if discovery is fit on development alone. P05
(n=23) is below any defensible power floor against an outcome standard deviation of €766 and is a
structural false negative at this scale, which `TASK-029` must not record as a methodology failure.

Details and required changes are carried to Data Engineer as `HANDOFF-010`. `TASK-003` stays
`IN_REVIEW` because items 1 and 2 change the generated artifacts.

## HANDOFF-007

**Created:** 2026-08-13
**From:** CODE_REVIEWER
**To:** ARCHITECT
**Status:** RESOLVED

**Task:** Define and enforce the hidden-ground-truth access boundary for `TASK-003` and the blind
discovery workflow in `TASK-017`.

**Context:** Adversarial review found that `synthetic_data/evaluation/hidden_ground_truth.json` is
present in the same repository checkout as the public benchmark and discovery code. The evaluator
accepts caller-controlled `status: "PERSISTED"` and any non-empty `persisted_at`, so these fields do
not prove that candidates existed before ground-truth access. Directory naming, an explicit CLI
argument, and documentation do not enforce the critical rule that ML Discovery must never receive
hidden truth before candidate persistence.

**Question:** What repository/storage/CI identity boundary will keep evaluation truth unavailable
to the discovery actor, and what trusted persistence/audit mechanism will establish candidate
commitment before evaluation access is granted?

**Files:**

- `TASKS.md`
- `packages/analytics/src/policy_analytics/synthetic_benchmark.py`
- `scripts/evaluate_synthetic_benchmark.py`
- `synthetic_data/evaluation/hidden_ground_truth.json`
- `tests/analytics/test_synthetic_benchmark.py`

**Expected output:** An enforceable blind-evaluation design, implementation changes, and adversarial
tests proving that the discovery actor cannot read truth or self-assert persistence before
evaluation.

**Blocking:** YES — blocks shipping `TASK-003` as satisfying its critical blind-evaluation rule and
blocks a credible `TASK-017` run.

**Resolution (2026-08-13, Architect):** Resolved with ADR-008 and
`docs/blind_benchmark_protocol.md`. A strict allowlist builder creates a fresh workspace outside the
trusted checkout; it omits hidden truth, generator/evaluator implementation, corruption and
generation manifests, private benchmark metadata, and evaluation artifacts. The single command
`make export-public-benchmark destination=...` rebuilds the analytical dataset and emits only its
four approved partitions plus sanitized schema, feature-timing, outcome, and run metadata. The
evaluation identity signs the exact candidate SHA-256 plus bundle ID with an evaluator-only HMAC
key. Evaluation verifies that receipt before it
opens hidden truth and rejects missing/forged receipts or modified candidates. Adversarial tests
cover restricted-file injection and post-commit candidate mutation. Discovery must be launched as
a separate actor scoped only to the generated workspace; handing it the full checkout or signing
key invalidates the protocol.

## HANDOFF-002

**Created:** 2026-08-13
**From:** ML_DISCOVERY
**To:** DATA_ENGINEER
**Status:** RESOLVED

**Task:** Provide the leakage-safe, versioned analytical dataset required by `TASK-015`.

**Context:** `TASK-015` depends on `TASK-011`, which remains `BLOCKED`. The repository contains
only a 200-row test fixture, not an analytical dataset with separated decision-time features,
outcomes, identifiers, metadata, transformation configuration, and lineage. Its documented
synthetic interaction is already visible to ML Discovery, so it is also ineligible for the later
blind evaluation in `TASK-017`.

**Question:** When `TASK-011` is complete, what immutable dataset/version reference, approved
decision-time feature set, outcome columns, time field, split labels, and lineage manifest should
ML Discovery consume without access to hidden evaluation artifacts?

**Files:**

- `TASKS.md`
- `ARCHITECTURE.md`
- `tests/fixtures/README.md`
- future `TASK-011` analytical-dataset artifacts

**Expected output:** A versioned analytical dataset and manifest satisfying the anti-leakage
boundary, with hidden-ground-truth and evaluation artifacts inaccessible to ML Discovery until
candidates from `TASK-017` are persisted.

**Blocking:** YES — blocks `TASK-015` and `TASK-017`.

**Resolution (2026-08-13, Data Engineer):** Delivered dataset version
`travel-bookings-analytical-v1.0.0` under
`synthetic_data/analytical/travel-bookings-analytical-v1.0.0/`. ML Discovery may consume
`features.csv`, `identifiers.csv`, and `metadata.csv`; `manifest.json` supplies immutable dataset
identity `490c65655aff645ec8da845cff257f23edfccea4abe609553b576b5b800f91e8`, source and artifact
SHA-256 lineage, exact schemas, the approved decision-time set, `booking_date` as the decision
timestamp, `customer_id` as clustering key, and chronological split labels. No post-decision,
outcome, identifier, metadata, or unknown field appears in `features.csv`.

`outcomes.csv` is physically separate. Statistics subsequently completed TASK-013, so the rebuilt
manifest now attaches outcome contract v1.0.0 and records its Statistics-selected primary outcome;
Data Engineering did not choose or reinterpret it. Exact discovery input root:
`synthetic_data/analytical/travel-bookings-analytical-v1.0.0/`. Aggregate entrypoint:
`manifest.json`; dedicated contracts: `feature_manifest.json`, `outcome_columns_manifest.json`,
`excluded_columns_manifest.json`, and `version_metadata.json`. Reproduce with
`make analytical-dataset`. Hidden ground truth and generator source remain outside the permitted
discovery inputs until blind candidate persistence.

## HANDOFF-003

**Created:** 2026-08-13
**From:** ML_DISCOVERY
**To:** STATISTICS
**Status:** RESOLVED

**Task:** Provide the versioned outcome definition required by `TASK-015`, then validate serious
candidates after discovery.

**Context:** `TASK-015` depends on `TASK-013`, which remains `BLOCKED`. ML Discovery cannot choose
the harm outcome, statistical evidence rules, or causal interpretation. No discovery run or
candidate findings have been produced because neither the analytical dataset nor outcome contract
exists.

**Question:** Which versioned harm outcome(s), direction, units, eligibility rules, and missing-data
handling should discovery use? Once candidates are persisted, which `TASK-018` validation contract
and evidence-classification workflow should be applied?

**Files:**

- `TASKS.md`
- `agents/ML_DISCOVERY.md`
- `agents/STATISTICS.md`
- future `TASK-013` outcome-definition artifacts
- future persisted `TASK-015` candidate artifact

**Expected output:** An approved outcome contract for discovery and, after candidates exist,
uncertainty, robustness, confounding, multiple-testing, evidence-classification, and causal-language
review under `TASK-019` and `TASK-020`.

**Blocking:** YES — the outcome contract blocks `TASK-015`; candidate validation waits on a
completed discovery run.

**Resolution:** Fully closed 2026-08-13 by Statistics, in two steps. The second question closed
first: validation and evidence contract v1.0.0 in `docs/validation_contract.md` and
`packages/analytics/src/policy_analytics/validation/` (`TASK-018`, ADR-007), which fixes the gate
sequence, evidence-level requirements, permitted language, and policy-readiness matrix that
`TASK-019`/`TASK-020` apply; discovery obligations from it are carried as `HANDOFF-011`. The first
question — versioned harm outcome, direction, units, eligibility, and missing-data handling — was
blocked pending `TASK-011`; once Data Engineer delivered the analytical dataset
`travel-bookings-analytical-v1.0.0` (this handoff's resolution) with `outcomes.csv` deliberately
left undirected (`primary_outcome: null`, `outcome_contract.status: PENDING_TASK_013`), Statistics
closed `TASK-013`: outcome contract v1.0.0 in `docs/outcome_contract.md` and
`packages/analytics/src/policy_analytics/outcomes/`. Primary outcome is `contribution_margin_eur`
(EUR/booking, decrease = harm, 0% missingness verified against `outcomes.csv`); six secondary/
decomposition outcomes; `repeat_purchase_180d` is exploratory-only and MNAR-bounded (9.72% overall
missingness, rising to 45.7% among cancelled bookings vs. 7.2% otherwise — an outcome-dependent
selection trap confirmed empirically, not assumed). A sign-normalized harm-score convention and a
deterministic historical-exposure formula are given so `TASK-016` can rank candidates across
outcomes without inventing meaning. The contract is pinned to the dataset's identity hash so a
future regeneration cannot silently drift underneath it. `TASK-013` is `DONE`; `TASK-015`'s
dependencies (`TASK-011`, `TASK-013`) are both satisfied, unblocking it for ML Discovery to pick
up. Real-customer outcome definition (`OQ-002`) and outcome maturation/right-censoring on live
data remain explicitly out of scope — see `docs/outcome_contract.md` §1 and §7.

## HANDOFF-008

**Created:** 2026-08-13
**From:** PRODUCT
**To:** ARCHITECT
**Status:** OPEN

**Task:** Extend the `TASK-024` full finding persistence model to cover fields required by the `TASK-027` finding detail screen.

**Context:** The finding detail screen UX specification (`docs/product/finding-detail-screen.md`) is complete, written ahead of the backend so `TASK-024` can be scoped against real UI requirements instead of a second design pass later. The current `FindingRead` skeleton (`apps/api/app/api/schemas.py`) only has `title`, `pattern_definition`, `sample_size`, `evidence_level`, `status`, `warnings` — it has no raw/adjusted effect, uncertainty, impact, stability, or confounder-check fields.

**Question:** Can `TASK-024` include: (1) a templated/structured plain-language pattern summary; (2) raw effect and adjusted effect as separate values with uncertainty ranges; (3) a list of checked alternative explanations/confounders with an outcome label (ruled out / partially explains / inconclusive) — this is Statistics' analytical output (`TASK-021`/`TASK-022`), Architect just needs to persist and expose it; (4) stability broken down by segment/time period rather than a single flag; (5) estimated impact as a range plus an explicit "annualization justified" flag; (6) the outcome metric name/unit as data, not an assumed constant (see `OQ-002`); (7) a finding-lifecycle status distinct from the existing job-oriented `ResourceStatus` enum (e.g. candidate awaiting review / validated / rejected / superseded)?

**Files:**

- `docs/product/finding-detail-screen.md`
- `apps/api/app/api/schemas.py`
- `apps/api/app/findings/`
- `ARCHITECTURE.md` (finding fields, §"Findings are first-class")

**Expected output:** A `TASK-024` field design that covers the above, with Statistics confirming the shape of confounder-check and stability fields.

**Blocking:** NO — does not block finalizing the UX spec, but should be resolved before `TASK-024` implementation locks the schema, since a second schema change would re-trigger frontend rework.

**Resolution:** Pending Architect implementation. Progress 2026-08-13 (Product): `FINDING_PRODUCT_CONTRACT.md` now supplies the full concrete answer — a required/optional/qualified-only field list mapped directly onto `ValidationReport`/`EffectEstimate` field names, so Architect isn't choosing between Product's and Statistics' proposals. It also confirms this handoff's questions (1)–(6) are satisfied by fields `ValidationReport` already defines in code; only question (7) (finding-lifecycle status) remains genuinely undecided — same conclusion `HANDOFF-012` reached independently from the Statistics side. Superseding inline list; `HANDOFF-012` remains the parallel Statistics-side answer and the two are cross-checked as compatible in the contract's header.

## HANDOFF-009

**Created:** 2026-08-13
**From:** PRODUCT
**To:** ARCHITECT
**Status:** OPEN

**Task:** Implement `TASK-027` (finding detail screen) against `docs/product/finding-detail-screen.md` once `TASK-025` is unblocked.

**Context:** No "Frontend Agent" role exists in `agents/`; `TASKS.md` lists ARCHITECT as the implementation owner for TASK-026/TASK-027. The UX specification is complete and durable; only backend availability blocks implementation. The specification also flags that the request originally referred to this work as "TASK-026," which in `TASKS.md` is actually the findings *list* screen — this document covers TASK-027, the detail screen.

**Question:** None outstanding for Product; this is a build handoff, not a decision request. Implement once `TASK-025` delivers real persisted findings with the fields resolved via `HANDOFF-004`.

**Files:**

- `docs/product/finding-detail-screen.md`
- `TASKS.md` (TASK-025, TASK-026, TASK-027)

**Expected output:** Working finding detail screen matching the specification's structure, copy rules, evidence-level gating, and run-status gating.

**Blocking:** YES — blocks closing `TASK-027`, but does not block anything else; TASK-025/TASK-024 remain the actual critical-path blockers.

**Resolution:** Pending completion of `TASK-025`. Progress 2026-08-13 (Product): `FINDING_PRODUCT_CONTRACT.md` is now the authoritative source for copy rules — the exact permitted-verb wording ladder (quoted verbatim from `LANGUAGE_RULES` in code), the never-shown-without-qualification list, and the finalized `policy_readiness`-driven action matrix (§9), which supersedes this spec's own §7. Implement against the contract's wording, not hand-authored phrasing, once `TASK-025` unblocks.

## HANDOFF-004

**Created:** 2026-08-13
**From:** FRONTEND (ad hoc dispatch — not a role defined in `AGENTS.md`)
**To:** PRODUCT
**Status:** RESOLVED

**Task:** Provide the approved product specification for the Finding Detail screen required by `TASK-027`.

**Context:** `TASKS.md` records only a one-line goal for `TASK-027` ("Explain what was found, population, impact, raw/adjusted effect, evidence, stability, alternatives, warnings, and next step in business language"). No approved UX spec, section layout, field-by-field content, or evidence wording exists in `DECISIONS.md`, `memory/`, or elsewhere. `agents/PRODUCT.md` assigns finding/evidence UX ownership to Product; an implementer must not invent evidence wording or product semantics.

**Question:** What is the approved Finding Detail spec — sections, field list, exact wording per evidence level (the five levels fixed in `DECISIONS.md`), warnings/alternatives presentation, and the "next step" call-to-action — given that the underlying finding data model (`TASK-024`) does not exist yet?

**Files:** `TASKS.md`, `agents/PRODUCT.md`, `DECISIONS.md`

**Expected output:** An approved product spec/content doc for Finding Detail, and which fields are mandatory vs. optional against the current minimal `Finding` skeleton.

**Blocking:** YES — blocks any UI implementation of `TASK-027`.

**Resolution:** Resolved 2026-08-13 by PRODUCT: `docs/product/finding-detail-screen.md` is the approved specification — sections, section-by-section content rules, evidence-level pill wording (mapped 1:1 from the five `EvidenceLevel` values), warnings/alternatives-checked presentation, and an evidence-gated next-step action matrix (provisional pending `OQ-003`). It also lists, as mandatory-vs-not-yet-available, the fields still missing from the current minimal `Finding` skeleton — see `HANDOFF-008` to Architect for closing that gap via `TASK-024`. Note: the request that generated this repository's finding-detail work referred to it as "TASK-026," which is actually the findings *list* screen in `TASKS.md`; this spec covers `TASK-027`, the detail screen — flag this if "TASK-026" was genuinely intended.

## HANDOFF-005

**Created:** 2026-08-13
**From:** FRONTEND (ad hoc dispatch — not a role defined in `AGENTS.md`)
**To:** ARCHITECT
**Status:** OPEN

**Task:** Confirm implementation ownership and deliver the Findings detail API required by `TASK-027`.

**Context:** `TASK-027` depends on `TASK-025` (Findings API completion) → `TASK-024` (full finding persistence model) → `TASK-020`/`TASK-023` (evidence classification, economic impact engine), all currently `BLOCKED`. `apps/api/app/findings` is still the minimal skeleton noted in `TASK-002` ("Remaining evolution tracked by TASK-023"); it does not serve raw/adjusted effect, uncertainty, impact, evidence level, stability, warnings, or lineage. `apps/web/app` is an unmodified Next.js bootstrap shell (`layout.tsx`, `page.tsx`, `styles.css` only) with no findings routes. Separately: no `agents/FRONTEND.md` exists, and `AGENTS.md`/`agents/README.md` define no "Frontend" role — UI implementation is assigned to `ARCHITECT` with `PRODUCT` owning UX/content. This session was dispatched as a standalone "Frontend Coding Agent," which does not match the repository's actual role contract.

**Question:** (1) Should a dedicated Frontend role/file be added under `agents/`, or should UI implementation stay under `ARCHITECT` per the existing contract? (2) When is `TASK-025`'s findings-detail API expected to exist, and what schema will it expose, so the UI isn't built against an invented contract?

**Files:** `AGENTS.md`, `agents/README.md`, `TASKS.md`, `apps/api/app/findings`, `apps/web/app`

**Expected output:** A decision on Frontend role placement, and either a completed `TASK-025` API contract or explicit confirmation that `TASK-027` stays `BLOCKED` until then.

**Blocking:** YES — blocks any real implementation of `TASK-027`.

**Resolution:** Pending. Question (2) content is now addressed by `HANDOFF-008` (PRODUCT → ARCHITECT), which lists the specific fields the finding detail UX spec (`docs/product/finding-detail-screen.md`) requires from `TASK-024`. Question (1), Frontend role placement, is unresolved and remains Architect's/Founder Strategy's call — this repository's current contract has no Frontend role, so `HANDOFF-009` (implementation handoff for `TASK-027`) was addressed to `ARCHITECT`, matching `TASKS.md`'s existing "Implementation: ARCHITECT" ownership rather than assuming a new role.

## HANDOFF-014

**Created:** 2026-08-13
**From:** FOUNDER_STRATEGY
**To:** CUSTOMER_DISCOVERY

**Status:** RESOLVED

**Task:** Confirm whether any real customer agreement, real customer dataset, or customer interview has occurred, ahead of the requested repeatability assessment (raised as "TASK-044").

**Context:** A repeatability assessment was requested against the label "TASK-044." In the current registry (`TASKS.md`), `TASK-044` is "Third independent dataset pilot" (owner `CUSTOMER_DISCOVERY`); the actual "Repeatability assessment" is `TASK-045` (owner `FOUNDER_STRATEGY`, support `STATISTICS`), depending on `TASK-043` + `TASK-044`, which depend on `MILESTONE-M3` ("First real discovery"). `MILESTONE-M3` itself depends on `TASK-042` → `TASK-041` → ... → `TASK-037`, and `TASK-037` depends on "Real customer agreement" — all currently `BLOCKED`. No customer discovery interview summaries, real customer datasets, or validated findings exist anywhere in this repository (`memory/FINDINGS.md` and `memory/EXPERIMENTS.md` are both empty of entries). No repeatability assessment is possible before at least one real, customer-confirmed finding exists.

**Question:** Has any real customer conversation, LOI, dataset commitment, or interview happened outside this repository's memory that should be recorded? If not, what is the current status of securing the first real pilot customer (the dependency blocking `TASK-037`/`MILESTONE-M3`)?

**Files:** `TASKS.md`, `memory/CURRENT_STATE.md`, `memory/FINDINGS.md`, `agents/CUSTOMER_DISCOVERY.md`

**Expected output:** Either durable evidence of real customer engagement recorded in `memory/` (so the roadmap can proceed), or an explicit confirmation that customer acquisition for the first pilot has not started, so the Founder can prioritize that as the actual next bottleneck instead of downstream repeatability work.

**Blocking:** YES — blocks any credible go/no-go recommendation for repeatability or continued build investment.

**Resolution (2026-08-13, Customer Discovery):** Confirmed independently while working a separate
request to review "TASK-041" findings with a customer (that label maps to `TASK-042` in this
registry). No real customer conversation, LOI, dataset commitment, or interview exists anywhere in
this repository — `DECISIONS.md` records no customer agreement, and `memory/FINDINGS.md` /
`memory/EXPERIMENTS.md` remain empty. Customer acquisition for the first pilot has not started.
This is the actual current bottleneck: everything from `TASK-037` through `MILESTONE-M3` is gated
on it, and no task in the registry currently tracks "secure the first real pilot customer" as
active work — Phase 14 assumes it as a precondition rather than owning it. Recommend Founder
Strategy treat first-pilot acquisition (founder-led sales / buyer mapping) as the top-priority
Customer Discovery task ahead of anything else in Phase 14/15. A findings-review protocol was
prepared in advance (`docs/customer_findings_review_protocol.md`) so `TASK-042` can execute
immediately once a customer, real dataset, and validated finding exist — but that is not evidence
of validation itself.

## HANDOFF-010

**Created:** 2026-08-13
**From:** STATISTICS
**To:** DATA_ENGINEER
**Status:** RESOLVED

**Task:** Supply the benchmark and analytical-dataset artifacts the validation contract requires.

**Context:** Validation contract v1.0.0 (`TASK-018`) is preregistered. Its gates cannot be
evaluated without inputs that do not exist yet, and its acceptance test against the benchmark
(`docs/validation_contract.md` §10) cannot be scored without ground-truth effect sizes. This
handoff carries the concrete changes from the `HANDOFF-006` benchmark review plus the dataset
requirements for `TASK-011`/`TASK-012`.

**Question:** Can the following be provided?

1. Per-pattern realized ATE per outcome in `hidden_ground_truth.json`, from a counterfactual
   regeneration pass with the pattern's effect disabled under the same seed and draws. Nominal
   `loss` constants are not usable: zero-truncation and effect-dependent variance in
   `max(0.0, gauss(42 + loss, 55 + 0.08 * loss))` make realized shifts differ from nominal.
2. A stable synthetic `customer_id`, without which `repeat_purchase_180d` cannot be linked or
   verified and customer-level dependence cannot be clustered.
3. In the analytical dataset: an explicit clustering key per record, chronological split labels,
   per-column feature timing carried through transformations, and per-column missingness rates
   broken down by exposure group (required by gate G07).
4. In `TASK-004` presets: at least one trap driven by an *unobserved* common cause. Every current
   trap is confounded by observed columns, so the benchmark cannot test sensitivity to unmeasured
   confounding — the failure mode gate G06 exists for.

**Files:**

- `docs/validation_contract.md`
- `packages/analytics/src/policy_analytics/validation/contract.py`
- `packages/analytics/src/policy_analytics/synthetic_benchmark.py`
- `synthetic_data/evaluation/hidden_ground_truth.json`

**Expected output:** Regenerated benchmark artifacts with per-pattern true effects and a customer
identifier, and a `TASK-011`/`TASK-012` dataset manifest carrying clustering key, split labels,
timing, and grouped missingness.

**Blocking:** YES — items 1 and 2 block `TASK-003` closure, `TASK-022`, and `TASK-028`; item 3
blocks `TASK-019`. Item 4 is not blocking.

**Resolution (2026-08-13):** Items 1–3 are delivered. Hidden truth now contains paired realized
effects for every pattern/outcome from identical-seed replay with only that pattern disabled;
nominal loss constants are not substituted for effects. The stable `customer_id`, clustering key,
chronological labels, timing lineage, split/overall missingness, and candidate-specific grouped
missingness helper are present. Item 4 was explicitly non-blocking and remains scoped to TASK-004.

## HANDOFF-011

**Created:** 2026-08-13
**From:** STATISTICS
**To:** ML_DISCOVERY
**Status:** RESOLVED

**Task:** Record the search space in the discovery run manifest, and persist candidates in the
shape validation consumes.

**Context:** Gate G05 controls the false discovery rate over the family of hypotheses discovery
*evaluated*, not the ones it reported. A search over 500 rules that returns its best 15 has a
family of 500, and `benjamini_hochberg_adjusted(..., family_size=500)` enforces that. Without the
evaluated count, no candidate can pass G05 and nothing this system produces can exceed
`descriptive_observation` — regardless of how strong the pattern looks.

**Question:** Can the `TASK-015`/`TASK-017` run manifest record (1) the number of candidate
hypotheses actually evaluated, including those pruned or discarded, (2) the search configuration
and seed that produced it, and (3) per candidate: the exact condition, the split it was fit on,
support, and the raw effect — with no post-hoc editing of conditions after validation results are
seen? Re-specifying a candidate after seeing its validation result creates a new candidate in a new
family and must be persisted as such.

**Files:**

- `docs/validation_contract.md` (§4, gate G05)
- `packages/analytics/src/policy_analytics/validation/grading.py`
- `TASKS.md` (`TASK-015`, `TASK-016`, `TASK-017`)

**Expected output:** A discovery run manifest carrying the evaluated-hypothesis count and search
configuration, and persisted candidates with immutable conditions.

**Blocking:** YES — blocks any evidence level above `descriptive_observation` in `TASK-019`.

**Resolution (2026-08-13, ML Discovery):** Implemented in
`packages/analytics/src/policy_analytics/discovery/engine.py` and persisted in
`artifacts/discovery/task-015-candidates.json`. The run records the exact search config and seed,
6,945 evaluated hypotheses (including discarded/pruned rules), dataset/outcome-contract versions,
and for each candidate the immutable exact condition, fit split, support, N, raw difference,
historical exposure, stability diagnostics, actionability, and warnings. Conditions were selected
on development only and were not edited after later-split diagnostics. Methodology is documented in
`docs/discovery_engine_v0.md`. Candidate validation is now routed back to Statistics in
HANDOFF-016.

## HANDOFF-016

**Created:** 2026-08-13
**From:** ML_DISCOVERY
**To:** STATISTICS
**Status:** OPEN

**Task:** Validate the serious TASK-015 candidate patterns under validation contract v1.0.0.

**Context:** Discovery engine v0 evaluated 6,945 hypotheses and persisted 15 interpretable
candidate conjunctions against the preregistered primary outcome `contribution_margin_eur` on
dataset `travel-bookings-analytical-v1.0.0` (identity
`490c65655aff645ec8da845cff257f23edfccea4abe609553b576b5b800f91e8`). Candidate conditions were
fit and ranked on development only; validation and future-holdout metrics are descriptive temporal
diagnostics. All reported effects and economic exposures are raw, unadjusted, unannualized
associations. No causal claim is made. The leading candidate family prominently contains high
discount conditions; this may reflect confounding, selection, broad main effects, or benchmark
structure and must not be interpreted as a policy finding before independent validation.

**Question:** Apply TASK-019/TASK-020 to the persisted candidates: uncertainty with customer-level
clustering, BH correction using family size 6,945, leakage/selection/missingness checks,
temporal/segment stability, confounding and robustness analysis, and the permitted evidence grade.
Which candidates survive, and what evidence-bounded language is allowed?

**Files:**

- `artifacts/discovery/task-015-candidates.json`
- `docs/discovery_engine_v0.md`
- `docs/validation_contract.md`
- `packages/analytics/src/policy_analytics/discovery/engine.py`
- `synthetic_data/analytical/travel-bookings-analytical-v1.0.0/`

**Expected output:** Validation reports and evidence classification for every serious candidate;
rejections with explicit failed gates; no causal language beyond the assigned evidence level.

**Blocking:** YES — candidates cannot become durable findings or policy candidates before this
review.

**Resolution:** Pending.

## HANDOFF-027

**Created:** 2026-08-13
**From:** DATA_ENGINEER
**To:** ML_DISCOVERY
**Status:** RESOLVED

**Task:** Deliver the versioned TASK-012 split contract for blind discovery.

**Context:** TASK-011 dataset `travel-bookings-analytical-v1.0.0` now carries deterministic,
non-overlapping chronological membership under split config
`travel-bookings-temporal-split-v1.0.0`. Statistics already fixed discovery usage in TASK-013
v1.1.0, so Data Engineering did not choose new statistical windows.

**Question:** None; this is a completed input handoff.

**Files:**

- `synthetic_data/analytical/travel-bookings-analytical-v1.0.0/feature_manifest.json`
- `synthetic_data/analytical/travel-bookings-analytical-v1.0.0/split_manifest.json`
- `synthetic_data/analytical/travel-bookings-analytical-v1.0.0/split_membership.csv`

**Expected output:** ML Discovery must use only the 4,999 rows whose `split_label` is
`development` for condition fitting, selection, tuning, and ranking. Validation and future
holdout rows are diagnostic-only and cannot modify candidate conditions.

**Blocking:** NO — delivered.

**Resolution:** Dataset ID
`98ad4e7e08e63ee9e31f9317ca408f2895da8bece49324482915e24df0aee04c`; input root
`synthetic_data/analytical/travel-bookings-analytical-v1.0.0/`; reproduce with
`make temporal-splits`. Hidden evaluation artifacts remain outside the blind allowlist.

## HANDOFF-012

**Created:** 2026-08-13
**From:** STATISTICS
**To:** ARCHITECT
**Status:** OPEN

**Task:** Persist the validation report contract in `TASK-024` and enforce evidence-bounded
language at the API edge.

**Context:** `ValidationReport` in `packages/analytics/src/policy_analytics/validation/report.py`
is the sanctioned output of validation; constructing one re-derives the evidence level from the
gate results, so a report cannot claim more than its checks support. `HANDOFF-008` asks Statistics
to confirm the shape of the confounder-check and stability fields for the finding detail screen —
this is that answer. `PolicyReadiness` currently lives in the analytics package because the
evidence vocabulary is Statistics-owned; whether it belongs in `policy_schemas` alongside
`EvidenceLevel` is an Architect call.

**Question:** For `TASK-024`, can the finding model persist: per-gate results (gate ID, outcome,
detail) rather than a single boolean; raw and adjusted effects each as value plus interval plus
method plus unit; the BH-adjusted p-value and the family size it was computed against; controlled
variables and potential confounders as separate lists; robustness tests run; stability broken down
by split; contract version; and policy readiness? Should `PolicyReadiness` move into
`policy_schemas.domain`? The API must not emit text stronger than `LANGUAGE_RULES` permits for the
persisted evidence level — is that enforced in serialization or in the service layer?

**Files:**

- `packages/analytics/src/policy_analytics/validation/report.py`
- `packages/analytics/src/policy_analytics/validation/contract.py` (`LANGUAGE_RULES`)
- `apps/api/app/api/schemas.py`
- `docs/product/finding-detail-screen.md`

**Expected output:** A `TASK-024` field design covering the report contract, a decision on
`PolicyReadiness` placement, and an enforcement point for evidence-bounded language.

**Blocking:** NO — but should be resolved before `TASK-024` locks the schema, since the report
shape is now fixed and a later change re-triggers frontend rework.

**Resolution:** Pending.

## HANDOFF-013

**Created:** 2026-08-13
**From:** STATISTICS
**To:** PRODUCT
**Status:** OPEN

**Task:** Align finding presentation with the approved evidence and readiness rules, and supply the
customer economics behind the materiality threshold.

**Context:** `OQ-003` is resolved: `docs/validation_contract.md` §6–§7 fixes the evidence-to-
readiness matrix and the permitted wording per level. The next-step action matrix in
`docs/product/finding-detail-screen.md` was written provisionally pending that decision and can now
be made final. Two constraints Product should know are binding: at levels 1–3 the causal verbs
(*causes, drives, leads to, reduces, increases*) are forbidden in all customer-facing text, and
economic impact at those levels is presented as **exposure** — value at stake in these records —
never as savings. Nothing can reach `HIGH_CONFIDENCE` until a policy backtest exists (`TASK-032`),
so the strongest readiness the first pilot can show is `SHADOW_POLICY`.

**Question:** The materiality thresholds in `ValidationThresholds`
(`min_material_annual_impact = 25000`, `min_material_outcome_share = 0.005`) are placeholders that
decide which findings are publishable at all. What are the real thresholds for the pilot customer —
below what annual figure is a finding not worth a decision to them? This depends on the same
customer economics as `OQ-002`.

**Files:**

- `docs/validation_contract.md` (§6, §7, §8)
- `docs/product/finding-detail-screen.md`
- `memory/OPEN_QUESTIONS.md` (`OQ-002`, `OQ-003`, `OQ-004`)

**Expected output:** A finalized next-step action matrix consistent with the readiness rules, and a
customer-grounded materiality threshold to replace the placeholder.

**Blocking:** NO — the placeholder is usable for synthetic work; it must be replaced before any
real-customer finding is published.

**Resolution:** Partially resolved 2026-08-13 (Product). The action-matrix half is done:
`FINDING_PRODUCT_CONTRACT.md` §9 finalizes it, driven by `policy_readiness` alone (redundant to also
gate on evidence level, since readiness already encodes it), and `docs/product/finding-detail-screen.md`
§7 now points there instead of keeping its own copy. The materiality-threshold half remains open —
Product cannot produce a real number from synthetic data; it requires an actual pilot customer's
economics, which does not exist until `TASK-057` delivers one, and belongs jointly with Customer
Discovery per `OQ-004`'s ownership. Redirected, not answered — see `HANDOFF-021`.

## HANDOFF-015

**Created:** 2026-08-13
**From:** STATISTICS
**To:** DATA_ENGINEER
**Status:** RESOLVED

**Note:** Originally logged as `HANDOFF-014`, colliding with the existing Founder Strategy →
Customer Discovery `HANDOFF-014` above; renumbered for a unique ID since `TASKS.md` (`TASK-042`
note) already references that entry by number.

**Task:** Update the analytical dataset manifest to reference the now-published outcome contract.

**Context:** `manifest.json` for `travel-bookings-analytical-v1.0.0` deliberately records
`primary_outcome: null` and `outcome_contract.status: "PENDING_TASK_013"`, correctly refusing to
direct an outcome until Statistics closed `TASK-013`. That contract now exists (`HANDOFF-003`
resolution, `docs/outcome_contract.md`, `OUTCOME_CONTRACT_VERSION = "1.0.0"`), pinned to this exact
`dataset_identity_sha256`. Statistics is not editing `manifest.json` directly — it is Data
Engineer's artifact and its lineage/checksum fields belong to that role.

**Question:** Can `manifest.json.outcome_contract` be updated to `status: "ATTACHED"`,
`primary_outcome: "contribution_margin_eur"`, and a reference to
`outcome_contract_version: "1.0.0"`, so a consumer reading only the manifest (without cross-
referencing `docs/outcome_contract.md`) sees the current state correctly?

**Files:**

- `synthetic_data/analytical/travel-bookings-analytical-v1.0.0/manifest.json`
- `docs/outcome_contract.md`
- `packages/analytics/src/policy_analytics/outcomes/contract.py`

**Expected output:** Updated manifest with a consistent lineage hash (or a documented reason the
identity hash is unaffected by a metadata-only change).

**Blocking:** NO — `docs/outcome_contract.md` is authoritative regardless; this is a consistency
improvement so the manifest does not read as stale.

**Resolution (2026-08-13, Data Engineer):** Attached Statistics-owned outcome contract v1.0.0 in
the aggregate and standalone outcome manifests. `primary_outcome` is
`contribution_margin_eur`, copied from `PRIMARY_OUTCOME_ID`; definitions, directions, units,
missing-data policies, cohort rule, and comparison rule are copied from the executable TASK-013
contract without reinterpretation. Dataset identity remains
`490c65655aff645ec8da845cff257f23edfccea4abe609553b576b5b800f91e8` because it identifies source
rows plus timing schema; attaching versioned metadata does not change partition bytes. Each
metadata artifact has its own SHA-256 in `manifest.json.supporting_artifacts`.

## HANDOFF-020

**Created:** 2026-08-13
**From:** PRODUCT
**To:** STATISTICS
**Status:** OPEN

**Task:** Resolve five wording/presentation questions raised while writing `FINDING_PRODUCT_CONTRACT.md`, deliberately not answered by Product because they touch statistical meaning, not just display.

**Context:** `FINDING_PRODUCT_CONTRACT.md` builds the Finding v0 field contract directly from `ValidationReport`/`LANGUAGE_RULES`/`docs/validation_contract.md` and invents no thresholds. A handful of presentation choices remain that could misrepresent methodology if Product decided them alone.

**Question:**

1. Standardized wording when an impact interval crosses zero — is there a preferred phrase (parallel to the backtest section's "no measurable net effect," `docs/validation_contract.md` §9), and should it also apply outside backtests, to ordinary economic-impact display?
2. Should `adjusted_p_value` / `family_size` ever be customer-facing, or stay analyst/audit-only? Product has no position; this is a Statistics + Architect call.
3. Display wording for `NOT_EVALUATED` gates (graded identically to `FAIL` per `GateOutcome`): "not yet evaluated" (reads as pending) or "failed" (reads as checked-and-rejected)? These leave different impressions of the same programmatic outcome.
4. The contract's §1 groups `controlled_variables` ("adjusted for") and `potential_confounders` ("considered and still possible") as two lists under one "what was checked" business narrative. Confirm this framing doesn't misrepresent the methodology to a reader who conflates the two.
5. Confirm the finding-lifecycle status vocabulary question (candidate/validated/rejected/superseded, distinct from `ResourceStatus`) — already open via `HANDOFF-008`/`HANDOFF-012` — is being tracked for `TASK-024` and isn't falling through between the two handoffs.

**Files:**

- `FINDING_PRODUCT_CONTRACT.md` (§10)
- `docs/validation_contract.md`
- `packages/analytics/src/policy_analytics/validation/contract.py` (`LANGUAGE_RULES`, `GateOutcome`)
- `packages/analytics/src/policy_analytics/validation/report.py` (`ValidationReport`)

**Expected output:** Answers to (1)–(4), and confirmation on (5); update `FINDING_PRODUCT_CONTRACT.md` §10 accordingly once answered.

**Blocking:** NO — the contract is usable as drafted; these refine wording precision before `TASK-024`/`TASK-025` implementation locks in copy.

**Resolution:** Pending.

## HANDOFF-021

**Created:** 2026-08-13
**From:** PRODUCT
**To:** CUSTOMER_DISCOVERY
**Status:** OPEN

**Task:** Supply (or confirm the continued absence of) the real customer economics needed to replace the materiality-threshold placeholder — the half of `HANDOFF-013` (Statistics → Product) that Product cannot answer.

**Context:** `HANDOFF-013` asked Product for the real materiality threshold behind `OQ-004` (`min_material_annual_impact = 25000`, `min_material_outcome_share = 0.005`, currently placeholders). Product finalized the action-matrix half of that handoff in `FINDING_PRODUCT_CONTRACT.md` §9/§11, but the threshold itself requires an actual pilot customer's P&L — data this repository does not have. `agents/PRODUCT.md` explicitly does not own customer willingness/economics; `agents/CUSTOMER_DISCOVERY.md` does. `TASK-057` (secure first real pilot customer, `ADR-010`) is the current bottleneck and, per `HANDOFF-014`'s resolution, has not started.

**Question:** Is there any real customer economic data (even partial — approximate annual booking volume, typical margin, or a customer's own stated "not worth it below €X" figure) available from Customer Discovery's work so far? If not — expected, given `TASK-057` is still `TODO` — please confirm explicitly so `OQ-004` stays correctly `OPEN` rather than silently stale, and flag this handoff as one of the concrete outputs `TASK-057` should produce once a pilot customer exists.

**Files:**

- `memory/OPEN_QUESTIONS.md` (`OQ-004`)
- `memory/HANDOFFS.md#HANDOFF-013`
- `FINDING_PRODUCT_CONTRACT.md` (§11)
- `TASKS.md` (`TASK-057`)

**Expected output:** Either real customer economics recorded (updating `OQ-004` and reversioning the validation contract's thresholds, which is then a further handoff back to Statistics), or explicit confirmation that none exists yet, keeping the placeholder in force for synthetic work only.

**Blocking:** NO — the placeholder remains usable for synthetic work; this must resolve before any real-customer finding is published.

**Resolution:** Pending.

## HANDOFF-017

**Created:** 2026-08-13
**From:** CODE_REVIEWER
**To:** ARCHITECT
**Status:** RESOLVED

**Task:** Close repository-readiness gaps in the blind execution boundary, CI, and local tooling
before the analytical pipeline proceeds.

**Context:** Readiness review confirmed that an ML Discovery agent launched in the normal shared
repository can directly read both `synthetic_data/evaluation/hidden_ground_truth.json` and the
generator source that encodes every pattern. ADR-008 is credible only when Discovery is a separate
actor scoped exclusively to the exported workspace. The documented export command currently fails
with `ModuleNotFoundError: policy_schemas`. Candidate commitment also accepts any caller-supplied
manifest with a matching bundle ID; it does not prove that the evaluator issued or validated that
manifest. CI does not regenerate committed benchmark/analytical artifacts and fail on drift, nor
does it test Alembic downgrade/model-to-migration drift.

**Question:** What enforced launcher/identity boundary will guarantee that Discovery receives only
the allowlisted workspace, how will issued bundle manifests be authenticated or registered before
candidate signing, and which CI/local-setup checks will make the documented workflow executable?

**Files:** `.github/workflows/ci.yml`, `Makefile`, `docs/blind_benchmark_protocol.md`,
`packages/analytics/src/policy_analytics/blind_isolation.py`, `scripts/prepare_blind_workspace.py`,
`apps/api/migrations/`

**Expected output:** A working isolated blind-run entrypoint; evaluator verification of an issued
and validated bundle; CI checks for generated-artifact drift and migration consistency; documented
successful commands.

**Blocking:** YES — blocks a credible `TASK-017` blind run and repository readiness for analytics.

**Resolution (2026-08-13, Architect implementation):** Blind export now has complete package paths,
requires an evaluator-owned key, and emits a coordinator-signed exact-allowlist manifest.
Candidate commitment rejects forged/incomplete manifests. `make blind-shell workspace=...` launches
a no-network, read-only-root container with only the issued workspace mounted; a repository-scoped
agent is explicitly ineligible. CI smoke-tests export, generated-artifact drift, repository data,
Alembic check, downgrade, and upgrade. Local PostgreSQL integration and migration round-trip passed.

## HANDOFF-018

**Created:** 2026-08-13
**From:** CODE_REVIEWER
**To:** DATA_ENGINEER
**Status:** RESOLVED

**Task:** Make analytical dataset versioning immutable and fully content-addressed, and tighten the
repository data-commit boundary.

**Context:** `build_analytical_dataset` writes into an existing fixed version directory with
`exist_ok=True` and overwrites partitions/manifests. Its `dataset_identity_sha256` hashes only the
version label, source CSV, and timing manifest; it excludes transformation code/version/config,
outcome contract, and output partition hashes. A changed transformation can therefore replace
`travel-bookings-analytical-v1.0.0` while retaining the same identity. Separately, `.gitignore`
unignores every CSV anywhere under `synthetic_data/`, so a mistakenly placed customer export could
become committable without a fixture allowlist or provenance guard.

**Question:** What immutable version/identity contract should bind source, timing, transformation,
configuration, contracts, and output bytes, and which exact synthetic paths may be committed while
all other data remains denied by default?

**Files:** `.gitignore`, `packages/analytics/src/policy_analytics/analytical_dataset.py`,
`synthetic_data/analytical/travel-bookings-analytical-v1.0.0/manifest.json`

**Expected output:** Fail-on-existing immutable writes or atomic creation of a new content-addressed
version; complete lineage identity; explicit synthetic artifact allowlist and tests/CI guard against
customer/private data commits.

**Blocking:** YES — blocks treating the current analytical dataset identity as immutable lineage.

**Resolution (2026-08-13, Data Engineer implementation):** Analytical builds now fail if the target
version directory exists. The reproducibility command builds into a temporary directory and only
accepts an existing version when every generated byte matches. Dataset identity binds source,
timing, complete transformation config, transformation implementation hash, outcome contract
version, schema version, and all partition hashes. Manifest paths are relative. `.gitignore` and
`scripts/check_repository_data.py` restrict tracked data to seven explicit synthetic fixtures; CI
enforces the allowlist. The strengthened `v1.0.0` identity is
`98ad4e7e08e63ee9e31f9317ca408f2895da8bece49324482915e24df0aee04c`.

## HANDOFF-019

**Created:** 2026-08-13
**From:** CODE_REVIEWER
**To:** STATISTICS
**Status:** RESOLVED

**Task:** Finish the benchmark truth fields required before downstream validation begins.

**Context:** During the readiness review the outcome contract and its tests changed concurrently;
the final reviewed snapshot passes the Python outcome-contract tests and Ruff. Existing
`HANDOFF-010` still records the unresolved need for per-pattern realized counterfactual effects in
hidden ground truth, required by later direction and impact-error evaluation. This review does not
assess unimplemented statistical methods.

**Question:** Can Statistics confirm that `HANDOFF-010` item 1 remains a blocker before `TASK-003`
is closed and accept the eventual ground-truth effect representation?

**Files:** `packages/analytics/src/policy_analytics/outcomes/contract.py`,
`tests/analytics/test_outcome_contract.py`, `synthetic_data/evaluation/hidden_ground_truth.json`,
`memory/HANDOFFS.md` (`HANDOFF-010`)

**Expected output:** An explicit acceptance/rejection of the ground-truth effect representation
needed by later benchmark evaluation.

**Blocking:** YES — `TASK-003` remains `IN_REVIEW` and later benchmark direction/impact-error
evaluation lacks approved truth effects.

**Resolution (2026-08-13, Statistics):** Confirmed — `HANDOFF-010` item 1 (per-pattern realized ATE
per outcome, from a counterfactual regeneration pass with each pattern's effect disabled under the
same seed/draws) remains an open blocker on `TASK-003` closure, `TASK-022`, and `TASK-028`, exactly
as recorded there. Nothing in the concurrent outcome-contract work (v1.0.0 or the v1.1.0 amendment
in this session, ADR-011) substitutes for it or narrows its scope: this item is about ground-truth
*injected* effects for benchmark scoring, not about the outcome *definition* discovery/validation
consume — the two are independent artifacts. No eventual ground-truth effect representation is
being pre-approved here; when Data Engineer delivers a regeneration, Statistics reviews the actual
representation (units, per-outcome breakdown, sign convention matching this outcome contract's
`harm_multiplier`) before accepting it, per the original `HANDOFF-010`/`HANDOFF-006` review
standard. Item 2 of `HANDOFF-010` (customer identifier) is separately confirmed delivered.

## HANDOFF-022

**Created:** 2026-08-13
**From:** CUSTOMER_DISCOVERY
**To:** FOUNDER_STRATEGY
**Status:** OPEN

**Task:** Resolve four ICP/positioning decisions raised by `CUSTOMER_DATA_ACQUISITION_PLAN.md`
before real data starts arriving from prospects outside travel agencies.

**Context:** `TASK-057` and the entire built pipeline (canonical schema, synthetic benchmark,
outcome contract) are travel-agency-specific. The requested acquisition plan targets three
verticals — travel agencies, recruitment/staffing agencies, and B2B wholesale distributors — to
source 20 prospects toward 3–5 real historical datasets for research, explicitly not validating
product sales. This widens data-acquisition scope beyond what `TASK-057`'s text and the current
canonical schema (`TASK-010`, travel-booking specific) assume, without any registry decision
having been made about that widening.

**Question:**
1. Does non-travel data get run through the existing pipeline (requiring new canonical-schema/
   outcome-contract work per vertical before any real discovery run), or is it collected now and
   analyzed manually/exploratorily outside the productized pipeline until one vertical is chosen?
2. Should Product predefine an outcome-definition template per vertical before outreach starts
   (multiplying `OQ-002`/`OQ-004` by three), or should Customer Discovery gather data first and
   resolve outcome definition per prospect afterward?
3. Should outreach mention a possible future product/pilot pricing at all, even softly, or stay
   strictly "independent research, no product" as currently drafted — this affects the data-use
   agreement wording and the narrative later used for `TASK-048`/fundraising materials?
4. Should travel agencies remain the clear #1 outreach priority (only vertical the pipeline
   actually supports today), with recruitment/distribution run as secondary validation of
   generality, or should all three be run at genuinely equal priority as currently drafted?

**Files:** `CUSTOMER_DATA_ACQUISITION_PLAN.md`, `TASKS.md` (`TASK-057`, `TASK-010`), `DECISIONS.md`
(`ADR-010`), `memory/OPEN_QUESTIONS.md` (`OQ-002`, `OQ-004`)

**Expected output:** A decision (recorded in `DECISIONS.md` if durable) on scope sequencing and
positioning, so outreach in the two non-travel verticals doesn't produce data with nowhere
approved to go.

**Blocking:** NO — outreach can start under the travel-agency track regardless; this blocks
committing real effort to the recruitment/distribution tracks in `CUSTOMER_DATA_ACQUISITION_PLAN.md`
§2.2/§2.3 in parallel rather than sequentially.

**Resolution (2026-08-13, implementation delivered for Statistics review):** The executable outcome
contract and tests are internally consistent and pass. Hidden truth now includes per-pattern,
per-outcome paired realized effects from identical-seed replay with only the selected pattern
disabled, including the estimand and paired record count. Nominal loss constants are not reported
as realized effects. This delivers `HANDOFF-010` item 1; Statistics retains authority to accept the
representation when completing TASK-003 review.

## HANDOFF-023

**Created:** 2026-08-13
**From:** STATISTICS
**To:** ML_DISCOVERY
**Status:** OPEN

**Task:** Adopt outcome contract v1.1.0 for any future discovery/ranking work; no action required on the existing `TASK-015` run.

**Context:** `TASK-013` is amended to v1.1.0 (ADR-011, `docs/outcome_contract.md` §9,
`packages/analytics/src/policy_analytics/outcomes/contract.py`). This does not reopen the primary
outcome, direction, or sign convention — it makes explicit, and machine-readable as
`DISCOVERY_CONTRACT`, several rules that were previously implicit: an empirically verified
`valid_range` per outcome (for anomaly-flagging, never clipping), a no-winsorization/no-transform
rule at discovery time, an explicit per-outcome aggregation rule, the mandatory search-fit split,
the minimum-support floor (imported from the validation contract's own gate G03, not a second
number), the excluded explanatory-variable classifications, and missing-outcome handling specific
to discovery.

**Verification already performed:** All 15 candidates in
`artifacts/discovery/task-015-candidates.json` were checked against every new rule and are
compliant — every condition uses only `DECISION_TIME` features (from `feature_manifest.json`'s 18
approved columns), every candidate has `n_exposed >= 50` on `development`, and conditions were fit
on `development` only with `validation`/`future_holdout` used strictly as diagnostics, matching
`HANDOFF-011`'s resolution. **No rerun of `TASK-015` is required.**

**Question:** None outstanding — this is a confirmatory handoff, not a decision request. For
`TASK-016` (candidate ranking) and any future discovery iteration: use `DISCOVERY_CONTRACT` as the
single source for the search-split rule, support floor, and excluded-feature list rather than
re-deriving them; candidate descriptions must stay within the causal-language limits in
`docs/outcome_contract.md` §9.4 even before validation assigns an evidence level. Separately,
`HANDOFF-016` (your request that Statistics validate the persisted candidates under `TASK-018`)
remains open and unaffected by this amendment — it is not addressed here.

**Files:**

- `docs/outcome_contract.md` (§9)
- `packages/analytics/src/policy_analytics/outcomes/contract.py` (`DISCOVERY_CONTRACT`)
- `artifacts/discovery/task-015-candidates.json`

**Expected output:** Acknowledgement; use `DISCOVERY_CONTRACT` for `TASK-016` and any future
discovery runs.

**Blocking:** NO — informational; the existing `TASK-015` artifact already complies.

**Resolution:** Pending.

## HANDOFF-024

**Created:** 2026-08-13
**From:** ARCHITECT
**To:** PRODUCT
**Status:** OPEN

**Task:** Finalize the Finding lifecycle enum and deterministic summary/title contract for
TASK-024.

**Context:** `docs/finding_persistence_contract.md` separates immutable CandidatePattern,
ValidationReport, and promoted Finding. The existing `ResourceStatus` describes jobs and cannot
represent Finding lifecycle. `FINDING_PRODUCT_CONTRACT.md`, HANDOFF-008, and HANDOFF-012 all flag
the lifecycle vocabulary as unresolved. The persistence migration cannot make a Finding status
column non-null or expose it through API schemas until Product fixes the allowed states and
transitions. Product also requires a deterministic plain-language summary, but its exact template
and whether title is stored or derived are not fixed.

**Question:** What exact Finding lifecycle enum and transition rules should TASK-024 persist? Is
the business summary/title stored as a versioned deterministic snapshot, derived on every read, or
both; and what template version identifies it?

**Files:**

- `docs/finding_persistence_contract.md`
- `FINDING_PRODUCT_CONTRACT.md`
- `docs/product/finding-detail-screen.md`
- `apps/api/app/findings/contracts.py`

**Expected output:** Final enum values/transitions and a versioned deterministic summary/title
contract suitable for Pydantic, database constraints, and API serialization.

**Blocking:** YES — blocks locking and implementing the TASK-024 Finding table/API shape, but does
not block CandidatePattern or ValidationReport table preparation.

**Resolution:** Pending.

## HANDOFF-025

**Created:** 2026-08-13
**From:** ARCHITECT
**To:** STATISTICS
**Status:** OPEN

**Task:** Finalize the versioned TASK-023 economic-impact output consumed by Finding persistence.

**Context:** Product requires affected records, per-record effect with interval, historical impact
with interval, outcome name/unit, materiality result, and explicitly gated annualization.
`EconomicImpactPersistence` in `apps/api/app/findings/contracts.py` is only a storage envelope for
those already-requested fields; Architect has not defined their estimators or semantics. TASK-023
is still BLOCKED on TASK-021 and has no executable result contract/version.

**Question:** Confirm or replace the proposed envelope fields and define the authoritative
versioned TASK-023 result, including sign convention, interval propagation/method, relationship
between exposed and affected records, materiality output, and when annualized impact is present.

**Files:**

- `docs/finding_persistence_contract.md`
- `apps/api/app/findings/contracts.py`
- `FINDING_PRODUCT_CONTRACT.md`
- `docs/validation_contract.md`

**Expected output:** A Statistics-owned executable economic-impact result contract and tests that
TASK-024 can persist without interpreting or recomputing statistical meaning.

**Blocking:** YES — blocks implementing non-null Finding impact persistence and therefore blocks
TASK-024 completion.

**Resolution:** Pending.

## HANDOFF-026

**Created:** 2026-08-13
**From:** CUSTOMER_DISCOVERY
**To:** FOUNDER_STRATEGY
**Status:** OPEN

**Task:** Decide how real-world outreach for `TASK-057` actually gets executed, given Customer
Discovery (running as an AI agent in this repository) has no outbound communication channel.

**Context:** Requested to obtain at least 3 serious conversations with real potential data
partners, using the offer text now recorded in `CUSTOMER_PIPELINE.md`. This session has no
connected email or calling tool (Gmail MCP is present but unauthenticated), no named list of real
companies, and — independent of tooling — a real reply-and-conversation cycle takes real-world
days, which cannot complete inside one agent turn regardless of what's connected. Result: 0 of 3
required conversations obtained; `CUSTOMER_PIPELINE.md` is a ready tracker and template with zero
real rows, not a report of activity that happened. `CUSTOMER_DATA_ACQUISITION_PLAN.md` (materials,
scripts, discovery-call questions) already exists and is unaffected by this gap — the gap is purely
about who/what actually sends the first message and receives the reply.

**Question:** Pick an execution path (not mutually exclusive): (1) the founder personally sends the
prepared outreach using their own network/contacts and reports real responses back to Customer
Discovery to log in `CUSTOMER_PIPELINE.md`; (2) authorize the Gmail connector (via claude.ai
connector settings) so outreach can be drafted and sent from this session, understanding replies
still won't arrive within a single turn; (3) Customer Discovery researches a concrete named target
list (real companies, public contact info) via web search to hand off, without sending anything
itself. Which should happen first, and does the founder have existing warm contacts in travel
agencies, recruitment agencies, or B2B distribution worth prioritizing over cold outreach?

**Files:** `CUSTOMER_PIPELINE.md`, `CUSTOMER_DATA_ACQUISITION_PLAN.md`, `TASKS.md` (`TASK-057`)

**Expected output:** A chosen execution path (or combination) so `TASK-057` can move past zero
real contacts; if a channel is authorized, note it in `DECISIONS.md` given it's a durable
capability change, not just a task update.

**Blocking:** YES — blocks `TASK-057` producing any real conversation regardless of how good the
prepared materials are.

**Resolution:** Pending.

## HANDOFF-027

**Created:** 2026-08-13
**From:** FOUNDER_STRATEGY
**To:** STATISTICS
**Status:** OPEN

**Task:** Confirm the numeric tier thresholds in `BENCHMARK_DECISION_GATE.md` (STRONG/PROMISING/WEAK/FAILED, using `TASK-028`'s six metrics) don't conflict with `docs/validation_contract.md`, before `TASK-017`/`TASK-028` run.

**Context:** Founder pre-registered a business decision gate ahead of the first blind benchmark evaluation, per explicit instruction that success criteria must be fixed before ground truth is opened (`ADR-012`). The gate reuses this repository's existing denominators (9 patterns, P05/P07 excluded from recall per §11, 5 traps) and existing weighting philosophy (trap promotion and leakage as hard disqualifiers, matching §10), but the specific numeric bands (e.g. "≥60% Top-K precision = STRONG", "≤25% median impact error = STRONG") are Founder's business judgment about how much evidence justifies real-customer risk, not a statistical methodology decision Founder is positioned to make alone.

**Question:** Do the six metric definitions, the "true pattern match" matching-statistic delegation to `TASK-028`, the hard-disqualifier list, and the numeric band cutoffs conflict with anything already fixed in `docs/validation_contract.md` (gate thresholds, `min_e_value`, materiality placeholders, or the §10 acceptance test)? Are the band cutoffs themselves statistically defensible given benchmark scale (10k bookings, per-pattern n from 23–333), or should any be widened/narrowed before they bind a real decision?

**Files:**

- `BENCHMARK_DECISION_GATE.md`
- `docs/validation_contract.md` (§4–§11)
- `DECISIONS.md` (`ADR-012`)
- `synthetic_data/evaluation/hidden_ground_truth.json` (counts only, already reflected in the gate document)

**Expected output:** Either confirmation that the gate is usable as drafted, or specific requested threshold changes, recorded before `TASK-028` executes — this handoff should resolve before ground truth is opened, same as the gate itself.

**Blocking:** YES — the gate governs whether `TASK-038` (real customer ingestion) may proceed off this benchmark's result; it should not bind a real decision without Statistics' methodological sign-off.

**Resolution:** Pending.
