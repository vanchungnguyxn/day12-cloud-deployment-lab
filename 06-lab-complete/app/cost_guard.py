"""Redis-backed monthly cost guard."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException

from app.config import settings
from app.storage import get_redis


def estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    # Approximate gpt-4o-mini style pricing for lab/demo purposes.
    input_cost = (input_tokens / 1000) * 0.00015
    output_cost = (output_tokens / 1000) * 0.00060
    return round(input_cost + output_cost, 8)


def monthly_cost_key(user_id: str) -> str:
    month_key = datetime.now(timezone.utc).strftime("%Y-%m")
    safe_user = user_id.replace(":", "_")[:80]
    return f"cost:{safe_user}:{month_key}"


def check_and_record_cost(user_id: str, cost_usd: float) -> float:
    key = monthly_cost_key(user_id)
    r = get_redis()

    current = float(r.get(key) or 0.0)
    if current + cost_usd > settings.monthly_budget_usd:
        raise HTTPException(
            status_code=402,
            detail=(
                f"Monthly budget exceeded for user '{user_id}'. "
                f"Limit=${settings.monthly_budget_usd:.2f}, current=${current:.6f}, requested=${cost_usd:.6f}"
            ),
        )

    new_total = float(r.incrbyfloat(key, cost_usd))
    r.expire(key, 32 * 24 * 3600)
    return new_total


def get_monthly_cost(user_id: str) -> float:
    return float(get_redis().get(monthly_cost_key(user_id)) or 0.0)
