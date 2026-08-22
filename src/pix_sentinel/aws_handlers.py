from __future__ import annotations

import base64
import json
import os
from datetime import UTC, datetime

from .generator import generate_transactions
from .models import Transaction
from .scoring import score_transaction


def producer_handler(event: dict, context: object) -> dict[str, int]:
    """Generate a small synthetic batch and publish it to Kinesis."""
    import boto3

    stream_name = os.environ["STREAM_NAME"]
    batch_size = min(int(os.environ.get("BATCH_SIZE", "25")), 100)
    seed = int(datetime.now(UTC).timestamp())
    records = generate_transactions(batch_size, seed)
    client = boto3.client("kinesis")
    response = client.put_records(
        StreamName=stream_name,
        Records=[
            {
                "Data": (json.dumps(item.to_dict(), separators=(",", ":")) + "\n").encode(),
                "PartitionKey": item.sender_id,
            }
            for item in records
        ],
    )
    return {"published": batch_size, "failed": response.get("FailedRecordCount", 0)}


def consumer_handler(event: dict, context: object) -> dict[str, int]:
    """Score Kinesis records and store an immutable JSONL micro-batch in S3."""
    import boto3

    scored: list[dict[str, object]] = []
    for record in event.get("Records", []):
        raw = base64.b64decode(record["kinesis"]["data"]).decode().strip()
        payload = json.loads(raw)
        transaction = Transaction(**payload)
        scored.append(score_transaction(transaction).to_dict())

    if not scored:
        return {"processed": 0, "alerts": 0}

    bucket_name = os.environ["DATA_BUCKET"]
    now = datetime.now(UTC)
    request_id = getattr(context, "aws_request_id", "local")
    key = now.strftime(f"silver/year=%Y/month=%m/day=%d/hour=%H/{request_id}.jsonl")
    body = "".join(json.dumps(item, separators=(",", ":")) + "\n" for item in scored)
    boto3.client("s3").put_object(
        Bucket=bucket_name,
        Key=key,
        Body=body.encode(),
        ContentType="application/x-ndjson",
        ServerSideEncryption="AES256",
    )
    return {
        "processed": len(scored),
        "alerts": sum(int(item["risk_score"]) >= 45 for item in scored),
    }

