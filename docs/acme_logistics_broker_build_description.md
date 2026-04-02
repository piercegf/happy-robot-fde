# Inbound Carrier Sales — Build Description for Acme Logistics

**Prepared for:** Acme Logistics  
**Subject:** AI-powered inbound carrier sales — scope delivered, carrier experience, and operational value

---

## Purpose of this document

This is a **business-facing description** of what was built for your inbound carrier sales use case: how a carrier’s call is handled end to end, what protections are in place for your brokerage, and what visibility your team gets after the fact. It is intended for operations, commercial, and leadership readers—not as an IT runbook.

---

## The problem we addressed

Inbound carrier calls are high-intent but easy to mishandle: after-hours volume, inconsistent rate discipline, and manual FMCSA checks slow down booking and create compliance risk. The build focuses on **capturing more bookable freight**, **protecting margin with consistent negotiation rules**, and **giving you a clear picture of what happened on every call**—without requiring carriers to learn a new app.

---

## What we delivered (in plain terms)

| Capability | What it means for Acme |
|------------|-------------------------|
| **24/7 voice coverage** | Carriers reach a professional voice agent anytime; you are not losing loads to voicemail or delay. |
| **Authority verification before quoting** | MC number is checked against FMCSA (with a backup source if needed) before load details are shared—reducing exposure to unauthorized or inactive carriers. |
| **Guided load matching** | The agent collects lane and equipment needs, then presents matching loads from your available inventory with the details a carrier expects (lane, rate, weight, timing, notes). |
| **Structured negotiation** | Rate discussions follow a defined playbook: up to three rounds, with a **firm floor at 95% of the posted rate** so you do not train the market to expect deep discounts on every call. |
| **Structured call outcomes** | Every call is classified (for example: booked, no agreement, not eligible, no loads available, callback requested, or other) and logged with the commercial details that matter for reporting. |
| **Operations visibility** | A secure web dashboard summarizes funnel performance, revenue capture versus posted rates, sentiment trends, lane demand, call timing, and negotiation effectiveness—so you can manage the channel like a product, not a black box. |

---

## The carrier experience (one call, start to finish)

1. **Answer and qualify** — The agent identifies as Acme Logistics, collects the carrier’s MC number, and verifies operating authority in real time. If the carrier is not authorized to operate, the call ends politely—before any freight discussion.

2. **Understand intent** — The agent asks what lane and equipment type the carrier is looking for.

3. **Match and present** — Available loads are matched to that intent. If nothing fits, the carrier is told clearly and the attempt is logged for demand insight.

4. **Quote and negotiate** — When there is a fit, the agent presents the load and rate. If the carrier pushes on price, the system responds within your guardrails (three rounds, down to the 95% floor). Accepted terms are confirmed as booked; walkaways and callbacks are handled explicitly.

5. **After the call** — Key facts from the conversation are extracted and stored for reporting: outcome, rates discussed, lane, equipment, and relationship signals your team can trend over time.

This flow mirrors how a strong inbound desk works—except it scales to **every hour of the week** with **consistent policy**.

---

## Why the negotiation design matters commercially

Brokers lose money in two predictable ways on inbound: **giving away too much** to close, or **refusing to flex** and losing the truck. The three-round structure is deliberate: it signals willingness to move while capping downside. The **95% floor** is your non-negotiable margin protection on automated quotes; it is simple to explain internally and to tune later if your lane strategy changes.

---

## What you can see in operations (dashboard)

The reporting layer is built around questions a brokerage actually asks:

- **Are we converting inbound interest into booked loads?**
- **When we book, how close are we to the posted rate?** (revenue capture and average discount)
- **Which lanes are carriers asking for most?**
- **When do carriers call—and are we staffed or covered?**
- **When price is discussed, how often do we still win the load?**
- **Are carriers leaving frustrated or satisfied, in aggregate?**

Together, these metrics support **pricing discipline**, **capacity planning**, and **carrier experience**—without listening to hundreds of recordings.

---

## Risk, privacy, and “production readiness”

- **Compliance-first quoting:** Load economics are not discussed with carriers who fail authority checks.
- **Hosted, encrypted access:** Production traffic uses industry-standard HTTPS; administrative access to the operations view should be treated like any internal tool URL (limited distribution, strong credentials, rotation if shared broadly).
- **Demo vs. enterprise scale:** The demonstration uses a lightweight database and a focused load file suitable for evaluation. A full production rollout would typically connect to your TMS or load board, add role-based access for larger teams, and align data retention with your policies.

---

## How this fits your stack conceptually

The **voice and conversation layer** runs on **HappyRobot** (telephony, speech, and the agent workflow). The **business rules**—verification, inventory search, negotiation math, logging, and the operations dashboard—run on a **dedicated backend** you control, so rates, outcomes, and reporting stay consistent with Acme’s rules.

For technical teams reviewing the implementation, the detailed architecture, APIs, and deployment notes are documented separately in the repository’s technical build document.

---

## Suggested next conversation with Acme

1. **Lane and pricing policy** — Confirm the 95% floor and round count match how Acme wants to quote inbound today.  
2. **Inventory source** — Decide whether loads stay in a managed table for pilot or sync from your live TMS.  
3. **Handoff to dispatch** — Define what “booked” means operationally (e.g., alert dispatch, create load hold, or CRM ticket).  
4. **Success metrics** — Agree on target conversion, revenue capture, and callback follow-up SLAs for a 30–60 day pilot.

---

## Appendix — demonstration access (evaluators only)

A **live operations dashboard** is hosted for this evaluation. Share the link only with Acme stakeholders who should see reporting and call outcomes; treat it like any internal admin tool.

**Dashboard:** [https://happy-robot-fde-production-f148.up.railway.app/dashboard](https://happy-robot-fde-production-f148.up.railway.app/dashboard)

Integration details, reproduction steps, and security configuration for IT are documented separately in the technical build package.

---

*This description reflects the build as delivered for evaluation and demonstration. It is not a legal contract or compliance certification; FMCSA and brokerage obligations remain with the licensed broker of record.*
