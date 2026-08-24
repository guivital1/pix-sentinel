import json
from types import SimpleNamespace

import boto3

from pix_sentinel.aws_handlers import consumer_handler, producer_handler
from pix_sentinel.generator import generate_transactions


class FakeSqs:
    def __init__(self) -> None:
        self.batches: list[list[dict[str, str]]] = []

    def send_message_batch(self, *, QueueUrl: str, Entries: list[dict[str, str]]) -> dict:
        assert QueueUrl == "https://sqs.example/test"
        self.batches.append(Entries)
        return {"Successful": Entries, "Failed": []}


class FakeS3:
    def __init__(self) -> None:
        self.objects: list[dict] = []

    def put_object(self, **kwargs: object) -> None:
        self.objects.append(kwargs)


def test_producer_respects_sqs_batch_limit(monkeypatch) -> None:
    sqs = FakeSqs()
    monkeypatch.setenv("QUEUE_URL", "https://sqs.example/test")
    monkeypatch.setenv("BATCH_SIZE", "25")
    monkeypatch.setattr(boto3, "client", lambda service: sqs)

    result = producer_handler({}, object())

    assert result == {"published": 25, "failed": 0}
    assert [len(batch) for batch in sqs.batches] == [10, 10, 5]
    first_event = json.loads(sqs.batches[0][0]["MessageBody"])
    assert first_event["schema_version"] == 1
    assert first_event["event_type"] == "pix.transaction"


def test_consumer_scores_valid_records_and_reports_invalid_ones(monkeypatch) -> None:
    s3 = FakeS3()
    transaction = generate_transactions(1, seed=5)[0]
    monkeypatch.setenv("DATA_BUCKET", "pix-sentinel-test")
    monkeypatch.setattr(boto3, "client", lambda service: s3)
    event = {
        "Records": [
            {"messageId": "valid", "body": json.dumps(transaction.to_dict())},
            {"messageId": "invalid", "body": "not-json"},
        ]
    }

    result = consumer_handler(event, SimpleNamespace(aws_request_id="request-1"))

    assert result["processed"] == 1
    assert result["batchItemFailures"] == [{"itemIdentifier": "invalid"}]
    assert len(s3.objects) == 1
    assert s3.objects[0]["Bucket"] == "pix-sentinel-test"
    assert "silver/year=" in str(s3.objects[0]["Key"])


def test_consumer_deduplicates_same_transaction_within_micro_batch(monkeypatch) -> None:
    s3 = FakeS3()
    transaction = generate_transactions(1, seed=8)[0]
    monkeypatch.setenv("DATA_BUCKET", "pix-sentinel-test")
    monkeypatch.setattr(boto3, "client", lambda service: s3)
    body = json.dumps(transaction.to_dict())

    result = consumer_handler(
        {"Records": [{"messageId": "one", "body": body}, {"messageId": "two", "body": body}]},
        SimpleNamespace(aws_request_id="request-2"),
    )

    assert result["processed"] == 1
    assert result["duplicates"] == 1
    assert len(s3.objects) == 1
