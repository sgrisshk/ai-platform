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
- `docs/benchmark/simulation-report.md`

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
`docs/benchmark/blind-benchmark-protocol.md`. A strict allowlist builder creates a fresh workspace outside the
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

**Operational closure (2026-08-14, Architect):** The lifecycle runner now requires an external
evaluator key file, signs the issued manifest, verifies that signature before launch/freeze, and
never mounts or exports the key to Discovery. Signed run `task-015-official-20260814-002` is issued
and `VERIFIED`; exact launch is recorded in `HANDOFF-032`. This closes the operational blocker on
`TASK-015` without launching Discovery or opening hidden truth.

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
first: validation and evidence contract v1.0.0 in `docs/analytics/validation-contract.md` and
`packages/analytics/src/policy_analytics/validation/` (`TASK-018`, ADR-007), which fixes the gate
sequence, evidence-level requirements, permitted language, and policy-readiness matrix that
`TASK-019`/`TASK-020` apply; discovery obligations from it are carried as `HANDOFF-011`. The first
question — versioned harm outcome, direction, units, eligibility, and missing-data handling — was
blocked pending `TASK-011`; once Data Engineer delivered the analytical dataset
`travel-bookings-analytical-v1.0.0` (this handoff's resolution) with `outcomes.csv` deliberately
left undirected (`primary_outcome: null`, `outcome_contract.status: PENDING_TASK_013`), Statistics
closed `TASK-013`: outcome contract v1.0.0 in `docs/analytics/outcome-contract.md` and
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
data remain explicitly out of scope — see `docs/analytics/outcome-contract.md` §1 and §7.

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

**Resolution:** Pending Architect implementation. Progress 2026-08-13 (Product): `docs/product/finding-product-contract.md` now supplies the full concrete answer — a required/optional/qualified-only field list mapped directly onto `ValidationReport`/`EffectEstimate` field names, so Architect isn't choosing between Product's and Statistics' proposals. It also confirms this handoff's questions (1)–(6) are satisfied by fields `ValidationReport` already defines in code; only question (7) (finding-lifecycle status) remains genuinely undecided — same conclusion `HANDOFF-012` reached independently from the Statistics side. Superseding inline list; `HANDOFF-012` remains the parallel Statistics-side answer and the two are cross-checked as compatible in the contract's header.

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

**Resolution:** Pending completion of `TASK-025`. Progress 2026-08-13 (Product): `docs/product/finding-product-contract.md` is now the authoritative source for copy rules — the exact permitted-verb wording ladder (quoted verbatim from `LANGUAGE_RULES` in code), the never-shown-without-qualification list, and the finalized `policy_readiness`-driven action matrix (§9), which supersedes this spec's own §7. Implement against the contract's wording, not hand-authored phrasing, once `TASK-025` unblocks.

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
prepared in advance (`docs/customer/findings-review-protocol.md`) so `TASK-042` can execute
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
(`docs/analytics/validation-contract.md` §10) cannot be scored without ground-truth effect sizes. This
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

- `docs/analytics/validation-contract.md`
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

- `docs/analytics/validation-contract.md` (§4, gate G05)
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
`docs/analytics/discovery-engine-v0.md`. Candidate validation is now routed back to Statistics in
HANDOFF-016.

## HANDOFF-016

**Created:** 2026-08-13
**From:** ML_DISCOVERY
**To:** STATISTICS
**Status:** IN_PROGRESS

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
- `docs/analytics/discovery-engine-v0.md`
- `docs/analytics/validation-contract.md`
- `packages/analytics/src/policy_analytics/discovery/engine.py`
- `synthetic_data/analytical/travel-bookings-analytical-v1.0.0/`

**Expected output:** Validation reports and evidence classification for every serious candidate;
rejections with explicit failed gates; no causal language beyond the assigned evidence level.

**Blocking:** YES — candidates cannot become durable findings or policy candidates before this
review.

**Resolution (2026-08-14, Statistics, in progress):** Ran the full 16-gate `TASK-018` contract
against all 15 candidates (`packages/analytics/src/policy_analytics/validation/apply.py`,
`scripts/validate_candidates.py`), frozen at
`artifacts/validation/task-019-validation-report.json`. No hidden ground truth was opened; the
confounding-adjustment covariates (manager, supplier) and heterogeneity covariate
(customer_segment) were fixed from generic booking-domain reasoning before running anything, not
from `hidden_ground_truth.json` or `synthetic_benchmark.py`.

**Result: all 15 candidates DOWNGRADE to `LEVEL_1_DESCRIPTIVE`, `EXPERIMENT_ONLY` readiness. None
PASS, none REJECT.** No candidate is handed to Architect/Product as a validated finding — there is
nothing that passed. On the redundancy question raised in this handoff's context: yes, 14/15
candidates include a `discount_rate` condition; this is now visible directly in the per-candidate
`pattern_definition` fields of the frozen report rather than only suspected, and `TASK-016`
ranking should treat these as substantially overlapping hypotheses, not 14 independent findings.

This is not a final answer for three independent reasons, none of which are about candidate
quality:

1. **Blind-protocol non-satisfaction** (already flagged in `TASK-015`'s own readiness note): the
   candidate artifact came from a full-checkout run, not the ADR-008 isolated workspace. Grading it
   is a legitimate dry run of the validation machinery, not a completed `TASK-017`.
2. **Founder readiness block**: `TASK-015` is held pending `TASK-012` and a workspace-launched
   rerun; this validation does not lift that.
3. **A newly discovered G05 defect** (`ADR-014`): the bootstrap p-value method's resolution floor
   cannot pass BH correction at `family_size = 6945` for any candidate regardless of true effect
   size. A diagnostic normal-approximation p-value (same bootstrap SE) puts every candidate below
   1e-6, suggesting this is an estimator artifact, not real non-significance — but the method was
   applied exactly as preregistered and not changed after seeing the result. A versioned fix is
   needed before the next run.

**Update (2026-08-14, Statistics):** Reason 3 is fixed. Validation contract **v1.1.0** (`ADR-015`)
replaces G05's p-value source with a normal approximation on the bootstrap standard error
(`math.erfc`-based, no resolution floor), verified mathematically sufficient to `family_size ~
100,000` with roughly 300 decades of headroom, and covered by 8 synthetic/mathematical regression
tests (`tests/analytics/test_g05_multiplicity_fix.py`) that never touch real candidate data or
ground truth. Applied as a code-behavior check to the real `TASK-015` candidates — nothing
persisted, nothing re-frozen — several now pass G05 at these effect sizes, confirming the fix
works; this does not change anything about reasons 1 and 2, which are untouched by this fix and
remain open. The v1.0.0 frozen artifact this handoff already produced is untouched;
`scripts/validate_candidates.py` now refuses to overwrite it without `--force`.

**Next steps before this can close:** (a) a genuine blind rerun of `TASK-015` from the approved
workspace once `TASK-012` completes and the founder readiness block is lifted; (b) re-run the
validation engine (now v1.1.0) against that new frozen artifact as a new, separately frozen run.
Full detail in `TASKS.md` (`TASK-019`) and `docs/analytics/validation-contract.md` §4a.

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

## HANDOFF-036

**Created:** 2026-08-14
**From:** ARCHITECT
**To:** FOUNDER_STRATEGY
**Status:** OPEN

**Task:** Revoke the exposed OpenAI provider credential and provide a newly generated credential
to the coordinator environment before issuing and launching the next blind run.

**Context:** The credential was pasted into a collaboration message after run `…-005` failed on
an obsolete Codex CLI flag. Treat it as compromised even if the failed container invocation did
not complete discovery. The secret value is deliberately not copied into repository state. The
launcher has been corrected and replacement run `…-006` is signed and `VERIFIED`, but it must not
be launched with the exposed credential.

**Question:** Revoke the exposed project key in the OpenAI dashboard, replace it in local secret
storage, export the replacement into the coordinator process, and confirm rotation without
sharing the value in chat, logs, source control, or handoff files.

**Files:** `.env` (local/untracked secret storage only; do not commit), `blind/README.md`.

**Expected output:** Confirmation that the old key is revoked and a new key is available only as
the coordinator's exported `OPENAI_API_KEY`; then issue and launch a new unique run.

**Blocking:** YES — blocks any provider-network launch of TASK-015.

**Resolution:** Pending human credential rotation; never record the replacement value here.
Readiness update 2026-08-14: run `task-015-official-20260814-006` was launched without usable
bearer authentication, received HTTP 401, exited before Discovery work, and is now irreversibly
`FAILED`. The coordinator process currently has no exported `OPENAI_API_KEY`. After the old key is
revoked and a replacement is exported without disclosing it, Architect/coordinator must issue and
verify new unique run `task-015-official-20260814-007`; `…-006` must not be retried or reused.

## HANDOFF-034

**Created:** 2026-08-14
**From:** ML_DISCOVERY
**To:** ARCHITECT
**Status:** RESOLVED

**Task:** Reissue and verify the official `TASK-015` blind workspace after the allowlisted Blind Discovery role contract changed.

**Context:** `agents/ML_DISCOVERY_BLIND.md` is included in `blind/allowlist.yaml`. Its current source SHA-256 is `9310aec37c92a5689b25ae442e3bf80cb5695af508936037cd92836df8491b1f`, while the immutable already-issued `task-015-official-20260814-002` workspace contains SHA-256 `ec1a8ede06d2d5d80dcfcd3bb2c5ec8df4e42194c34792685a46edd007277f70`. The old run was never launched and must remain unchanged for audit. It cannot represent execution under the new narrow actor contract.

**Question:** Issue a new run ID from the current allowlist, verify its signed manifest and pinned container/runtime settings, then provide the exact launch command to the ML Discovery Orchestrator.

**Files:**

- `agents/ML_DISCOVERY_BLIND.md`
- `blind/allowlist.yaml`
- `blind/README.md`
- `docs/benchmark/blind-benchmark-protocol.md`
- `TASKS.md` (`TASK-015`)

**Expected output:** A newly issued and verified external workspace whose manifest hashes the current role file, plus updated run ID, manifest hash, bundle ID, and coordinator launch command. Do not launch the Blind Discovery actor as part of this handoff.

**Blocking:** YES — blocks `TASK-015`, `TASK-016`, and `TASK-017`.

**Resolution (2026-08-14, Architect):** Issued and verified immutable run
`task-015-official-20260814-005`. Workspace:
`/tmp/policy-blind-runs/task-015-official-20260814-005/workspace`; manifest SHA-256
`e6f3b31a4011527e05084746ba47e05e38a967b366b3241738d26943cc276cfc`; bundle ID
`4bb19187c3dc2f286e0a2326aacc54bf8c8959461a75d607ef5bdf0b10b1216d`; current role SHA-256
`fa173df267d677e9cd29e945ac64f16401b5d5dc4263969ba4a42bf0aba1bfdc`. Source/allowlist drift is
checked before launch. Exact coordinator command:

```sh
OPENAI_API_KEY=<provider-key> make blind-shell \
  RUN=task-015-official-20260814-005 AGENT=codex BLIND_NETWORK=provider
```

Discovery was not launched. Run `…-002` remains unchanged audit-only; `…-003`/`…-004` are failed,
non-launchable issuance attempts.

**Supersession (2026-08-14, Architect):** Run `…-005` later failed before agent execution because
Codex CLI 0.147.0 rejects the removed `--full-auto` option. The launcher now uses supported
ephemeral automation flags. Replacement run `task-015-official-20260814-006` is signed and
`VERIFIED`; manifest SHA-256 is
`f2981fbc8ff55ba31ba4f4124d3a7bab38d0c844b0024832bdc1e024700d6a10`, with the same allowlisted
bundle ID `4bb19187c3dc2f286e0a2326aacc54bf8c8959461a75d607ef5bdf0b10b1216d`.

## HANDOFF-035

**Created:** 2026-08-14
**From:** ML_DISCOVERY
**To:** ARCHITECT
**Status:** RESOLVED

**Task:** Make the blind runner's pinned-image provenance and frozen output validation satisfy the
official TASK-015/TASK-016 acceptance contract.

**Context:** Coordinator readiness inspection for the first compliant blind run found that the
runner boundary tests pass, the evaluator key is external with mode `0600`, and the existing
workspace is outside the checkout. Two infrastructure contracts remain insufficient. First,
`BLIND_AGENT_IMAGE` defaults to mutable tag `policy-blind-agent:local`; although the current local
image resolves to a digest, launch provenance records neither the requested image reference nor
the resolved immutable image ID/digest. Second, `tools/blind_agent/models.py` schema v1.0.0 accepts
candidate output without dataset identity, outcome/discovery contract versions, model/run version,
temporal metadata, provenance hashes, or allowed feature classification; it does not enforce a
10–20 candidate count or reject unsupported causal language. `freeze()` therefore cannot perform
the coordinator acceptance checks required before commitment.

**Question:** Can the runner (1) require an immutable image digest at launch and record both the
reference and resolved image ID/digest in provenance before state becomes `RUNNING`; and (2)
version the output schemas/validator so freeze requires dataset identity, pinned outcome and
discovery contract versions, temporal/development-only selection metadata, model/run version,
provenance hashes, 10–20 candidates (or an explicitly approved insufficiency status), approved
decision-time feature classes, and evidence-bounded non-causal warnings/language?

**Files:**

- `Makefile`
- `infra/docker/blind-agent.Dockerfile`
- `tools/blind_agent/core.py`
- `tools/blind_agent/models.py`
- `tests/blind_agent/test_runner.py`
- `agents/ML_DISCOVERY_BLIND.md`
- `docs/benchmark/blind-benchmark-protocol.md`

**Expected output:** Tested fail-closed runner changes, a pinned immutable image reference recorded
in run provenance, versioned output schemas covering the official acceptance fields, and updated
protocol/runbook commands. Reissue the official workspace only after these contracts and the
allowlisted role are stable.

**Blocking:** YES — blocks launch, output acceptance, freeze, and therefore TASK-015/TASK-016/
TASK-017.

**Resolution (2026-08-14, Architect):** Launch now accepts only a signed-issued immutable
`name@sha256:<digest>` reference, resolves it at issuance and again before `RUNNING`, rejects any
substitution, and records requested reference plus resolved image ID/repo digest in provenance.
Output schema v1.1.0 requires signed dataset identity/version, outcome/discovery/method/run
versions, development-only selection metadata, exact input hashes, complete feature timing map,
and either 10–20 persisted candidates or explicit insufficiency status/reason. Freeze rejects
non-decision-time features, unapproved outcome/method, metadata drift, and prohibited causal
phrasing. Security/runner tests cover mutable images, source drift, provenance recording, contract
drift, and causal language. The signed runtime for run `…-005` is
`policy-blind-agent@sha256:f42e3cdaf1e6a766e312e6a28c2a9d377b7137bb8643379dcf3588a01398cf1d`.

## HANDOFF-032

**Created:** 2026-08-14
**From:** ARCHITECT
**To:** ML_DISCOVERY
**Status:** CANCELLED

**Task:** Execute `TASK-015` as a fresh Blind Discovery actor in the issued workspace.

**Context:** Operational issuance is complete. Run `task-015-official-20260814-002` is `VERIFIED`
at `/tmp/policy-blind-runs/task-015-official-20260814-002/workspace`. Its signed manifest SHA-256
is `5c989777638fa9e7116b1e3320f7e8413cc9bce7199c797bc0b156d994b496cd`; bundle ID is
`fd7570750014c8278c4eb2944fb7bb669f3235e7cc626057ecb4ddfd34e1ffc8`. The prior
repository-scoped ML session is ineligible. The evaluator key remains outside the run tree and
must not be requested, received, logged, or retained by Discovery.

**Question:** Execute the frozen method in a genuinely fresh session and produce only the three
required outputs. Do not open the full checkout and do not evaluate against hidden truth.

**Files:**

- `/tmp/policy-blind-runs/task-015-official-20260814-002/workspace`
- `blind/README.md` (coordinator runbook; not granted as an additional actor mount)

**Expected output:** The coordinator starts the fresh actor from the trusted checkout with:

```sh
OPENAI_API_KEY=<provider-key> make blind-shell \
  RUN=task-015-official-20260814-002 AGENT=codex BLIND_NETWORK=provider
```

After a successful actor exit, the evaluator/coordinator runs:

```sh
make blind-freeze RUN=task-015-official-20260814-002
```

Discovery receives only the allowlisted `/workspace` mount plus `OPENAI_API_KEY`; it does not
receive the evaluator key, repository checkout, CLI home, or prior session history.

**Blocking:** YES — execution/freeze is the remaining TASK-015 work; operational readiness is no
longer blocked.

**Resolution (2026-08-14, ML Discovery Orchestrator):** Cancelled without launch. The allowlisted
`agents/ML_DISCOVERY_BLIND.md` changed after this workspace was issued, so run
`task-015-official-20260814-002` remains immutable audit evidence only and cannot execute the
current contract. `HANDOFF-034` owns reissuance under a new unique run ID; `HANDOFF-035` owns the
pinned-image provenance and output-schema blockers found before that reissuance. No candidate
output was produced or frozen from this run.

## HANDOFF-013

**Created:** 2026-08-13
**From:** STATISTICS
**To:** PRODUCT
**Status:** OPEN

**Task:** Align finding presentation with the approved evidence and readiness rules, and supply the
customer economics behind the materiality threshold.

**Context:** `OQ-003` is resolved: `docs/analytics/validation-contract.md` §6–§7 fixes the evidence-to-
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

- `docs/analytics/validation-contract.md` (§6, §7, §8)
- `docs/product/finding-detail-screen.md`
- `memory/OPEN_QUESTIONS.md` (`OQ-002`, `OQ-003`, `OQ-004`)

**Expected output:** A finalized next-step action matrix consistent with the readiness rules, and a
customer-grounded materiality threshold to replace the placeholder.

**Blocking:** NO — the placeholder is usable for synthetic work; it must be replaced before any
real-customer finding is published.

**Resolution:** Partially resolved 2026-08-13 (Product). The action-matrix half is done:
`docs/product/finding-product-contract.md` §9 finalizes it, driven by `policy_readiness` alone (redundant to also
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
resolution, `docs/analytics/outcome-contract.md`, `OUTCOME_CONTRACT_VERSION = "1.0.0"`), pinned to this exact
`dataset_identity_sha256`. Statistics is not editing `manifest.json` directly — it is Data
Engineer's artifact and its lineage/checksum fields belong to that role.

**Question:** Can `manifest.json.outcome_contract` be updated to `status: "ATTACHED"`,
`primary_outcome: "contribution_margin_eur"`, and a reference to
`outcome_contract_version: "1.0.0"`, so a consumer reading only the manifest (without cross-
referencing `docs/analytics/outcome-contract.md`) sees the current state correctly?

**Files:**

- `synthetic_data/analytical/travel-bookings-analytical-v1.0.0/manifest.json`
- `docs/analytics/outcome-contract.md`
- `packages/analytics/src/policy_analytics/outcomes/contract.py`

**Expected output:** Updated manifest with a consistent lineage hash (or a documented reason the
identity hash is unaffected by a metadata-only change).

**Blocking:** NO — `docs/analytics/outcome-contract.md` is authoritative regardless; this is a consistency
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

**Task:** Resolve five wording/presentation questions raised while writing `docs/product/finding-product-contract.md`, deliberately not answered by Product because they touch statistical meaning, not just display.

**Context:** `docs/product/finding-product-contract.md` builds the Finding v0 field contract directly from `ValidationReport`/`LANGUAGE_RULES`/`docs/analytics/validation-contract.md` and invents no thresholds. A handful of presentation choices remain that could misrepresent methodology if Product decided them alone.

**Question:**

1. Standardized wording when an impact interval crosses zero — is there a preferred phrase (parallel to the backtest section's "no measurable net effect," `docs/analytics/validation-contract.md` §9), and should it also apply outside backtests, to ordinary economic-impact display?
2. Should `adjusted_p_value` / `family_size` ever be customer-facing, or stay analyst/audit-only? Product has no position; this is a Statistics + Architect call.
3. Display wording for `NOT_EVALUATED` gates (graded identically to `FAIL` per `GateOutcome`): "not yet evaluated" (reads as pending) or "failed" (reads as checked-and-rejected)? These leave different impressions of the same programmatic outcome.
4. The contract's §1 groups `controlled_variables` ("adjusted for") and `potential_confounders` ("considered and still possible") as two lists under one "what was checked" business narrative. Confirm this framing doesn't misrepresent the methodology to a reader who conflates the two.
5. Confirm the finding-lifecycle status vocabulary question (candidate/validated/rejected/superseded, distinct from `ResourceStatus`) — already open via `HANDOFF-008`/`HANDOFF-012` — is being tracked for `TASK-024` and isn't falling through between the two handoffs.

**Files:**

- `docs/product/finding-product-contract.md` (§10)
- `docs/analytics/validation-contract.md`
- `packages/analytics/src/policy_analytics/validation/contract.py` (`LANGUAGE_RULES`, `GateOutcome`)
- `packages/analytics/src/policy_analytics/validation/report.py` (`ValidationReport`)

**Expected output:** Answers to (1)–(4), and confirmation on (5); update `docs/product/finding-product-contract.md` §10 accordingly once answered.

**Blocking:** NO — the contract is usable as drafted; these refine wording precision before `TASK-024`/`TASK-025` implementation locks in copy.

**Resolution:** Pending.

## HANDOFF-021

**Created:** 2026-08-13
**From:** PRODUCT
**To:** CUSTOMER_DISCOVERY
**Status:** OPEN

**Task:** Supply (or confirm the continued absence of) the real customer economics needed to replace the materiality-threshold placeholder — the half of `HANDOFF-013` (Statistics → Product) that Product cannot answer.

**Context:** `HANDOFF-013` asked Product for the real materiality threshold behind `OQ-004` (`min_material_annual_impact = 25000`, `min_material_outcome_share = 0.005`, currently placeholders). Product finalized the action-matrix half of that handoff in `docs/product/finding-product-contract.md` §9/§11, but the threshold itself requires an actual pilot customer's P&L — data this repository does not have. `agents/PRODUCT.md` explicitly does not own customer willingness/economics; `agents/CUSTOMER_DISCOVERY.md` does. `TASK-057` (secure first real pilot customer, `ADR-010`) is the current bottleneck and, per `HANDOFF-014`'s resolution, has not started.

**Question:** Is there any real customer economic data (even partial — approximate annual booking volume, typical margin, or a customer's own stated "not worth it below €X" figure) available from Customer Discovery's work so far? If not — expected, given `TASK-057` is still `TODO` — please confirm explicitly so `OQ-004` stays correctly `OPEN` rather than silently stale, and flag this handoff as one of the concrete outputs `TASK-057` should produce once a pilot customer exists.

**Files:**

- `memory/OPEN_QUESTIONS.md` (`OQ-004`)
- `memory/HANDOFFS.md#HANDOFF-013`
- `docs/product/finding-product-contract.md` (§11)
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

**Files:** `.github/workflows/ci.yml`, `Makefile`, `docs/benchmark/blind-benchmark-protocol.md`,
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
**Status:** RESOLVED

**Task:** Resolve four ICP/positioning decisions raised by `docs/customer/data-acquisition-plan.md`
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

**Files:** `docs/customer/data-acquisition-plan.md`, `TASKS.md` (`TASK-057`, `TASK-010`), `DECISIONS.md`
(`ADR-010`), `memory/OPEN_QUESTIONS.md` (`OQ-002`, `OQ-004`)

**Expected output:** A decision (recorded in `DECISIONS.md` if durable) on scope sequencing and
positioning, so outreach in the two non-travel verticals doesn't produce data with nowhere
approved to go.

**Blocking:** NO — outreach can start under the travel-agency track regardless; this blocks
committing real effort to the recruitment/distribution tracks in `docs/customer/data-acquisition-plan.md`
§2.2/§2.3 in parallel rather than sequentially.

**Resolution (2026-08-13, implementation delivered for Statistics review):** The executable outcome
contract and tests are internally consistent and pass. Hidden truth now includes per-pattern,
per-outcome paired realized effects from identical-seed replay with only the selected pattern
disabled, including the estimand and paired record count. Nominal loss constants are not reported
as realized effects. This delivers `HANDOFF-010` item 1; Statistics retains authority to accept the
representation when completing TASK-003 review.

**Resolution (2026-08-14, Founder Strategy — ICP scope questions, superseding the note above which answered a different, statistics-track handoff pasted under this ID by mistake):** `ADR-016`. Option A: travel agencies only, until `MILESTONE-M3` or a demonstrated travel-outreach dead-end. Answering the four questions directly — (1) non-travel data is neither piped through the product nor collected yet; that choice is deferred, not resolved by building three schemas; (2) no per-vertical outcome-definition template is predefined; (3) outreach stays "independent research, no product"; (4) travel agencies are the only active vertical for now, not merely top priority. Recruitment/distribution rows in `docs/customer/prospect-target-list.md` are kept as a paused, not closed, backlog.

## HANDOFF-023

**Created:** 2026-08-13
**From:** STATISTICS
**To:** ML_DISCOVERY
**Status:** OPEN

**Task:** Adopt outcome contract v1.1.0 for any future discovery/ranking work; no action required on the existing `TASK-015` run.

**Context:** `TASK-013` is amended to v1.1.0 (ADR-011, `docs/analytics/outcome-contract.md` §9,
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
`docs/analytics/outcome-contract.md` §9.4 even before validation assigns an evidence level. Separately,
`HANDOFF-016` (your request that Statistics validate the persisted candidates under `TASK-018`)
remains open and unaffected by this amendment — it is not addressed here.

**Files:**

- `docs/analytics/outcome-contract.md` (§9)
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
**Status:** RESOLVED

**Task:** Finalize the Finding lifecycle enum and deterministic summary/title contract for
TASK-024.

**Context:** `docs/architecture/finding-persistence-contract.md` separates immutable CandidatePattern,
ValidationReport, and promoted Finding. The existing `ResourceStatus` describes jobs and cannot
represent Finding lifecycle. `docs/product/finding-product-contract.md`, HANDOFF-008, and HANDOFF-012 all flag
the lifecycle vocabulary as unresolved. The persistence migration cannot make a Finding status
column non-null or expose it through API schemas until Product fixes the allowed states and
transitions. Product also requires a deterministic plain-language summary, but its exact template
and whether title is stored or derived are not fixed.

**Question:** What exact Finding lifecycle enum and transition rules should TASK-024 persist? Is
the business summary/title stored as a versioned deterministic snapshot, derived on every read, or
both; and what template version identifies it?

**Files:**

- `docs/architecture/finding-persistence-contract.md`
- `docs/product/finding-product-contract.md`
- `docs/product/finding-detail-screen.md`
- `apps/api/app/findings/contracts.py`

**Expected output:** Final enum values/transitions and a versioned deterministic summary/title
contract suitable for Pydantic, database constraints, and API serialization.

**Blocking:** YES — blocks locking and implementing the TASK-024 Finding table/API shape, but does
not block CandidatePattern or ValidationReport table preparation.

**Resolution (2026-08-13, Product):** `docs/product/finding-product-contract.md` §12 answers both questions.

Lifecycle enum `FindingLifecycleStatus`: `ACTIVE` (default/only status shown), `SUPERSEDED`
(replaced by a re-specified/re-validated candidate's Finding, carries `superseded_by_finding_id`),
`WITHDRAWN` (pulled for any other reason, carries a required `withdrawal_reason`). Transitions are
forward-only from `ACTIVE`; nothing returns to `ACTIVE` — a pattern found valid again is promoted as
a new Finding, matching the append-only treatment already used for `CandidatePattern`. Deliberately
excludes a "reviewed" state (per-viewer, and no auth exists yet — `TASK-053` `BLOCKED`) and any
"awaiting validation" state (structurally impossible for a `findings` row given `FindingPromotion`'s
own invariant). Staleness against the live `validation_contract_version` is computed at read time,
not stored.

Title/summary: stored, versioned, deterministic snapshot computed once at promotion time (never
derived live, never LLM-authored at render), two fields (`title`, short; `summary`, one paragraph)
sharing one `title_template_version`. v0 template (`"v0-mechanical"`) is a pure function of
`CandidatePattern.conditions` plus the outcome contract's harm-direction phrase; feature names are
formatted mechanically pending a real `display_label` field this schema doesn't have yet — flagged
to Data Engineer as `HANDOFF-028`, not blocking v0.

Both consumed by the new `docs/product/findings-list-screen.md` (TASK-026) and the updated
`docs/product/finding-detail-screen.md`, which replaces its old `ResourceStatus`-based run-status
gating with this lifecycle enum.

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

- `docs/architecture/finding-persistence-contract.md`
- `apps/api/app/findings/contracts.py`
- `docs/product/finding-product-contract.md`
- `docs/analytics/validation-contract.md`

**Expected output:** A Statistics-owned executable economic-impact result contract and tests that
TASK-024 can persist without interpreting or recomputing statistical meaning.

**Blocking:** YES — blocks implementing non-null Finding impact persistence and therefore blocks
TASK-024 completion.

**Resolution:** Pending.

## HANDOFF-026

**Created:** 2026-08-13
**From:** CUSTOMER_DISCOVERY
**To:** FOUNDER_STRATEGY
**Status:** RESOLVED

**Task:** Decide how real-world outreach for `TASK-057` actually gets executed, given Customer
Discovery (running as an AI agent in this repository) has no outbound communication channel.

**Context:** Requested to obtain at least 3 serious conversations with real potential data
partners, using the offer text now recorded in `docs/customer/pipeline.md`. This session has no
connected email or calling tool (Gmail MCP is present but unauthenticated), no named list of real
companies, and — independent of tooling — a real reply-and-conversation cycle takes real-world
days, which cannot complete inside one agent turn regardless of what's connected. Result: 0 of 3
required conversations obtained; `docs/customer/pipeline.md` is a ready tracker and template with zero
real rows, not a report of activity that happened. `docs/customer/data-acquisition-plan.md` (materials,
scripts, discovery-call questions) already exists and is unaffected by this gap — the gap is purely
about who/what actually sends the first message and receives the reply.

**Question:** Pick an execution path (not mutually exclusive): (1) the founder personally sends the
prepared outreach using their own network/contacts and reports real responses back to Customer
Discovery to log in `docs/customer/pipeline.md`; (2) authorize the Gmail connector (via claude.ai
connector settings) so outreach can be drafted and sent from this session, understanding replies
still won't arrive within a single turn; (3) Customer Discovery researches a concrete named target
list (real companies, public contact info) via web search to hand off, without sending anything
itself. Which should happen first, and does the founder have existing warm contacts in travel
agencies, recruitment agencies, or B2B distribution worth prioritizing over cold outreach?

**Files:** `docs/customer/pipeline.md`, `docs/customer/data-acquisition-plan.md`, `TASKS.md` (`TASK-057`)

**Expected output:** A chosen execution path (or combination) so `TASK-057` can move past zero
real contacts; if a channel is authorized, note it in `DECISIONS.md` given it's a durable
capability change, not just a task update.

**Blocking:** YES — blocks `TASK-057` producing any real conversation regardless of how good the
prepared materials are.

**Resolution:** Partially actioned by the founder directly (2026-08-14), all three non-exclusive
paths selected: (1) founder has existing contacts and will hand them off; (2) Gmail connector
requested — still unauthenticated as of this update, needs founder action via claude.ai connector
settings, Customer Discovery cannot authorize it; (3) done — `docs/customer/prospect-target-list.md` delivers 21
sourced, named candidate companies (global, including Asia) across the three verticals, explicitly
unqualified/uncontacted. Still open: founder has not yet supplied their own contacts, and no send
channel is live, so `TASK-057` remains at 0 of 3 required conversations.

**Resolution (2026-08-14, Founder Strategy — finalized as `ADR-017`):** All three paths confirmed combined and time-boxed into a concrete 7-day sprint, `docs/customer/acquisition-sprint-7day.md`, scoped to the travel-agency-only prospects per `ADR-016`. Numeric target: 15 outbound touches → 4 real replies/exchanges → 1 serious conversation, by 2026-08-21. Explicit instruction to avoid a second silent stall: outreach proceeds via founder-sent LinkedIn/email from day 2 regardless of whether Gmail authorization has completed. Owners: founder executes/authorizes sending; Customer Discovery sources, drafts, and logs honestly. This does not close `TASK-057` — it commits to the execution plan that can.

## HANDOFF-027

**Created:** 2026-08-13
**From:** FOUNDER_STRATEGY
**To:** STATISTICS
**Status:** OPEN

**Task:** Confirm the numeric tier thresholds in `docs/benchmark/decision-gate.md` (STRONG/PROMISING/WEAK/FAILED, using `TASK-028`'s six metrics) don't conflict with `docs/analytics/validation-contract.md`, before `TASK-017`/`TASK-028` run.

**Context:** Founder pre-registered a business decision gate ahead of the first blind benchmark evaluation, per explicit instruction that success criteria must be fixed before ground truth is opened (`ADR-012`). The gate reuses this repository's existing denominators (9 patterns, P05/P07 excluded from recall per §11, 5 traps) and existing weighting philosophy (trap promotion and leakage as hard disqualifiers, matching §10), but the specific numeric bands (e.g. "≥60% Top-K precision = STRONG", "≤25% median impact error = STRONG") are Founder's business judgment about how much evidence justifies real-customer risk, not a statistical methodology decision Founder is positioned to make alone.

**Question:** Do the six metric definitions, the "true pattern match" matching-statistic delegation to `TASK-028`, the hard-disqualifier list, and the numeric band cutoffs conflict with anything already fixed in `docs/analytics/validation-contract.md` (gate thresholds, `min_e_value`, materiality placeholders, or the §10 acceptance test)? Are the band cutoffs themselves statistically defensible given benchmark scale (10k bookings, per-pattern n from 23–333), or should any be widened/narrowed before they bind a real decision?

**Files:**

- `docs/benchmark/decision-gate.md`
- `docs/analytics/validation-contract.md` (§4–§11)
- `DECISIONS.md` (`ADR-012`)
- `synthetic_data/evaluation/hidden_ground_truth.json` (counts only, already reflected in the gate document)

**Expected output:** Either confirmation that the gate is usable as drafted, or specific requested threshold changes, recorded before `TASK-028` executes — this handoff should resolve before ground truth is opened, same as the gate itself.

**Blocking:** YES — the gate governs whether `TASK-038` (real customer ingestion) may proceed off this benchmark's result; it should not bind a real decision without Statistics' methodological sign-off.

**Resolution:** Pending.

## HANDOFF-028

**Created:** 2026-08-14
**From:** PRODUCT
**To:** DATA_ENGINEER
**Status:** OPEN

**Task:** Add a human-authored display label per column, for use by the Finding title/summary template (`docs/product/finding-product-contract.md` §12.2).

**Context:** The v0 Finding title template renders feature names mechanically (`snake_case` → "Title Case", e.g. `discount_rate` → "Discount Rate") because no column anywhere in the schema carries a curated business label — `DatasetColumn` (`packages/schemas/src/policy_schemas/domain.py`) has only `name`, `data_type`, `timing`, `nullable`. This is disclosed as a v0 simplification, not a defect, and does not block `TASK-024`/`TASK-026`/`TASK-027`.

**Question:** Should `DatasetColumn` (or the schema-profiling output from a future `TASK-007`, or the canonical schema from a future `TASK-010`) carry an optional `display_label: str | None` — human-authored or a better-than-mechanical default (e.g. splitting on underscores with domain-specific overrides for known columns like `discount_rate` → "discount given")? This is a data-contract question, not a wording question — Product will supply the actual label text once the field exists, this handoff only asks for the field.

**Files:**

- `packages/schemas/src/policy_schemas/domain.py` (`DatasetColumn`)
- `docs/product/finding-product-contract.md` (§12.2)
- `synthetic_data/analytical/travel-bookings-analytical-v1.0.0/` (feature manifest, for the synthetic case)

**Expected output:** A decision on where `display_label` lives and whether it's populated now for the synthetic benchmark or deferred to real customer ingestion.

**Blocking:** NO — v0 ships with the mechanical fallback; this only improves later wording quality.

**Resolution:** Pending.

## HANDOFF-029

**Created:** 2026-08-14
**From:** PRODUCT
**To:** ARCHITECT
**Status:** OPEN

**Task:** Implement `TASK-026` (findings list screen) against the new `docs/product/findings-list-screen.md`, once `TASK-025` delivers a real findings API — mirrors `HANDOFF-009`'s pattern for `TASK-027`.

**Context:** No Frontend role exists in `agents/` (established across `HANDOFF-005`/`HANDOFF-009`); `TASKS.md` lists `ARCHITECT` as `TASK-026`'s implementation owner. The list-screen UX specification is now complete, grounded in the concrete `docs/architecture/finding-persistence-contract.md`/`apps/api/app/findings/contracts.py` schema rather than a conceptual one. Two implementation details are explicitly left to Architect, not fixed by Product: pagination mechanism (page size, cursor vs. offset) and the exact tie-break sort key for findings whose impact interval crosses zero (Product only requires the list not omit them and not reshuffle stably-sorted pages).

**Question:** None outstanding for Product; this is a build handoff. Implement once `TASK-025` exists; the two open implementation details above may be resolved by Architect directly without a Product decision, as long as the constraints in `docs/product/findings-list-screen.md` (default `ACTIVE`-only visibility, no summed/aggregate KPI tiles, sort/filter rules) are respected.

**Files:**

- `docs/product/findings-list-screen.md`
- `docs/product/finding-product-contract.md`
- `apps/web/app/(app)/findings/page.tsx` (current placeholder to replace)
- `apps/web/lib/api/findings.ts`, `apps/web/components/states/`

**Expected output:** Working findings list screen matching the specification's information hierarchy, field-to-copy mapping, sort/filter rules, and states.

**Blocking:** YES — blocks closing `TASK-026`, but does not block anything else; `TASK-025`/`TASK-024` remain the actual critical-path blockers.

**Resolution:** Pending completion of `TASK-025`.

## HANDOFF-030

**Created:** 2026-08-14
**From:** DATA_ENGINEER
**To:** STATISTICS
**Status:** OPEN

**Task:** Perform the final TASK-003 review of the private per-pattern true-effect representation.

**Context:** Statistics approved the benchmark in substance and required an explicit, reviewable
per-pattern truth artifact. The regenerated private `true_effect` object now records `pattern_id`,
configured mechanism, identical-seed factual-minus-disabled realized effect, harmful direction,
affected N/support, harm-positive realized economic impact, valid interval, relevant outcome, and
units. The relevant outcome and sign are read from TASK-013 outcome contract v1.1.0
(`contribution_margin_eur`, decrease = harm); the existing per-outcome replay detail is retained.
No statistical evaluation methodology was changed. Restricted ground-truth SHA-256 is
`5c41aab8ad6765332b708fd8b91567b63839b84add2dd8aa206d87c159cab506`.

**Question:** Does this representation satisfy the `HANDOFF-010`/`HANDOFF-019` requirement so
TASK-003 can be marked `DONE`?

**Files:**

- `synthetic_data/evaluation/hidden_ground_truth.json` (PRIVATE, evaluation-only)
- `synthetic_data/evaluation/checksums.json` (PRIVATE)
- `packages/analytics/src/policy_analytics/synthetic_benchmark.py`
- `tests/analytics/test_synthetic_benchmark.py`
- `docs/benchmark/simulation-report.md`

**Expected output:** Statistics acceptance, or a specific schema/sign/unit correction. Do not
publish the private values or expose them to an ML Discovery session.

**Blocking:** YES — final acceptance blocks moving TASK-003 from `IN_REVIEW` to `DONE`.

**Resolution:** Pending.

## HANDOFF-031

**Created:** 2026-08-14
**From:** PRODUCT
**To:** ARCHITECT
**Status:** OPEN

**Task:** Future persistence design for Finding feedback (`TASK-035`), against `docs/product/finding-feedback-contract.md`. Not a request to implement now.

**Context:** `docs/product/finding-feedback-contract.md` formalizes the six `TASK-035` values (`KNOWN_ALREADY`/`NEW`/`WRONG`/`NOT_ACTIONABLE`/`INTERESTING`/`ACTIONABLE`) into two nullable single-select axes (novelty, actionability) plus a multi-select qualifier-tag set (`WRONG`, `INTERESTING`), fixes which additional fields are needed (customer comment, customer-reported certainty — explicitly not statistical confidence, intended action, commitment strength, customer/internal owners, follow-up date), and fixes an append-only record lifecycle keyed on `(finding_id, review_session)`. It explicitly does not design persistence, UI, or any statistical treatment of the data.

**Question:** When `TASK-027` and `TASK-035` unblock, does this shape map cleanly onto a `findings_feedback` table (or similar), and does the `review_session` reference need a formal Customer Discovery session/interview persistence object to exist first, or can it start as a loosely-typed reference (e.g. company name + date) mirroring the current markdown-log reality in `docs/customer/pipeline.md`?

**Files:**

- `docs/product/finding-feedback-contract.md`
- `docs/product/finding-detail-screen.md` (reserved UI slot)
- `docs/customer/findings-review-protocol.md`
- `docs/customer/pipeline.md` (current session-record reality)

**Expected output:** Eventually, a `TASK-035` persistence proposal consuming this contract — no immediate output required.

**Blocking:** NO — explicitly deferred. `TASK-035` remains `BLOCKED` on `TASK-027`, which remains `BLOCKED` on `TASK-025`→`TASK-024`. This handoff exists so the contract is available ahead of time, not to unblock anything now.

**Resolution:** Pending.

## HANDOFF-032

**Created:** 2026-08-14
**From:** FRONTEND (ad hoc dispatch — see `HANDOFF-005` question (1), still unresolved: no Frontend role exists in `agents/`)
**To:** ARCHITECT
**Status:** OPEN

**Task:** Add the newly-added frontend test suite to CI.

**Context:** A frontend readiness pass for the future `TASK-026`/`TASK-027` implementation found `apps/web` had no test runner at all (no `test` script, no `vitest`/`jest`, nothing in CI beyond lint/typecheck/build). Fixed as infrastructure: `vitest` + `@testing-library/react` are now wired up (`apps/web/vitest.config.mts`, `pnpm --filter web test`), with tests for the typed API-client error contract and the loading/error/empty state primitives — no Finding-content tests, since no validated Finding is served yet. `make test` now runs it alongside `uv run pytest`. `.github/workflows/ci.yml`'s `frontend` job (lines 56-70) still only runs `pnpm install`, `lint`, `typecheck`, `build` — not deliberately excluded, just written before this suite existed.

**Question:** Add `- run: pnpm --filter web test` to the `frontend` job in `.github/workflows/ci.yml`, alongside the existing lint/typecheck/build steps? Mechanical, one line, no design decision — flagged rather than done directly because workflow files are explicit CI/CD ownership (`AGENTS.md`).

**Files:**

- `.github/workflows/ci.yml`
- `apps/web/package.json` (`test` script)
- `apps/web/vitest.config.mts`
- `Makefile` (`test` target, already updated)

**Expected output:** One CI step added; frontend tests then run on every PR the same way lint/typecheck/build already do.

**Blocking:** NO — the suite runs locally and via `make test` regardless; this only affects CI enforcement.

**Resolution:** Pending.

## HANDOFF-033

**Created:** 2026-08-14
**From:** CUSTOMER_DISCOVERY
**To:** FOUNDER_STRATEGY
**Status:** OPEN

**Task:** Concrete manual steps to actually send the 7 ready-drafted outreach messages in
`docs/customer/pipeline.md` §"Ready-to-send outreach" — no tool in this session can send them.

**Context:** Asked to move `TASK-057` from planning into real execution: ≥3 real conversations or
≥1 explicit dataset-sharing agreement this iteration. Checked directly (2026-08-14): no email/
calling tool is connected in this session, and no SMTP/API credentials exist anywhere in the
repository or environment (`env | grep -i mail`, `.env*` — both empty). The founder mentioned
having created an email address for this use, but no corresponding tool appeared and the address
itself was not shared with this session, so it cannot be used here in any form yet. Result: 7 of
the 21 `docs/customer/prospect-target-list.md` candidates were researched further (real contact
paths confirmed from each company's own site: 5 email addresses, 2 phone/call-first contacts with
named individuals) and turned into personalized, ready-to-send drafts. Zero have been sent. Zero
conversations exist. This is a harder floor than `HANDOFF-026`: even with a channel, "drafted" is
not "sent," and "sent" is not "replied."

**What a human needs to do by hand, right now, to move this forward:**

1. Tell Customer Discovery two things it does not have: (a) the actual email address created for
   this, and (b) what name/signature should replace `[YOUR NAME]` / `[YOUR EMAIL/PHONE]` in the
   drafts. Without both, nothing in `docs/customer/pipeline.md` can be finalized, sent by the
   founder, or drafted-to-send if a channel is later connected.
2. Either (a) copy the 5 email drafts (Craft Travel — sales@crafttravel.com; The Staffing Agency —
   info@thestaffingagency.co.uk; SP Muthiah & Sons — sales@spmuthiah.com; Cleveland Wholesale —
   sales@clevelandwholesale.com; IRC — via contact form at ircfs.com/contact, its listed email is
   obfuscated/unreadable by this session's tools) into that mailbox and send them directly, or (b)
   finish authorizing the Gmail connector via claude.ai connector settings so a future turn in this
   session can send them instead.
3. Two contacts have no public email and need an actual phone call, which no tool in this session
   can place: Travel Discounters (Canada, ask for Binod Singh, (416) 481-6701) and Pettitts Travel
   (UK, ask for Steven or David Pettitt, 01892 515966). Call scripts are in
   `docs/customer/pipeline.md`.
4. Whatever comes back — a reply, silence, a call outcome — needs to be reported back to Customer
   Discovery verbatim so it can be logged in `docs/customer/pipeline.md` §Log. Polite interest
   ("interesting," "keep us posted") is not a pilot commitment and will be logged as such, not
   upgraded.

**Files:** `docs/customer/pipeline.md`, `docs/customer/prospect-target-list.md`, `TASKS.md`
(`TASK-057`), `memory/HANDOFFS.md` (`HANDOFF-026`, still open and superset of this)

**Expected output:** Either the founder supplies identity details and sends the drafts (or asks
Customer Discovery to adjust them first), or confirms Gmail authorization is complete so sending
can happen from this session next turn.

**Blocking:** YES — this is the literal last step between "prepared" and "sent"; nothing currently
in this repository can cross it without a human action.

**Resolution:** Pending.
