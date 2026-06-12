# Day 12 — Cloud Infrastructure & Deployment Lab

**Student:** Nguyen Van Chung  
**Student ID:** 2A202600647  
**Course:** AI20K  
**Lab:** Day 12 — Cloud Infrastructure and Deployment  
**Final Public URL:** `https://day12-cloud-deployment-lab.onrender.com`

---

## 1. Project Overview

This repository contains the complete Day 12 lab implementation for building, containerizing, securing, scaling, and deploying an AI agent application.

The lab starts from a simple localhost-only FastAPI agent and gradually improves it into a production-ready cloud-deployed agent with Docker, API security, Redis-backed stateless design, health checks, readiness checks, rate limiting, cost guard, structured logging, and Render deployment.

The final production-ready implementation is located in:

```text
06-lab-complete/
```

---

## 2. Final Result Summary

The final app satisfies the main Part 6 requirements:

| Requirement | Status | Evidence |
|---|---:|---|
| REST API agent response | ✅ Done | `POST /ask` |
| Conversation history | ✅ Done | Redis-backed history, `history_turns_used` |
| Streaming responses | Optional | Not required by rubric |
| Multi-stage Docker build | ✅ Done | `06-lab-complete/Dockerfile` |
| Config from environment variables | ✅ Done | `app/config.py`, Render env vars |
| API key authentication | ✅ Done | `X-API-Key` required |
| Rate limit: 10 req/min/user | ✅ Done | Redis sliding window, 429 after limit |
| Cost guard: $10/month/user | ✅ Done | Redis monthly budget tracker |
| Health check | ✅ Done | `GET /health` |
| Readiness check | ✅ Done | `GET /ready`, Redis ping |
| Graceful shutdown | ✅ Done | SIGTERM/SIGINT handling |
| Stateless design | ✅ Done | State stored in Redis |
| Structured JSON logging | ✅ Done | JSON log format |
| Cloud deployment | ✅ Done | Render |
| Public URL works | ✅ Done | `https://day12-cloud-deployment-lab.onrender.com` |
| Production readiness check | ✅ Done | `20/20 checks passed` |

---

## 3. Repository Structure

```text
.
├── 01-localhost-vs-production/
│   ├── develop/                 # Localhost/dev anti-pattern version
│   └── production/              # 12-factor style production version
│
├── 02-docker/
│   ├── develop/                 # Basic Dockerfile example
│   └── production/              # Multi-service Docker Compose stack
│
├── 03-cloud-deployment/
│   ├── railway/                 # Railway deployment attempt
│   ├── render/                  # Render deployment config
│   └── production-cloud-run/    # Cloud Run reference configuration
│
├── 04-api-gateway/
│   ├── develop/                 # API key authentication example
│   └── production/              # JWT/rate-limit/cost-guard security stack
│
├── 05-scaling-reliability/
│   ├── develop/                 # Health check + graceful shutdown
│   └── production/              # Redis stateless design + Nginx scaling demo
│
├── 06-lab-complete/             # Final production-ready AI agent
│   ├── app/
│   │   ├── main.py              # FastAPI app and endpoints
│   │   ├── config.py            # Environment-based config
│   │   ├── auth.py              # API key authentication
│   │   ├── rate_limiter.py      # Redis-backed 10 req/min/user limit
│   │   ├── cost_guard.py        # Redis-backed monthly cost guard
│   │   └── storage.py           # Redis helpers and conversation history
│   ├── utils/
│   │   └── mock_llm.py          # Mock LLM fallback
│   ├── Dockerfile               # Multi-stage production Dockerfile
│   ├── docker-compose.yml       # Local Docker Compose stack
│   ├── render.yaml              # Render deployment config
│   ├── railway.toml             # Railway deployment config
│   ├── requirements.txt
│   ├── .env.example
│   ├── .dockerignore
│   ├── check_production_ready.py
│   └── README.md
│
├── screenshots/                 # Evidence screenshots
├── DAY12_DELIVERY_CHECKLIST.md  # Submission checklist
├── DEPLOYMENT.md                # Deployment evidence and public URL tests
└── MISSION_ANSWERS.md           # Lab answers and reflections
```

---

## 4. Learning Path by Section

### Part 1 — Localhost vs Production

Folder:

```text
01-localhost-vs-production/
```

This section compares a development-only agent with a production-oriented version.

The `develop/` version intentionally contains anti-patterns such as:

- Hardcoded API keys
- Debug logs exposing sensitive values
- Localhost-only configuration
- No health check endpoint
- No graceful shutdown
- No environment-based config

The `production/` version improves the app by adding:

- Environment variable configuration
- `0.0.0.0` host binding
- Health check endpoint
- Safer logging
- Mock LLM fallback when `OPENAI_API_KEY` is not set

Run example:

```bash
cd 01-localhost-vs-production/production
python app.py
```

Test:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

---

### Part 2 — Docker

Folder:

```text
02-docker/
```

This section demonstrates the difference between a basic Docker image and an optimized production Docker image.

Key concepts:

- Single-stage vs multi-stage Docker builds
- Smaller production image size
- `.dockerignore`
- Docker Compose
- Nginx reverse proxy
- Redis/Qdrant service dependencies

Build develop image:

```bash
docker build -f 02-docker/develop/Dockerfile -t day12-agent-develop .
```

Run production stack:

```bash
cd 02-docker/production
docker compose up --build
```

Test through Nginx:

```powershell
Invoke-RestMethod -Uri "http://localhost/health" -Method GET
```

---

### Part 3 — Cloud Deployment

Folder:

```text
03-cloud-deployment/
```

This section explores cloud deployment options:

| Platform | Purpose |
|---|---|
| Railway | Simple MVP deployment |
| Render | Simple GitHub-connected deployment |
| Google Cloud Run | Production-grade serverless container deployment |

Railway was attempted first, but the workspace was restricted. Render was then used successfully.

Final public deployment:

```text
https://day12-cloud-deployment-lab.onrender.com
```

---

### Part 4 — API Gateway & Security

Folder:

```text
04-api-gateway/
```

This section implements API security concepts:

- API key authentication
- JWT authentication
- Rate limiting
- Cost guard
- Request protection before calling the agent

Security request flow:

```text
Request
  → Auth check
  → Rate limit check
  → Cost guard check
  → Agent response
```

Expected behavior:

- Missing/invalid key returns `401`
- Too many requests returns `429`
- Budget exhaustion returns `402` or a budget-related error

---

### Part 5 — Scaling & Reliability

Folder:

```text
05-scaling-reliability/
```

This section focuses on production reliability:

- Health checks
- Readiness checks
- Graceful shutdown
- Stateless design
- Redis-backed shared state
- Horizontal scaling behind Nginx

Scaling concept:

```text
Client → Nginx Load Balancer → Agent Instance 1
                            → Agent Instance 2
                            → Agent Instance 3
                                  ↕
                                Redis
```

The key lesson is that user/session state must not be stored in local memory when an application is scaled to multiple instances. Redis is used as shared state so any instance can serve any request.

---

### Part 6 — Final Production-Ready Agent

Folder:

```text
06-lab-complete/
```

This is the final integrated production agent.

It combines all Day 12 concepts:

- FastAPI REST API
- Dockerized deployment
- Multi-stage Dockerfile
- Environment-based configuration
- API key authentication
- Redis-backed rate limiting
- Redis-backed monthly cost guard
- Redis-backed conversation history
- Health endpoint
- Readiness endpoint
- Metrics endpoint
- Structured JSON logging
- Graceful shutdown
- Render deployment

---

## 5. Final App Architecture

```text
Client
  │
  ▼
Render Public URL
  │
  ▼
FastAPI Agent Container
  │
  ├── API key authentication
  ├── Rate limiting: 10 req/min/user
  ├── Cost guard: $10/month/user
  ├── Conversation history
  ├── Health/readiness checks
  └── Structured JSON logging
  │
  ▼
Render Key Value / Redis
  ├── history:{user_id}:{conversation_id}
  ├── rate:{user_id}
  ├── cost:{user_id}:{YYYY-MM}
  └── metrics counters
```

The application is stateless because shared state is stored in Redis. This allows the app to scale horizontally behind a load balancer.

---

## 6. Final App API

### Base URL

Local:

```text
http://localhost:8000
```

Production:

```text
https://day12-cloud-deployment-lab.onrender.com
```

---

### `GET /health`

Liveness probe.

Example:

```powershell
Invoke-RestMethod -Uri "$BASE/health" -Method GET
```

Example response:

```text
status         : ok
version        : 1.0.0
environment    : production
uptime_seconds : 6.3
shutting_down  : False
checks         : @{process=ok; llm=mock}
```

---

### `GET /ready`

Readiness probe. It checks whether the app is ready and whether Redis is reachable.

Example:

```powershell
Invoke-RestMethod -Uri "$BASE/ready" -Method GET
```

Example response:

```text
ready redis
----- -----
 True ok
```

---

### `POST /ask`

Ask the AI agent a question. This endpoint requires an API key.

Required header:

```text
X-API-Key: <your-agent-api-key>
```

Request body:

```json
{
  "user_id": "chung",
  "conversation_id": "render",
  "question": "Hello final Render app"
}
```

PowerShell example:

```powershell
$BASE="https://day12-cloud-deployment-lab.onrender.com"
$KEY="<YOUR_AGENT_API_KEY>"

Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -Headers @{"X-API-Key"=$KEY} `
  -ContentType "application/json" `
  -Body '{"user_id":"chung","conversation_id":"render","question":"Hello final Render app"}'
```

Example response:

```text
question           : Hello final Render app
answer             : Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.
user_id            : chung
conversation_id    : render
model              : gpt-4o-mini
usage              : @{input_tokens=8; output_tokens=26}
cost_usd           : 1.68E-05
monthly_cost_usd   : 1.68E-05
history_turns_used : 0
```

---

### `GET /metrics`

Returns basic operational metrics. This endpoint requires an API key.

Example:

```powershell
Invoke-RestMethod -Uri "$BASE/metrics?user_id=chung" `
  -Method GET `
  -Headers @{"X-API-Key"=$KEY}
```

Example response fields:

```text
uptime_seconds
total_requests
error_count
monthly_cost_usd
monthly_budget_usd
budget_used_pct
```

---

## 7. Run Final App Locally

### Prerequisites

- Docker Desktop
- Docker Compose
- Python 3.11+ for running the readiness checker

### Step 1 — Go to final app folder

```powershell
cd 06-lab-complete
```

### Step 2 — Create local environment file

```powershell
copy .env.example .env.local
```

Recommended local `.env.local`:

```env
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

APP_NAME=Chung Day12 Production Agent
APP_VERSION=1.0.0

OPENAI_API_KEY=
LLM_MODEL=gpt-4o-mini

AGENT_API_KEY=chung-day12-secret
JWT_SECRET=chung-jwt-secret-change-me

RATE_LIMIT_PER_MINUTE=10
MONTHLY_BUDGET_USD=10.0

REDIS_URL=redis://redis:6379/0
ALLOWED_ORIGINS=*
```

### Step 3 — Start Docker Compose

```powershell
docker compose down -v
docker compose up --build
```

The stack starts:

- `agent`: FastAPI production agent
- `redis`: Redis state store

---

## 8. Local Test Commands

Open a new PowerShell window:

```powershell
$BASE="http://localhost:8000"
$KEY="chung-day12-secret"
```

### Health

```powershell
Invoke-RestMethod -Uri "$BASE/health" -Method GET
```

### Readiness

```powershell
Invoke-RestMethod -Uri "$BASE/ready" -Method GET
```

### Auth test: missing key should fail

```powershell
Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"hello without key"}'
```

Expected result:

```text
401 Unauthorized
```

### Ask with API key

```powershell
Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -Headers @{"X-API-Key"=$KEY} `
  -ContentType "application/json" `
  -Body '{"user_id":"chung","conversation_id":"lab12","question":"Hello final app"}'
```

### Conversation history test

Run a second request with the same `user_id` and `conversation_id`:

```powershell
Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -Headers @{"X-API-Key"=$KEY} `
  -ContentType "application/json" `
  -Body '{"user_id":"chung","conversation_id":"lab12","question":"Bạn còn nhớ câu trước không?"}'
```

Expected result:

```text
history_turns_used : 1
```

### Rate limit test

```powershell
1..12 | ForEach-Object {
  try {
    Invoke-RestMethod -Uri "$BASE/ask" `
      -Method POST `
      -Headers @{"X-API-Key"=$KEY} `
      -ContentType "application/json" `
      -Body "{`"user_id`":`"rate-test`",`"conversation_id`":`"lab12`",`"question`":`"test $_`"}"
  } catch {
    Write-Host "Request $_ =>" $_.Exception.Response.StatusCode.value__
  }
}
```

Expected result:

```text
Request 11 => 429
Request 12 => 429
```

### Metrics test

```powershell
Invoke-RestMethod -Uri "$BASE/metrics?user_id=chung" `
  -Method GET `
  -Headers @{"X-API-Key"=$KEY}
```

---

## 9. Production Readiness Check

Run:

```powershell
cd 06-lab-complete
python check_production_ready.py
```

Expected result:

```text
Result: 20/20 checks passed (100%)
PRODUCTION READY
```

This script checks:

- Required files
- `.env` ignored by Git
- No hardcoded secrets in code
- Health endpoint defined
- Readiness endpoint defined
- Authentication implemented
- Rate limiting implemented
- Graceful shutdown implemented
- Structured JSON logging
- Multi-stage Docker build
- Non-root Docker user
- Docker healthcheck
- `.dockerignore` coverage

---

## 10. Deploy on Render

### Render setup

1. Push this repository to GitHub.
2. Go to Render Dashboard.
3. Create a new Web Service or Blueprint.
4. Use final app folder:

```text
06-lab-complete
```

5. Runtime:

```text
Docker
```

6. Health check path:

```text
/health
```

7. Create a Render Key Value / Redis service.
8. Copy the Redis Internal URL.
9. Set it as `REDIS_URL` in the Web Service environment variables.

### Required Render environment variables

```env
ENVIRONMENT=production
APP_NAME=day12-agent-chung-final
APP_VERSION=1.0.0
AGENT_API_KEY=<secret>
JWT_SECRET=<secret>
RATE_LIMIT_PER_MINUTE=10
MONTHLY_BUDGET_USD=10.0
REDIS_URL=redis://<render-redis-internal-host>:6379
OPENAI_API_KEY=
LLM_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
ALLOWED_ORIGINS=*
```

Important:

```text
REDIS_URL must start with redis:// or rediss://
```

Wrong examples:

```text
red-xxxxx:6379
<Render Redis Internal URL>
localhost:6379
```

Correct examples:

```text
redis://red-xxxxx:6379
rediss://red-xxxxx:6379
```

---

## 11. Public Render Test Commands

```powershell
$BASE="https://day12-cloud-deployment-lab.onrender.com"
$KEY="<YOUR_AGENT_API_KEY>"
```

### Health

```powershell
Invoke-RestMethod -Uri "$BASE/health" -Method GET
```

Expected:

```text
status : ok
environment : production
```

### Ready

```powershell
Invoke-RestMethod -Uri "$BASE/ready" -Method GET
```

Expected:

```text
ready : True
redis : ok
```

### Missing API key

```powershell
Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"hello without key"}'
```

Expected:

```text
401 Unauthorized
```

### Valid API key

```powershell
Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -Headers @{"X-API-Key"=$KEY} `
  -ContentType "application/json" `
  -Body '{"user_id":"chung","conversation_id":"render","question":"Hello final Render app"}'
```

Expected:

```text
answer returned successfully
```

### Conversation history

```powershell
Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -Headers @{"X-API-Key"=$KEY} `
  -ContentType "application/json" `
  -Body '{"user_id":"chung","conversation_id":"render","question":"Bạn còn nhớ câu trước không?"}'
```

Expected:

```text
history_turns_used : 1
```

### Rate limit

```powershell
1..12 | ForEach-Object {
  try {
    Invoke-RestMethod -Uri "$BASE/ask" `
      -Method POST `
      -Headers @{"X-API-Key"=$KEY} `
      -ContentType "application/json" `
      -Body "{`"user_id`":`"render-rate-test`",`"conversation_id`":`"render`",`"question`":`"test $_`"}"
  } catch {
    Write-Host "Request $_ =>" $_.Exception.Response.StatusCode.value__
  }
}
```

Expected:

```text
Request 11 => 429
Request 12 => 429
```

### Metrics

```powershell
Invoke-RestMethod -Uri "$BASE/metrics?user_id=chung" `
  -Method GET `
  -Headers @{"X-API-Key"=$KEY}
```

Expected fields:

```text
uptime_seconds
total_requests
error_count
monthly_cost_usd
monthly_budget_usd
budget_used_pct
```

---

## 12. Evidence Screenshots

Evidence screenshots are stored in:

```text
screenshots/
```

Recommended screenshots:

```text
part1-develop-ask.png
part2-image-size.png
part3-public-url-test.png
part4-api-key.png
part4-rate-limit.png
part5-stateless-redis.png
part6-render-health-ready.png
part6-render-auth-history.png
part6-render-rate-limit.png
part6-render-metrics.png
part6-production-ready.png
```

These screenshots demonstrate:

- Localhost/development agent behavior
- Docker image size comparison
- Public Render deployment
- API authentication
- Rate limiting
- Stateless Redis design
- Final production health/readiness
- Conversation history
- Metrics
- Production readiness checker result

---

## 13. Security Notes

This project follows these security practices:

- Real `.env` files should not be committed.
- Use `.env.example` as a safe template only.
- API key is read from environment variables.
- Public `/ask` requires `X-API-Key`.
- Rate limit prevents abuse.
- Cost guard prevents unlimited LLM spending.
- Redis stores shared state instead of local memory.
- Docker runs as a non-root user.
- Security headers are added in middleware.

Before final submission, verify:

```powershell
git ls-files | findstr ".env"
```

The result should only include safe templates such as:

```text
.env.example
```

It should not include:

```text
.env
.env.local
```

---

## 14. Submission Checklist

Final submission should include:

```text
✅ MISSION_ANSWERS.md
✅ DEPLOYMENT.md
✅ DAY12_DELIVERY_CHECKLIST.md
✅ 06-lab-complete/ final source code
✅ screenshots/ evidence
✅ Public Render URL
✅ No real .env secrets committed
```

Useful final Git commands:

```powershell
git status --short
git add README.md DEPLOYMENT.md MISSION_ANSWERS.md DAY12_DELIVERY_CHECKLIST.md 06-lab-complete screenshots
git commit -m "complete day12 cloud deployment lab"
git push origin main
```

Final verification:

```powershell
git status --short
git ls-files | findstr ".env"
```

---

## 15. Final Reflection

The main lesson from this lab is that a production AI agent is not just an LLM endpoint. It also needs cloud deployment readiness, safe configuration, authentication, rate limiting, cost control, health checks, graceful shutdown, structured logging, and stateless design.

The most important improvement in the final app is moving shared state into Redis. Conversation history, rate limit state, cost tracking, and metrics should not live in local memory when an app may run across multiple instances. Redis makes the app safer to scale horizontally and closer to a real production architecture.
