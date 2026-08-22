from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    occurred_at: str
    sender_id: str
    receiver_id: str
    amount_brl: float
    device_id: str
    city: str
    account_age_days: int
    transactions_last_hour: int
    is_new_device: bool

    @property
    def hour(self) -> int:
        return datetime.fromisoformat(self.occurred_at).hour

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScoredTransaction:
    transaction: Transaction
    risk_score: int
    risk_level: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.transaction.to_dict(),
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "reasons": list(self.reasons),
        }
