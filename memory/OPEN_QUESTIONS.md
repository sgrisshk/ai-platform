# Open Questions

## OQ-001 — Raw object storage boundary

- **Owner:** ARCHITECT
- **Status:** OPEN
- **Question:** Which storage provider and regional/data-residency constraints will apply to immutable customer uploads?
- **Why it matters:** Determines encryption, retention, deletion, content-addressing, and deployment integration.
- **Blocking:** Provider selection is not required for interface design, but is required before a real hosted pilot.
- **Resolution condition:** Pilot constraints and deployment provider are known and recorded in `DECISIONS.md`.

## OQ-002 — Canonical economic outcome

- **Owner:** PRODUCT
- **Support:** CUSTOMER_DISCOVERY, STATISTICS
- **Status:** OPEN (benchmark-scoped choice made; real-customer choice still open)
- **Question:** Is the pilot’s primary outcome gross margin, contribution margin after downstream costs, cancellation-adjusted value, or another agreed measure?
- **Why it matters:** Discovery targets and economic impact must reflect the customer’s actual decision objective.
- **Blocking:** Blocks production analytical design, not ingestion bootstrap.
- **Resolution condition:** Customer definition, calculation, time horizon, and exclusions are documented and approved.
- **Note (2026-08-13, Statistics):** `TASK-013` fixed `contribution_margin_eur` as the primary
  outcome for the synthetic benchmark only (`docs/outcome_contract.md`) — the fullest realized,
  zero-missingness measure available in that schema. This is not evidence toward answering OQ-002
  for a real customer; it is a benchmark-exercise default explicitly scoped as such, and a real
  outcome contract needs its own Product/Customer Discovery decision plus a right-censoring/
  maturation-window design this benchmark did not need.

## OQ-003 — Evidence required for policy readiness

- **Owner:** STATISTICS
- **Support:** PRODUCT
- **Status:** RESOLVED (2026-08-13)
- **Question:** What minimum validation and stability requirements map evidence levels to `EXPERIMENT_ONLY`, `SHADOW_POLICY`, and `HIGH_CONFIDENCE`?
- **Why it matters:** Prevents discovery results from being promoted directly into business rules.
- **Resolution:** Validation contract v1.0.0 (`TASK-018`, ADR-007, `docs/validation_contract.md` §7) fixes the matrix: `NOT_READY` when rejected or economically immaterial; `EXPERIMENT_ONLY` at levels 1–2, or level 3 without operational feasibility; `SHADOW_POLICY` at level 3 with materiality and feasibility, or at levels 4–5 without a positive backtest; `HIGH_CONFIDENCE` only at levels 4–5 with materiality, feasibility, and a backtest whose net-effect interval excludes zero. Encoded in `assign_policy_readiness`. Because no policy backtest exists until `TASK-032`, nothing can currently reach `HIGH_CONFIDENCE`.

## OQ-004 — Customer materiality threshold

- **Owner:** PRODUCT
- **Support:** CUSTOMER_DISCOVERY, STATISTICS
- **Status:** OPEN
- **Question:** Below what annual economic figure is a finding not worth a decision to the pilot customer?
- **Why it matters:** Gate G15 decides which findings are publishable at all. The current thresholds (`min_material_annual_impact = 25000`, `min_material_outcome_share = 0.005`) are placeholders calibrated to benchmark scale, not to any real business. Too low floods the customer with noise; too high hides real money.
- **Blocking:** Not blocking synthetic work. Blocks publishing any real-customer finding.
- **Resolution condition:** A customer-grounded threshold is recorded and the contract is reversioned; depends on the same economics as `OQ-002`. Tracked as `HANDOFF-013`.
