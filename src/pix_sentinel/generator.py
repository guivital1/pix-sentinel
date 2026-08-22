from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime, timedelta

from .models import Transaction

CITIES = ("Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Recife")


def generate_transactions(count: int = 500, seed: int = 42) -> list[Transaction]:
    """Generate deterministic, entirely synthetic PIX-like transactions."""
    if count < 1:
        raise ValueError("count must be greater than zero")

    rng = random.Random(seed)
    start = datetime(2026, 8, 21, 8, tzinfo=UTC)
    transactions: list[Transaction] = []

    for index in range(count):
        scenario = rng.random()
        suspicious = scenario < 0.075
        watchlist = 0.075 <= scenario < 0.16
        sender_number = rng.randint(1, 80)
        occurred_at = start + timedelta(seconds=index * 21 + rng.randint(0, 15))

        if suspicious:
            amount = round(rng.uniform(4_500, 19_000), 2)
            new_device = rng.random() < 0.82
            velocity = rng.randint(8, 22)
            account_age = rng.randint(1, 45)
            if rng.random() < 0.45:
                occurred_at = occurred_at.replace(hour=rng.choice((0, 1, 2, 3, 4)))
        elif watchlist:
            amount = round(rng.uniform(900, 6_500), 2)
            new_device = rng.random() < 0.45
            velocity = rng.randint(3, 9)
            account_age = rng.randint(20, 350)
            if rng.random() < 0.15:
                occurred_at = occurred_at.replace(hour=rng.choice((0, 1, 2, 3, 4)))
        else:
            amount = round(min(rng.lognormvariate(4.7, 0.85), 3_800), 2)
            new_device = rng.random() < 0.06
            velocity = rng.randint(0, 5)
            account_age = rng.randint(60, 2_500)

        transactions.append(
            Transaction(
                transaction_id=f"pix_{uuid.UUID(int=rng.getrandbits(128)).hex[:16]}",
                occurred_at=occurred_at.isoformat().replace("+00:00", "Z"),
                sender_id=f"acct_{sender_number:04d}",
                receiver_id=f"acct_{rng.randint(81, 260):04d}",
                amount_brl=amount,
                device_id=f"dev_{rng.randint(1, 180):04d}",
                city=rng.choice(CITIES),
                account_age_days=account_age,
                transactions_last_hour=velocity,
                is_new_device=new_device,
            )
        )

    return transactions
