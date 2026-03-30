# Acme Logistics — Inbound Carrier Sales System
### Technical Build Document

---

## 1. Executive Summary

We built an AI-powered inbound carrier sales system for Acme Logistics that automates the entire carrier intake process — from verifying a carrier's FMCSA authority, to matching them with available loads, to negotiating rates within defined guardrails. The system provides 24/7 availability (no more missed after-hours calls), consistent rate management that protects margins, and a real-time operations dashboard that gives dispatchers and management immediate visibility into conversion, revenue capture, and carrier relationship health.

---

## 2. Solution Overview — The Carrier Experience

When a carrier calls Acme Logistics, the HappyRobot voice agent handles the entire conversation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    INBOUND CARRIER CALL FLOW                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📞 Carrier Calls In                                            │
│       │                                                         │
│       ▼                                                         │
│  [1] Greeting & MC Number Collection                            │
│       │                                                         │
│       ▼                                                         │
│  [2] FMCSA Authority Verification ──── Not Authorized? ──► End  │
│       │                                                         │
│       ▼                                                         │
│  [3] Lane & Equipment Inquiry                                   │
│       │                                                         │
│       ▼                                                         │
│  [4] Load Search & Match ──── No Match? ──► Log & End           │
│       │                                                         │
│       ▼                                                         │
│  [5] Present Load Details (origin, dest, rate, weight, pickup)  │
│       │                                                         │
│       ▼                                                         │
│  [6] Rate Negotiation (up to 3 rounds, 5% floor)               │
│       │                                                         │
│       ├── Accepted ──► Book & Confirm                           │
│       ├── Rejected ──► Log & End                                │
│       └── Callback ──► Schedule Follow-Up                       │
│                                                                 │
│  [7] Post-Call: AI Extract + Classify → Log to Database         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Step-by-step:**

1. **Greeting:** The agent answers professionally, identifies itself as Acme Logistics, and asks for the carrier's MC number.
2. **Verification:** The MC number is checked against the FMCSA database in real time. If the carrier's authority is inactive or revoked, the call is politely ended.
3. **Lane Inquiry:** The agent asks what lane the carrier is looking for (origin, destination, equipment type).
4. **Load Matching:** The API searches available loads using fuzzy matching. If no loads match, the agent lets the carrier know and logs the inquiry.
5. **Load Presentation:** Matching loads are presented with full details — lane, rate, weight, pickup/delivery windows, and special instructions.
6. **Negotiation:** If the carrier wants to negotiate, the system supports up to 3 rounds with counter-offers, never going below 95% of the posted rate.
7. **Logging:** Every call is logged with full metadata — outcome, sentiment, rates, duration, and negotiation details.

---

## 3. Technical Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  HappyRobot Platform                     │
│                                                          │
│   Inbound Call ──► Voice Agent ──► Post-Call Processing  │
│                      │   │              │                │
│                      │   │              │                │
└──────────────────────┼───┼──────────────┼────────────────┘
                       │   │              │
            ┌──────────┘   │              │
            │              │              │
   ┌────────▼───┐  ┌──────▼─────┐  ┌─────▼──────┐
   │   FMCSA    │  │  FastAPI   │  │  Call Log   │
   │   Lookup   │  │  Backend   │  │  + Metrics  │
   │  (verify)  │  │  (Railway) │  │  (SQLite)   │
   └────────────┘  └──────┬─────┘  └─────────────┘
                          │
                   ┌──────▼──────┐
                   │  Dashboard  │
                   │  (Chart.js) │
                   └─────────────┘
```

**Components:**

- **HappyRobot Platform:** Hosts the voice agent, handles telephony, speech-to-text, and natural language understanding. Tool calls are made to the FastAPI backend during the conversation.
- **FastAPI Backend:** Python 3.12 application serving REST endpoints for carrier verification, load search, rate negotiation, call logging, and metrics aggregation. Deployed as a Docker container on Railway.
- **SQLite Database:** Lightweight, zero-config database storing loads and call records. Sufficient for the current scale; easily replaceable with PostgreSQL for production growth.
- **FMCSA Integration:** Real-time carrier authority verification via the official FMCSA API, with a fallback to VerifyCarrier.com if the primary source is unavailable.
- **Operations Dashboard:** Single-page application served from the same backend, using Chart.js for visualization. Auto-refreshes every 30 seconds.

---

## 4. Carrier Verification

Every carrier is verified before any load information is shared. The verification checks:

| Check | What It Confirms |
|---|---|
| **Operating Authority** | MC number is active and authorized |
| **Allowed to Operate** | Carrier hasn't been revoked or suspended |
| **Carrier Operation Type** | Interstate vs. intrastate classification |
| **Safety Rating** | Current FMCSA safety rating |
| **Fleet Size** | Total power units and drivers on file |

**Why this matters:** Sharing load details or booking freight with an unauthorized carrier exposes the brokerage to significant legal and financial liability. This automated check replaces manual lookups that dispatchers would otherwise need to perform, and it happens in under 2 seconds during the call.

The system uses a dual-source strategy: FMCSA's official API is the primary source, with VerifyCarrier.com as an automatic fallback. If both sources are unavailable, the carrier is flagged as unverified and the call is handled accordingly.

---

## 5. Negotiation Engine

The rate negotiation follows a structured 3-round strategy designed to protect margins while keeping carriers engaged:

| Round | Counter-Offer | Message Tone |
|---|---|---|
| **Round 1** | 100% of posted rate | Firm but professional — "The rate for this lane is $X" |
| **Round 2** | 97% of posted rate | Flexible — "Best I can offer is $X" |
| **Round 3** | 95% of posted rate (floor) | Final — "Absolute lowest I can go is $X" |

**The 5% Floor Rule:** No load is booked at more than 5% below the loadboard rate. This ensures minimum margin protection across all lanes. If the carrier's offer at any point meets or exceeds the floor, the deal is accepted immediately.

**Design Rationale:** The 3-round structure mirrors how experienced brokers negotiate. It creates a natural cadence — the carrier feels heard, sees movement, and knows when the final number is on the table. This avoids the two failure modes of automated negotiation: accepting too quickly (leaving money on the table) or being too rigid (losing bookable freight).

---

## 6. Metrics & Analytics

The operations dashboard tracks metrics chosen specifically for freight brokerage operations:

| Metric | What It Tells You |
|---|---|
| **Conversion Rate** | Are we winning business? What % of inbound calls result in booked loads. |
| **Revenue Capture Rate** | Are we leaving money on the table? How close to posted rates are we actually booking. |
| **Avg Discount Given** | How much are carriers negotiating off? Identifies if the floor is too generous or too tight. |
| **Carrier Sentiment** | Are we maintaining good carrier relationships? Negative sentiment trends could signal problems. |
| **Top Lanes** | Which lanes generate the most inbound interest? Informs where to post loads and set rates. |
| **Peak Calling Hours** | When are carriers most active? Helps optimize staffing and agent availability. |
| **Negotiation Win Rate** | When carriers negotiate, how often do we still close? Measures negotiation effectiveness. |
| **Avg Call Duration** | Efficiency metric — shorter booked calls mean a smoother process. |

---

## 7. Security

| Layer | Implementation |
|---|---|
| **API Authentication** | All endpoints require an API key via `X-API-Key` header |
| **Transport** | HTTPS enforced via Railway's edge proxy |
| **Data Scope** | Only business data is stored (MC numbers, rates, lanes). No PII, no call recordings, no personal carrier information beyond company name |
| **Database** | SQLite file stored on the server filesystem, not exposed externally |
| **Environment Variables** | API keys and credentials stored as environment variables, not in code |

---

## 8. Deployment

The system is fully containerized and deployed as a single service:

- **Containerization:** Docker image based on Python 3.12-slim, ~120MB final image
- **Platform:** Railway cloud (single-click deploy from GitHub)
- **Endpoints:** One URL serves both the API and the dashboard
- **Persistence:** SQLite database stored in a mounted volume
- **Health Check:** `/health` endpoint returns status, timestamp, and version
- **Restart Policy:** Automatic restart on failure (up to 10 retries)

To deploy: push to the connected GitHub repository. Railway builds the Docker image and deploys automatically.

---

## 9. Recommendations for Next Phase

1. **Dynamic Pricing:** Integrate market rate data from DAT or Truckstop to adjust negotiation floors per lane based on real-time supply/demand. High-demand lanes could hold at 98%, while oversupplied lanes might flex to 90%.

2. **Carrier Scoring System:** Build a carrier reliability score based on booking history, on-time performance, and claim frequency. Prioritize load offers to higher-scored carriers.

3. **TMS/CRM Integration:** Connect to Acme's existing systems (McLeod, Turvo, or similar) to pull live load data instead of a static database, and push booked loads directly into dispatch.

4. **Outbound Callback Automation:** Automatically call back carriers who expressed interest but needed to check availability. The system already tracks "callback" outcomes — this data feeds directly into an outbound campaign.

5. **Spanish Language Support:** A significant portion of the carrier base operates primarily in Spanish. Adding bilingual capability would capture calls that currently go unserviced.

6. **Carrier Self-Service Portal:** A web interface where carriers can browse available loads, submit offers, and check their verification status without calling in — reducing inbound call volume while increasing load coverage.
