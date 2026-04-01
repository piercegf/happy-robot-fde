import sqlite3
import os
import json

DB_PATH = os.getenv("DB_PATH", "data/carrier_sales.db")

SEED_LOADS = [
    {
        "load_id": "LD-1001", "origin": "Chicago, IL", "destination": "Dallas, TX",
        "pickup_datetime": "2026-04-02T08:00", "delivery_datetime": "2026-04-03T18:00",
        "equipment_type": "Dry Van", "loadboard_rate": 2850.0, "weight": 38000,
        "commodity_type": "Consumer Electronics", "num_of_pieces": 24, "miles": 920,
        "dimensions": "48x40x48 pallets", "notes": "Dock-to-dock. No touch freight.",
    },
    {
        "load_id": "LD-1002", "origin": "Los Angeles, CA", "destination": "Phoenix, AZ",
        "pickup_datetime": "2026-04-01T06:00", "delivery_datetime": "2026-04-01T20:00",
        "equipment_type": "Reefer", "loadboard_rate": 1800.0, "weight": 42000,
        "commodity_type": "Fresh Produce", "num_of_pieces": 20, "miles": 370,
        "dimensions": "48x40x60 pallets", "notes": "Temperature controlled at 34°F. Must have temp recorder.",
    },
    {
        "load_id": "LD-1003", "origin": "Atlanta, GA", "destination": "Miami, FL",
        "pickup_datetime": "2026-04-02T10:00", "delivery_datetime": "2026-04-03T08:00",
        "equipment_type": "Flatbed", "loadboard_rate": 2200.0, "weight": 45000,
        "commodity_type": "Steel Beams", "num_of_pieces": 8, "miles": 660,
        "dimensions": "40ft lengths", "notes": "Tarps required. Oversize load.",
    },
    {
        "load_id": "LD-1004", "origin": "Houston, TX", "destination": "New Orleans, LA",
        "pickup_datetime": "2026-04-01T14:00", "delivery_datetime": "2026-04-02T06:00",
        "equipment_type": "Dry Van", "loadboard_rate": 1200.0, "weight": 28000,
        "commodity_type": "Packaged Food", "num_of_pieces": 32, "miles": 350,
        "dimensions": "48x40x48 pallets", "notes": "FCFS. Driver assist unload.",
    },
    {
        "load_id": "LD-1005", "origin": "Newark, NJ", "destination": "Boston, MA",
        "pickup_datetime": "2026-04-03T05:00", "delivery_datetime": "2026-04-03T14:00",
        "equipment_type": "Dry Van", "loadboard_rate": 950.0, "weight": 22000,
        "commodity_type": "Retail Goods", "num_of_pieces": 18, "miles": 215,
        "dimensions": "48x40x48 pallets", "notes": "Appointment required. No lumper fees.",
    },
    {
        "load_id": "LD-1006", "origin": "Seattle, WA", "destination": "Portland, OR",
        "pickup_datetime": "2026-04-01T09:00", "delivery_datetime": "2026-04-01T16:00",
        "equipment_type": "Reefer", "loadboard_rate": 750.0, "weight": 35000,
        "commodity_type": "Frozen Seafood", "num_of_pieces": 15, "miles": 175,
        "dimensions": "48x40x48 pallets", "notes": "Frozen. Temp at 0°F. Short haul.",
    },
    {
        "load_id": "LD-1007", "origin": "Denver, CO", "destination": "Salt Lake City, UT",
        "pickup_datetime": "2026-04-02T07:00", "delivery_datetime": "2026-04-02T22:00",
        "equipment_type": "Flatbed", "loadboard_rate": 1650.0, "weight": 48000,
        "commodity_type": "Building Materials", "num_of_pieces": 12, "miles": 525,
        "dimensions": "Various", "notes": "Construction materials. Chains/straps required.",
    },
    {
        "load_id": "LD-1008", "origin": "Chicago, IL", "destination": "Indianapolis, IN",
        "pickup_datetime": "2026-04-01T11:00", "delivery_datetime": "2026-04-01T18:00",
        "equipment_type": "Dry Van", "loadboard_rate": 680.0, "weight": 18000,
        "commodity_type": "Auto Parts", "num_of_pieces": 40, "miles": 185,
        "dimensions": "Mixed boxes", "notes": "Live unload. ETA call required 2hrs before.",
    },
    {
        "load_id": "LD-1009", "origin": "Memphis, TN", "destination": "Nashville, TN",
        "pickup_datetime": "2026-04-03T08:00", "delivery_datetime": "2026-04-03T14:00",
        "equipment_type": "Dry Van", "loadboard_rate": 550.0, "weight": 20000,
        "commodity_type": "Paper Products", "num_of_pieces": 22, "miles": 210,
        "dimensions": "48x40x48 pallets", "notes": "Straight shot. Quick turn.",
    },
    {
        "load_id": "LD-1010", "origin": "Dallas, TX", "destination": "Los Angeles, CA",
        "pickup_datetime": "2026-04-02T06:00", "delivery_datetime": "2026-04-04T18:00",
        "equipment_type": "Dry Van", "loadboard_rate": 3400.0, "weight": 40000,
        "commodity_type": "Consumer Electronics", "num_of_pieces": 28, "miles": 1435,
        "dimensions": "48x40x48 pallets", "notes": "High value. Sealed trailer. No stops.",
    },
    {
        "load_id": "LD-1011", "origin": "San Antonio, TX", "destination": "Houston, TX",
        "pickup_datetime": "2026-04-01T07:00", "delivery_datetime": "2026-04-01T13:00",
        "equipment_type": "Reefer", "loadboard_rate": 650.0, "weight": 12000,
        "commodity_type": "Pharmaceuticals", "num_of_pieces": 10, "miles": 200,
        "dimensions": "Small pallets", "notes": "Pharmaceutical. Temp 36-46°F. White glove.",
    },
    {
        "load_id": "LD-1012", "origin": "Charlotte, NC", "destination": "Raleigh, NC",
        "pickup_datetime": "2026-04-02T09:00", "delivery_datetime": "2026-04-02T14:00",
        "equipment_type": "Dry Van", "loadboard_rate": 480.0, "weight": 15000,
        "commodity_type": "Textiles", "num_of_pieces": 30, "miles": 170,
        "dimensions": "48x40x48 pallets", "notes": "Local run. FCFS.",
    },
    {
        "load_id": "LD-1013", "origin": "Minneapolis, MN", "destination": "Chicago, IL",
        "pickup_datetime": "2026-04-03T06:00", "delivery_datetime": "2026-04-03T20:00",
        "equipment_type": "Reefer", "loadboard_rate": 1400.0, "weight": 38000,
        "commodity_type": "Dairy", "num_of_pieces": 20, "miles": 410,
        "dimensions": "48x40x60 pallets", "notes": "Dairy products. Temp 34°F strict.",
    },
    {
        "load_id": "LD-1014", "origin": "Kansas City, MO", "destination": "St. Louis, MO",
        "pickup_datetime": "2026-04-01T10:00", "delivery_datetime": "2026-04-01T16:00",
        "equipment_type": "Flatbed", "loadboard_rate": 700.0, "weight": 35000,
        "commodity_type": "Industrial Machinery", "num_of_pieces": 4, "miles": 250,
        "dimensions": "Heavy equipment", "notes": "Machinery. Forklift on site for loading.",
    },
    {
        "load_id": "LD-1015", "origin": "Philadelphia, PA", "destination": "Washington, DC",
        "pickup_datetime": "2026-04-02T12:00", "delivery_datetime": "2026-04-02T20:00",
        "equipment_type": "Dry Van", "loadboard_rate": 620.0, "weight": 25000,
        "commodity_type": "Office Supplies", "num_of_pieces": 35, "miles": 140,
        "dimensions": "Mixed", "notes": "Government facility. Driver needs valid ID.",
    },
    {
        "load_id": "LD-1016", "origin": "Jacksonville, FL", "destination": "Savannah, GA",
        "pickup_datetime": "2026-04-03T07:00", "delivery_datetime": "2026-04-03T13:00",
        "equipment_type": "Reefer", "loadboard_rate": 580.0, "weight": 30000,
        "commodity_type": "Frozen Poultry", "num_of_pieces": 18, "miles": 140,
        "dimensions": "48x40x48 pallets", "notes": "USDA inspected. Temp log required.",
    },
    {
        "load_id": "LD-1017", "origin": "Detroit, MI", "destination": "Columbus, OH",
        "pickup_datetime": "2026-04-01T08:00", "delivery_datetime": "2026-04-01T17:00",
        "equipment_type": "Dry Van", "loadboard_rate": 720.0, "weight": 26000,
        "commodity_type": "Automotive Parts", "num_of_pieces": 42, "miles": 200,
        "dimensions": "Mixed boxes and crates", "notes": "JIT delivery. Cannot be late.",
    },
    {
        "load_id": "LD-1018", "origin": "San Francisco, CA", "destination": "Sacramento, CA",
        "pickup_datetime": "2026-04-02T06:00", "delivery_datetime": "2026-04-02T11:00",
        "equipment_type": "Flatbed", "loadboard_rate": 520.0, "weight": 32000,
        "commodity_type": "Solar Panels", "num_of_pieces": 6, "miles": 90,
        "dimensions": "Oversized crates", "notes": "Fragile. Secure with edge protectors.",
    },
]


def _get_db_path():
    return os.getenv("DB_PATH", DB_PATH)


def get_db():
    db_path = _get_db_path()
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS loads (
            load_id TEXT PRIMARY KEY,
            origin TEXT,
            destination TEXT,
            pickup_datetime TEXT,
            delivery_datetime TEXT,
            equipment_type TEXT,
            loadboard_rate REAL,
            notes TEXT,
            weight INTEGER,
            commodity_type TEXT,
            num_of_pieces INTEGER,
            miles INTEGER,
            dimensions TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            call_id TEXT PRIMARY KEY,
            timestamp TEXT,
            carrier_mc TEXT,
            carrier_name TEXT,
            requested_origin TEXT,
            requested_destination TEXT,
            equipment_type TEXT,
            load_id_matched TEXT,
            loadboard_rate REAL,
            agreed_rate REAL,
            negotiation_rounds INTEGER DEFAULT 0,
            outcome TEXT,
            sentiment TEXT,
            call_duration_seconds INTEGER,
            counter_offers TEXT,
            notes TEXT
        )
    """)

    cur.execute("SELECT COUNT(*) FROM loads")
    if cur.fetchone()[0] == 0:
        for load in SEED_LOADS:
            cur.execute("""
                INSERT INTO loads (load_id, origin, destination, pickup_datetime, delivery_datetime,
                    equipment_type, loadboard_rate, notes, weight, commodity_type, num_of_pieces, miles, dimensions)
                VALUES (:load_id, :origin, :destination, :pickup_datetime, :delivery_datetime,
                    :equipment_type, :loadboard_rate, :notes, :weight, :commodity_type, :num_of_pieces, :miles, :dimensions)
            """, load)

    conn.commit()
    conn.close()


def get_loads_by_criteria(origin=None, destination=None, equipment_type=None):
    conn = get_db()
    cur = conn.cursor()
    query = "SELECT * FROM loads WHERE 1=1"
    params = []
    if origin:
        query += " AND origin LIKE ?"
        params.append(f"%{origin}%")
    if destination:
        query += " AND destination LIKE ?"
        params.append(f"%{destination}%")
    if equipment_type:
        query += " AND equipment_type LIKE ?"
        params.append(f"%{equipment_type}%")
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_load_by_id(load_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM loads WHERE load_id = ?", (load_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def log_call(call_data: dict):
    conn = get_db()
    cur = conn.cursor()
    if "counter_offers" in call_data and isinstance(call_data["counter_offers"], (list, dict)):
        call_data["counter_offers"] = json.dumps(call_data["counter_offers"])
    cur.execute("""
        INSERT INTO calls (call_id, timestamp, carrier_mc, carrier_name, requested_origin,
            requested_destination, equipment_type, load_id_matched, loadboard_rate, agreed_rate,
            negotiation_rounds, outcome, sentiment, call_duration_seconds, counter_offers, notes)
        VALUES (:call_id, :timestamp, :carrier_mc, :carrier_name, :requested_origin,
            :requested_destination, :equipment_type, :load_id_matched, :loadboard_rate, :agreed_rate,
            :negotiation_rounds, :outcome, :sentiment, :call_duration_seconds, :counter_offers, :notes)
    """, call_data)
    conn.commit()
    conn.close()


def get_all_calls():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM calls ORDER BY timestamp DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


BOOKED_OUTCOMES = ("booked", "load_booked")
REJECTED_OUTCOMES = ("rejected", "no_agreement")


def _is_booked(outcome_col="outcome"):
    vals = ",".join(f"'{v}'" for v in BOOKED_OUTCOMES)
    return f"{outcome_col} IN ({vals})"


def _is_rejected(outcome_col="outcome"):
    vals = ",".join(f"'{v}'" for v in REJECTED_OUTCOMES)
    return f"{outcome_col} IN ({vals})"


def get_call_metrics():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM calls")
    total_calls = cur.fetchone()[0]

    empty = {
        "total_calls": 0, "conversion_rate": 0, "avg_negotiation_rounds": 0,
        "outcome_breakdown": {}, "sentiment_breakdown": {},
        "avg_discount_pct": 0, "total_revenue_booked": 0,
        "total_potential_revenue": 0, "revenue_capture_rate": 0,
        "top_lanes": [], "avg_call_duration": 0, "calls_over_time": {},
        "booked_by_equipment": {}, "avg_rate_by_lane": [],
        "negotiation_success_rate": 0, "calls_by_hour": {},
        "avg_time_to_book": 0, "revenue_per_minute": 0,
        "missed_revenue": 0, "sentiment_to_booking": {},
        "top_carriers": [], "recent_calls": [], "all_calls": [],
        "call_flow_funnel": {"total": 0, "verified": 0, "eligible": 0, "loads_searched": 0, "negotiated": 0, "booked": 0},
    }

    if total_calls == 0:
        conn.close()
        return empty

    cur.execute(f"SELECT COUNT(*) FROM calls WHERE {_is_booked()}")
    booked = cur.fetchone()[0]
    conversion_rate = round((booked / total_calls) * 100, 1) if total_calls else 0

    cur.execute("SELECT AVG(negotiation_rounds) FROM calls")
    avg_rounds = round(cur.fetchone()[0] or 0, 1)

    cur.execute("SELECT outcome, COUNT(*) as cnt FROM calls GROUP BY outcome")
    outcome_breakdown = {row["outcome"]: row["cnt"] for row in cur.fetchall()}

    cur.execute("SELECT sentiment, COUNT(*) as cnt FROM calls GROUP BY sentiment")
    sentiment_breakdown = {row["sentiment"]: row["cnt"] for row in cur.fetchall()}

    cur.execute(f"SELECT SUM(agreed_rate) FROM calls WHERE {_is_booked()} AND agreed_rate IS NOT NULL")
    total_revenue_booked = round(cur.fetchone()[0] or 0, 2)

    cur.execute(f"SELECT SUM(loadboard_rate) FROM calls WHERE {_is_booked()} AND loadboard_rate IS NOT NULL")
    total_potential_revenue = round(cur.fetchone()[0] or 0, 2)

    revenue_capture_rate = round((total_revenue_booked / total_potential_revenue) * 100, 1) if total_potential_revenue else 0

    cur.execute(f"""
        SELECT AVG(
            CASE WHEN loadboard_rate > 0 AND agreed_rate IS NOT NULL
                THEN ((loadboard_rate - agreed_rate) / loadboard_rate) * 100
                ELSE NULL END
        ) FROM calls WHERE {_is_booked()}
    """)
    avg_discount_pct = round(cur.fetchone()[0] or 0, 1)

    cur.execute(f"""
        SELECT requested_origin || ' → ' || requested_destination as lane,
            COUNT(*) as cnt,
            ROUND(SUM(CASE WHEN {_is_booked()} THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1) as booking_rate
        FROM calls
        WHERE requested_origin IS NOT NULL AND requested_destination IS NOT NULL
        GROUP BY lane ORDER BY cnt DESC LIMIT 5
    """)
    top_lanes = [{"lane": r["lane"], "count": r["cnt"], "booking_rate": r["booking_rate"]} for r in cur.fetchall()]

    cur.execute("SELECT AVG(call_duration_seconds) FROM calls")
    avg_call_duration = round(cur.fetchone()[0] or 0, 1)

    cur.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as cnt
        FROM calls GROUP BY day ORDER BY day
    """)
    calls_over_time = {row["day"]: row["cnt"] for row in cur.fetchall()}

    cur.execute(f"""
        SELECT equipment_type, COUNT(*) as cnt
        FROM calls WHERE {_is_booked()} AND equipment_type IS NOT NULL
        GROUP BY equipment_type
    """)
    booked_by_equipment = {row["equipment_type"]: row["cnt"] for row in cur.fetchall()}

    cur.execute(f"""
        SELECT requested_origin || ' → ' || requested_destination as lane,
            ROUND(AVG(loadboard_rate), 2) as avg_loadboard,
            ROUND(AVG(agreed_rate), 2) as avg_agreed
        FROM calls
        WHERE {_is_booked()} AND loadboard_rate IS NOT NULL AND agreed_rate IS NOT NULL
        GROUP BY lane ORDER BY COUNT(*) DESC LIMIT 5
    """)
    avg_rate_by_lane = [
        {"lane": r["lane"], "avg_loadboard": r["avg_loadboard"], "avg_agreed": r["avg_agreed"]}
        for r in cur.fetchall()
    ]

    cur.execute("SELECT COUNT(*) FROM calls WHERE negotiation_rounds > 0")
    negotiated_total = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM calls WHERE negotiation_rounds > 0 AND {_is_booked()}")
    negotiated_booked = cur.fetchone()[0]
    negotiation_success_rate = round((negotiated_booked / negotiated_total) * 100, 1) if negotiated_total else 0

    cur.execute("""
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hr, COUNT(*) as cnt
        FROM calls GROUP BY hr ORDER BY hr
    """)
    calls_by_hour = {str(row["hr"]): row["cnt"] for row in cur.fetchall()}

    cur.execute(f"SELECT AVG(call_duration_seconds) FROM calls WHERE {_is_booked()}")
    avg_time_to_book = round(cur.fetchone()[0] or 0, 1)

    cur.execute("SELECT SUM(call_duration_seconds) FROM calls WHERE call_duration_seconds IS NOT NULL")
    total_call_seconds = cur.fetchone()[0] or 0
    revenue_per_minute = round((total_revenue_booked / (total_call_seconds / 60)), 2) if total_call_seconds > 0 else 0

    cur.execute(f"SELECT SUM(loadboard_rate) FROM calls WHERE {_is_rejected()} AND loadboard_rate IS NOT NULL")
    missed_revenue = round(cur.fetchone()[0] or 0, 2)

    cur.execute(f"""
        SELECT sentiment,
            ROUND(SUM(CASE WHEN {_is_booked()} THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 1) as book_rate
        FROM calls WHERE sentiment IS NOT NULL
        GROUP BY sentiment
    """)
    sentiment_to_booking = {row["sentiment"]: row["book_rate"] for row in cur.fetchall()}

    cur.execute(f"""
        SELECT carrier_name, COUNT(*) as cnt,
            SUM(CASE WHEN {_is_booked()} THEN 1 ELSE 0 END) as booked_cnt,
            ROUND(SUM(COALESCE(agreed_rate, 0)), 2) as total_rev
        FROM calls WHERE carrier_name IS NOT NULL
        GROUP BY carrier_name ORDER BY cnt DESC LIMIT 8
    """)
    top_carriers = [
        {"name": r["carrier_name"], "calls": r["cnt"], "booked": r["booked_cnt"], "revenue": r["total_rev"]}
        for r in cur.fetchall()
    ]

    cur.execute("""
        SELECT call_id, timestamp, carrier_name, carrier_mc,
            requested_origin || ' → ' || requested_destination as lane,
            outcome, sentiment, agreed_rate, call_duration_seconds
        FROM calls ORDER BY timestamp DESC LIMIT 10
    """)
    recent_calls = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT call_id, timestamp, carrier_name, carrier_mc,
            requested_origin, requested_destination, equipment_type,
            load_id_matched, loadboard_rate, agreed_rate,
            negotiation_rounds, outcome, sentiment,
            call_duration_seconds, notes
        FROM calls ORDER BY timestamp DESC LIMIT 50
    """)
    all_calls = [dict(r) for r in cur.fetchall()]

    # Call flow funnel
    cur.execute("SELECT COUNT(*) FROM calls WHERE carrier_mc IS NOT NULL AND carrier_mc != ''")
    verified = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM calls WHERE outcome NOT IN ('carrier_not_eligible', 'not_authorized')")
    eligible = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM calls WHERE requested_origin IS NOT NULL AND requested_origin != ''")
    loads_searched = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM calls WHERE negotiation_rounds > 0")
    negotiated = cur.fetchone()[0]

    call_flow_funnel = {
        "total": total_calls,
        "verified": verified,
        "eligible": eligible,
        "loads_searched": loads_searched,
        "negotiated": negotiated,
        "booked": booked,
    }

    conn.close()

    return {
        "total_calls": total_calls,
        "conversion_rate": conversion_rate,
        "avg_negotiation_rounds": avg_rounds,
        "outcome_breakdown": outcome_breakdown,
        "sentiment_breakdown": sentiment_breakdown,
        "avg_discount_pct": avg_discount_pct,
        "total_revenue_booked": total_revenue_booked,
        "total_potential_revenue": total_potential_revenue,
        "revenue_capture_rate": revenue_capture_rate,
        "top_lanes": top_lanes,
        "avg_call_duration": avg_call_duration,
        "calls_over_time": calls_over_time,
        "booked_by_equipment": booked_by_equipment,
        "avg_rate_by_lane": avg_rate_by_lane,
        "negotiation_success_rate": negotiation_success_rate,
        "calls_by_hour": calls_by_hour,
        "avg_time_to_book": avg_time_to_book,
        "revenue_per_minute": revenue_per_minute,
        "missed_revenue": missed_revenue,
        "sentiment_to_booking": sentiment_to_booking,
        "top_carriers": top_carriers,
        "recent_calls": recent_calls,
        "all_calls": all_calls,
        "call_flow_funnel": call_flow_funnel,
    }
