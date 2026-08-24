from pix_sentinel.models import Transaction
from pix_sentinel.scoring import score_transaction


def transaction(**overrides: object) -> Transaction:
    payload: dict[str, object] = {
        "transaction_id": "pix_test",
        "occurred_at": "2026-08-21T12:00:00Z",
        "sender_id": "acct_0001",
        "receiver_id": "acct_0081",
        "amount_brl": 120.0,
        "device_id": "dev_0001",
        "city": "Sao Paulo",
        "account_age_days": 500,
        "transactions_last_hour": 1,
        "is_new_device": False,
    }
    payload.update(overrides)
    return Transaction(**payload)  # type: ignore[arg-type]


def test_normal_transaction_is_low_risk() -> None:
    result = score_transaction(transaction())
    assert result.risk_score == 0
    assert result.risk_level == "low"
    assert result.reasons == ()


def test_suspicious_transaction_is_explainable() -> None:
    result = score_transaction(
        transaction(
            occurred_at="2026-08-21T02:00:00Z",
            amount_brl=15_000,
            account_age_days=5,
            transactions_last_hour=15,
            is_new_device=True,
        )
    )
    assert result.risk_score == 100
    assert result.risk_level == "critical"
    assert set(result.reasons) == {
        "very_high_amount",
        "extreme_velocity",
        "new_device",
        "new_account",
        "unusual_hour",
    }
