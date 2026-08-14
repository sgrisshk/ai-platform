# 7-Day Acquisition Sprint

**Owner:** FOUNDER_STRATEGY (execution/sending), CUSTOMER_DISCOVERY (materials/sourcing/logging)
**Relates to:** `TASK-057`, `ADR-016`, `ADR-017`, `docs/customer/pipeline.md`, `docs/customer/prospect-target-list.md`
**Window:** 2026-08-14 → 2026-08-21
**Scope:** Travel agencies only, per `ADR-016`. Do not spend sprint time on recruitment/distribution rows.

## Why a 7-day box

`HANDOFF-026` showed the channel, not the pitch, was the blocker: zero of three required conversations after a full day, entirely because no send channel existed and no warm contact had been supplied. Real replies take real-world days regardless of tooling — 7 days is the shortest window that can produce an honest read on whether the current combination of channels and offer works, without waiting out the full 30-day plan to find out.

## Numeric target

**15 outbound touches → 4 real replies/exchanges → 1 serious conversation** (logged in `docs/customer/pipeline.md` under its existing `Status` bar — `CALL SCHEDULED`, `CALL DONE`, or an equivalent written back-and-forth about actual data specifics, not a polite acknowledgment).

This is a checkpoint inside the full acquisition plan's funnel (`docs/customer/data-acquisition-plan.md` §10: 20 prospects → 12–14 calls → ≥3 conversations → 3–5 datasets), not a replacement for it. Hitting 1 serious conversation in 7 days keeps that larger funnel on schedule; missing it is itself a data point (see go/no-go in `memory/CURRENT_STATE.md`).

## Execution path (combined, per ADR-017)

1. **Founder-sent, warm contacts first.** Any existing personal or professional contact at a travel agency or tour operator, anywhere, takes priority over cold outreach — highest reply-rate channel available and requires no tooling.
2. **Gmail connector.** Founder authorizes it via claude.ai connector settings. Once live, Customer Discovery can draft and send email directly and track replies. **Do not wait on this before starting (1) or (3).**
3. **Founder-sent cold outreach** (LinkedIn connection + message, or email) to the 8 researched travel-agency prospects in `docs/customer/prospect-target-list.md` (T1–T8), using the approved offer text in `docs/customer/pipeline.md` verbatim. Customer Discovery drafts each message; founder sends it, since neither LinkedIn nor unauthenticated email is reachable from this session.

## Day-by-day

| Day | Founder | Customer Discovery |
|---|---|---|
| 1 | Authorize Gmail connector (claude.ai connector settings). Supply any warm contacts, even one or two names. | Finalize named decision-maker contacts (owner/ops lead, not just company) for T1–T8. Source 4–6 additional real, named travel-agency prospects to backstop the 15-touch target if T1–T8 alone falls short. Draft first-touch messages per prospect from the approved offer text. |
| 2–3 | Send first wave: warm contacts + drafted messages for T1–T8 (LinkedIn/email/manual, whichever channel is live). Target: 10 cumulative touches by end of day 3. | Log every send as `CONTACTED, no reply yet` in `docs/customer/pipeline.md` immediately — not after a reply. Prepare wave-2 messages for any newly sourced prospects. |
| 4–5 | Send remaining touches to reach 15 cumulative. Follow up once (not more) on day-2 sends with no reply. Report any real replies back to Customer Discovery the same day. | Log replies as they're reported: `Status`, source, and every field the prospect actually stated — no inferred fields, per `docs/customer/pipeline.md`'s own rule. Flag which replies look like a path to a serious conversation. |
| 6–7 | Hold or schedule any conversation that materializes. Report outcome — including silence or decline — honestly. | Update the funnel table in `docs/customer/pipeline.md`. Write a short, factual sprint result (touches sent, replies received, conversations held, verbatim objections if any) for Founder Strategy's 14-day milestone review. |

## What counts, and what doesn't

- A LinkedIn connection request alone is not a touch until it carries the approved offer message.
- A reply that only says "not interested" or is silence after a follow-up counts toward the 15/4 denominators honestly — it is evidence, not a failure to log.
- No row moves to `CALL SCHEDULED` or beyond without an actual reply confirming it. `docs/customer/pipeline.md`'s existing rule against invented or forecasted entries applies without exception here.

## Owner note

Every send in this sprint is founder-executed or founder-authorized — this session has no autonomous outbound channel (email, LinkedIn, or phone). Customer Discovery's role this week is sourcing, drafting, and honest logging, not sending. If day 7 arrives with fewer than 15 touches sent, report the actual number and why, rather than treating the target as met.
