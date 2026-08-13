# Agent Handoffs

All unresolved cross-role work is recorded here. Status values are `OPEN`, `IN_PROGRESS`, `RESOLVED`, or `CANCELLED`. Resolved entries remain as durable history.

## HANDOFF-001

**Created:** 2026-08-13  
**From:** ARCHITECT  
**To:** DATA_ENGINEER  
**Status:** OPEN

**Task:** Define the immutable ingestion contract for `TASK-001`.

**Context:** The repository foundation, metadata models, PostgreSQL migration, API skeleton, security baseline, and synthetic travel fixture exist. Upload handling and customer-data storage intentionally do not exist. Architecture requires raw → normalized → analytical reproducibility and explicit feature timing.

**Question:** What typed ingestion manifest, validation stages, data-quality output, and lineage identifiers are required before implementing file acceptance?

**Files:**

- `ARCHITECTURE.md`
- `SECURITY.md`
- `TASKS.md`
- `packages/schemas/src/policy_schemas/domain.py`
- `tests/fixtures/synthetic_travel_bookings.csv`

**Expected output:** Reviewed ingestion/data-quality contract and proposed tests; any persistence or infrastructure questions handed back to Architect.

**Blocking:** YES — blocks `TASK-002` and acceptance of real customer data.

**Resolution:** Pending.

