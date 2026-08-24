"""Deterministic local throughput benchmark for PIX scoring micro-batches."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from statistics import mean

from pix_sentinel.generator import generate_transactions
from pix_sentinel.pipeline import score_batch


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    index = min(round((len(ordered) - 1) * quantile), len(ordered) - 1)
    return ordered[index]


def benchmark(count: int, batch_size: int, seed: int) -> dict[str, float | int]:
    transactions = generate_transactions(count=count, seed=seed)
    latencies_ms: list[float] = []
    started = time.perf_counter()
    for offset in range(0, len(transactions), batch_size):
        batch_started = time.perf_counter()
        score_batch(transactions[offset : offset + batch_size])
        latencies_ms.append((time.perf_counter() - batch_started) * 1000)
    elapsed = time.perf_counter() - started
    return {
        "events": count,
        "batch_size": batch_size,
        "batches": len(latencies_ms),
        "elapsed_seconds": round(elapsed, 6),
        "events_per_second": round(count / elapsed, 1),
        "batch_latency_mean_ms": round(mean(latencies_ms), 4),
        "batch_latency_p50_ms": round(percentile(latencies_ms, 0.50), 4),
        "batch_latency_p95_ms": round(percentile(latencies_ms, 0.95), 4),
        "batch_latency_p99_ms": round(percentile(latencies_ms, 0.99), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.count < 1 or args.batch_size < 1:
        parser.error("count and batch-size must be positive")
    result = benchmark(args.count, args.batch_size, args.seed)
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
