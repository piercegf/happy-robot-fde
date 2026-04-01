# Reviewer handoff — Inbound carrier sales (Acme Logistics)

**For:** Carlos Becker · **From:** Alejandro Pérez  
**Purpose:** Everything you need to review the build before we meet — live links, repo map, access model, and discussion topics.

---

## 1. Live environment (production)

| What | URL / check |
|------|----------------|
| **Operations dashboard** | https://happy-robot-fde-production-f148.up.railway.app/dashboard |
| **Health** (no auth) | https://happy-robot-fde-production-f148.up.railway.app/health |
| **API base** | https://happy-robot-fde-production-f148.up.railway.app — root redirects to the dashboard |

Open the **dashboard** in a normal browser session (not a downloaded copy of static HTML). The server injects credentials the UI needs to load metrics; treat this URL as an **internal reviewer surface**, not a public marketing page.

---

## 2. HappyRobot workflow

**Workflow:** https://platform.happyrobot.ai/fdealejandroperez/workflows/gchtmr5tol1e  

HTTP tools and webhooks point at the Railway base URL above (`/api/...` paths as configured in the workflow). For **voice**, use whatever web-call or test entry you normally use in the platform for this workflow — you do not need my local `client/` / `server/` stack for that.

---

## 3. Source code & documentation

| Resource | Location |
|----------|-----------|
| **Repository** | https://github.com/piercegf/happy-robot-fde |
| **Technical build doc** | Repo: `docs/acme_logistics_build_doc.md` |
| **Deployment / reproduction** | Repo: `docs/deployment_for_word.html` (Word-friendly) and §8 of the build doc |
| **Business-facing summary** (broker-style) | Repo: `docs/acme_logistics_broker_build_description.md` and `docs/broker_build_description_for_word.html` |

---

## 4. Access & keys — what you need

| Scenario | Do you need a key from me? |
|----------|----------------------------|
| Dashboard + charts | **No** — open the live dashboard URL. |
| Workflow in HappyRobot UI | **No** — your org access (same as usual). |
| Clone repo & run **FastAPI locally** | **No** for a default setup — copy `.env.example` → `.env`; local `API_KEY` matches README examples. |
| **Direct** calls to production API (`curl`, Postman) | **Yes** — production `X-API-Key` matches the server’s `API_KEY` on Railway; I can share out-of-band if you need raw API testing, or you can use the dashboard’s in-page behavior. |
| Local **browser voice test app** (`server/` + `client/`) | **HappyRobot API key** with access to this workflow — typically mine in `server/.env`, or your own key if policy allows. See README “Optional: local web voice client.” |

---

## 5. What the build does (one minute)

Inbound voice on HappyRobot → tools hit a **FastAPI** backend on Railway: **FMCSA-backed MC verification** (with fallback), **fuzzy load search** from SQLite, **negotiation** capped at **95% of posted rate** (max 5% off) across up to **three rounds**, then **post-call extract/classify** into outcomes aligned with the dashboard funnel. Ops metrics: conversion, revenue vs posted rate, sentiment, lanes, peak hours, negotiation outcomes.

---

## 6. Topics I’d like your take on

1. **Dynamic floor** — Should the negotiation floor vary by lane or demand instead of a flat 95% rule?  
2. **Mid-call pivots** — Best pattern when the first lane doesn’t match (nearby lanes, equipment swap) without resetting the conversation.  
3. **Outbound / callbacks** — Productizing follow-up for `callback_requested` (and similar) outcomes.  
4. **Spanish** — Feasibility and priority for a large carrier segment.

---

## 7. Security note (reviewer context)

Production uses **HTTPS**. The dashboard is designed for **trusted reviewers**; anyone with the link can inspect browser traffic. After external review cycles, rotating **`API_KEY`** on Railway is reasonable if the URL was broadly shared.

---

*Questions before we meet — ping me anytime.*
