# Customer / Data-Partner Pipeline Log

**Owner:** CUSTOMER_DISCOVERY
**Relates to:** `TASK-057`, `docs/customer/data-acquisition-plan.md`
**Last updated:** 2026-08-14
**Status: 0 of 3 required serious conversations obtained. 0 real prospects contacted.** 21
researched (unqualified, uncontacted) candidate companies exist in `docs/customer/prospect-target-list.md`;
7 of them now have a verified contact path and a ready-to-send draft below — still 0 sent.

## Rule for this file

Only log a row here after a real exchange with a real person at a real company actually happened.
No row may be created, and no field filled in, from an assumed or typical answer. If a prospect
has been messaged but has not replied, they get a row with `Status: CONTACTED, no reply yet` and
every other field left as `—` — not a guess. This file is evidence, not a forecast; see
`agents/CUSTOMER_DISCOVERY.md` on treating polite interest as validation.

## Approved outreach offer (verbatim, use for all first-touch contact)

> "We are testing a system that analyzes historical business decisions and downstream outcomes to
> find non-obvious patterns associated with economic loss. For an early pilot we need anonymized
> historical transactional data and will return a confidential findings report."

Do not describe a finished platform. Do not say "proves," "causes," or "guarantees." At most:
candidate patterns, at most adjusted observational association — see `DECISIONS.md` evidence-level
ADR. This matches the constraint already fixed in `docs/customer/data-acquisition-plan.md` §0.

## Ready-to-send outreach (drafted 2026-08-14 — STATUS: NOT SENT)

Seven of the 21 candidates in `docs/customer/prospect-target-list.md` were researched further
(real contact path confirmed via each company's own site, not the earlier LinkedIn-only entries)
and turned into ready-to-send drafts. **None of these have been sent.** Sending requires either (a)
the founder pasting/sending them from the email address just set up, or (b) the Gmail connector
being authorized so this session can send directly — see the Founder handoff (`HANDOFF-033`). Two
entries (T2, T5) have no public email and are call/form-first, not email-first — noted per row.

**Scope correction (2026-08-14, `ADR-016`, resolving `HANDOFF-022`): recruitment and distribution
are paused, not active, for this sprint.** `ADR-016` restricts all outreach effort to travel
agencies only until `MILESTONE-M3` or a demonstrated travel-only dead-end. **R2, R3, D1, and D3
below are drafted and kept for later reactivation but must NOT be sent right now** — sending them
would contradict the current Founder decision. Only **T1, T2, T5** (travel) are live this sprint;
`docs/customer/acquisition-sprint-7day.md` is the current execution plan and scope for the active
window (2026-08-14 → 2026-08-21).

Two placeholders need the founder's input before anything goes out: `[YOUR NAME]` and
`[YOUR EMAIL/PHONE]`. Nothing here should be sent with those still unfilled.

### Track 1 — Travel agency (ACTIVE — the only live track this sprint, per ADR-016)

**T1 — Craft Travel (Miami, FL / Cape Town) — sales@crafttravel.com**

> Subject: A free, confidential look at decision patterns in Craft Travel's booking history
>
> Hi Craft Travel team,
>
> I came across Craft Travel's story — the shift from Brazil Nuts Tours in 1984 to today's
> boutique model — and wanted to reach out directly rather than through a general form.
>
> I'm testing a research project that studies historical business decisions and their downstream
> outcomes, looking for non-obvious patterns associated with economic loss — the kind that quietly
> hurt margin without anyone noticing at the time. For an early pilot, I'm looking for a small
> number of travel businesses willing to share anonymized historical booking data, purely for this
> research, in exchange for a free, confidential findings report on whatever we find — including if
> we find nothing.
>
> To be upfront about what this isn't: there's no finished platform to buy, and I won't claim to
> have proven anything — at most, patterns worth your own judgment, not guaranteed causes or
> savings.
>
> Would a short call make sense to see if this is a fit?
>
> [YOUR NAME]
> [YOUR EMAIL/PHONE]

**T2 — Travel Discounters (North York, Ontario) — no public email found; phone (416) 481-6701 /
(800) 842-6943; principal contact named as Binod Singh, Manager.** Call-first, not email-first.

> Call opening (ask for Binod Singh by name): "Hi, is Binod available? ... Hi Binod, I'll keep this
> short — I'm researching whether historical travel-booking data hides costly patterns businesses
> don't normally notice, and I'm looking for a few agencies willing to share anonymized historical
> data for a free, confidential analysis — no platform to buy, no promise of proven savings, just a
> findings report either way. Would that be worth 15 minutes sometime this week?"

**T5 — Pettitts Travel (Tunbridge Wells, UK) — no public email found; phone 01892 515966; enquiry
form at pettitts.co.uk/enquiry-form; founder Steven Pettitt, product lead David Pettitt.** Call-
first (ask for Steven or David Pettitt by name), since the enquiry form is built for trip bookings,
not business inquiries.

> Call opening: "Hi, could I speak with Steven or David Pettitt? ... I'm doing independent research
> into whether historical booking data hides costly decision patterns — the kind that don't show up
> until you look at data across many bookings. I'm looking for a few independent agencies willing to
> share anonymized historical data for a free, confidential analysis in return — no product, no
> promise of proven savings. Would that be worth a short call?"

### Track 2 — Recruitment agency (⏸ PAUSED per ADR-016 — kept as backlog, not active)

**⏸ PAUSED per ADR-016 — do not send this sprint.**

**R2 — The Staffing Agency (UK) — info@thestaffingagency.co.uk**

> Subject: A free, confidential look at what's quietly costing you placements
>
> Hi team,
>
> I'm testing a research project that studies historical business decisions and downstream outcomes
> for patterns associated with economic loss — for a recruitment agency, that might mean placement
> or guarantee-period patterns that quietly cost money without being obvious case by case.
>
> For an early pilot, I'm looking for a small number of agencies willing to share anonymized
> historical placement data, purely for this research, in exchange for a free, confidential
> findings report either way. No platform to buy, no promise of proven causes or savings.
>
> Would a short call make sense?
>
> [YOUR NAME]
> [YOUR EMAIL/PHONE]

**⏸ PAUSED per ADR-016 — do not send this sprint.**

**R3 — Independent Resourcing Consultancy / IRC (London, UK) — contact form at ircfs.com/contact**
(the page's email is protected by a script this session's tools cannot decode into a real address —
noted so no one treats the garbled placeholder as real; the form is the working path).

> Form message (short, form-safe): "Independent researcher studying whether historical placement
> data hides costly patterns recruitment firms don't normally notice. Looking for a few agencies
> willing to share anonymized historical data for a free, confidential findings report — no product,
> no promised savings. Could we have a short call? [YOUR EMAIL/PHONE]"

### Track 3 — B2B distributor (⏸ PAUSED per ADR-016 — kept as backlog, not active)

**⏸ PAUSED per ADR-016 — do not send this sprint.**

**D1 — SP Muthiah & Sons (Singapore) — sales@spmuthiah.com**

> Subject: A free, confidential look at decision patterns in SP Muthiah & Sons' order history
>
> Hi SP Muthiah & Sons team,
>
> A business with roots back to 1902 has a lot of order history behind it — I'm doing independent
> research into whether that kind of historical order data hides costly decision patterns (discount
> or credit-term patterns that quietly cost margin, for example) that don't show up case by case.
>
> For an early pilot, I'm looking for a small number of distributors willing to share anonymized
> historical order data, purely for this research, in exchange for a free, confidential findings
> report either way. No platform to buy, no promise of proven causes or savings.
>
> Would a short call make sense?
>
> [YOUR NAME]
> [YOUR EMAIL/PHONE]

**⏸ PAUSED per ADR-016 — do not send this sprint.**

**D3 — Cleveland Wholesale Cash & Carry (Cleveland, OH) — sales@clevelandwholesale.com**

> Subject: A free, confidential look at what's quietly costing Cleveland Wholesale money
>
> Hi Cleveland Wholesale team,
>
> I'm doing independent research into whether historical order data hides costly decision patterns
> — the kind that quietly affect margin without any single order looking wrong. I'm looking for a
> small number of family-run distributors willing to share anonymized historical order data, purely
> for this research, in exchange for a free, confidential findings report either way. No platform to
> buy, no promise of proven causes or savings.
>
> Would a short call make sense?
>
> [YOUR NAME]
> [YOUR EMAIL/PHONE]

## Per-prospect record template

Copy this block per prospect once a real conversation happens; do not pre-fill.

```md
### P-<number> — <company name> (<vertical>)

- **Source:** <warm intro / cold email / LinkedIn / other, and who/what>
- **First contact date:** YYYY-MM-DD
- **Status:** CONTACTED, no reply yet | CALL SCHEDULED | CALL DONE | SAMPLE PROVIDED | SCHEMA SHOWN | DECLINED | GHOSTED
- **Transaction volume:** <rows/month or /year, as stated by prospect — not estimated by us>
- **Months of history available:** <as stated>
- **Available decision-time fields:** <what they described, e.g. agent/manager, discount, channel, terms>
- **Available outcome fields:** <e.g. cancellation, refund, margin, default, churn>
- **Ability to anonymize:** <yes/no/unsure, and what they said about how>
- **Person who controls the data:** <name/role, and whether this is the person we're talking to>
- **Willingness to provide a sample:** <yes/no/conditional, and the condition>
- **Security objections raised:** <verbatim or close paraphrase, not resolved/argued in the log>
- **Timeframe:** <when they said they could realistically act>
- **Notes:** <anything that doesn't fit above; do not editorialize interest level — record what was said, not what it seemed to mean>
```

**Status disambiguation (for the two call-first tracks, T2/T5, most likely to log first):**
`CALL SCHEDULED` = a future call time was agreed but hasn't happened yet (used when a cold email/
form reply asks to schedule). `CALL DONE` = a real conversation actually took place — this is the
status a cold call (T2/T5) logs directly the moment someone answers and talks, with no
`CALL SCHEDULED` step in between. If a cold call gets voicemail or no pickup, log it as `CONTACTED,
no reply yet`, not `GHOSTED` — `GHOSTED` is for someone who engaged first (replied, took the call)
and then went silent on a promised next step.

## First 2 minutes of a call (T2/T5) — assembled from already-approved material, nothing new

Opener: use the exact call-opening script already written per prospect above (§"Ready-to-send
outreach"). Once they're actually talking, the first two questions to ask — before anything else in
`docs/customer/data-acquisition-plan.md` §4 — are that section's own opening pair, asked in this
order: (1) "What's your role, and are you the person who'd approve sharing a historical data
export?" (2) "What's the last time something like this went wrong in a way that cost real money?
What happened, and what did it cost, roughly?" These two alone are enough to know whether to keep
going into the rest of §4 or to close politely — everything else in §4 only matters once those two
answers suggest a real fit.

## Log

_No entries yet. Zero real prospects have been contacted as of 2026-08-14._

## Funnel status against `docs/customer/data-acquisition-plan.md` §10 target

| Stage | Target | Actual |
|---|---|---|
| Prospect targets identified (named) | 20 | 21 (`docs/customer/prospect-target-list.md`, unqualified — see caveats there) |
| Discovery calls booked | 12–14 | 0 |
| Serious conversations (this task's bar) | ≥3 | 0 |
| Verbal yes to sample/export | 5–7 | 0 |
| Datasets received | 3–5 | 0 |

## Why this is still at zero

Customer Discovery, running as an AI agent in this repository, still has no outbound communication
channel available in this session — no connected email or calling tool, and no SMTP/API
credentials anywhere in the repository or environment, checked directly (2026-08-14). The founder
mentioned creating an email address for outreach use, but no tool that could use it appeared for
this session, and the address itself has not been shared, so it is not yet usable here in any form.
Seven prospects now have a verified contact path and a written, personalized draft (§"Ready-to-send
outreach" above) — a real step past the 21 unqualified names in
`docs/customer/prospect-target-list.md` — but "drafted" is not "sent," and none of the fields in the
per-prospect template below are known for any of them because no real reply exists. Getting a real
reply also inherently takes real-world days regardless of tooling; a single agent turn cannot
produce a completed multi-day back-and-forth. Concrete manual next steps are in `HANDOFF-033`
(Customer Discovery → Founder Strategy) rather than papering over the gap with invented
conversations.
