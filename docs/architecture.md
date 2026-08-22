# Architecture

## Event path

1. The producer generates a maximum of 25 synthetic transactions per scheduled invocation.
2. Kinesis partitions events by the synthetic sender ID and retains them for 24 hours.
3. The consumer receives micro-batches, validates the contract, calculates the risk score, and preserves the contributing reasons.
4. S3 stores newline-delimited JSON in Hive-style hourly partitions.
5. Athena exposes the event history for SQL analysis and portfolio evidence.
6. The public dashboard uses a sanitized, deterministic snapshot committed under `docs/data`.

## Why two execution modes?

The local mode is free, immediate, and reproducible. The AWS mode proves managed streaming integration during controlled demonstrations. Separating them prevents the public portfolio from depending on a continuously running paid stream.

## Risk levels

| Score | Level | Intended action |
| ---: | --- | --- |
| 0–24 | Low | Accept into the analytical history |
| 25–44 | Medium | Monitor |
| 45–69 | High | Add to the review queue |
| 70–100 | Critical | Prioritize for simulated investigation |

The weights are transparent heuristics for learning purposes. A production system would combine supervised or anomaly-detection models, model monitoring, feedback labels, bias review, and human decision controls.

