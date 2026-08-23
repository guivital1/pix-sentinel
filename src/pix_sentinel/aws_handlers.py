from __future__ import annotations

import json
import os
from datetime import UTC, datetime

from .generator import generate_transactions
from .models import Transaction
from .scoring import score_transaction


def producer_handler(event: dict, context: object) -> dict[str, int]:
    """Generate a small synthetic batch and publish it to SQS."""
    import boto3

    queue_url = os.environ["QUEUE_URL"]
    batch_size = min(int(os.environ.get("BATCH_SIZE", "25")), 100)
    seed = int(datetime.now(UTC).timestamp())
    records = generate_transactions(batch_size, seed)
    client = boto3.client("sqs")
    failed = 0
    for start in range(0, len(records), 10):
        chunk = records[start : start + 10]
        response = client.send_message_batch(
            QueueUrl=queue_url,
            Entries=[
                {
                    "Id": str(start + index),
                    "MessageBody": json.dumps(item.to_dict(), separators=(",", ":")),
                }
                for index, item in enumerate(chunk)
            ],
        )
        failed += len(response.get("Failed", []))
    return {"published": batch_size - failed, "failed": failed}


def consumer_handler(event: dict, context: object) -> dict[str, object]:
    """Score SQS records and store an immutable JSONL micro-batch in S3."""
    import boto3

    scored: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []
    for record in event.get("Records", []):
        try:
            payload = json.loads(record["body"])
            transaction = Transaction(**payload)
            scored.append(score_transaction(transaction).to_dict())
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            failures.append({"itemIdentifier": record.get("messageId", "unknown")})

    if not scored:
        return {"processed": 0, "alerts": 0, "batchItemFailures": failures}

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
        "batchItemFailures": failures,
    }
