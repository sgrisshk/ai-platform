# Agent Team and Routing

Agents form a sequential specialist pipeline, not a committee that runs on every task. Activate only the roles required by the decision.

## Default routing

| Situation | Primary role | Required next review/handoff |
|---|---|---|
| Product direction or scope changes | `FOUNDER_STRATEGY` | Domain specialist affected by the decision |
| Customer file arrives | `DATA_ENGINEER` | `CODE_REVIEWER`; `STATISTICS` for eligibility/leakage questions |
| Outcome/evidence methodology is unclear | `STATISTICS` | `PRODUCT` for business semantics |
| Candidate discovery implementation | `ML_DISCOVERY` | `STATISTICS` for every serious candidate |
| Production architecture or code | `ARCHITECT` | `CODE_REVIEWER` |
| Validated finding needs a workflow/screen | `PRODUCT` | `STATISTICS` for evidence wording |
| Interview, pilot, buying, or pricing evidence | `CUSTOMER_DISCOVERY` | `FOUNDER_STRATEGY` if thesis changes |
| YC application or fundraising material | `FUNDRAISING` | Evidence owners for every factual claim |

## Typical finding pipeline

```text
Customer dataset
→ Data Engineer: quality, canonicalization, leakage classification
→ Statistics: outcome and validation design
→ ML Discovery: interpretable candidate generation
→ Statistics: validation and evidence grade
→ Product: decision workflow and conservative presentation
→ Customer Discovery: customer reaction and behavior
→ Founder Strategy: thesis/scope decision if evidence changes direction
```

Architect turns approved interfaces and algorithms into production code. Code Reviewer independently reviews serious changes before shipment.

## Independence rule

An agent must not be the sole judge of its own high-risk output:

- ML Discovery cannot validate causality.
- Architect cannot be the only reviewer of a security-sensitive change.
- Product cannot assign evidence strength.
- Customer Discovery cannot convert polite interest into validated demand.
- Fundraising cannot invent or strengthen underlying evidence.

Use `memory/HANDOFFS.md` whenever required specialist work is unresolved. Do not create handoffs merely to narrate routine sequential work already captured in `TASKS.md`.

## Daily core and on-demand roles

At the present stage, the most frequently useful modes are Founder Strategy, Architect, Data/Statistics, and Code Reviewer. Product, Customer Discovery, ML Discovery, and Fundraising activate when their concrete input or decision exists. This is guidance, not permission to collapse role boundaries.

