"""Safely replay messages from the project DLQ into the transaction queue."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--destination-url", required=True)
    parser.add_argument("--max-messages", type=int, default=10)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.max_messages <= 100:
        parser.error("max-messages must be between 1 and 100")
    if not args.execute:
        print("Dry run only. Add --execute to move messages from the DLQ.")
        return

    import boto3

    sqs = boto3.client("sqs")
    moved = 0
    while moved < args.max_messages:
        response = sqs.receive_message(
            QueueUrl=args.source_url,
            MaxNumberOfMessages=min(10, args.max_messages - moved),
            WaitTimeSeconds=1,
            VisibilityTimeout=30,
        )
        messages = response.get("Messages", [])
        if not messages:
            break
        for message in messages:
            sqs.send_message(QueueUrl=args.destination_url, MessageBody=message["Body"])
            sqs.delete_message(QueueUrl=args.source_url, ReceiptHandle=message["ReceiptHandle"])
            moved += 1
    print(f"Replayed {moved} message(s)")


if __name__ == "__main__":
    main()
