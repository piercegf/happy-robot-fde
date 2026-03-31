# Inbound Carrier Sales — FDE Technical Challenge

AI-powered inbound carrier sales system for Acme Logistics, built on HappyRobot's voice agent platform with a custom FastAPI backend and real-time operations dashboard.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  HappyRobot Platform                │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │
│  │ Web Call  │→ │  Voice   │→ │  Post-Call      │   │
│  │ Trigger  │  │  Agent   │  │  AI Extract +   │   │
│  └──────────┘  │  + Tools │  │  AI Classify    │   │
│                └────┬─────┘  └───────┬────────┘   │
│                     │                │             │
└─────────────────────┼────────────────┼─────────────┘
                      │                │
             ┌────────▼────────────────▼──────┐
             │      FastAPI Backend (Railway)  │
             │  /api/carrier/verify → FMCSA   │
             │  /api/loads/search → SQLite     │
             │  /api/negotiate → Logic Engine  │
             │  /api/calls/log → Call Logger   │
             │  /api/metrics → Dashboard Data  │
             │  /dashboard → Operations UI     │
             └────────────────────────────────┘
```

## Tech Stack

- **Runtime:** Python 3.12
- **Framework:** FastAPI + Uvicorn
- **Database:** SQLite
- **Dashboard:** Chart.js, Inter & JetBrains Mono
- **Deployment:** Docker, Railway
- **External APIs:** FMCSA Carrier Verification

---

## Local Setup

```bash
# Clone the repository
git clone https://github.com/piercegf/happy-robot-fde.git
cd happyrobot-fde

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your FMCSA web key (optional)

# Create data directory
mkdir -p data

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API is now running at `http://localhost:8000` and the dashboard at `http://localhost:8000/dashboard`.

### Seed Test Data

```bash
python scripts/seed_calls.py --url http://localhost:8000 --api-key acme-logistics-2026
```

This inserts 28 realistic test calls with a distribution of booked, rejected, no_match, callback, and not_authorized outcomes.

---

## Docker Setup

```bash
docker-compose up --build
```

The service starts on port 8000 with a persistent `data/` volume for the SQLite database.

---

## Railway Deployment

1. Push this repository to GitHub
2. Connect the repo to [Railway](https://railway.app)
3. Set environment variables: `API_KEY`, `FMCSA_WEBKEY`
4. Railway auto-detects the Dockerfile and deploys

The `railway.json` config handles build and start command settings.

---

## API Documentation

All endpoints require the `X-API-Key` header (default: `acme-logistics-2026`).

### `GET /health`

Health check — no auth required.

```json
{
  "status": "ok",
  "timestamp": "2026-03-30T12:00:00+00:00",
  "version": "1.0.0"
}
```

### `GET /api/carrier/verify/{mc_number}`

Verify a carrier's FMCSA authority.

```bash
curl -H "X-API-Key: acme-logistics-2026" http://localhost:8000/api/carrier/verify/120500
```

```json
{
  "mc_number": "120500",
  "legal_name": "Swift Transportation Co",
  "allowed_to_operate": "Y",
  "is_eligible": true,
  "carrier_operation": "Interstate",
  "safety_rating": "Satisfactory",
  "total_power_units": 18340,
  "total_drivers": 21500,
  "source": "FMCSA"
}
```

### `POST /api/loads/search`

Search available loads by origin, destination, and/or equipment type. All fields are optional; matching is fuzzy (LIKE).

```bash
curl -X POST http://localhost:8000/api/loads/search \
  -H "X-API-Key: acme-logistics-2026" \
  -H "Content-Type: application/json" \
  -d '{"origin": "Chicago", "equipment_type": "Dry Van"}'
```

```json
{
  "loads": [
    {
      "load_id": "LD-1001",
      "origin": "Chicago, IL",
      "destination": "Dallas, TX",
      "equipment_type": "Dry Van",
      "loadboard_rate": 2850.0,
      "miles": 920,
      "weight": 38000,
      "pickup_datetime": "2026-04-02T08:00",
      "delivery_datetime": "2026-04-03T18:00",
      "commodity_type": "Consumer Electronics",
      "notes": "Dock-to-dock. No touch freight."
    }
  ],
  "count": 1
}
```

### `GET /api/loads/{load_id}`

Get a single load by ID.

```bash
curl -H "X-API-Key: acme-logistics-2026" http://localhost:8000/api/loads/LD-1001
```

### `POST /api/negotiate`

Negotiate a rate on a load. Supports up to 3 rounds. Floor is 95% of loadboard rate.

```bash
curl -X POST http://localhost:8000/api/negotiate \
  -H "X-API-Key: acme-logistics-2026" \
  -H "Content-Type: application/json" \
  -d '{"load_id": "LD-1001", "offered_rate": 2600, "round_number": 1}'
```

```json
{
  "accepted": false,
  "counter_offer": 2850.0,
  "message": "I appreciate the offer, but the posted rate for this Chicago, IL to Dallas, TX lane is $2,850. That's where we need to be to cover this load.",
  "final": false
}
```

### `POST /api/calls/log`

Log a completed call. `call_id` and `timestamp` are auto-generated if omitted.

```bash
curl -X POST http://localhost:8000/api/calls/log \
  -H "X-API-Key: acme-logistics-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "carrier_mc": "MC-120500",
    "carrier_name": "Swift Transportation",
    "requested_origin": "Chicago, IL",
    "requested_destination": "Dallas, TX",
    "equipment_type": "Dry Van",
    "load_id_matched": "LD-1001",
    "loadboard_rate": 2850.0,
    "agreed_rate": 2780.0,
    "negotiation_rounds": 2,
    "outcome": "booked",
    "sentiment": "positive",
    "call_duration_seconds": 245,
    "counter_offers": [2850, 2765.5],
    "notes": "Good call. Carrier familiar with lane."
  }'
```

```json
{
  "status": "logged",
  "call_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### `GET /api/calls`

List all logged calls, most recent first.

```bash
curl -H "X-API-Key: acme-logistics-2026" http://localhost:8000/api/calls
```

### `GET /api/metrics`

Aggregated metrics for the dashboard — conversion rate, revenue, sentiment, top lanes, hourly distribution, and more.

```bash
curl -H "X-API-Key: acme-logistics-2026" http://localhost:8000/api/metrics
```

### `GET /dashboard`

Opens the operations dashboard in a browser. No API key required.

---

## Dashboard

Access at `http://localhost:8000/dashboard` (or your Railway URL + `/dashboard`).

The dashboard displays:
- KPI cards (total calls, conversion rate, revenue, negotiation stats, call duration)
- Call outcome and sentiment breakdowns
- Revenue intelligence (captured vs. potential, capture rate, avg discount)
- Call volume over time and peak hour distribution
- Top lanes leaderboard and equipment mix

Auto-refreshes every 30 seconds. Click the refresh button for manual updates.

---

## Links

- **Live Dashboard:** [https://happy-robot-fde-production-f148.up.railway.app/dashboard](https://happy-robot-fde-production-f148.up.railway.app/dashboard)
- **GitHub Repo:** [https://github.com/piercegf/happy-robot-fde](https://github.com/piercegf/happy-robot-fde)
- **HappyRobot Workflow:** [https://platform.happyrobot.ai/fdealejandroperez/workflows/gchtmr5tol1e](https://platform.happyrobot.ai/fdealejandroperez/workflows/gchtmr5tol1e)
- **Demo Video:** [VIDEO_URL]
