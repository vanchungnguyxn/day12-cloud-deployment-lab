# Delivery Checklist — Day 12 Lab Submission

> **Student Name:** Nguyen Van Chung
> **Student ID:** 2A202600647
> **Date:** 12/06/2026

---

## Submission Requirements

Submit a **GitHub repository** containing:

---

## 1. Mission Answers — 40 points

* [x] Created `MISSION_ANSWERS.md`
* [x] Answered Part 1: Localhost vs Production
* [x] Answered Exercise 1.1: Anti-patterns found
* [x] Answered Exercise 1.3: Comparison table
* [x] Answered Part 2: Docker
* [x] Answered Exercise 2.1: Dockerfile questions
* [x] Answered Exercise 2.3: Image size comparison
* [x] Answered Part 3: Cloud Deployment
* [x] Included Railway deployment attempt
* [x] Included Render deployment result
* [x] Included public Render URL
* [x] Answered Part 4: API Security
* [x] Included API key test results
* [x] Included JWT authentication test results
* [x] Included rate limit test results
* [x] Explained cost guard
* [x] Answered Part 5: Scaling & Reliability
* [x] Included health check result
* [x] Included readiness/stateless explanation
* [x] Included Redis-based stateless scaling test result

### Mission Answers File

```text
MISSION_ANSWERS.md
```

---

## 2. Full Source Code — Lab 06 Complete — 60 points

The final production-ready agent is included in:

```text
06-lab-complete/
```

The final app contains:

```text
06-lab-complete/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── auth.py
│   ├── rate_limiter.py
│   └── cost_guard.py
├── utils/
│   └── mock_llm.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .dockerignore
├── railway.toml
├── render.yaml
├── README.md
└── check_production_ready.py
```

### Requirements

* [x] All code runs without errors
* [x] Multi-stage Dockerfile implemented
* [x] Docker image is production optimized
* [x] API key authentication implemented
* [x] Rate limiting implemented
* [x] Cost guard implemented
* [x] Health check endpoint implemented
* [x] Readiness endpoint implemented
* [x] Graceful shutdown implemented
* [x] Stateless design using Redis
* [x] No hardcoded secrets in code
* [x] `.env.local` is not committed
* [x] Only `.env.example` is included

### Production Readiness Result

```text
Result: 20/20 checks passed (100%)
🎉 PRODUCTION READY! Deploy nào!
```

---

## 3. Service Domain Link

Created:

```text
DEPLOYMENT.md
```

### Public URL

```text
https://day12-agent-chung.onrender.com
```

### Platform

```text
Render
```

### Cloud Deployment Status

* [x] Railway attempted
* [x] Railway blocked due to workspace restriction
* [x] Render deployment completed successfully
* [x] Public URL is accessible
* [x] `/health` endpoint works on public URL
* [x] `/ask` endpoint works on public URL
* [x] Deployment screenshots included

---

## 4. Public URL Self-Test

### Health Check

```bash
curl https://day12-agent-chung.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

Status:

```text
Passed
```

### Ask Endpoint

```bash
curl -X POST https://day12-agent-chung.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello from Render cloud deployment"}'
```

Expected:

```text
The agent returns a valid answer.
```

Status:

```text
Passed
```

---

## 5. Final Local Production Self-Test

### Start Final App

```bash
cd 06-lab-complete
docker compose up --build
```

Status:

```text
Passed
```

### Health Check

```bash
curl http://localhost:8000/health
```

Status:

```text
Passed
```

Actual result:

```text
status         : ok
version        : 1.0.0
environment    : staging
checks         : @{llm=mock}
```

### Readiness Check

```bash
curl http://localhost:8000/ready
```

Status:

```text
Passed
```

Actual result:

```text
ready : True
```

### Authentication Required

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```

Expected:

```text
401 Unauthorized
```

Status:

```text
Passed
```

Actual result:

```json
{
  "detail": "Invalid or missing API key. Include header: X-API-Key: <key>"
}
```

### Ask With API Key

```bash
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: chung-day12-secret" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello final production app"}'
```

Expected:

```text
200 OK
```

Status:

```text
Passed
```

Actual result:

```text
question  : Hello final production app
answer    : Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.
model     : gpt-4o-mini
```

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics \
  -H "X-API-Key: chung-day12-secret"
```

Status:

```text
Passed
```

Actual result:

```text
uptime_seconds   : 74.2
total_requests   : 0
error_count      : 0
daily_cost_usd   : 0
daily_budget_usd : 5
budget_used_pct  : 0
```

---

## 6. Screenshots

Screenshots are included in:

```text
screenshots/
```

### Screenshot List

* [x] `part1-develop-ask.png`
* [x] `part2-image-size.png`
* [x] `part3-public-url-test.png`
* [x] `part3-render-blueprint.png`
* [x] `part3-render-logs-success.png`
* [x] `part4-api-key.png`
* [x] `part4-rate-limit.png`
* [x] `part6-final-health-ready-ask.png`
* [x] `part6-production-ready.png`

### Recommended Extra Screenshot

* [ ] `part5-stateless-redis.png`

Note: Part 5 was tested successfully through terminal output. Adding a screenshot for Part 5 is recommended but not required if the test result is already documented in `MISSION_ANSWERS.md`.

---

## 7. Pre-Submission Checklist

* [x] Repository is public or instructor has access
* [x] `MISSION_ANSWERS.md` completed with all exercises
* [x] `DEPLOYMENT.md` has working public URL
* [x] Final source code is included in `06-lab-complete/`
* [x] `README.md` exists
* [x] No `.env` file committed
* [x] No `.env.local` file committed
* [x] Only `.env.example` is committed
* [x] No hardcoded secrets in code
* [x] Public URL is accessible and working
* [x] Screenshots included in `screenshots/` folder
* [x] Production readiness checker passed 20/20 checks

---

## 8. Repository URL

```text
https://github.com/vanchungnguyxn/day12-cloud-deployment-lab
```

---

## 9. Final Submission Status

```text
Ready for submission
```

---

## Final Note

The Day 12 lab requirements were completed successfully. The repository includes mission answers, deployment information, screenshots, and the final production-ready agent. The final app passed all production readiness checks with a score of 20/20.
