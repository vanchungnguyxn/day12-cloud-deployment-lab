"""Redis storage helpers.

All shared state lives in Redis so the app stays stateless across multiple workers/instances.
"""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

import redis

from app.config import settings


@lru_cache(maxsize=1)
def get_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def ping_redis() -> bool:
    return bool(get_redis().ping())


def history_key(user_id: str, conversation_id: str = "default") -> str:
    safe_user = user_id.replace(":", "_")[:80]
    safe_conv = conversation_id.replace(":", "_")[:80]
    return f"history:{safe_user}:{safe_conv}"


def get_history(user_id: str, conversation_id: str = "default", limit: int = 6) -> list[dict[str, Any]]:
    raw_items = get_redis().lrange(history_key(user_id, conversation_id), -limit, -1)
    history: list[dict[str, Any]] = []
    for item in raw_items:
        try:
            history.append(json.loads(item))
        except json.JSONDecodeError:
            continue
    return history


def save_turn(user_id: str, question: str, answer: str, conversation_id: str = "default") -> None:
    key = history_key(user_id, conversation_id)
    item = json.dumps({"question": question, "answer": answer}, ensure_ascii=False)
    r = get_redis()
    r.rpush(key, item)
    r.ltrim(key, -20, -1)  # keep the last 20 turns only
    r.expire(key, 7 * 24 * 3600)
