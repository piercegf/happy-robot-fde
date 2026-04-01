#!/usr/bin/env python3
"""Remove all rows from the calls table only (loads / knowledge base unchanged).

Uses DB_PATH if set, otherwise app default (data/carrier_sales.db).

Examples:
  python scripts/clear_calls_db.py
  DB_PATH=/path/to/carrier_sales.db python scripts/clear_calls_db.py

  # Railway production (from repo root, CLI logged in):
  railway run python scripts/clear_calls_db.py
"""

import argparse
import os
import sys

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db, init_db  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="Delete all call log rows; keep loads table.")
    p.add_argument(
        "--db-path",
        help="SQLite file path (overrides DB_PATH env)",
    )
    args = p.parse_args()
    if args.db_path:
        os.environ["DB_PATH"] = args.db_path

    init_db()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM calls")
    before = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM loads")
    loads = cur.fetchone()[0]
    cur.execute("DELETE FROM calls")
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM calls")
    after = cur.fetchone()[0]
    conn.close()
    print(f"calls: removed {before} row(s), now {after}")
    print(f"loads: {loads} row(s) (unchanged)")


if __name__ == "__main__":
    main()
