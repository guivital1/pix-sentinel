from __future__ import annotations

from .models import ScoredTransaction, Transaction


def score_transaction(transaction: Transaction) -> ScoredTransaction:
    """Apply an explainable risk model whose weights total at most 100 points."""
    score = 0
    reasons: list[str] = []

    if transaction.amount_brl >= 10_000:
        score += 35
        reasons.append("very_high_amount")
    elif transaction.amount_brl >= 4_000:
        score += 22
        reasons.append("high_amount")

    if transaction.transactions_last_hour >= 12:
        score += 30
        reasons.append("extreme_velocity")
    elif transaction.transactions_last_hour >= 7:
        score += 20
        reasons.append("high_velocity")

    if transaction.is_new_device:
        score += 18
        reasons.append("new_device")

    if transaction.account_age_days < 30:
        score += 12
        reasons.append("new_account")

    if transaction.hour < 5:
        score += 10
        reasons.append("unusual_hour")

    score = min(score, 100)
    level = (
        "critical" if score >= 70 else "high" if score >= 45 else "medium" if score >= 25 else "low"
    )
    return ScoredTransaction(transaction, score, level, tuple(reasons))
