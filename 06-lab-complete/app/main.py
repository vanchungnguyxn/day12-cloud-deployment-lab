"""Production AI Agent — Day 12 final app.

Features:
- Environment-based config
- Structured JSON logging
- API key authentication
- Redis-backed rate limiting: 10 req/min per user
- Redis-backed monthly cost guard: $10/month per user
- Redis-backed conversation history
- Health/readiness probes
- Graceful shutdown awareness
- Security headers and CORS
"""
from __future__ import annotations

import json
import logging
import signal
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import check_and_record_cost, estimate_cost_usd, get_monthly_cost
from app.rate_limiter import check_rate_limit
from app.storage import get_history, get_redis, ping_redis, save_turn
from utils.mock_llm import ask as llm_ask

logging.basicConfig(
    level=logging.DEBUG if settings.debug else getattr(logging, settings.log_level.upper(), logging.INFO),
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False
_is_shutting_down = False


def _handle_sigterm(signum, frame):  # noqa: ARG001
    global _is_shutting_down, _is_ready
    _is_shutting_down = True
    _is_ready = False
    logger.info(json.dumps({"event": "SIGTERM_received", "message": "Graceful shutdown started"}))


signal.signal(signal.SIGTERM, _handle_sigterm)
signal.signal(signal.SIGINT, _handle_sigterm)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    global _is_ready
    logger.info(json.dumps({
        "event": "startup",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }))
    ping_redis()
    _is_ready = True
    logger.info(json.dumps({"event": "ready", "redis": "ok"}))
    yield
    _is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start_time = time.time()
    r = get_redis()

    try:
        response = await call_next(request)
    except Exception:
        r.incr("metrics:error_count")
        logger.exception(json.dumps({
            "event": "request_error",
            "method": request.method,
            "path": request.url.path,
        }))
        raise
    finally:
        r.incr("metrics:total_requests")

    duration = time.time() - start_time
    logger.info(json.dumps({
        "event": "request",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
    }))

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    user_id: str = Field(default="demo-user", min_length=1, max_length=80)
    conversation_id: str = Field(default="default", min_length=1, max_length=80)


class AskResponse(BaseModel):
    question: str
    answer: str
    user_id: str
    conversation_id: str
    model: str | None = None
    usage: dict = {}
    cost_usd: float
    monthly_cost_usd: float
    history_turns_used: int
    timestamp: str


@app.get("/", tags=["Info"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "endpoints": {
            "ask": "POST /ask (requires X-API-Key)",
            "health": "GET /health",
            "ready": "GET /ready",
            "metrics": "GET /metrics (requires X-API-Key)",
        },
    }


@app.post("/ask", response_model=AskResponse, tags=["Agent"])
def ask_agent(body: AskRequest, request: Request, _api_key: str = Depends(verify_api_key)):
    if _is_shutting_down:
        raise HTTPException(status_code=503, detail="Server is shutting down")

    user_id = body.user_id.strip()
    check_rate_limit(user_id)

    history = get_history(user_id, body.conversation_id, limit=6)
    context = "\n".join(
        f"User: {item.get('question', '')}\nAssistant: {item.get('answer', '')}"
        for item in history
    )
    prompt = f"Previous conversation:\n{context}\n\nCurrent question: {body.question}" if context else body.question

    logger.info(json.dumps({
        "event": "agent_call",
        "user_id": user_id,
        "conversation_id": body.conversation_id,
        "q_len": len(body.question),
        "client": str(request.client.host) if request.client else "unknown",
    }))

    answer = llm_ask(prompt)
    input_tokens = max(1, len(prompt.split()) * 2)
    output_tokens = max(1, len(answer.split()) * 2)
    cost_usd = estimate_cost_usd(input_tokens, output_tokens)
    monthly_cost = check_and_record_cost(user_id, cost_usd)
    save_turn(user_id, body.question, answer, body.conversation_id)

    return AskResponse(
        question=body.question,
        answer=answer,
        user_id=user_id,
        conversation_id=body.conversation_id,
        model=settings.llm_model,
        usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
        cost_usd=cost_usd,
        monthly_cost_usd=round(monthly_cost, 8),
        history_turns_used=len(history),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/health", tags=["Operations"])
def health():
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "shutting_down": _is_shutting_down,
        "checks": {"process": "ok", "llm": "mock" if not settings.openai_api_key else "openai"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready", tags=["Operations"])
def ready():
    if not _is_ready or _is_shutting_down:
        raise HTTPException(status_code=503, detail="Not ready")
    try:
        ping_redis()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Redis not ready: {exc}") from exc
    return {"ready": True, "redis": "ok"}


@app.get("/metrics", tags=["Operations"])
def metrics(user_id: str = "demo-user", _api_key: str = Depends(verify_api_key)):
    r = get_redis()
    total_requests = int(r.get("metrics:total_requests") or 0)
    error_count = int(r.get("metrics:error_count") or 0)
    monthly_cost = get_monthly_cost(user_id)
    return {
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": total_requests,
        "error_count": error_count,
        "monthly_cost_usd": round(monthly_cost, 8),
        "monthly_budget_usd": settings.monthly_budget_usd,
        "budget_used_pct": round(monthly_cost / settings.monthly_budget_usd * 100, 4),
    }
