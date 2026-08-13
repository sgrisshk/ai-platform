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
- **Status:** OPEN
- **Question:** Is the pilot’s primary outcome gross margin, contribution margin after downstream costs, cancellation-adjusted value, or another agreed measure?
- **Why it matters:** Discovery targets and economic impact must reflect the customer’s actual decision objective.
- **Blocking:** Blocks production analytical design, not ingestion bootstrap.
- **Resolution condition:** Customer definition, calculation, time horizon, and exclusions are documented and approved.

## OQ-003 — Evidence required for policy readiness

- **Owner:** STATISTICS
- **Support:** PRODUCT
- **Status:** OPEN
- **Question:** What minimum validation and stability requirements map evidence levels to `EXPERIMENT_ONLY`, `SHADOW_POLICY`, and `HIGH_CONFIDENCE`?
- **Why it matters:** Prevents discovery results from being promoted directly into business rules.
- **Blocking:** Blocks finding/policy workflow and discovery acceptance criteria.
- **Resolution condition:** `TASK-018` produces a reviewed contract and the decision is recorded.
