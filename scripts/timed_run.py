from __future__ import annotations

import argparse
import time


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a lightweight timed prompt assessment simulation.")
    parser.add_argument("--minutes", type=int, default=75, help="Total simulation duration in minutes (default: 75)")
    args = parser.parse_args()

    total_seconds = max(1, args.minutes * 60)
    interval = 5 * 60

    print("Timed simulation started.")
    print("Suggested cadence:")
    print("  1) Edit prompts in src/prompts/*.txt")
    print("  2) Run visible tests: pytest -q")
    print("  3) Iterate until stable")
    print("  4) Final check: python scripts/grade.py")

    remaining = total_seconds
    while remaining > 0:
        mins = remaining // 60
        print(f"Time remaining: {mins} minutes")
        sleep_for = min(interval, remaining)
        time.sleep(sleep_for)
        remaining -= sleep_for

    print("Time is up. Run: python scripts/grade.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
