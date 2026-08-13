# Project Memory Protocol

Project memory contains durable information that changes future decisions. Agents must not store arbitrary conversation summaries. Keep this directory small enough to read quickly.

## Write rules

Update `CURRENT_STATE.md` when the current milestone, blocker, active customer, or MVP scope materially changes.

Update root `DECISIONS.md` when a deliberate durable decision is made. Every decision records date, decision, context, alternatives, reason, and consequences. Do not rewrite history; add a superseding decision.

Update `EXPERIMENTS.md` when a product, business, or ML experiment starts or finishes. Record hypothesis, method, success/kill criteria, status, and result.

Update `FINDINGS.md` only when a validated durable product/business/analytical finding emerges. Candidate patterns belong in run artifacts, not durable memory, until validation establishes their significance.

Update `OPEN_QUESTIONS.md` when an unresolved question materially affects or blocks future work. Assign an owner and a resolution condition.

Update `HANDOFFS.md` when another specialist is required. Resolve entries explicitly; do not delete their history.

## Do not store

- routine implementation details;
- temporary debugging notes;
- full chat transcripts;
- speculative ideas without decision relevance;
- generated numerical claims without executable evidence;
- information already obvious from code;
- secrets, credentials, PII, or customer records.

Memory files are reviewed like code. Claims must distinguish observed fact, decision, hypothesis, and open question.

