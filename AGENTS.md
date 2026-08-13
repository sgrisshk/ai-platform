# Agent Operating Rules

This repository is developed by multiple specialized AI agents. No agent is expected to solve every problem. Specialization prevents architectural drift, statistical mistakes, duplicated work, uncontrolled refactoring, and domain decisions being made by the wrong agent.

## Required reading

Before starting any task, read in order:

1. `PROJECT_CONTEXT.md`
2. `ARCHITECTURE.md`
3. `AGENTS.md`
4. `agents/README.md` and your role file under `agents/`
5. relevant entries from `DECISIONS.md`
6. the assigned task in `TASKS.md`
7. relevant durable state in `memory/`

Do not begin implementation before understanding these files.

## Source-of-truth hierarchy

When information conflicts, use this priority:

1. Explicit current user/founder instruction
2. `DECISIONS.md`
3. `ARCHITECTURE.md`
4. `PROJECT_CONTEXT.md`
5. Role-specific agent instructions
6. Existing implementation
7. Agent assumptions

If code conflicts with architecture documentation, do not silently choose one. Report the conflict. A deliberate resolution must update the relevant source of truth.

## Role boundaries and handoffs

Each agent has a defined responsibility in `agents/`. If a task is outside that responsibility, do not solve it as the responsible specialist. Record a handoff in `memory/HANDOFFS.md` using:

```md
## HANDOFF-<number>

Created: YYYY-MM-DD
From: <role>
To: <role>
Status: OPEN | IN_PROGRESS | RESOLVED | CANCELLED
Task: <specific task>
Context: <durable facts>
Question: <exact decision or output required>
Files: <relevant paths>
Expected output: <deliverable>
Blocking: YES | NO
Resolution: <filled when resolved>
```

You may continue portions that remain within your responsibility.

## Available roles

- **Architect:** repository, boundaries, backend infrastructure, persistence, APIs, CI/CD, deployment, and dependency strategy.
- **Founder Strategy:** company/product thesis, scope discipline, prioritization, and cheapest credible validation.
- **Data Engineer:** ingestion, canonicalization, validation, lineage, transformations, data quality, and time-availability classification.
- **ML Discovery:** interpretable candidate-pattern discovery and ranking; never causal proof.
- **Statistics:** uncertainty, robustness, confounding, causal methodology, and evidence classification.
- **Code Reviewer:** adversarial correctness, security, privacy, architecture, test, and regression review.
- **Product:** product behavior, UX, finding/policy semantics, workflow, and prioritization.
- **Customer Discovery:** interviews, pilots, ICP, buying process, willingness to pay, and business validation.
- **Fundraising:** evidence-grounded YC/application and investor communication; activated when fundraising work is actually needed.

Detailed ownership and exclusions live in the corresponding `agents/*.md` file.

## Shared engineering rules

Never:

- commit real customer datasets or secrets;
- use an LLM as the source of truth for calculations, statistics, causal estimates, finance, eligibility, or policy backtests;
- claim causality without an evidence classification;
- silently introduce infrastructure or change architectural boundaries;
- add ML/LLM frameworks without a concrete need;
- perform unrelated large refactors;
- allow unknown or post-decision fields into explanatory features silently.

All deterministic numbers must come from executable code. All analysis must be reproducible. Preserve raw-data immutability, lineage, and the decision-time/post-decision/outcome boundary.

Every feature requires tests, types, error handling, and documentation when behavior changes. Do not modify unrelated files.

## Blind benchmark rule

ML Discovery agents performing benchmark evaluation **must not run in the full repository checkout**.

A valid blind run must:

1. start in a newly created isolated workspace;
2. be launched through the approved blind-workspace command;
3. contain only explicitly allowlisted public benchmark inputs;
4. use a fresh agent session that has never had access to the full repository or hidden benchmark artifacts.

Example:

```sh
make blind-shell workspace=.blind/run-001
```

An ML Discovery agent that has previously operated in the full repository checkout is permanently ineligible for that benchmark run.

Blindness cannot be restored retroactively by deleting files, changing instructions, or asking the agent to ignore previously accessible information.

Discovery outputs must be frozen through the approved commitment process before hidden ground truth is exposed to any evaluation process. The complete operational protocol is defined in `docs/blind_benchmark_protocol.md` and the architecture decision is recorded in `DECISIONS.md` (ADR-008).

## Completion protocol

Before marking a task complete:

1. run relevant tests;
2. run lint;
3. run typecheck;
4. inspect the git diff;
5. update behavior/architecture documentation where necessary;
6. update task status in `TASKS.md`;
7. record unresolved cross-role work in `memory/HANDOFFS.md`;
8. update `memory/CURRENT_STATE.md` only if project state materially changed.

Do not claim a check passed unless it was actually executed.
