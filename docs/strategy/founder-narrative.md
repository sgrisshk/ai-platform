# Founder Narrative

**Owner:** FOUNDER_STRATEGY
**Covers:** `TASK-048` (company one-liner), `TASK-049` (founder story draft)
**Status as of writing (2026-08-18):** Decision-gate verdict **PROMISING**, travel-benchmark only. Zero real customer conversations. `TASK-057` reopened, `TODO`. Nothing below is written to survive contact with real data unrevised — both sections are living documents, expected to change the moment `TASK-057`/`TASK-038` produce a real result.

## Company one-liner (`TASK-048`)

> We test whether a business's own historical records already contain a costly pattern it hasn't noticed.

**Why this wording, not a longer or more confident version:**
- "Test whether" instead of "find" or "reveal" — the sentence describes a method being run, not a result already delivered to anyone. This mirrors the evidence-language discipline `docs/product/finding-product-contract.md` enforces on findings themselves (`LANGUAGE_RULES`: no verb stronger than what the evidence level supports) — applied here to company-level language, not just per-finding text.
- No "AI," "platform," "intelligent," or similar broad-positioning words. The mechanism is a deterministic discovery-and-validation pipeline with a fixed evidence taxonomy (`ADR-004`, `ADR-005`); leading with "AI" would misdescribe where the actual work happens and would read as exactly the generic-platform positioning `agents/FOUNDER_STRATEGY.md`'s differentiation guardrails warn against.
- No named vertical. The current wedge (travel agencies, `ADR-016`) is a go-to-market choice, not the thesis itself — `PROJECT_CONTEXT.md`'s vision is domain-general, and this sentence should not need rewriting every time the ICP is revisited.
- No claim of savings, accuracy, or customer outcome. As of this writing that would be false: zero real companies have been analyzed.

## Founder story draft (`TASK-049`)

### Why this problem

Most businesses that have run for a few years are sitting on a large, ordinary asset they never look at twice: the full record of what they decided and what happened afterward. Which manager approved which exception, which channel a customer came through, which discount was offered on which day — cross-referenced against what it actually cost or earned, months later. Nobody goes back and checks whether some specific, non-obvious combination of those decisions has been quietly losing money the whole time. A standard BI dashboard shows this quarter's numbers; it doesn't search the last two years of decisions for the one combination that's been bleeding margin. That search is the product.

### Why now

Two things make this tractable for a small team now that weren't true a few years ago: cheap-enough compute to run an exhaustive, interpretable search over thousands of candidate rules against a real transaction history, and language models capable of turning a validated statistical result into a plain-language explanation a business owner can act on. The second part is deliberately constrained, not embraced wholesale: an LLM may explain a finding, but every number — the effect size, the confidence interval, the economic impact — comes from deterministic code, never from a model's generation (`ADR-004`). That constraint is the actual bet: that discovery can be both automated and conservative enough to trust, instead of forcing a choice between the two.

### What's proven so far

Everything proven to date is on synthetic data, and that qualifier is load-bearing, not a formality.

A 10,000-booking, 24-month synthetic travel-agency benchmark was built with nine deliberately planted harmful patterns and five deliberately planted confounding traps — decoys designed to look like real findings but that a sound method should reject. The discovery mechanism ran genuinely blind: it never had access to which patterns were real before its candidates were cryptographically committed. Validation was pre-registered before that first blind run — the pass/fail bands (`docs/benchmark/decision-gate.md`) were written down before anyone saw a result, specifically so standards couldn't shift to fit whatever came out.

The first blind run graded **FAILED** — not because the method found nothing, but because its economic-impact estimates were off by a median of 204%, later diagnosed as an estimation-granularity defect rather than a failure of the search itself. One remediation cycle later, the same protocol re-run graded **PROMISING**: 90% precision in its top 10 candidates, 100% correct effect direction, zero leakage, zero confounding traps promoted to a finding, and impact error down to a median of 37.5%. That FAILED result, reported honestly rather than quietly re-run until it looked better, is itself part of what makes the PROMISING result worth something.

Generator infrastructure now also exists for six further synthetic domains beyond travel (e-commerce, SaaS subscriptions, insurance claims, manufacturing QA, B2B sales, and healthcare scheduling), built to eventually test whether this method is travel-specific or genuinely general. No discovery run has been evaluated against any of them yet — that generality question is open, not answered, and this story will say so until it isn't.

### What's explicitly not proven

No real company has shared its data. No real dataset has been ingested. No real customer conversation has happened — `TASK-057` (secure first real pilot customer) is reopened and at zero. There is no evidence yet that a real business would find a resulting pattern new, material, or worth acting on, that they would trust it enough to change a decision, or that they would pay for it. Every number in the section above describes performance against a benchmark built with fully known answers; none of it describes an outcome for a real business, and none of it will be represented as such.

### What happens next

`TASK-057` is the one thing standing between this story and its next real revision. Everything past it — real data ingestion, policy backtesting, hardening, authentication, fundraising materials with real metrics — is intentionally not being built ahead of a real customer. This section gets rewritten the day that changes, not before.
