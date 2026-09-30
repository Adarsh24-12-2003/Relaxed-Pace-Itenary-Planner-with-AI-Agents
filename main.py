"""Run the multi-agent travel planner from a normal Python file."""

import argparse

from orchestrator import run_pipeline
from utils import pretty_json


DEFAULT_REQUEST = (
    "Plan a relaxed 4-day trip from Delhi to Dubai for two people. Keep it "
    "mid-budget, avoid red-eye flights, and prefer food, city views, and cultural "
    "sites. Schedule no more than one main activity per day, leave generous breaks "
    "and unplanned time, and keep the total hotel budget under ₹45,000."
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Relaxed-pace multi-agent travel planner")
    parser.add_argument("--request", default=DEFAULT_REQUEST)
    parser.add_argument("--show-trace", action="store_true")
    args = parser.parse_args()

    print(
        "Running Manager, Flight, Hotel, Activity, and Critic agents...\n"
    )
    result = run_pipeline(args.request)

    print("FINAL TRAVEL PLAN\n")
    print(pretty_json(result["final_output"]))

    if args.show_trace:
        print("\nFULL PIPELINE TRACE\n")
        print(pretty_json(result))


if __name__ == "__main__":
    main()
