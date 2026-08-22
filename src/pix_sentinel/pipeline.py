from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from statistics import mean

from .models import ScoredTransaction, Transaction
from .scoring import score_transaction


def score_batch(transactions: Iterable[Transaction]) -> list[ScoredTransaction]:
    return [score_transaction(transaction) for transaction in transactions]


def build_dashboard_payload(scored: list[ScoredTransaction]) -> dict[str, object]:
    if not scored:
        raise ValueError("at least one scored transaction is required")

    levels = Counter(item.risk_level for item in scored)
    reasons = Counter(reason for item in scored for reason in item.reasons)
    city_totals: dict[str, dict[str, float | int]] = {}
    for item in scored:
        city = item.transaction.city
        metrics = city_totals.setdefault(city, {"transactions": 0, "volume_brl": 0.0, "alerts": 0})
        metrics["transactions"] = int(metrics["transactions"]) + 1
        metrics["volume_brl"] = round(float(metrics["volume_brl"]) + item.transaction.amount_brl, 2)
        if item.risk_score >= 45:
            metrics["alerts"] = int(metrics["alerts"]) + 1

    alerts = sorted((item for item in scored if item.risk_score >= 45), key=lambda item: item.risk_score, reverse=True)
    return {
        "generated_at": max(item.transaction.occurred_at for item in scored),
        "summary": {
            "transactions": len(scored),
            "volume_brl": round(sum(item.transaction.amount_brl for item in scored), 2),
            "alerts": len(alerts),
            "average_risk": round(mean(item.risk_score for item in scored), 1),
        },
        "risk_distribution": {level: levels.get(level, 0) for level in ("low", "medium", "high", "critical")},
        "top_reasons": [{"reason": reason, "count": count} for reason, count in reasons.most_common(5)],
        "cities": [{"city": city, **metrics} for city, metrics in sorted(city_totals.items())],
        "alerts": [item.to_dict() for item in alerts[:12]],
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_local_pipeline(count: int, seed: int, output: Path) -> dict[str, object]:
    from .generator import generate_transactions

    transactions = generate_transactions(count=count, seed=seed)
    scored = score_batch(transactions)
    payload = build_dashboard_payload(scored)
    write_json(output, payload)
    return payload

