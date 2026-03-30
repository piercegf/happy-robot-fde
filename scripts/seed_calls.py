#!/usr/bin/env python3
"""Seed the Acme Logistics Inbound Carrier Sales API with 28 realistic test calls."""

import argparse
import json
import random
import uuid
from datetime import datetime, timedelta, timezone

import httpx

CARRIERS = [
    ("Swift Transportation", "MC-120500"), ("Heartland Express", "MC-215987"),
    ("JB Hunt Transport", "MC-107039"), ("Werner Enterprises", "MC-142400"),
    ("Schneider National", "MC-133655"), ("Knight-Swift", "MC-120500"),
    ("Old Dominion", "MC-105637"), ("XPO Logistics", "MC-171702"),
    ("Saia Inc", "MC-197080"), ("FedEx Freight", "MC-184704"),
    ("Estes Express", "MC-161870"), ("USF Holland", "MC-146483"),
    ("ABF Freight", "MC-113459"), ("Conway Freight", "MC-121873"),
    ("Marten Transport", "MC-169044"), ("USA Truck", "MC-173289"),
    ("Celadon Group", "MC-152437"), ("Covenant Transport", "MC-181462"),
    ("Ryder System", "MC-158324"), ("Landstar System", "MC-143123"),
    ("Echo Global", "MC-192074"), ("Coyote Logistics", "MC-200618"),
    ("Total Quality Logistics", "MC-184021"), ("Arrive Logistics", "MC-210435"),
    ("Nolan Transportation", "MC-172901"), ("Anderson Trucking", "MC-118456"),
    ("Mercer Transportation", "MC-125689"), ("Heartland Express", "MC-215987"),
]

LOAD_IDS = [f"LD-{1001 + i}" for i in range(18)]

LOADS = {
    "LD-1001": ("Chicago, IL", "Dallas, TX", "Dry Van", 2850),
    "LD-1002": ("Los Angeles, CA", "Phoenix, AZ", "Reefer", 1800),
    "LD-1003": ("Atlanta, GA", "Miami, FL", "Flatbed", 2200),
    "LD-1004": ("Houston, TX", "New Orleans, LA", "Dry Van", 1200),
    "LD-1005": ("Newark, NJ", "Boston, MA", "Dry Van", 950),
    "LD-1006": ("Seattle, WA", "Portland, OR", "Reefer", 750),
    "LD-1007": ("Denver, CO", "Salt Lake City, UT", "Flatbed", 1650),
    "LD-1008": ("Chicago, IL", "Indianapolis, IN", "Dry Van", 680),
    "LD-1009": ("Memphis, TN", "Nashville, TN", "Dry Van", 550),
    "LD-1010": ("Dallas, TX", "Los Angeles, CA", "Dry Van", 3400),
    "LD-1011": ("San Antonio, TX", "Houston, TX", "Reefer", 650),
    "LD-1012": ("Charlotte, NC", "Raleigh, NC", "Dry Van", 480),
    "LD-1013": ("Minneapolis, MN", "Chicago, IL", "Reefer", 1400),
    "LD-1014": ("Kansas City, MO", "St. Louis, MO", "Flatbed", 700),
    "LD-1015": ("Philadelphia, PA", "Washington, DC", "Dry Van", 620),
    "LD-1016": ("Jacksonville, FL", "Savannah, GA", "Reefer", 580),
    "LD-1017": ("Detroit, MI", "Columbus, OH", "Dry Van", 720),
    "LD-1018": ("San Francisco, CA", "Sacramento, CA", "Flatbed", 520),
}

NO_MATCH_LANES = [
    ("Portland, OR", "Boise, ID", "Dry Van"),
    ("Austin, TX", "Tulsa, OK", "Reefer"),
    ("Tampa, FL", "Birmingham, AL", "Flatbed"),
    ("Las Vegas, NV", "Tucson, AZ", "Dry Van"),
]

NOW = datetime.now(timezone.utc)


def random_timestamp():
    """Random time in the last 7 days, between 7am and 6pm."""
    day_offset = random.randint(0, 6)
    hour = random.randint(7, 17)
    minute = random.randint(0, 59)
    dt = NOW - timedelta(days=day_offset)
    return dt.replace(hour=hour, minute=minute, second=random.randint(0, 59)).isoformat()


def make_booked_call(carrier):
    load_id = random.choice(LOAD_IDS)
    origin, dest, equip, lb_rate = LOADS[load_id]
    discount = random.uniform(0.0, 0.05)
    agreed = round(lb_rate * (1 - discount), 2)
    rounds = random.choices([0, 1, 2, 3], weights=[15, 40, 30, 15])[0]
    counters = []
    if rounds >= 1:
        counters.append(lb_rate)
    if rounds >= 2:
        counters.append(round(lb_rate * 0.97, 2))
    if rounds >= 3:
        counters.append(round(lb_rate * 0.95, 2))
    return {
        "carrier_mc": carrier[1], "carrier_name": carrier[0],
        "requested_origin": origin, "requested_destination": dest,
        "equipment_type": equip, "load_id_matched": load_id,
        "loadboard_rate": lb_rate, "agreed_rate": agreed,
        "negotiation_rounds": rounds, "outcome": "booked",
        "sentiment": random.choices(["positive", "neutral"], weights=[75, 25])[0],
        "call_duration_seconds": random.randint(120, 350),
        "counter_offers": counters,
        "notes": random.choice([
            "Smooth call. Carrier accepted quickly.",
            "Good rapport. Carrier familiar with this lane.",
            "Rate negotiation was efficient.",
            "Carrier asked about future loads on this lane.",
            "Driver available same day. Quick booking.",
        ]),
        "timestamp": random_timestamp(),
    }


def make_rejected_call(carrier):
    load_id = random.choice(LOAD_IDS)
    origin, dest, equip, lb_rate = LOADS[load_id]
    return {
        "carrier_mc": carrier[1], "carrier_name": carrier[0],
        "requested_origin": origin, "requested_destination": dest,
        "equipment_type": equip, "load_id_matched": load_id,
        "loadboard_rate": lb_rate, "agreed_rate": None,
        "negotiation_rounds": random.randint(2, 3), "outcome": "rejected",
        "sentiment": random.choice(["neutral", "negative"]),
        "call_duration_seconds": random.randint(150, 400),
        "counter_offers": [lb_rate, round(lb_rate * 0.97, 2)],
        "notes": random.choice([
            "Carrier wanted 15% above posted rate.",
            "Rate too low for carrier. Hung up after round 2.",
            "Carrier has better-paying load already.",
        ]),
        "timestamp": random_timestamp(),
    }


def make_no_match_call(carrier):
    lane = random.choice(NO_MATCH_LANES)
    return {
        "carrier_mc": carrier[1], "carrier_name": carrier[0],
        "requested_origin": lane[0], "requested_destination": lane[1],
        "equipment_type": lane[2], "load_id_matched": None,
        "loadboard_rate": None, "agreed_rate": None,
        "negotiation_rounds": 0, "outcome": "no_match",
        "sentiment": "neutral",
        "call_duration_seconds": random.randint(60, 120),
        "counter_offers": [],
        "notes": "No loads available for requested lane.",
        "timestamp": random_timestamp(),
    }


def make_callback_call(carrier):
    load_id = random.choice(LOAD_IDS)
    origin, dest, equip, lb_rate = LOADS[load_id]
    return {
        "carrier_mc": carrier[1], "carrier_name": carrier[0],
        "requested_origin": origin, "requested_destination": dest,
        "equipment_type": equip, "load_id_matched": load_id,
        "loadboard_rate": lb_rate, "agreed_rate": None,
        "negotiation_rounds": random.randint(0, 1), "outcome": "callback",
        "sentiment": random.choice(["positive", "neutral"]),
        "call_duration_seconds": random.randint(90, 180),
        "counter_offers": [],
        "notes": random.choice([
            "Carrier needs to check driver availability.",
            "Wants to call back after confirming with dispatch.",
            "Interested but needs to review schedule.",
        ]),
        "timestamp": random_timestamp(),
    }


def make_not_authorized_call(carrier):
    return {
        "carrier_mc": "999999", "carrier_name": carrier[0],
        "requested_origin": "Unknown", "requested_destination": "Unknown",
        "equipment_type": None, "load_id_matched": None,
        "loadboard_rate": None, "agreed_rate": None,
        "negotiation_rounds": 0, "outcome": "not_authorized",
        "sentiment": random.choice(["neutral", "negative"]),
        "call_duration_seconds": random.randint(45, 90),
        "counter_offers": [],
        "notes": "Carrier MC authority could not be verified.",
        "timestamp": random_timestamp(),
    }


def main():
    parser = argparse.ArgumentParser(description="Seed carrier sales call data")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", default="acme-logistics-2026", help="API key")
    args = parser.parse_args()

    random.seed(42)
    shuffled = random.sample(CARRIERS, len(CARRIERS))

    calls = []
    for i in range(14):
        calls.append(make_booked_call(shuffled[i % len(shuffled)]))
    for i in range(5):
        calls.append(make_rejected_call(shuffled[(14 + i) % len(shuffled)]))
    for i in range(4):
        calls.append(make_no_match_call(shuffled[(19 + i) % len(shuffled)]))
    for i in range(3):
        calls.append(make_callback_call(shuffled[(23 + i) % len(shuffled)]))
    for i in range(2):
        calls.append(make_not_authorized_call(shuffled[(26 + i) % len(shuffled)]))

    random.shuffle(calls)

    print(f"Seeding {len(calls)} calls to {args.url}...")
    with httpx.Client(timeout=30.0) as client:
        for idx, call in enumerate(calls, 1):
            call["call_id"] = str(uuid.uuid4())
            resp = client.post(
                f"{args.url}/api/calls/log",
                json=call,
                headers={"X-API-Key": args.api_key},
            )
            status = "OK" if resp.status_code == 200 else f"ERR {resp.status_code}"
            outcome = call["outcome"].upper()
            carrier = call["carrier_name"]
            print(f"  [{idx:2d}/28] {status} | {outcome:<16} | {carrier}")
    print("\nDone! All 28 calls seeded.")


if __name__ == "__main__":
    main()
