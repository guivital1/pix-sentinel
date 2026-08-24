from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_local_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the PIX Sentinel local simulation")
    parser.add_argument("--count", type=int, default=500, help="number of synthetic transactions")
    parser.add_argument("--seed", type=int, default=42, help="deterministic random seed")
    parser.add_argument("--output", type=Path, default=Path("docs/data/dashboard.json"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = run_local_pipeline(args.count, args.seed, args.output)
    summary = payload["summary"]
    print(
        f"Processed {summary['transactions']} synthetic transactions · "
        f"{summary['alerts']} alerts · dashboard data: {args.output}"
    )


if __name__ == "__main__":
    main()
