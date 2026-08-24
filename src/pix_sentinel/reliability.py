"""Schema evolution and idempotency helpers for event processing."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .models import Transaction

SCHEMA_VERSION = 1
EVENT_TYPE = "pix.transaction"


class EventSchemaError(ValueError):
    """Raised when an event cannot be safely interpreted."""


@dataclass(frozen=True)
class DeduplicationResult:
    unique: tuple[Transaction, ...]
    duplicate_ids: tuple[str, ...]


def event_envelope(transaction: Transaction) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "event_type": EVENT_TYPE,
        "event_id": transaction.transaction_id,
        "payload": transaction.to_dict(),
    }


def parse_event(payload: dict[str, Any]) -> Transaction:
    """Parse versioned events while retaining compatibility with v0 raw payloads."""

    if "schema_version" not in payload:
        return Transaction(**payload)
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise EventSchemaError(f"unsupported schema version: {payload.get('schema_version')!r}")
    if payload.get("event_type") != EVENT_TYPE:
        raise EventSchemaError(f"unsupported event type: {payload.get('event_type')!r}")
    body = payload.get("payload")
    if not isinstance(body, dict):
        raise EventSchemaError("event payload must be an object")
    transaction = Transaction(**body)
    if payload.get("event_id") != transaction.transaction_id:
        raise EventSchemaError("event_id must match transaction_id")
    return transaction


def deduplicate(transactions: Iterable[Transaction]) -> DeduplicationResult:
    seen: set[str] = set()
    unique: list[Transaction] = []
    duplicate_ids: list[str] = []
    for transaction in transactions:
        if transaction.transaction_id in seen:
            duplicate_ids.append(transaction.transaction_id)
            continue
        seen.add(transaction.transaction_id)
        unique.append(transaction)
    return DeduplicationResult(tuple(unique), tuple(duplicate_ids))
