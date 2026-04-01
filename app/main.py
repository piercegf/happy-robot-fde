import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, model_validator

from app.database import (
    init_db,
    get_loads_by_criteria,
    get_load_by_id,
    get_all_loads,
    log_call,
    get_all_calls,
    clear_all_calls,
    get_call_metrics,
    get_carrier_intelligence,
)

load_dotenv()

API_KEY = os.getenv("API_KEY", "acme-logistics-2026")
FMCSA_WEBKEY = os.getenv("FMCSA_WEBKEY", "")

app = FastAPI(
    title="Acme Logistics — Inbound Carrier Sales API",
    version="1.0.0",
    description="Backend API for HappyRobot-powered inbound carrier sales automation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # Do not use allow_credentials=True with wildcard origins (invalid per fetch spec).
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class LoadSearchRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None


class NegotiateRequest(BaseModel):
    load_id: str
    offered_rate: float
    round_number: int


def _coerce_float(v):
    if v is None or v == "":
        return None
    return float(v)

def _coerce_int(v, default=0):
    if v is None or v == "":
        return default
    return int(v)

class CallLogRequest(BaseModel):
    call_id: Optional[str] = None
    timestamp: Optional[str] = None
    carrier_mc: Optional[str] = None
    carrier_name: Optional[str] = None
    requested_origin: Optional[str] = None
    requested_destination: Optional[str] = None
    equipment_type: Optional[str] = None
    load_id_matched: Optional[str] = None
    loadboard_rate: Optional[float] = None
    agreed_rate: Optional[float] = None
    negotiation_rounds: int = 0
    outcome: Optional[str] = None
    sentiment: Optional[str] = None
    call_duration_seconds: Optional[int] = None
    counter_offers: Optional[list] = None
    notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def coerce_numeric_fields(cls, values):
        if isinstance(values, dict):
            if values.get("sentiment") in (None, "") and values.get("sentiment_classifier") not in (
                None,
                "",
            ):
                values["sentiment"] = values["sentiment_classifier"]
            values["loadboard_rate"] = _coerce_float(values.get("loadboard_rate"))
            values["agreed_rate"] = _coerce_float(values.get("agreed_rate"))
            values["negotiation_rounds"] = _coerce_int(values.get("negotiation_rounds"), 0)
            raw_dur = values.get("call_duration_seconds")
            if raw_dur is None or raw_dur == "":
                values["call_duration_seconds"] = None
            else:
                values["call_duration_seconds"] = int(raw_dur)
        return values


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
def startup():
    init_db()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }


@app.get("/api/carrier/verify/{mc_number}")
async def verify_carrier(mc_number: str, api_key: str = Security(verify_api_key)):
    mc_number = re.sub(r"^[Mm][Cc]-?", "", mc_number.strip())

    # Try FMCSA official API first
    if FMCSA_WEBKEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}?webKey={FMCSA_WEBKEY}"
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("content", [{}])
                    carrier = content[0].get("carrier", {}) if content else {}
                    allowed = carrier.get("allowedToOperate", "N")
                    return {
                        "mc_number": mc_number,
                        "legal_name": carrier.get("legalName", "Unknown"),
                        "allowed_to_operate": allowed,
                        "is_eligible": allowed == "Y",
                        "carrier_operation": carrier.get("carrierOperation", {}).get("carrierOperationDesc", "Unknown"),
                        "safety_rating": carrier.get("safetyRating", "Not Rated"),
                        "total_power_units": carrier.get("totalPowerUnits", 0),
                        "total_drivers": carrier.get("totalDrivers", 0),
                        "source": "FMCSA",
                    }
        except Exception:
            pass

    # Fallback to VerifyCarrier
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://verifycarrier.com/api/lookup/dot/MC{mc_number}"
            resp = await client.get(url)
            if resp.status_code == 200:
                raw = resp.json()
                data = raw.get("data", raw)
                authority = data.get("authority", {})
                safety = data.get("safety", {})
                fleet = data.get("fleet", {})
                common_auth = authority.get("common", "N")
                out_of_service = safety.get("out_of_service", True)
                is_eligible = common_auth == "A" and not out_of_service
                if not is_eligible and common_auth in ("A", "I"):
                    is_eligible = common_auth != "N" and not out_of_service
                return {
                    "mc_number": mc_number,
                    "legal_name": data.get("legal_name", "Unknown"),
                    "allowed_to_operate": "Y" if is_eligible else "N",
                    "is_eligible": is_eligible,
                    "dot_number": data.get("dot_number", "Unknown"),
                    "common_authority": common_auth,
                    "out_of_service": out_of_service,
                    "total_power_units": fleet.get("power_units", 0),
                    "total_drivers": fleet.get("drivers", 0),
                    "source": "FMCSA",
                }
    except Exception:
        pass

    return {
        "mc_number": mc_number,
        "is_eligible": False,
        "reason": "FMCSA and backup verification services are unavailable. Please try again later or verify manually.",
        "source": "none",
    }


@app.post("/api/loads/search")
async def search_loads(body: LoadSearchRequest, api_key: str = Security(verify_api_key)):
    loads = get_loads_by_criteria(body.origin, body.destination, body.equipment_type)
    if not loads:
        return {"loads": [], "count": 0, "message": "No matching loads found."}
    return {"loads": loads, "count": len(loads)}


@app.get("/api/loads/{load_id}")
async def get_load(load_id: str, api_key: str = Security(verify_api_key)):
    load = get_load_by_id(load_id)
    if not load:
        raise HTTPException(status_code=404, detail=f"Load {load_id} not found")
    return load


@app.post("/api/negotiate")
async def negotiate(body: NegotiateRequest, api_key: str = Security(verify_api_key)):
    load = get_load_by_id(body.load_id)
    if not load:
        raise HTTPException(status_code=404, detail=f"Load {body.load_id} not found")

    loadboard_rate = load["loadboard_rate"]
    floor = loadboard_rate * 0.95
    offered = body.offered_rate
    round_num = body.round_number

    if round_num < 1 or round_num > 3:
        raise HTTPException(status_code=400, detail="round_number must be between 1 and 3")

    if offered >= floor:
        return {
            "accepted": True,
            "counter_offer": None,
            "message": f"We have a deal. ${offered:,.0f} works for the {load['origin']} to {load['destination']} lane. I'll get the rate confirmation sent over.",
            "final": True,
        }

    if round_num == 1:
        counter = loadboard_rate
        return {
            "accepted": False,
            "counter_offer": counter,
            "message": f"I appreciate the offer, but the posted rate for this {load['origin']} to {load['destination']} lane is ${counter:,.0f}. That's where we need to be to cover this load.",
            "final": False,
        }

    if round_num == 2:
        counter = round(loadboard_rate * 0.97, 2)
        return {
            "accepted": False,
            "counter_offer": counter,
            "message": f"Let me see what I can do... the best I can offer on this one is ${counter:,.0f}. That's already a discount off the posted rate.",
            "final": False,
        }

    counter = round(floor, 2)
    return {
        "accepted": False,
        "counter_offer": counter,
        "message": f"Look, I want to make this work. The absolute lowest I can go is ${counter:,.0f}. That's my final number on this lane.",
        "final": True,
    }


@app.post("/api/calls/log")
async def log_call_endpoint(body: CallLogRequest, api_key: str = Security(verify_api_key)):
    call_data = body.model_dump()
    if not call_data.get("call_id"):
        call_data["call_id"] = str(uuid.uuid4())
    if not call_data.get("timestamp"):
        call_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    if call_data.get("counter_offers") and isinstance(call_data["counter_offers"], list):
        call_data["counter_offers"] = json.dumps(call_data["counter_offers"])
    elif call_data.get("counter_offers") is None:
        call_data["counter_offers"] = "[]"
    log_call(call_data)
    return {"status": "logged", "call_id": call_data["call_id"]}


@app.get("/api/calls")
async def list_calls(api_key: str = Security(verify_api_key)):
    calls = get_all_calls()
    return {"calls": calls, "count": len(calls)}


@app.get("/api/loads")
async def list_all_loads(api_key: str = Security(verify_api_key)):
    loads = get_all_loads()
    return {"loads": loads, "count": len(loads)}


@app.get("/api/intelligence/carriers")
async def carrier_intelligence(api_key: str = Security(verify_api_key)):
    carriers = get_carrier_intelligence()
    return {"carriers": carriers, "count": len(carriers)}


@app.get("/api/metrics")
async def metrics(api_key: str = Security(verify_api_key)):
    return get_call_metrics()


@app.post("/api/admin/clear-calls")
async def admin_clear_calls(api_key: str = Security(verify_api_key)):
    """Remove all call log rows. Same auth as the rest of the API (demo admin)."""
    deleted = clear_all_calls()
    return {"status": "ok", "deleted": deleted}


@app.get("/dashboard")
async def dashboard():
    return FileResponse("dashboard/index.html")


@app.get("/dashboard/{filename}")
async def dashboard_static(filename: str):
    root = Path("dashboard").resolve()
    try:
        candidate = (root / filename).resolve()
    except OSError:
        raise HTTPException(status_code=404, detail="File not found")
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(candidate))
