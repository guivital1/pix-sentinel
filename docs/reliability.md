# Reliability and replay

PIX Sentinel treats failures as part of the design rather than an exceptional
demo condition.

## Event contract

New events use a versioned envelope with `schema_version`, `event_type`,
`event_id` and `payload`. The consumer remains compatible with the original raw
transaction format, rejects unknown versions and returns the failed SQS message
identifier for partial-batch retry.

## Idempotency boundary

The consumer removes duplicate transaction IDs inside each Lambda micro-batch.
Production systems should extend this boundary with a TTL-backed DynamoDB key
store when the same event can be delivered across separate batches. The current
scope deliberately demonstrates the contract without creating a persistent
database for a synthetic, short-lived environment.

## Failure path

1. Invalid or unsupported events are returned through `batchItemFailures`.
2. SQS retries the individual event up to three receives.
3. Exhausted messages move to the encrypted dead-letter queue.
4. The DLQ CloudWatch alarm triggers when a message becomes visible.
5. `scripts/replay_dlq.py` performs bounded replay and requires `--execute`.

## Operational signals

The CloudWatch dashboard and alarms expose Lambda errors and duration, queue
depth, age of the oldest event and DLQ visibility. The controlled environment
keeps event generation disabled by default.

## Benchmark

`make benchmark` scores 10,000 deterministic transactions in micro-batches and
reports throughput plus mean, p50, p95 and p99 batch latency. This is a local
CPU benchmark, not a claim about AWS network or end-to-end production latency.
