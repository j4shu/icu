import argparse
import json
import sys

from dotenv import load_dotenv

from intervals_client import build_training_summary, get_athlete, get_events


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        prog="triclops", description="Fetch Intervals.icu training data as JSON."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    summary = sub.add_parser(
        "summary", help="Wellness + activities + events for the past N days."
    )
    summary.add_argument("--days", type=int, default=42, help="Lookback window (default: 42).")
    summary.add_argument(
        "--force", action="store_true", help="Bypass cache and re-fetch the window."
    )

    sub.add_parser("events", help="Upcoming/recent races only.")
    sub.add_parser("athlete", help="Athlete profile from .athlete.")

    args = parser.parse_args()
    try:
        if args.command == "summary":
            out = build_training_summary(args.days, force=args.force)
        elif args.command == "events":
            out = get_events()
        elif args.command == "athlete":
            out = get_athlete()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    json.dump(out, sys.stdout, indent=2, default=str)
    print()


if __name__ == "__main__":
    main()
