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
- **Status:** DONE
- **Depends on:** TASK-001
- **Goal:** Generate 10,000 bookings across 24 months with a fixed seed and hidden ground truth.
- **Scope:** Seasonality, managers, suppliers, customer segments, discounts, payments, cancellations, refunds, support costs, gross profit, and contribution margin; at least 8 harmful patterns, 5 confounding traps, drift, heterogeneous effects, selection bias, leakage fields, missingness, and a dirty-data variant.
- **Outputs:** `synthetic_data/{raw,reference,metadata,evaluation}/`, clean/dirty CSVs, schema and feature-timing metadata, hidden ground truth, corruption/config manifests, evaluator, and `docs/benchmark/simulation-report.md`.
- **Critical rule:** ML Discovery must never receive hidden ground truth before candidates are persisted.
- **Blind boundary:** `make export-public-benchmark destination=...` rebuilds an allowlist-only
  artifact containing the approved analytical partitions and sanitized public metadata; see
  ADR-008 and `docs/benchmark/blind-benchmark-protocol.md`. HANDOFF-007 is resolved.
- **Done when:** Generation is reproducible, configured patterns/traps exist, time splits work, public inputs contain no answer leakage, and tests pass.
- **Implementation evidence:** Deterministic generator, 10,000-row clean/dirty artifacts,
  schema/timing/split/corruption/checksum manifests, restricted ground truth, blind-evaluation
  guard, analytics tests, and `docs/benchmark/simulation-report.md` completed on 2026-08-13. Statistics
  review is tracked by `HANDOFF-006`.
- **Review outcome (2026-08-13, STATISTICS):** Approved in substance — mechanisms, traps, drift,
  heterogeneity, selection bias, and leakage fields are suitable and do not overstate
  identifiability. Two artifact changes required before `DONE`: per-pattern realized effect sizes
  in the hidden ground truth (without them `TASK-022`/`TASK-028` cannot score direction or impact
  error) and a stable customer identifier (without it `repeat_purchase_180d` cannot be linked and
  customer-level clustering is impossible). Carried as `HANDOFF-010`.
- **Artifact remediation (2026-08-14, DATA_ENGINEER):** The private hidden truth now records a
  complete per-pattern `true_effect` object: configured mechanism, identical-draw replay effect for
  the TASK-013 primary outcome, direction/sign convention, affected N/support, realized economic
  impact, valid interval, outcome, and units. Fixed-seed regeneration produced restricted SHA-256
  `5c41aab8ad6765332b708fd8b91567b63839b84add2dd8aa206d87c159cab506`; leakage tests confirm the
  fields are absent from public, analytical, and blind-export artifacts. Final Statistics
  acceptance is requested in `HANDOFF-030`; status remains `IN_REVIEW` until that review resolves.
- **Final acceptance (2026-08-16, Statistics, `HANDOFF-030` resolved) → `DONE`.** Independently
  reverified, not just read: recomputed `sha256(hidden_ground_truth.json)` locally, matches the
  claimed and recorded checksum; confirmed `realized_economic_impact == |realized_effect| ×
  affected_n` to the cent for all 9 patterns; hand-verified the harm-score sign convention against
  `policy_analytics.outcomes.aggregation.harm_score` for P01; read the counterfactual-replay
  implementation and confirmed disabling a pattern changes only accumulated constants, never an
  `rng.*()` call, preserving paired-draw validity; ran `test_synthetic_benchmark.py` (4/4 pass,
  including the leakage scan). This artifact was then used, unmodified, as `TASK-028`'s scoring
  input (`docs/benchmark/task-029-benchmark-report-v1.md`).

### TASK-004 — Benchmark difficulty presets

- **Owner:** DATA_ENGINEER
- **Priority:** P1
- **Status:** READY
- **Depends on:** TASK-003
- **Goal:** Add `EASY`, `MEDIUM`, `HARD`, and `BRUTAL` presets varying noise, effects, missingness, confounding, rarity, and temporal instability.
- **Status note (2026-08-16, Data Engineer):** Unblocked — `TASK-003` is `DONE` (`HANDOFF-030`
  accepted). Not picked up this iteration; `TASK-005`/`TASK-006` (below) were the assigned priority.

## Phase 2 — Data ingestion

### TASK-005 — Immutable ingestion contract

- **Owner:** DATA_ENGINEER
- **Reviewer:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-002
- **Goal:** Specify checksums, file validation, size/type limits, safe names, retention, versioning, immutable storage, logging/privacy boundaries, and typed ingestion manifest.
- **Handoff:** `HANDOFF-001`, resolved.
- **Evidence (2026-08-16, Data Engineer, paired with Architect):** `docs/architecture/ingestion-contract.md`
  answers every question in `HANDOFF-001`: SHA-256 content addressing (`raw/{sha256[:2]}/{sha256}.csv`),
  an ordered validation pipeline (filename → bounded size read → content sniff → content-address +
  immutable persist → name/version identity resolution), `name`+`version` as the versioning identity
  with adjacent-latest duplicate rejection (`409`, no silent overwrite), retention deferred to
  `TASK-055`, and a logging boundary that never emits filenames or row content. The manifest is
  realized as typed columns on `datasets` (`checksum_sha256`, `size_bytes`, `content_type`,
  `source_type`, `storage_path`) rather than a separate sidecar schema, to avoid a second driftable
  source of truth — this superseded an initial draft manifest module
  (`packages/schemas/src/policy_schemas/ingestion.py`), which was removed once the column-based
  design was confirmed working end to end in `TASK-006`. Contract and implementation were produced
  together in this iteration rather than as a sequential spec-then-build handoff.

### TASK-006 — Dataset upload API and raw storage

- **Owner:** ARCHITECT
- **Data contract:** DATA_ENGINEER
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-005
- **Goal:** Accept CSV through `POST /api/v1/datasets`, preserve raw bytes immutably, and persist filename, checksum, timestamp, size, version, and source type without logging contents.
- **Done when:** A synthetic CSV can be uploaded and every version is traceable; identical identity rules prevent silent overwrite.
- **Evidence (2026-08-16, Architect + Data Engineer):** `POST /api/v1/datasets` now takes a
  multipart `name` + `file` upload (`apps/api/app/datasets/routes.py`, `service.py`). Filename
  sanitization and CSV content sniffing (`app/ingestion/validation.py`), a bounded streaming read
  that aborts at `Settings.max_upload_bytes` regardless of a spoofed `Content-Length`, and
  content-addressed immutable storage with atomic temp-write + `fsync` + `os.replace` + read-only
  `chmod` (`app/ingestion/storage.py`) implement the `TASK-005` pipeline. `datasets` gained
  `checksum_sha256`/`size_bytes`/`content_type`/`source_type`/`storage_path` plus a
  `UNIQUE(name, version)` constraint (migration `20260816_0002`); a same-name upload with an
  unchanged checksum is rejected `409` without a new row, a changed checksum creates the next
  version, and a concurrent-insert race is caught and mapped to `409` rather than corrupting version
  order. Data Engineer review found and fixed one real pre-existing gap: `pyright` failed on
  `read_bounded`'s protocol (`UploadFile.file` is position-only `read(n, /)`, the declared protocol
  was not) — fixed by making the protocol's parameter position-only; also fixed two lint findings
  (unsorted imports, one overlong line). Verified, not just read: `uv run pytest` — 29 unit tests for
  `validation.py`/`storage.py` (filename rejection cases, size/encoding/structure rejection, content
  addressing determinism, immutability, no temp-file leftovers) plus 6 integration tests
  (`tests/api/test_datasets_upload.py`) run against a real ephemeral PostgreSQL container — happy
  path with full manifest fields, duplicate-content rejection, version increment, oversized-upload
  rejection, wrong-extension rejection, and a log-inspection test proving the filename never reaches
  a log record — all pass (163 passed project-wide with the DB attached); `ruff check .` and
  `pyright` both clean. This satisfies the stated done condition. `TASK-007` is unblocked.
- **Known scope limits, not defects:** only Excel is deferred (CSV only, matching this task's own
  goal text); duplicate detection compares against the latest version only, not full history;
  malware scanning is a deployment-platform hook per `SECURITY.md`, not implemented locally;
  authentication/tenant isolation remain `TASK-053`/`TASK-054`. An independent adversarial security
  pass before real customer bytes flow through this path is `TASK-037`, already gated on
  `TASK-057` — not reopened here, and unaffected by/independent of the `TASK-029` decision-gate
  `FAILED` verdict (`HANDOFF-043`), which blocks `TASK-038` on its own separate grounds.

### TASK-007 — Schema profiler

- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-006
- **Goal:** Persist inferred type, missingness, distinct count, relevant min/max, safe examples, suspicious values, and likely semantic type per column.
- **Status note (2026-08-16, Data Engineer):** Unblocked — `TASK-006` is `DONE`. Not started this
  iteration.
- **Implementation (2026-08-17, Architect) → `DONE`.** No design doc existed for this one yet
  (unlike `TASK-005`'s `HANDOFF-001` or `TASK-024`'s prep doc) — designed and built together.
  Deliberately kept **separate** from `DatasetColumn`/`DatasetModel.columns` (that JSONB field is
  `TASK-008`'s eventual feature-timing-classification output, a different pipeline stage) — new
  `dataset_column_profiles` table instead (migration `20260817_0004`), one row per column, written
  once per dataset version. Pure computation in
  `packages/analytics/src/policy_analytics/profiling/schema_profiler.py`: majority-vote structural
  type inference (integer → float → boolean → date → string, first candidate clearing a 98% match
  rate wins; every non-matching value becomes a capped, counted "suspicious value" — deliberately
  no ML/black-box guessing, `ADR-004`). "Likely semantic type" and "safe examples" are explicitly
  disclosed heuristics, not validated facts or a real PII detector: examples are suppressed for
  likely-identifier/free-text high-cardinality columns, a conservative floor, not a claim of
  complete redaction. Runs synchronously inside the upload request (no job-queue infrastructure
  exists yet; files are capped at `MAX_UPLOAD_BYTES`); a profiling failure logs and leaves the
  dataset unprofiled rather than failing the already-completed, already-immutable upload.
  **Real bug found and fixed via live verification, not just unit tests:** the semantic-type name
  hints originally matched raw substrings, so `trip_duration` was misclassified `percentage_rate`
  purely because "duration" contains "ratio" as a substring — caught by uploading the real
  `tests/fixtures/synthetic_travel_bookings.csv` fixture through a live `uvicorn` instance, fixed
  by switching to whole-token matching, regression-tested. Verified end to end against a real
  ephemeral Postgres: migration up/down/up round-trips; full suite green twice in a row (230
  passed) against the same live database; a real upload of the 200-row, 24-column fixture produces
  correct profiles for every column (e.g. `booking_id` → suppressed identifier, `manual_exception`/
  `cancellation` → boolean, `booking_changes` → a real 0-3 integer count, not the boolean its name
  might suggest — verified against actual data, not assumed from the column name). 33 new tests
  (17 pure profiler unit tests + 2 DB-gated integration tests via the real upload path + existing
  suite growth); `ruff`/`pyright` clean.
- **Second real bug found and fixed (2026-08-17, Architect), by manual repro rather than trusting
  the passing suite:** `_min_max` filtered a numeric column's range with the broader
  `_matches_float` (which also accepts plain integers) instead of the *winning* type's own
  predicate, so a suspicious non-conforming value — already flagged separately as suspicious —
  could still be silently reported as the column's own `min_value`/`max_value`. Repro: 99 clean
  integers `1`..`99` plus one `"999999.5"` outlier graded `integer` (99% match, clears the 98%
  threshold) reported `max_value = "999999.5"` — the exact flagged outlier laundered into what
  looks like a normal range boundary. Fixed by computing min/max only from the values that survive
  the winning type's own predicate; 2 new regression tests (integer and date cases). Did not
  reproduce on the clean synthetic fixture (which is exactly why it needed a deliberate repro, not
  just rerunning the existing suite) but is a real risk on messy real-world data, which is this
  task's actual point. Full suite re-verified against a live ephemeral Postgres afterward (237
  passed), `ruff`/`pyright` clean.

### TASK-008 — Feature-timing classification

- **Owner:** DATA_ENGINEER
- **Priority:** P0
- **Status:** READY
- **Depends on:** TASK-007
- **Goal:** Classify every field as `DECISION_TIME`, `POST_DECISION`, `OUTCOME`, `IDENTIFIER`, `METADATA`, or `UNKNOWN`.
- **Invariant:** Post-decision, outcome, and unknown fields cannot enter discovery features.
- **Done when:** Benchmark classification matches expected metadata and leakage tests pass.
- **Status note (2026-08-17, Architect):** Unblocked — `TASK-007` is `DONE`. Not started this
  iteration; this is a real, separate design task (classification methodology, and
  `FeatureTiming` — `packages/schemas/domain.py` — doesn't have an `UNKNOWN` member yet), not a
  drive-by extension of `TASK-007`'s profiler.

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
- **Status:** DONE
- **Depends on:** TASK-010
- **Goal:** Build versioned analytical datasets with separate features, outcomes, identifiers, and metadata plus transformation configuration and lineage.
- **Evidence:** Synthetic analytical dataset `travel-bookings-analytical-v1.0.0` contains four
  physically separate, row-aligned CSV partitions; a typed schema, source/artifact SHA-256 lineage,
  feature timing, customer clustering key, chronological splits, missingness diagnostics, and an
  attached Statistics-owned TASK-013 outcome contract. Standalone feature, outcome-column,
  excluded-column, and version manifests plus `make analytical-dataset` provide the first blind
  discovery input contract. Completed 2026-08-13 by explicit founder direction; production
  customer-input canonicalization under TASK-010 remains blocked and is not implied.

### TASK-012 — Temporal split builder

- **Owner:** DATA_ENGINEER
- **Reviewer:** STATISTICS
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-011
- **Goal:** Deterministically create development, validation, and future holdout splits without random time shuffling.
- **Evidence:** Split contract `travel-bookings-temporal-split-v1.0.0` and row membership are in
  the approved TASK-011 directory. Closed, contiguous booking-date intervals assign every row
  exactly once with no shuffle: development 2024, validation H1 2025, future holdout H2 2025.
  Outcome finality follows Statistics-owned TASK-013's closed-benchmark contract; the manifest
  forbids carrying that assumption to live data without maturation windows. Boundary, overlap,
  ordering, determinism, alignment, and availability tests passed on 2026-08-13.

## Phase 4 — Outcome analytics

### TASK-013 — Outcome definition layer

- **Owner:** STATISTICS
- **Implementation support:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-011
- **Goal:** Version explicit definitions for actual gross profit, contribution margin/value percentage, cancellation, refund, support cost, and repeat purchase.
- **Evidence:** Outcome contract v1.0.0 preregistered on 2026-08-13 in `docs/analytics/outcome-contract.md`
  and `packages/analytics/src/policy_analytics/outcomes/` (`contract.py` = versioned definitions,
  `aggregation.py` = pure group-summary/sign-convention arithmetic), pinned to the delivered
  analytical dataset `travel-bookings-analytical-v1.0.0` (dataset identity
  `98ad4e7e08e63ee9e31f9317ca408f2895da8bece49324482915e24df0aee04c`). Primary outcome is
  `contribution_margin_eur` (0% missingness, verified against `outcomes.csv`); six secondary/
  decomposition outcomes plus `repeat_purchase_180d` as MNAR-bounded exploratory only (9.72%
  overall missingness, 45.7% among cancelled bookings vs. 7.2% otherwise — an empirically confirmed
  outcome-dependent selection trap). Harm-direction sign convention and deterministic historical
  exposure formula are given so `TASK-016` can rank across outcomes without inventing semantics.
  14 contract tests (including two pinned to the live dataset artifact), ruff, and pyright were
  executed and pass. Closes the outcome-contract half of `HANDOFF-003`.
- **Amendment (2026-08-13, v1.1.0, ADR-011):** Added, without reopening the primary-outcome
  decision: empirically verified `valid_range` per outcome, an explicit
  no-winsorization/no-transformation-at-discovery rule, an explicit `aggregation_rule` per outcome,
  and a machine-readable `DISCOVERY_CONTRACT` (`DiscoveryStatisticalContract`) fixing the
  discovery-time statistical contract — search-fit split (`development` only; `validation`/
  `future_holdout` are diagnostic-only), minimum support (imported from validation gate G03's
  `min_exposed_records = 50`, not a second number), excluded explanatory-variable classifications
  (only `DECISION_TIME` may appear in a condition), causal-language limits for candidate text, and
  missing-outcome handling for discovery specifically. Verified against the persisted `TASK-015`
  run: all 15 candidates comply (only `DECISION_TIME` features used, `n_exposed >= 50` on
  development, fit on development only) — no rerun required. 21 outcome-contract tests (up from
  14), ruff, and pyright executed and pass; full suite 60 passed. Handoffs: `HANDOFF-015` (Data
  Engineer) confirmed already fulfilled; new confirmatory handoff to ML Discovery below.
- **Not included:** The real-customer outcome contract (`OQ-002`, still open) and right-censoring/
  outcome-maturation handling for live data — both explicitly out of scope, see
  `docs/analytics/outcome-contract.md` §1 and §7.

### TASK-014 — Baseline business statistics

- **Owner:** STATISTICS
- **Priority:** P1
- **Status:** READY
- **Depends on:** TASK-013
- **Goal:** Sanity-check overall distributions, time/segment/supplier/manager trends, and outcome prevalence before discovery.
- **Status note (2026-08-17, Architect):** Unblocked — `TASK-013` is `DONE`. Not started; P1, so it
  has not displaced the P0 chain (`TASK-005`–`TASK-024`).

## Phase 5 — Pattern discovery

### TASK-015 — Discovery engine v0

- **Owner:** ML_DISCOVERY
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-011, TASK-012, TASK-013, HANDOFF-007
- **Goal:** Use simple interpretable methods first—shallow trees, boosting with rule extraction, and subgroup discovery—to return 10–20 harmful candidate patterns.
- **Candidate contract:** Conditions, support, N, raw difference, deterministic economic exposure, stability indicators, and warnings.
- **Operational readiness (2026-08-14, Architect):** The isolated runner has migrated from Codex
  to a minimal pinned Groq tool-calling actor. `HANDOFF-036`, `HANDOFF-037`, and
  `HANDOFF-038` are resolved: exposed historical credentials were revoked and authenticated
  container preflight passed with model
  `openai/gpt-oss-120b`. Signed run `task-015-official-20260814-006` attempted launch without usable
  bearer authentication, received HTTP 401, exited before Discovery work, and is irreversibly
  `FAILED`; it cannot be verified, retried, or reused. Its manifest SHA-256 was
  `f2981fbc8ff55ba31ba4f4124d3a7bab38d0c844b0024832bdc1e024700d6a10`; bundle ID was
  `4bb19187c3dc2f286e0a2326aacc54bf8c8959461a75d607ef5bdf0b10b1216d`. The runner pins the Groq actor
  image `policy-blind-agent@sha256:0d64b3acd49008577216fd79e14c9c242e6c99b52712931ee7ef2392ecae98a2`
  and output schema v1.1.0. Verify/launch reject current-source drift; freeze validates signed
  dataset/contracts/splits/provenance/timing/candidate-count/language requirements. Discovery did
  not execute. Run `…-002` remains audit-only; `…-003`/`…-004` are failed issuance attempts;
  `…-005` is a failed CLI launch caused by the obsolete `--full-auto` flag; `…-006` is the failed
  unauthenticated launch; `…-007` is a second failed HTTP-401 launch before Discovery work. None
  is eligible; `…-008` is a third failed HTTP-401 launch before Discovery work. After credential
  auth setup, require successful `make blind-provider-preflight` with the exact Groq key and
  model before issuing unique run `task-015-official-20260814-011`. Agent/model/image are signed
  and launch fails closed on drift. Do not issue runs
  merely to test authentication. Only then perform fresh Blind Discovery execution and freeze.
  The replacement actor has bounded list/read/Python tools, a read-only workspace plus a separate
  writable `output/` mount, exact three-file output enforcement, and regression coverage proving
  missing/invalid outputs transition `COMPLETED` runs to `FAILED`. Official run `…-011` then failed
  before discovery on the account's 8,000 TPM limit; it is irreversibly `FAILED` with no outputs.
  `HANDOFF-039` is resolved: completion/context/tool-output budgets, capped 429 retries, a
  three-tool-turn regression, and authenticated two-turn container preflight passed on image
  `policy-blind-agent@sha256:d6885a0cbaa3d752e99411ad3960cdf1f27a6551e9fd872d21fcb3c9a17ff9d6`.
  `…-012` subsequently failed before producing outputs because the model generated a paginated
  `read_file(line_start, line_end)` call not admitted by the frozen tool schema; the run is
  irreversibly `FAILED`. `HANDOFF-040` is resolved: 1-based inclusive pagination capped at 250
  lines, exact GPT-OSS `200..400` regression coverage, and authenticated two-page preflight passed
  on the current pinned image. Official run `…-013` then failed with no outputs when the approved
  model requested an undeclared bounded workspace `search(path, query)` tool and Groq returned
  `tool_use_failed`. `HANDOFF-041` implementation is complete: the actor now exposes bounded literal
  `search(path, query)` with path/symlink/file/byte/result caps and permits at most two corrective
  turns after provider `tool_use_failed`. On 2026-08-15 image
  `policy-blind-agent@sha256:5503b6d0c6cc02adda6f854a1eb51e8589ae58834760c9780ba28fb73ce6565a`
  passed an authenticated, production-isolated rehearsal with `openai/gpt-oss-120b`: workspace
  listing, paginated reads, exact bounded search, Python execution, controlled failure recovery,
  and host validation of exactly three schema-v1.1.0 dummy outputs. The final type-safe rebuild is
  pinned as `policy-blind-agent@sha256:0d64b3acd49008577216fd79e14c9c242e6c99b52712931ee7ef2392ecae98a2`,
  but its two authenticated repetitions failed closed on Groq's 200,000 TPD quota before completing
  acceptance. On 2026-08-16 the human coordinator reported `BLIND_REHEARSAL_VALID` for the final
  digest; `HANDOFF-041` is resolved. Official run `task-015-official-20260815-014` is issued and
  `VERIFIED`, signed to `openai/gpt-oss-120b`, but is now audit-only because the runtime/source
  contract changed before launch. `HANDOFF-042` is resolved: official execution is deterministic,
  networkless, and uses zero provider requests/tokens/cost. `scripts/run_discovery.py` consumes
  dataset identity, outcome metadata, contract versions, feature timing, method version, seed, and
  provenance hashes from signed `BLIND_MANIFEST.json`; it no longer expects the absent private
  dataset `manifest.json` or hardcodes outcome contract v1.0.0. Image
  `policy-blind-agent@sha256:9ad6e1a78ca41a7c04895d1d99c7775e77fc2c8fbb4f23cee268ed04534c7c9b`
  passed a full truth-free Docker rehearsal and normal freeze validation on 2026-08-16.
- **Blind-compliant run (2026-08-16, Architect):** Issued, launched, and froze
  `task-015-official-20260816-015` end to end through the deterministic, networkless, zero-token
  pipeline (`make blind-issue`/`blind-verify`/`blind-shell`/`blind-freeze`), satisfying ADR-008
  isolation unlike the earlier full-checkout artifact below. `status=PERSISTED`, 15 candidates from
  6,945 evaluated hypotheses. Committed via `scripts/commit_blind_candidates.py` (signed receipt
  `artifacts/blind/task-015-official-20260816-015.receipt.json`) before
  `scripts/evaluate_synthetic_benchmark.py` opened `hidden_ground_truth.json`
  (`artifacts/blind/task-015-official-20260816-015.evaluation.json`): commitment verified,
  `ground_truth_pattern_count=9`. Precision/recall/direction/impact-error scoring is intentionally
  not computed here — that belongs to `TASK-028`, still `BLOCKED`. Frozen artifacts archived in
  `artifacts/blind/task-015-official-20260816-015.*`.
- **Evidence:** Deterministic interpretable beam-search engine and CLI in
  `packages/analytics/src/policy_analytics/discovery/engine.py` and `scripts/run_discovery.py`;
  methodology in `docs/analytics/discovery-engine-v0.md`; 2026-08-13 run artifact
  `artifacts/discovery/task-015-candidates.json` contains 15 immutable candidate conjunctions from
  6,945 evaluated hypotheses, pinned to analytical dataset identity
  `98ad4e7e08e63ee9e31f9317ca408f2895da8bece49324482915e24df0aee04c` and outcome contract v1.0.0.
  Conditions were selected on development only; validation/future splits are diagnostics. No
  hidden-ground-truth artifact was opened, but this full-checkout run does not satisfy ADR-008 and
  therefore does not close TASK-017. Statistics validation is requested in HANDOFF-016.

### TASK-016 — Candidate ranking v0

- **Owner:** ML_DISCOVERY
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-015
- **Goal:** Rank candidates by economic impact, support, stability, actionability, and novelty—not model importance alone.
- **Status note (2026-08-16, Architect):** Unblocked — `TASK-015` is `DONE`. No ranking
  implementation exists yet (`grep` for a ranking module in `packages/analytics` finds nothing);
  this is unstarted work, not a stale blocker.
- **Implementation evidence (2026-08-16, ML Discovery, ADR-020):** A pure, deterministic
  five-component ranker — `packages/analytics/src/policy_analytics/discovery/ranking.py`
  (`rank_candidates`/`CandidateSignals`/`RankingWeights`), `ranking_signals.py` (builds those
  inputs from a frozen candidates document plus the analytical dataset, reusing
  `validation.apply`'s already-tested split/condition-evaluation functions rather than a third
  duplicate implementation), and `discovery/actionability.py` (extracted from `discovery.engine`
  so the search-time label and the ranking component share one definition — `engine.py`'s own
  output and existing tests are unchanged). CLI: `scripts/rank_candidates.py`. Methodology:
  `docs/analytics/candidate-ranking-v0.md`. Weights (v0 defaults, generic business reasoning, not
  tuned against results or hidden ground truth — see ADR-020) score economic impact, support,
  temporal-stability, actionability, and novelty (non-redundancy against other candidates in the
  batch); missing stability scores `0.0`, never `1.0`. Ran for real against all 15
  `task-015-official-20260816-015` candidates, frozen at
  `artifacts/discovery/task-016-candidate-ranking-task-015-official-20260816-015.json`. 24
  new/updated tests, `ruff`, and `pyright` pass; full suite (170 passed, 9 pre-existing
  PostgreSQL-integration skips) passes. Weights are provisional pending Product/Statistics review,
  requested in `HANDOFF-045`.

### TASK-017 — Blind discovery test

- **Owner:** ML_DISCOVERY
- **Reviewer:** CODE_REVIEWER
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-003, TASK-016
- **Goal:** Run without hidden ground truth and persist candidates before evaluation files are opened.
- **Status note (2026-08-16, Architect):** Reconciled against `memory/CURRENT_STATE.md`. The
  literal behavioral goal — a fully blind (ADR-008-compliant) run that persists a signed candidate
  commitment before evaluation opens hidden ground truth — was demonstrated by
  `task-015-official-20260816-015` (commit receipt predates `evaluate_synthetic_benchmark.py`
  reading `hidden_ground_truth.json`; see `TASK-015` evidence). That retires the blind-infrastructure
  risk this task exists to catch. It is **not** marked `DONE`: its own listed dependencies are not
  both satisfied — `TASK-003` is `IN_REVIEW` (not `DONE`) and `TASK-016` is `READY` (ranking
  unimplemented), and the candidates persisted in that run are unranked raw discovery output, not
  the ranked artifact `TASK-016` is meant to produce. Closing this task once those land should be
  wiring/confirmation, not new blind-runtime risk.
- **Status note (2026-08-16, ML Discovery):** Both listed dependencies are now satisfied —
  `TASK-003` closed the same day via `HANDOFF-030`, and `TASK-016` (above) is now `DONE` with a
  ranked artifact over the exact `task-015-official-20260816-015` candidates this task's blind run
  produced. Per the Architect note directly above, closing this task from here should be
  Architect/Code-Reviewer wiring/confirmation, not new implementation — requested in `HANDOFF-045`.
- **Closed on confirmation basis (2026-08-17, Architect) → `DONE`.** Verified, not just taken on
  trust: `TASK-003`'s `HANDOFF-030` resolution and `TASK-016`'s artifacts
  (`ranking.py`/`ranking_signals.py`/`actionability.py`, `docs/analytics/candidate-ranking-v0.md`,
  `artifacts/discovery/task-016-candidate-ranking-task-015-official-20260816-015.json`, `ADR-020`)
  all exist and are real. No new blind-runtime work is needed — the behavioral goal (run without
  hidden truth, persist a signed commitment before evaluation opens ground truth) was already
  satisfied by `task-015-official-20260816-015`. `HANDOFF-045`'s separate question — whether the v0
  ranking weights are a Product/Statistics-approved business contract, not just an ML Discovery
  default — remains genuinely open and is **not** resolved by this closure; that question is
  outside Architect/Code-Reviewer authority to answer and stays with Product/Statistics in
  `HANDOFF-045`.

## Phase 6 — Statistical validation

### TASK-018 — Validation and evidence contract

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** DONE
- **Depends on:** none
- **Goal:** Predefine sample-size, uncertainty, temporal/segment stability, multiple testing, confounding, leakage, selection, seasonality, evidence grades, and policy-readiness rules.
- **Evidence:** Contract v1.0.0 preregistered on 2026-08-13 in `docs/analytics/validation-contract.md` and `packages/analytics/src/policy_analytics/validation/` (16 ordered gates, thresholds, cumulative evidence requirements, language rules, readiness matrix, backtest methodology). 26 contract tests, ruff, and pyright were executed and pass. See ADR-007.
- **Not included:** Applying the contract to candidates (TASK-019), which requires persisted candidates from TASK-017.
- **Known limitation (2026-08-14, ADR-014), fixed (2026-08-14, ADR-015):** First real application
  (`TASK-019` dry run) found gate G05's bootstrap p-value method structurally unable to pass BH
  correction at family sizes in the low thousands, regardless of true effect size. Fixed same day
  in contract **v1.1.0**: G05's p-value source is now `normal_approx_two_sided_p` on the bootstrap
  standard error (`math.erfc`-based, no resolution floor), mathematically verified sufficient to
  roughly `family_size = 100,000` with ~300 decades of headroom. Regression tests
  (`tests/analytics/test_g05_multiplicity_fix.py`, synthetic/mathematical only, no ground truth)
  prove the old method's structural failure, the new method passing a strong synthetic effect, and
  the new method still rejecting a null synthetic effect. The already-frozen v1.0.0 dry-run
  artifact was not touched or re-graded. See `docs/analytics/validation-contract.md` §4a.

### TASK-019 — Validation framework implementation

- **Owner:** STATISTICS
- **Implementation support:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-017, TASK-018
- **Goal:** Apply the standardized validation contract to persisted candidates.
- **Dry-run evidence (2026-08-14, Statistics):** Implemented and ran the full 16-gate engine
  (`packages/analytics/src/policy_analytics/validation/apply.py`, CLI
  `scripts/validate_candidates.py`) against the persisted `TASK-015` artifact, freezing
  `artifacts/validation/task-019-validation-report.json`. Per candidate: cluster bootstrap
  (customer_id, 2000 reps, seed 20260813) for uncertainty; BH correction at family_size=6945 from
  the discovery manifest; stratified (manager × supplier) confounding adjustment with an E-value;
  customer_segment heterogeneity check; three-split temporal-stability check; a seasonality
  concentration check; a 12-perturbation robustness battery (leave-one-manager-out, winsorized
  outcome, alternative outcome, threshold perturbation); and a combined-cohort bootstrap CI for
  economic materiality. The adjustment/heterogeneity covariates (manager, supplier,
  customer_segment) were chosen from generic booking-domain reasoning before running anything, not
  from `hidden_ground_truth.json` or `synthetic_benchmark.py` — neither file was opened. 12 unit
  tests plus one real-artifact integration test pass; ruff and pyright are clean.
  **Result: all 15 candidates DOWNGRADE to `LEVEL_1_DESCRIPTIVE`** (`policy_readiness =
  EXPERIMENT_ONLY`); none PASS, none REJECT. Every candidate fails gate G05 (multiple comparisons)
  and G13/G14 (no design, not randomized — expected and correct for observational data); several
  also fail G12 (robustness) or G06 (CAND-014 only, confounding).
- **Why this does not close the task:** (1) **Blind-protocol non-satisfaction.** Per TASK-015's own
  readiness note, the candidate artifact was produced in a full-checkout run that does not satisfy
  ADR-008/TASK-017; grading its statistical soundness is not the same as completing a blind
  discovery test, and this run must not be represented as one. (2) **Founder readiness block.**
  TASK-015 carries an explicit instruction not to advance this pipeline until TASK-012 completes
  and readiness is rechecked from the approved blind workspace; this validation does not lift that
  block. (3) **A newly discovered G05 methodology defect.** Every candidate's bootstrap p-value
  sits at the 2000-replicate resolution floor (~0.0005), which cannot pass BH correction at
  family_size=6945 for any candidate regardless of true effect size — the floor exceeds
  alpha·rank/family_size for every rank once family_size is in the low thousands. A supplementary
  normal-approximation diagnostic (same bootstrap SE, no scipy) puts every candidate's p-value
  below 1e-6, meaning this is very likely an estimator-precision artifact, not real absence of
  significance — but the preregistered method was applied faithfully and was not changed after
  seeing this outcome. See ADR-014 for the recommended fix, to be applied as a new contract version
  before the next run, not retroactively to this one.
- **Handoff:** No candidate reached `PASS`, so no "validated findings" handoff to Architect/Product
  was made — there is nothing to hand off yet. `HANDOFF-016` is updated to `IN_PROGRESS` with this
  result and what is needed before a closing run.
- **G05 fix shipped (2026-08-14, Statistics, ADR-015):** Validation contract bumped to **v1.1.0**.
  G05's binding p-value is now `normal_approx_two_sided_p` (bootstrap SE, `math.erfc`-based, no
  resolution floor) instead of the empirical `bootstrap_two_sided_p`; nothing else in the contract
  changed. `packages/analytics/src/policy_analytics/validation/apply.py` now computes this as the
  binding G05 source and reports the old empirical value as a labeled diagnostic (swap of the
  previous roles). `scripts/validate_candidates.py` now refuses to overwrite an existing frozen
  output without `--force`, protecting the v1.0.0 dry-run artifact structurally, not just by
  discipline. Verified against real `TASK-015` candidate data as a **code-behavior check only,
  nothing persisted**: several candidates' G05 gate now passes at these effect sizes (some reach
  `adjusted_observational_association`/`shadow_policy` if graded in isolation), confirming the
  estimator works — this changes nothing about the two governance blockers in the previous bullet,
  which remain the reason `TASK-019` stays `IN_PROGRESS`. 8 new regression tests
  (`tests/analytics/test_g05_multiplicity_fix.py`) plus fixes to 2 existing test files; 97 tests
  total pass, ruff and pyright clean. Full defect/fix/migration write-up:
  `docs/analytics/validation-contract.md` §4a.
- **Still not `DONE` at that point:** the fix only removed the third blocker from the list above.
  `TASK-019` was to close only once a genuinely `TASK-017`-compliant candidate artifact existed and
  was graded under v1.1.0 as a new, separately frozen run.
- **Closing-run readiness (2026-08-14, Statistics, ADR-018):** Checked the actual blind-agent
  output schema (`tools/blind_agent/models.py`, `OUTPUT_SCHEMA_VERSION = "1.1.0"`) against what
  the validation engine parses and found it materially different from the artifact the dry run
  used — no per-split breakdown on each candidate, and `evaluated_hypotheses` lives in a sibling
  `discovery_metrics.json`, not inline. `_validate_one` already recomputes every quantity from the
  analytical dataset via each candidate's `conditions` and never trusted the old schema's
  precomputed split stats either, so only the evaluated-hypothesis lookup needed a real fix
  (`_evaluated_hypotheses()`, checked against both shapes). `run_validation` gained an optional
  `metrics_path` parameter, an `INSUFFICIENT_CANDIDATES` status handler with the recorded reason
  surfaced, and a candidate/payload outcome-ID consistency check. `scripts/validate_candidates.py`
  is now `argparse`-driven (`--candidates`, `--metrics`, `--dataset-root`, `--output`,
  `--analysis-run-id`, `--force`) instead of hardcoded paths, and requires explicit
  `--blind-compliant`/`--founder-block-lifted` flags — frozen into the output's
  `process_compliance` block — whenever grading anything other than the historical dry-run
  artifact; nothing is inferred from `TASKS.md` prose. Verified end-to-end, both via pytest and a
  direct CLI invocation, against a schema-valid `CandidatesDocument`/`MetricsDocument` built from
  the real Pydantic models (not a guessed shape) — parses, grades, and freezes correctly with the
  compliance flags recorded. New tests: `tests/analytics/test_validation_apply.py`
  (`_evaluated_hypotheses` unit tests, a full schema-compatibility integration test, an
  outcome-mismatch rejection test, an `INSUFFICIENT_CANDIDATES` error test). 106 tests total pass,
  ruff and pyright clean. The v1.0.0 dry-run artifact remains untouched throughout.
  **Definition of done for this readiness work is met: the next genuine blind `TASK-015`/`TASK-017`
  artifact, whatever exact filenames the blind runner produces, can be pointed at directly.** What
  remains before `TASK-019` itself closes is entirely outside Statistics: a successful blind run
  (`HANDOFF-036`/`HANDOFF-037`, credential/preflight issues) producing that artifact.
- **Closing run (2026-08-16, Statistics) → `DONE`.** `task-015-official-20260816-015` (issued,
  launched, and frozen through `blind/`'s deterministic pipeline; candidates committed via signed
  receipt before ground truth was opened) graded end to end: `uv run python
  scripts/validate_candidates.py --candidates artifacts/blind/task-015-official-20260816-015.candidates.json
  --metrics artifacts/blind/task-015-official-20260816-015.discovery_metrics.json --output
  artifacts/validation/task-019-official-20260816-015.json --analysis-run-id
  task-019-validation-run-official-015 --blind-compliant --founder-block-lifted`. Schema
  compatibility held exactly as `ADR-018` verified it would — no code changes needed. **Result: 6
  of 15 candidates PASS at `adjusted_observational_association`/`SHADOW_POLICY`
  (`CAND-004/007/009/010/012/015`); 9 DOWNGRADE to `descriptive_observation`/`EXPERIMENT_ONLY`; none
  REJECT.** This is the first genuine positive validation result in the project — not a dry run,
  not a code-behavior check. Frozen at `artifacts/validation/task-019-official-20260816-015.json`,
  `validation_contract_version = "1.1.0"`. Full suite still 125 passed, ruff/pyright clean. Feeds
  `TASK-020`/`TASK-021`/`TASK-022`/`TASK-023`/`TASK-028` directly — see below.

### TASK-020 — Evidence classification

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-019
- **Goal:** Assign exactly one level: descriptive, predictive association, adjusted observational, quasi-causal, or experimental.
- **Evidence (2026-08-16):** Produced automatically as part of `TASK-019` grading, not a separate
  implementation — `classify_evidence_level` (`packages/analytics/src/policy_analytics/validation/grading.py`)
  assigns exactly one of the five levels per candidate from cumulative gate satisfaction, enforced
  by `ValidationReport.__post_init__` (a report cannot claim a level its own gates don't support).
  On the closing run: 6 candidates at `adjusted_observational_association`, 9 at
  `descriptive_observation`, 0 rejected. No candidate reached `quasi_causal_evidence` or above,
  correctly — `IdentificationDesign.OBSERVATIONAL` caps every candidate at level 3 regardless of
  gate outcomes, since no design or randomization exists for any of them.

### TASK-021 — Adjusted effect estimation v0

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-019
- **Goal:** Estimate adjusted effects with the simplest defensible method, uncertainty, controls, and explicit non-identifiability/limitations.
- **Evidence (2026-08-16):** Also produced as part of `TASK-019`'s engine, not separately — exposure-
  weighted stratification on (`manager`, `supplier`) with an E-value (`_stratified_two_way_adjustment`,
  `e_value` in `apply.py`), gated by gate G06 (attenuation ≤50%, E-value ≥1.5, sign preserved,
  ≥50% stratum coverage). Every `ValidationReport` carries `adjusted_effect` as a full
  `EffectEstimate` (value, CI, method, unit) alongside the raw one, plus `controlled_variables` and
  `potential_confounders` explicitly listed. Non-identifiability is explicit by construction:
  `IdentificationDesign.OBSERVATIONAL` caps every candidate at
  `adjusted_observational_association` regardless of adjustment quality — adjustment narrows
  confounding risk, it never claims identification. On the closing run, all 6 PASS candidates
  cleared G06; `TASK-028`'s scoring (below) found the adjusted point estimates still substantially
  diluted relative to ground truth — a real, disclosed limitation, not hidden by this task's own
  framing.

### TASK-022 — Confounding-trap evaluation

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-003, TASK-021
- **Goal:** Verify that known manager/supplier and other synthetic traps are rejected or conservatively downgraded.
- **Evidence (2026-08-16), via `TASK-028`:** None of T01–T05's `apparent_feature` conditions
  (`manager`, `supplier`, `acquisition_channel`, `payment_method`; `manual_exception == true`)
  appear in any of the 15 persisted candidates — the closest, `manual_exception == false` in three
  candidates, is the opposite polarity from T05 and does not match. **Result: 0/5 traps
  promoted.** This satisfies the hard-disqualifier floor, but honestly: it is non-promotion by
  absence (the traps were never proposed as candidates at all), not demonstrated active rejection
  of a trap-shaped candidate by gate G06 — a materially weaker claim, stated as such in
  `docs/benchmark/task-029-benchmark-report-v1.md` §3.3 rather than reported as unqualified
  success. The closest active analog: all 6 PASS candidates independently cleared G06's
  manager×supplier stratified adjustment as ordinary `TASK-019` grading, exercising the same
  adjustment machinery the traps exist to stress-test, just not against a trap-shaped candidate.

## Phase 7 — Economic impact

### TASK-023 — Economic impact engine v0

- **Owner:** STATISTICS
- **Implementation support:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-021
- **Goal:** Deterministically report affected records, average effect, historical impact, justified annualization, and uncertainty range.
- **Evidence (2026-08-16):** Gate G15 in `apply.py` reports affected records (`exposed_total`),
  average effect (`harm_per_booking`), historical impact with a cluster-bootstrap 95% CI
  (`historical_exposure_ci_eur`), and compares against `min_material_annual_impact`/
  `min_material_outcome_share`. Annualization is deliberately **not** claimed — the benchmark
  window is fixed at 24 months and nothing here extrapolates beyond the observed window, matching
  `docs/analytics/validation-contract.md` §8's justified-annualization requirement by declining to
  annualize rather than inventing a rate.
- **Known limitation, found by `TASK-028`, not hidden:** reported historical impact is computed
  over each candidate's *own* exposed population, which — on the closing run — is routinely
  15–16× larger than the specific ground-truth pattern it partially recovers. This inflates
  reported total impact well past the true value even though the per-booking direction and the
  qualitative finding are correct (`docs/benchmark/task-029-benchmark-report-v1.md` §3.6). A
  remediation (reporting a range bounded by whole-rule exposure and attribution-narrowed exposure)
  is proposed there and tracked via `HANDOFF-043`, not yet implemented.
- **Versioned result contract (2026-08-17, `HANDOFF-025` resolution, `ADR-021`):**
  `EconomicImpactResult`/`build_economic_impact_result`
  (`packages/analytics/src/policy_analytics/validation/economic_impact.py`,
  `ECONOMIC_IMPACT_CONTRACT_VERSION = "1.0.0"`) gives G15's already-computed diagnostics a
  field-for-field, tested output shape matching `EconomicImpactPersistence` — the point estimate is
  now the real combined-window sample statistic (not the bootstrap replicate mean), with a
  per-record CI exposed separately from the total-exposure CI. `affected_records` is confirmed to
  be the full combined window, not `exposed_records` — a correction flagged to Product
  (`HANDOFF-046`). Full semantics: `docs/analytics/economic-impact-contract.md`. Does not change the
  known-limitation above; that remains `HANDOFF-043`'s open question.

## Phase 8 — Validated findings

### TASK-024 — Full finding persistence model

- **Owner:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-020, TASK-023
- **Goal:** Extend the current skeleton with pattern, support, raw/adjusted effects, uncertainty, impact, evidence, warnings, stability, status, and lineage.
- **Product field contract:** `docs/product/finding-product-contract.md` (Required for MVP / Optional later / Never-shown-without-qualification field lists, mapped to `ValidationReport`) is available ahead of this task, complementing `HANDOFF-008`/`HANDOFF-012`. Status remains `BLOCKED` — this is input for scoping, not implementation.
- **Preparation (2026-08-13):** Database/migration, Pydantic, API boundary, promotion invariant,
  and lineage proposal completed in `docs/architecture/finding-persistence-contract.md`; preparation schemas
  live in `apps/api/app/findings/contracts.py`. CandidatePattern is explicitly separate from
  Finding, and rejected/unvalidated candidates cannot be promoted. Implementation remains blocked
  by TASK-020/TASK-023 plus Product lifecycle/summary semantics (`HANDOFF-024`) and the final
  Statistics-owned impact result (`HANDOFF-025`).
- **Product lifecycle/summary contract (2026-08-14):** `HANDOFF-024` resolved — `docs/product/finding-product-contract.md`
  §12 fixes `FindingLifecycleStatus` (`ACTIVE`/`SUPERSEDED`/`WITHDRAWN`, forward-only transitions,
  no "reviewed" or "awaiting validation" states) and the stored/versioned `title`/`summary` snapshot
  contract (mechanical v0 template, `title_template_version`). Status remains `BLOCKED` on
  `HANDOFF-025` (Statistics-owned impact result) — this only clears the Product-owned half.
- **Status note (2026-08-17, Architect):** Unblocked — `TASK-020` and `TASK-023` are `DONE`
  (`task-015-official-20260816-015`'s closing run: 6/15 candidates `PASS` at
  `adjusted_observational_association`/`SHADOW_POLICY`), and `HANDOFF-025` is now resolved with a
  verified field-by-field mapping from `TASK-023`'s real output to `EconomicImpactPersistence`.
- **Implementation (2026-08-17, Architect) → `DONE`.** Migration `20260817_0003` extends
  `analysis_runs` with the reproducibility envelope, adds `candidate_patterns`/`validation_reports`,
  and replaces `findings` with the real read-optimized shape (lineage as JSONB per row — a
  deliberate v0 simplification from the 5-table relational lineage the prep doc proposed, since
  `contracts.py`'s own `LineageReference` was already a plain value object, not a relational
  construct). `app/findings/persistence.py` implements the three internal services the prep doc
  specified (candidate/report persistence, promotion), enforcing the invariant that a report with
  no `evidence_level` cannot be promoted. `app/findings/summary.py` implements the product
  contract's exact v0-mechanical title/summary template; `harm_direction_phrase` added to
  `OutcomeDefinition` to source it. `scripts/promote_findings.py` (the actual demo entrypoint)
  ingests the three real closing-run artifacts and persists everything through that pipeline —
  re-deriving per-split metrics from the real analytical dataset via `apply.py`'s own
  `split_stats`/`rule_expr` rather than trusting anything precomputed. **Real result, run against a
  live ephemeral PostgreSQL container: 1 `AnalysisRun`, 15 `CandidatePattern`/`ValidationReport`
  rows, and — per `docs/product/finding-product-contract.md` §0 ("a Finding is any graded candidate
  output," not only a `PASS`-verdict one) — all 15 candidates promote to `Finding`, since none
  `REJECT` on this run: 6 at `adjusted_observational_association`/`shadow_policy`, 9 at
  `descriptive_observation`/`experiment_only`.** (An earlier draft of this work assumed only the 6
  `PASS` candidates should promote and wrote a test asserting exactly that; the test caught its own
  wrong assumption against the real run and was corrected, not the code.) 22 new tests (unit +
  live-Postgres integration through the real HTTP routes) pass, full suite green twice in a row
  against the same database (rerun-safety), `ruff`/`pyright`/`pnpm typecheck` all clean.

### TASK-025 — Findings API completion

- **Owner:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-024
- **Goal:** Make existing list/detail endpoints serve real persisted validated findings with safe evidence-aligned schemas.
- **Implementation (2026-08-17, Architect) → `DONE`.** `FindingRead` rewritten to
  `docs/product/finding-product-contract.md` §1's exact "Required for MVP" field list — nothing
  from §2 "Optional later" (e.g. full 16-gate detail table stays on `validation_reports`, not
  duplicated into the API response). `affected_records` (not `exposed_records`) is used for
  money-at-stake, per Statistics' `HANDOFF-046` recommendation. `materiality_pass` is exposed as
  pass/fail only — the underlying threshold never appears in the response (verified: grepped a live
  response for `min_material_annual_impact`, not present). `GET /api/v1/findings` filters to
  `lifecycle_status=ACTIVE` by default (§12.1); non-`ACTIVE` findings remain reachable by direct
  ID. Verified against the real closing-run data through a running `uvicorn` instance and live
  `curl`, not just `TestClient`: 15 findings listed, evidence/impact shape matches §1 exactly for
  both a `shadow_policy` and an `experiment_only` finding. `apps/web/lib/api/types.ts`'s `Finding`
  type synced to match (mechanical only, same posture as `HANDOFF-044`); one pre-existing page
  reference (`finding.status`, from the old `ResourceStatus`-based skeleton) fixed to
  `finding.lifecycle_status` — `pnpm typecheck`/`lint`/`test` all pass.

## Phase 9 — First product UI

**Frontend application shell (2026-08-13):** Ahead of `TASK-026`/`TASK-027` themselves, a
minimal, product-semantics-free foundation now exists at `apps/web`: an application shell
(`app/(app)/layout.tsx`, nav, routing) distinct from the marketing page at `/`; a typed API
client (`lib/api/`, documented in `lib/api/README.md`) that mirrors `apps/api/app/api/schemas.py`
and `packages/schemas` by hand and normalizes FastAPI's error envelope into a typed `ApiError`;
reusable `LoadingState`/`ErrorState`/`EmptyState` primitives (`components/states/`); routed
`/datasets` and `/findings` placeholder list pages wired to the real (currently minimal) API,
each `force-dynamic` so they reflect live backend state per request rather than a build-time
snapshot; and a dev-only `/dev/status` view of `/health`/`/ready` (404s outside development).
Both pages show real API data/errors/empty-state today, not mock content — no business findings
are hardcoded. This does not change either task's `BLOCKED` status at the time: both needed
`TASK-025`'s real findings API before real content can render, and `TASK-026` additionally needed
an approved Product list-screen spec, delivered below. No new Architect handoff was needed for this
shell work; the existing Findings-API gap is already tracked by `HANDOFF-005`.

**Frontend readiness pass (2026-08-14):** Audited (not implemented) the shell above against the now-
complete `docs/product/findings-list-screen.md`/`finding-detail-screen.md`. Findings: API client
boundary is clean (`fetch` called only from `lib/api/client.ts`; no page bypasses it); `ApiError`
typed-error handling, the three state primitives, routing (`app/(app)/`), and the server/client
component split are all sound and require no changes; `lib/api/types.ts` still matches the live
`FindingRead`/`DatasetRead` byte-for-byte (no drift, no invented/duplicated schema); no mock/fake
finding data anywhere in `apps/web`. Gap found and fixed (infrastructure-level, no Finding semantics
touched): no frontend test runner existed at all. Added `vitest` + `@testing-library/react`
(`apps/web/vitest.config.mts`, `pnpm --filter web test`, wired into `make test`) with tests proving
the API-client error contract and the state primitives' accessible roles — deliberately no tests
asserting Finding content, since none is served yet. Added `apps/web/README.md` as the frontend
conventions reference that did not previously exist. Verdict: `READY_FOR_FINDINGS_IMPLEMENTATION`
once `TASK-025` unblocks — infrastructure is not what's blocking `TASK-026`/`TASK-027`. One residual
gap handed to Architect, not fixed directly (CI/CD ownership): `.github/workflows/ci.yml`'s
`frontend` job doesn't run `pnpm --filter web test` — see `HANDOFF-032`.

### TASK-026 — Findings list screen

- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Priority:** P1
- **Status:** DONE
- **Depends on:** TASK-025
- **Goal:** Show ranked findings without becoming a generic dashboard.
- **UX specification (2026-08-14):** `docs/product/findings-list-screen.md` (complete; written against the concrete `docs/architecture/finding-persistence-contract.md`/`apps/api/app/findings/contracts.py` schema, never against synthetic ground truth). Information hierarchy, sort/filter rules (default sort by `impact.historical_impact.ci_low`), field-to-copy mapping, edge cases, and loading/empty/error states tied to the real `apps/web/components/states/` primitives. See `HANDOFF-028` (feature display-label gap, to Data Engineer, non-blocking) and `HANDOFF-029` (implementation handoff to Architect).
- **Implementation (2026-08-17, Architect) → `DONE`.** `apps/web/app/(app)/findings/page.tsx`
  rewritten to the spec's row hierarchy (title, evidence/readiness pills, warning badge,
  equal-or-greater-weight exposure figure, population, low-priority date). Sort/filter/pagination
  via URL search params (`sort`/`readiness`/`evidence`/`warnings`/`page`), resolved server-side in
  `sortFindings.ts` — no new backend query params, nothing computed that isn't already in
  `EconomicImpactPersistence`/`ValidationMetadataPersistence`, per the spec's own "never" rule.
  15-of-15 real findings verified rendering correctly via a live `pnpm dev` + `uvicorn` +
  ephemeral Postgres run (not just `TestClient`): default exposure sort, a `?sort=readiness&
  readiness=shadow_policy` filter correctly narrowing to exactly the 6 real `shadow_policy`
  findings, zero-crossing "no measurable economic effect" case covered by tests (no real finding
  on this run happens to cross zero). Empty-state copy updated per spec. **Known gap, documented
  not fabricated:** the "near G03 power floor" small-sample qualifier both this task and TASK-027
  call for cannot be implemented — `FindingRead` doesn't expose the MDE/power diagnostic needed to
  compute "near," and inventing a threshold client-side would violate `ADR-004`. Real fix is a
  small future `FindingRead` addition, not something improvised in the UI.
- **Tests:** `sortFindings.test.ts` (sort/filter/pagination logic, 14 cases) plus shared pill/
  exposure component tests. `pnpm --filter web typecheck`/`lint`/`test` all pass (39 tests total).

### TASK-027 — Finding detail screen

- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-025
- **Goal:** Explain what was found, population, impact, raw/adjusted effect, evidence, stability, alternatives, warnings, and next step in business language.
- **UX specification:** `docs/product/finding-detail-screen.md` (complete; written ahead of the backend so TASK-024 can be scoped against real UI requirements). See `HANDOFF-008` (field requirements to Architect) and `HANDOFF-009` (implementation handoff to Architect).
- **Update (2026-08-14):** Refreshed against the now-concrete persistence schema: consolidated field-to-copy mapping table, edge cases, and loading/empty/error states tied to the real `apps/web/components/states/` primitives; `ResourceStatus`-based run-status gating replaced by `FindingLifecycleStatus` gating per the `HANDOFF-024` resolution (`docs/product/finding-product-contract.md` §12).
- **Note (2026-08-13):** Pickup attempted by an ad hoc "Frontend" dispatch (no `agents/FRONTEND.md` or Frontend role exists in `AGENTS.md`). Confirmed still correctly `BLOCKED`: no approved Product spec/content exists, and `TASK-025`/`TASK-024` remain `BLOCKED` so no real findings API exists. See `HANDOFF-004` (spec, to PRODUCT) and `HANDOFF-005` (API + role placement, to ARCHITECT). No implementation was made against invented product semantics or an invented API contract.
- **Implementation (2026-08-17, Architect) → `DONE`.** New `apps/web/app/(app)/findings/[id]/page.tsx`
  implements all 7 sections + header + provenance strip + lifecycle-status banner exactly per the
  spec's field-to-copy table. `<details>`/`<summary>` (zero JS) for the collapsed technical rule
  definition and the provenance strip. New `apps/web/lib/api/analysisRuns.ts` (`getAnalysisRun`)
  added so the provenance strip can show real dataset/code/contract versions, not just IDs — the
  one small backend-adjacent addition this task needed (the route already existed, just no client
  wrapper). Next-step action matrix implemented verbatim from
  `finding-product-contract.md` §9 (`NOT_READY`/`EXPERIMENT_ONLY`/`SHADOW_POLICY`/
  `HIGH_CONFIDENCE`, the last unreachable today but coded, not stubbed). Feedback capture
  (`TASK-035`/`036`) is a reserved, visibly-disabled chip row only, per spec. 404 and network
  failure share one `ErrorState` path, no special-cased not-found page, per spec. Verified live
  (not just `TestClient`) against a real promoted finding: all 7 sections render real content,
  `adjusted_effect` correctly shown even at `descriptive_observation` evidence level (a real
  finding from `TASK-024`'s own data — adjustment is computed independently of which gate capped
  the evidence ceiling), evidence ladder highlights the correct step, action list correctly shows
  only `["Flag for review", "Design a controlled experiment"]` for an `experiment_only` finding
  (no policy-candidate action offered, matching the matrix). Same known G03-power-floor gap as
  `TASK-026`, documented there, not repeated.

## Phase 10 — Blind benchmark evaluation

### TASK-028 — Ground-truth evaluator

- **Owner:** STATISTICS
- **Implementation support:** DATA_ENGINEER
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-022, TASK-023
- **Goal:** Compute precision, recall, Top-K/economic-weighted recall, false-positive and confounder-rejection rates, direction accuracy, impact error, and leakage violations.
- **Evidence (2026-08-16):** `scripts/evaluate_benchmark.py`, frozen at
  `artifacts/evaluation/task-028-benchmark-evaluation.json`. Matching statistic (Statistics'
  methodological call per `docs/benchmark/decision-gate.md`): candidate recovers pattern P if
  recall(P by candidate's full-cohort exposed set) ≥ 0.5, fixed before any overlap was computed —
  see the script's module docstring for the reasoning. Opens `hidden_ground_truth.json` only after
  both discovery commitment (signed receipt) and validation freezing were already complete. 7 unit
  tests (`tests/analytics/test_evaluate_benchmark.py`); full suite 125 passed, ruff/pyright clean.
  **Results:** Top-10 precision 90% (9/10); economic-weighted recall 45.2% (P01, P06 of 7
  scoreable patterns); 0/5 traps promoted (see `TASK-022`'s caveat); 0 leakage violations; 100%
  direction accuracy (3/3 validated+matched); median economic impact estimation error **204%**.

### TASK-029 — Benchmark report v1

- **Owner:** STATISTICS
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-028
- **Goal:** Document recovered/missed patterns, false positives, confounding failures, expensive misses, and the largest methodological weakness.
- **Evidence (2026-08-16):** `docs/benchmark/task-029-benchmark-report-v1.md`. Recovered: P01, P06.
  Missed: P02, P03, P04, P08, P09 (candidates never combined destination/segment/season/supplier
  conditions with the discount/price/lead-time features the search favored). No confirmed false
  positive (no trap promoted) but a genuine, named methodological weakness: reported economic
  impact is inflated 2–4.8× because validated candidates' exposed populations are ~15–16× larger
  than the true patterns they partially recover — diagnosed mechanism, not just an observed
  number, in report §3.6. `docs/benchmark/decision-gate.md`'s "Post-benchmark comparison" appended
  (not edited above the line) with the full band-by-band scoring. **Overall verdict at the time
  this evidence was written: FAILED**, driven by the impact-error metric alone; no hard
  disqualifier fired. `HANDOFF-043` requests ML_DISCOVERY/FOUNDER_STRATEGY concurrence on
  Statistics' fixable-defect attribution before a remediation rerun is authorized. `ADR-019`
  records that original verdict and its consequences.
- **Superseded same day (2026-08-17, Statistics/Architect, `ADR-025`):** the `TASK-058`/`TASK-059`
  remediation produced a new blind run (`task-058-remediation-20260817-001`), re-graded by
  `TASK-019`/`TASK-028` for real. **Overall verdict is now PROMISING**, not FAILED — median
  economic impact estimation error dropped from 204% to 37.5% (FAILED band → PROMISING band);
  Top-K precision (90%), leakage (0), and direction accuracy (100%) held or improved. This entry's
  own `FAILED` line above is historical record of the first grading, not the current state — see
  `docs/benchmark/decision-gate.md`'s "Post-benchmark comparison" second entry for the full
  band-by-band re-score, and `memory/CURRENT_STATE.md` for the consolidated current picture.

## MILESTONE-M1 — Synthetic end-to-end MVP

- **Status:** DONE (synthetic-benchmark scope)
- **Depends on:** TASK-029

Complete when synthetic CSV → ingestion → profiling → canonical dataset → discovery → validation → impact → persisted finding → UI → blind evaluation works end to end. Several true patterns must be recovered, high-impact patterns rank near the top, major traps are rejected/downgraded, no post-treatment leakage occurs, and findings are understandable.

**2026-08-16 assessment (Statistics):** the pipeline itself now runs end to end, deterministically,
with the blind boundary held throughout (`task-015-official-20260816-015` → `TASK-019` → `TASK-028`
→ `TASK-029`, in that order, verified). Recovery (P01, P06) and trap-avoidance (0/5 promoted) both
hold. The milestone's own bar is not fully met: economic impact estimation is unreliable (§ above),
and the overall `docs/benchmark/decision-gate.md` verdict is FAILED. This milestone is not marked
`DONE` — real customer data does not proceed (`ADR-019`) until a remediation run re-grades at
STRONG or PROMISING. The UI/persisted-finding half of this milestone's scope (`TASK-024`–`TASK-027`)
remains separately blocked on Architect's implementation work regardless of this benchmark result.

**Reconciled 2026-08-17 (Architect) → `DONE` for its stated "Synthetic end-to-end MVP" scope.**
Every blocking condition in the assessment above has since cleared, verified, not assumed:
`docs/benchmark/decision-gate.md`'s overall verdict is **PROMISING**, not FAILED (`ADR-025`,
same-day remediation, `TASK-058`/`TASK-059` both `DONE`); the "UI/persisted-finding half"
(`TASK-024`–`TASK-027`) is `DONE` with real data, verified live against a running instance
(this session). Every stage the milestone's own text lists runs for the synthetic path: synthetic
CSV (`TASK-003`) → the synthetic analytical dataset (`TASK-011`, which serves as this path's
canonical-equivalent stage — see caveat below) → discovery (`TASK-015`) → validation (`TASK-019`)
→ impact (`TASK-023`) → persisted finding (`TASK-024`) → UI (`TASK-026`/`TASK-027`) → blind
evaluation (`TASK-028`/`TASK-029`), all `DONE`, all against the real closing run.
**Explicit caveat, not swept under this closure:** "ingestion → profiling → canonical dataset" in
the literal pipeline description above refers to the *real-customer-data* path
(`TASK-005`→`TASK-006`→`TASK-007`→`TASK-008`→`TASK-009`→`TASK-010`). `TASK-005`/`006`/`007` are now
`DONE`, but `TASK-010` (canonical schema, real inputs) is still genuinely `BLOCKED` — the synthetic
benchmark's dataset was built directly by `TASK-011` from the generator's already-canonical-shaped
output, never exercising `TASK-010`'s general-purpose normalizer. This milestone's title is
"**Synthetic** end-to-end MVP," so closing it on the synthetic path is faithful to its own scope,
not a redefinition — but the real-ingestion path is a materially separate, still-open piece of
work, correctly gating `TASK-038` on its own terms (see `memory/CURRENT_STATE.md` "Current
blocker"), not reopened or implied-done by this closure.

## Phase 11 — Policy candidates (after M1)

### TASK-030 — Policy candidate domain model
- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Priority:** P1
- **Status:** READY
- **Depends on:** MILESTONE-M1
- **Goal:** Define trigger, scope, action, expected benefit, evidence, exceptions, and status.
- **Status note (2026-08-17, Architect):** Unblocked — `MILESTONE-M1` is `DONE` for its synthetic
  scope (see its own entry). Real, persisted, UI-visible Findings now exist to attach a policy
  candidate concept to (`TASK-024`–`TASK-027`). Implementation not started this iteration.

### TASK-031 — Policy candidate generator
- **Owner:** PRODUCT
- **Implementation:** ARCHITECT
- **Reviewer:** STATISTICS
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-030
- **Goal:** Deterministically translate validated findings into reviewable interventions; an LLM may later explain but never invent numerical thresholds.
- **Status note (2026-08-17, Architect):** Correctly still `BLOCKED` — `TASK-030` (the domain
  model this generator would produce instances of) is `READY`, not `DONE`.

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
- **Status:** READY
- **Depends on:** TASK-027
- **Values:** `KNOWN_ALREADY`, `NEW`, `WRONG`, `NOT_ACTIONABLE`, `INTERESTING`, `ACTIONABLE`.
- **Semantic contract (2026-08-14, FROZEN v0):** `docs/product/finding-feedback-contract.md`. Splits
  the six values into two nullable single-select axes — novelty (`KNOWN_ALREADY`/`NEW`) and
  actionability (`ACTIONABLE`/`NOT_ACTIONABLE`) — plus a multi-select qualifier-tag set (`WRONG`,
  `INTERESTING`), fixes additional fields (comment, customer-reported certainty — explicitly not
  statistical confidence, intended action, commitment strength, owners, follow-up date), an
  append-only record lifecycle, product-learning use, and what must never be read as validation
  (never writes `evidence_level`/`policy_readiness`). This was semantic prep, not implementation.
  See `HANDOFF-031` (future persistence, explicitly deferred to Architect).
- **Status note (2026-08-17, Architect):** Unblocked — `TASK-027` is `DONE`, and its detail screen
  already reserves the UI slot this task would wire up (`findingDetail-feedback`, currently a
  visibly non-interactive chip row). Real persistence/auth for who is giving feedback is a
  separate concern — `TASK-053` (basic authentication) is still needed before this can be more
  than a UI mock. Implementation not started this iteration.

### TASK-036 — Customer review workflow
- **Owner:** PRODUCT
- **Priority:** P1
- **Status:** BLOCKED
- **Depends on:** TASK-035
- **Goal:** Structured one-by-one finding review.
- **Note (2026-08-14):** Session mechanics are already specified in `docs/customer/findings-review-protocol.md`; `docs/product/finding-feedback-contract.md` now fixes what each per-finding capture actually stores. Remains `BLOCKED` on `TASK-035`.

## Phase 14 — First real customer data

### TASK-057 — Secure first real pilot customer
- **Owner:** CUSTOMER_DISCOVERY
- **Support:** FOUNDER_STRATEGY
- **Priority:** P0
- **Status:** TODO
- **Depends on:** none
- **Goal:** Obtain a real travel-agency customer agreement (LOI or equivalent commitment) and a real booking-export dataset, sufficient to unblock `TASK-037`.
- **Context (2026-08-13):** `HANDOFF-014` (Founder Strategy → Customer Discovery, resolved) confirmed no real customer agreement, dataset, or interview exists anywhere in this repository. This was previously an implicit, unowned precondition on `TASK-037` ("Real customer agreement") rather than tracked work — it is the actual critical-path bottleneck ahead of `MILESTONE-M3`, independent of and equally urgent to the ingestion-contract work blocking `TASK-006`–`TASK-029`. See `ADR-010`.
- **Done when:** A named customer agreement (or documented equivalent commitment) and a dataset-access plan are recorded in `DECISIONS.md`, unblocking `TASK-037`.
- **Plan (2026-08-13):** `docs/customer/data-acquisition-plan.md` lays out ICP, outreach, discovery-call
  script, minimal data ask, privacy objection handling, and a 20-prospect pipeline targeting 3–5
  received datasets, across travel agencies plus two additional verticals (recruitment agencies,
  B2B distributors) run in parallel as a generality check. No outreach has occurred yet. The
  vertical widening beyond this task's travel-agency text is a scope question raised to Founder
  Strategy as `HANDOFF-022`, not yet resolved.
- **Execution attempt (2026-08-13):** Asked to obtain ≥3 serious data-partner conversations using a
  fixed offer script. `docs/customer/pipeline.md` created as the tracker (approved offer text, per-
  prospect record template, funnel status). Result: 0 of 3 obtained — Customer Discovery has no
  outbound communication channel in this session (no connected email/calling tool, no named
  contact list), and real replies take real-world days regardless of tooling. Escalated as
  `HANDOFF-026` to Founder Strategy to pick an execution path. Not marking any progress here that
  did not actually happen.
- **Research follow-up (2026-08-14):** Founder chose (via direct instruction) to pursue named-
  company research, warm contacts, and a Gmail connector in parallel. Delivered
  `docs/customer/prospect-target-list.md`: 21 real, sourced, web-researched candidate companies (global scope
  including Asia) across the three verticals, explicitly marked unqualified/uncontacted. Gmail
  remains unauthenticated — the founder needs to authorize it via claude.ai connector settings
  before Customer Discovery can send anything through it. Still 0 of 3 required conversations;
  still waiting on either the founder's own warm contacts or a send channel to move a row from the
  target list into `docs/customer/pipeline.md`.
- **Founder decisions (2026-08-14):** `ADR-016` resolves `HANDOFF-022` — scope stays travel-agency
  only until `MILESTONE-M3` or a demonstrated dead-end; recruitment/distribution rows in the
  prospect list are paused, not pursued. `ADR-017` resolves `HANDOFF-026` — execution path is all
  three combined (warm contacts, Gmail once authorized, founder-sent cold outreach), time-boxed to
  `docs/customer/acquisition-sprint-7day.md`'s 7-day sprint (2026-08-14→21) with a numeric target
  of 15 touches → 4 replies → 1 serious conversation. This is the concrete near-term plan toward
  this task's done condition, not the done condition itself.
- **Execution push (2026-08-14):** Instructed to move from planning to real execution: ≥3
  conversations or ≥1 explicit dataset-sharing agreement this iteration, working only from the
  existing 21 targets (no new prospect list created), travel weighted primary per
  `HANDOFF-022` remaining unresolved. Founder reported creating an email address for outreach, but
  no send tool appeared in this session and no SMTP/API credentials exist anywhere in the repo or
  environment (checked directly) — the address itself was also not shared, so it is unusable here
  in any form. Delivered instead: 7 of the 21 targets (3 travel, 2 recruitment, 2 distribution)
  researched to a verified contact path (5 real emails, 2 named phone contacts) and turned into
  personalized, ready-to-send drafts in `docs/customer/pipeline.md` — explicitly marked NOT SENT,
  not counted as contact, not counted as conversations. Concrete manual next steps for the founder
  are `HANDOFF-033`. Still 0 of 3 conversations and 0 explicit agreements — this iteration's success
  bar is not met, and is not being reported as met.
- **Paused (2026-08-17, Founder, `ADR-022`), then reopened same day (`ADR-025`):** Active outreach
  was paused until `docs/benchmark/decision-gate.md` re-grades at STRONG or PROMISING — a founder
  prioritization call, not a dispute of `ADR-010`'s or `ADR-017`'s reasoning, both of which
  explicitly designed this as parallel, unblocked work. That condition was met the same day: the
  `TASK-058`/`TASK-059` remediation rerun re-graded the decision gate to **PROMISING** (`ADR-025`),
  so per `ADR-022`'s own stated reopening condition, outreach resumes automatically, no further ADR
  required. Already-drafted material (`docs/customer/pipeline.md` drafts,
  `docs/customer/prospect-target-list.md`) was preserved throughout. Note: this reopens *outreach*
  (`TASK-057`) only — `TASK-038` (real customer data ingestion) is a separate gate not resolved by
  this re-grade alone; see `ADR-025` consequence 2.

### TASK-058 — Search-selection precision term (`HANDOFF-043` remediation, part 2)

- **Owner:** ML_DISCOVERY
- **Reviewer:** STATISTICS
- **Priority:** P0
- **Status:** DONE
- **Depends on:** TASK-015 (DONE)
- **Goal:** Add a precision/specificity term to `discovery.engine`'s beam-survival score (or a
  lightweight post-search "tightening" pass trying one additional narrowing categorical condition
  on an already-found broad rule) so future discovery runs' candidates are inherently tighter, not
  only differently reported. Stays within interpretable-conjunction search — no core-approach
  change.
- **Context (2026-08-17, `HANDOFF-043`):** ML Discovery diagnosed that `_development_score`
  (`historical_exposure / (1 + 0.15·(depth−1))`) maximizes raw population × effect with no
  precision term, so a beam-search step adding a narrowing categorical condition (e.g.
  `supplier`/`destination`, both eligible `DECISION_TIME` features unused by any of the 15
  `task-015-official-20260816-015` candidates) structurally loses to one that stays broad — before
  any candidate is even reported. `TASK-016`'s ranking cannot fix this; it only reorders an
  already-selected top-15. Founder authorized both remediation parts 2026-08-17 (`HANDOFF-043`
  resolution).
- **Done when:** A new blind discovery run under the existing `TASK-015`/`TASK-017` protocol
  produces candidates with materially narrower exposed populations relative to matched true
  patterns than `task-015-official-20260816-015`, without a hidden-ground-truth boundary
  violation.
- **Implementation evidence (2026-08-17, ML Discovery):** `DiscoveryConfig.population_score_exponent`
  (default `0.5`, `(0.0, 1.0]`, validated) added; `_development_score` now scores
  `harm_per_booking × n_exposed^population_score_exponent` instead of linear
  `historical_exposure` — a geometric-mean-style balance between total materiality and per-booking
  purity. `population_score_exponent = 1.0` reproduces `v0.1.0`'s exact ranking (regression-tested).
  `DISCOVERY_METHOD_VERSION` bumped to `discovery-engine-v0.2.0`. Methodology:
  `docs/analytics/discovery-engine-v0.md` ("Precision term" section). 4 new tests (2 direct scoring
  tests with hand-computed expected values, 1 config-validation test, 1 end-to-end search test at
  both exponents); full suite, `ruff`, `pyright` pass.
- **New official blind run (2026-08-17, ML Discovery):** Issued, verified, launched (deterministic
  agent, network `none`, image unchanged —
  `policy-blind-agent@sha256:9ad6e1a78ca41a7c04895d1d99c7775e77fc2c8fbb4f23cee268ed04534c7c9b`, no
  Dockerfile change so no rebuild was needed), frozen, and **committed via signed receipt before
  any evaluation opened `hidden_ground_truth.json`** — run ID `task-058-remediation-20260817-001`,
  `status=PERSISTED`, 15 candidates, `discovery_method_version=discovery-engine-v0.2.0`. Frozen
  artifacts archived at `artifacts/blind/task-058-remediation-20260817-001.*` (gitignored,
  reproducible, matching existing convention for `task-015-official-20260816-015.*`).
  **Direct, pre-registration-compliant evidence the fix changed candidate composition**: comparing
  this run's 15 candidate condition sets against `task-015-official-20260816-015`'s (both public,
  no ground truth opened) — 2 of 15 candidates now use a categorical condition that never appeared
  in any of the 15 original candidates: `CAND-012` = `booking_lead_days < 23 AND discount_rate >=
  0.08 AND supplier == BlueWing`; `CAND-014` = `booking_lead_days < 23 AND destination == Tokyo AND
  payment_method == bank_transfer`. These match the pattern identities already disclosed in the
  frozen `docs/benchmark/task-029-benchmark-report-v1.md` ("P01 BlueWing discount+short-lead", "P06
  Tokyo urgent bank-transfer") — a name match observed from that already-public report, not from
  opening `hidden_ground_truth.json` here.
- **Done condition met (2026-08-17, Statistics/Architect, `ADR-025`):** `TASK-019`/`TASK-028` ran
  for real against `task-058-remediation-20260817-001`
  (`artifacts/validation/task-019-official-20260817-task-058-remediation-001.json`,
  `artifacts/evaluation/task-028-task-058-remediation-001.json`). Governing economic impact
  estimation error dropped 204%→37.5% median (now PROMISING band, was FAILED); Top-K precision,
  leakage, and direction accuracy held or improved. Full comparison:
  `docs/benchmark/decision-gate.md` "Post-benchmark comparison" (2026-08-17 entry). Resolves
  `HANDOFF-048`. `docs/benchmark/decision-gate.md`'s overall verdict is now **PROMISING** (was
  FAILED, `ADR-019`).
- **Aggregate public-data addendum (2026-08-17, ML Discovery, `HANDOFF-048`):** whole-set comparison
  of the two already-public candidate documents (no ground truth opened) — mean/max `support` and
  `sample_size` both down ~28% (mean support 0.2473→0.1787, mean `sample_size` 1236→893, max
  `sample_size` 1911→1368) while median barely moved and total reported economic exposure fell only
  ~8% (3.89M→3.56M). Reduction is not driven only by the 2 new categorical candidates — suggestive
  the precision term tightened several candidates across the ranking, not just those two — but is
  not itself the matched-true-pattern comparison `TASK-019`/`TASK-028` must still provide.

### TASK-059 — Benchmark-only attribution-narrowed impact diagnostic (`HANDOFF-043` remediation, part 1)

- **Owner:** STATISTICS
- **Reviewer:** ML_DISCOVERY
- **Priority:** P0
- **Status:** DONE
- **Depends on:** none (operates on already-frozen `TASK-028` inputs)
- **Goal:** Add an explicitly benchmark-evaluation-only diagnostic to `TASK-028`'s evaluator:
  economic impact restricted to the subpopulation actually overlapping a matched true pattern, for
  a fairer metric-6 read on `hidden_ground_truth.json`-scored runs. **Must not** be added as a
  general `TASK-021`/`TASK-023` production `EconomicImpactResult` field — it is only computable
  when a known ground-truth pattern exists to overlap against, which no real customer finding has
  (`HANDOFF-043`, ML Discovery dissent).
- **Done when:** `scripts/evaluate_benchmark.py` reports both the existing whole-rule exposure
  metric and the new attribution-narrowed one, clearly labeled, with the production impact
  contract (`economic_impact.py`, `ADR-021`) untouched.
- **Warning on record (`HANDOFF-043`):** this task alone, without `TASK-058`, would likely improve
  the reported metric-6 number without changing which candidates discovery actually finds — do not
  treat a `TASK-059`-only rerun as sufficient grounds for a STRONG/PROMISING re-grade.
- **Implementation evidence (2026-08-17, Statistics, `ADR-024`):** `scripts/evaluate_benchmark.py`
  adds `metrics.economic_impact_estimation_error_attribution_narrowed_diagnostic` (two new pure
  helpers, `_attribution_overlap_ids`/`_attribution_narrowed_impact`, 4 unit tests on synthetic
  fixtures) alongside the untouched governing `economic_impact_estimation_error`, both clearly
  labeled in the payload, module docstring, and CLI output. Dry-run against the frozen run's
  actual inputs (scratch output, frozen file not touched): attribution-narrowed median relative
  error 79% vs. the governing metric's 199% — real reduction, still short of a re-grade threshold
  on its own, exactly as `HANDOFF-043` warned. The originally-frozen
  `artifacts/evaluation/task-028-benchmark-evaluation.json`/`task-019-official-20260816-015.json`
  were deliberately left un-regenerated (see `HANDOFF-047`'s resolution) — instead,
  `scripts/evaluate_benchmark.py` gained `--validation-report`/`--output`/`--force` CLI flags
  (2026-08-17, Statistics/Architect, `ADR-025`) so the diagnostic could be exercised against a
  *new*, separately-numbered run (`task-058-remediation-20260817-001`) without touching the frozen
  original. `TASK-059` closes on that evidence, alongside `TASK-058` — see `ADR-025`.

### TASK-037 — Real-dataset security review
- **Owner:** CODE_REVIEWER
- **Support:** ARCHITECT
- **Priority:** P0
- **Status:** BLOCKED
- **Depends on:** TASK-057
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
- **Note (2026-08-13):** Customer Discovery confirmed this is still correctly `BLOCKED`, not
  `IN_PROGRESS` (a request referenced this work as "TASK-041," which in this registry is Customer
  statistical validation, owned by Statistics). No real customer agreement is recorded in
  `DECISIONS.md`, and `TASK-037` through `TASK-041` have not started — no real dataset, discovery
  run, or validated candidate exists, so no review can be conducted against synthetic or invented
  findings. This resolves the open question in `memory/HANDOFFS.md#HANDOFF-014` (Founder → Customer
  Discovery), which independently asked whether any real customer engagement exists — it does not.
  A review protocol was prepared in advance (`docs/customer/findings-review-protocol.md`) so
  execution can start immediately once preconditions are met.

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
- **Priority:** P1
- **Status:** READY
- **Depends on:** none (implementation-ready)
- **Status note (2026-08-17, Architect):** Reprioritized `P2`→`P1`, `BLOCKED`→`READY`. Originally
  deprioritized pending "real external users" (no auth-worthy multi-user need yet). That's no
  longer the only justification: `TASK-035` (finding feedback) is `READY` and its detail-screen UI
  slot is already built (`findingDetail-feedback`, currently a visibly-disabled placeholder,
  `TASK-027`), but real feedback persistence has no way to attribute *who* gave it without some
  identity concept — `TASK-035` cannot become more than a UI mock without this. Not implemented
  this iteration — real authentication (session/token handling, credential storage) is a genuinely
  separate, security-sensitive design task deserving its own pass, not a drive-by addition to a
  status-reconciliation sweep. `TASK-054` (tenant isolation) remains correctly `BLOCKED` below —
  this reprioritization is about single-identity attribution for `TASK-035`, not multi-tenancy.

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
