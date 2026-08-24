import pytest

from pix_sentinel.generator import generate_transactions
from pix_sentinel.reliability import EventSchemaError, deduplicate, event_envelope, parse_event


def test_versioned_event_round_trip() -> None:
    transaction = generate_transactions(1, seed=11)[0]
    assert parse_event(event_envelope(transaction)) == transaction


def test_unknown_schema_is_rejected_for_dlq_handling() -> None:
    transaction = generate_transactions(1, seed=11)[0]
    event = event_envelope(transaction)
    event["schema_version"] = 99
    with pytest.raises(EventSchemaError, match="unsupported schema"):
        parse_event(event)


def test_duplicate_transaction_id_is_removed_deterministically() -> None:
    transaction = generate_transactions(1, seed=11)[0]
    result = deduplicate([transaction, transaction])
    assert result.unique == (transaction,)
    assert result.duplicate_ids == (transaction.transaction_id,)
