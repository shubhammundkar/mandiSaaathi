"""Live test script for agmarknet package.

Attempts to fetch the last 7 days of Tomato for Maharashtra using the agmarknet package.
Prints:
- Package method used
- Column names
- Row count
- 10 real rows
If it fails:
- Shows the full error and traceback, and stops (exits with non-zero code).
"""

import sys
import traceback
from datetime import datetime, timedelta

def run_live_test():
    print("=" * 70)
    print("Mandi Saathi — Live Agmarknet Package Test")
    print("=" * 70)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    from_date_str = start_date.strftime("%Y-%m-%d")
    to_date_str = end_date.strftime("%Y-%m-%d")

    method_description = (
        "agmarknet.Agmarknet().report(\n"
        f"    commodity='Tomato',\n"
        f"    state='Maharashtra',\n"
        f"    from_date='{from_date_str}',\n"
        f"    to_date='{to_date_str}',\n"
        f"    timeout=15\n"
        ")"
    )

    print(f"\n1. Package Method Used:\n{method_description}\n")
    print(f"Filter parameters: Commodity='Tomato', State='Maharashtra', Range={from_date_str} to {to_date_str}")
    print("Attempting live network call to https://api.agmarknet.gov.in/v1/daily-price-arrival/report ...\n")

    try:
        from agmarknet import Agmarknet
        client = Agmarknet()
        df = client.report(
            commodity="Tomato",
            state="Maharashtra",
            from_date=from_date_str,
            to_date=to_date_str,
            timeout=15
        )

        if df is None or df.empty:
            print("Result: Agmarknet returned an empty DataFrame.")
            print("Row count: 0")
            print("Stopping: No data received.")
            sys.exit(1)

        print("-" * 70)
        print("SUCCESS! Live records retrieved successfully:")
        print(f"2. Column names ({len(df.columns)}): {list(df.columns)}")
        print(f"3. Row count: {len(df)}")
        print("\n4. 10 Real Rows:")
        print(df.head(10).to_string())
        print("-" * 70)

    except Exception as exc:
        print("!" * 70)
        print("LIVE FETCH FAILED!")
        print("!" * 70)
        print(f"Exception Class: {exc.__class__.__module__}.{exc.__class__.__name__}")
        print(f"Error Message: {exc}")
        
        # Extract underlying HTTP response details if available
        cause = getattr(exc, "__cause__", None)
        if cause and hasattr(cause, "response"):
            resp = cause.response
            print(f"Underlying HTTP Status Code: {resp.status_code}")
            print(f"Underlying HTTP Response: {resp.text}")
        elif hasattr(exc, "response"):
            resp = getattr(exc, "response")
            print(f"HTTP Status Code: {resp.status_code}")
            print(f"HTTP Response: {resp.text}")

        print("\nFull Traceback:")
        traceback.print_exc()
        print("!" * 70)
        print("Stopping as requested.")
        sys.exit(1)

if __name__ == "__main__":
    run_live_test()
