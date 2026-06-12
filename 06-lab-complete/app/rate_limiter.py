"""Redis-backed sliding-window rate limiter."""
from __future__ import annotations

import time
import uuid

from fastapi import HTTPException

from app.config import settings
from app.storage import get_redis


def check_rate_limit(user_id: str) -> None:
    now_ms = int(time.time() * 1000)
    window_start = now_ms - 60_000
    key = f"rate:{user_id}"
    member = f"{now_ms}:{uuid.uuid4().hex}"

    r = get_redis()
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zcard(key)
    _, current_count = pipe.execute()

    if int(current_count) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min per user",
            headers={"Retry-After": "60"},
        )

    pipe = r.pipeline()
    pipe.zadd(key, {member: now_ms})
    pipe.expire(key, 120)
    pipe.execute()
