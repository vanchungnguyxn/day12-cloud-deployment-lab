# Deployment Information

## Student Information

* **Name:** Nguyen Van Chung
* **Course:** AI20K
* **Lab:** Day 12 - Cloud Infrastructure and Deployment
* **Repository:** https://github.com/vanchungnguyxn/day12-cloud-deployment-lab

---

# 1. Public Cloud Deployment

## Public URL

```text
https://day12-agent-chung.onrender.com
```

## Platform

```text
Render
```

## Service Name

```text
day12-agent-chung
```

## Deployment Type

The application was deployed to Render using a Blueprint configuration file:

```text
render.yaml
```

Railway was attempted first, but the Railway workspace was restricted. Therefore, Render was used to complete the cloud deployment requirement.

---

# 2. Railway Attempt

## Railway Status

I first attempted to deploy the app using Railway CLI.

### Commands Used

```bash
cd 03-cloud-deployment/railway
railway login
railway init
railway up
railway up --detach
```

### Railway Error

```text
Your workspace has been restricted. Please attach a payment method or contact support to resolve this.
```

## Railway Conclusion

The Railway deployment failed because of a workspace/trial limitation, not because of an application error.

I switched to Render and successfully deployed the application there.

---

# 3. Render Deployment

## Render Public URL

```text
https://day12-agent-chung.onrender.com
```

## Render Configuration

The app was deployed using `render.yaml`.

```yaml
services:
  - type: web
    name: day12-agent-chung
    runtime: python
    region: singapore
    plan: free
    rootDir: 03-cloud-deployment/railway
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: APP_NAME
        value: day12-agent-chung
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: AGENT_API_KEY
        value: my-secret-key
```

## Render Dashboard Evidence

The Render dashboard shows:

* Web service name: `day12-agent-chung`
* Runtime: Python 3
* Plan: Free
* Branch: `main`
* Repository: `vanchungnguyxn/day12-cloud-deployment-lab`
* Public URL: `https://day12-agent-chung.onrender.com`
* Deployment status: Live

---

# 4. Public URL Test Commands

## 4.1 Health Check

### PowerShell

```powershell
$BASE="https://day12-agent-chung.onrender.com"

Invoke-RestMethod -Uri "$BASE/health" -Method GET
```

### Expected Result

```text
status : ok
platform : Render
```

### Actual Result

```text
status uptime_seconds platform timestamp
------ -------------- -------- ---------
ok              129.50 Render   6/12/2026 12:03:05 PM
```

---

## 4.2 Ask Endpoint

### PowerShell

```powershell
Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"Hello from Render cloud deployment"}'
```

### Expected Result

The agent should return a valid answer.

### Actual Result

```text
question                           answer                                                          platform
--------                           ------                                                          --------
Hello from Render cloud deployment Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được. Render
```

---

# 5. Final Production App

## Final App Location

The final production-ready app is located in:

```text
06-lab-complete/
```

This folder contains the final production implementation with:

```text
app/
utils/
Dockerfile
docker-compose.yml
requirements.txt
.env.example
.dockerignore
railway.toml
render.yaml
README.md
check_production_ready.py
```

## Final App Features

The final app includes:

* Dockerized FastAPI application
* Multi-stage Dockerfile
* Redis dependency
* Environment-based configuration
* API key authentication
* Rate limiting
* Cost guard
* Health check endpoint
* Readiness endpoint
* Metrics endpoint
* Structured JSON logging
* Graceful shutdown
* Non-root Docker user
* Docker healthcheck
* Mock LLM fallback when `OPENAI_API_KEY` is not set

---

# 6. Final Local Production Test

The final production app was tested locally with Docker Compose.

## 6.1 Start Final App

```bash
cd 06-lab-complete
docker compose up --build
```

The stack starts:

* `agent`
* `redis`

Redis becomes healthy and the agent starts on port `8000`.

---

## 6.2 Health Check

### PowerShell

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

### Actual Result

```text
status         : ok
version        : 1.0.0
environment    : staging
uptime_seconds : 10.3
total_requests : 0
checks         : @{llm=mock}
timestamp      : 6/12/2026 2:30:35 PM
```

---

## 6.3 Readiness Check

### PowerShell

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ready" -Method GET
```

### Actual Result

```text
ready
-----
True
```

---

## 6.4 Authentication Required Test

### Request Without API Key

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"Hello final app without key"}'
```

### Actual Result

```json
{
  "detail": "Invalid or missing API key. Include header: X-API-Key: <key>"
}
```

This proves that the final app requires authentication.

---

## 6.5 Ask Endpoint With API Key

### PowerShell

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -Headers @{"X-API-Key"="chung-day12-secret"} `
  -ContentType "application/json" `
  -Body '{"question":"Hello final production app"}'
```

### Actual Result

```text
question  : Hello final production app
answer    : Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.
model     : gpt-4o-mini
usage     :
timestamp : 6/12/2026 2:30:46 PM
```

This proves that authenticated requests are accepted and the agent returns a valid response.

---

## 6.6 Metrics Endpoint

### PowerShell

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/metrics" `
  -Method GET `
  -Headers @{"X-API-Key"="chung-day12-secret"}
```

### Actual Result

```text
uptime_seconds   : 74.2
total_requests   : 0
error_count      : 0
daily_cost_usd   : 0
daily_budget_usd : 5
budget_used_pct  : 0
```

The metrics endpoint returns operational information such as uptime, request count, error count, daily cost, budget, and budget usage percentage.

---

# 7. Environment Variables

## 7.1 Render Environment Variables

The Render service uses these variables:

```text
ENVIRONMENT=production
APP_NAME=day12-agent-chung
PYTHON_VERSION=3.11.9
AGENT_API_KEY=my-secret-key
PORT=<provided by Render>
```

## 7.2 Final Local Production Environment

The final local app uses `.env.local` during local Docker Compose testing.

Example environment configuration:

```text
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=staging
DEBUG=false

APP_NAME=Chung Day12 Production Agent
APP_VERSION=1.0.0

OPENAI_API_KEY=
LLM_MODEL=gpt-4o-mini

AGENT_API_KEY=chung-day12-secret
JWT_SECRET=chung-jwt-secret

RATE_LIMIT_PER_MINUTE=10
DAILY_BUDGET_USD=10.0

REDIS_URL=redis://redis:6379/0
ALLOWED_ORIGINS=*
```

## Security Note

The real `.env.local` file is not committed to GitHub.

Only `.env.example` is included in the repository.

---

# 8. Production Readiness Check

I ran the production readiness checker inside the final app folder.

## Command

```bash
cd 06-lab-complete
python check_production_ready.py
```

## Result

```text
=======================================================
  Production Readiness Check — Day 12 Lab
=======================================================

Required Files
✅ Dockerfile exists
✅ docker-compose.yml exists
✅ .dockerignore exists
✅ .env.example exists
✅ requirements.txt exists
✅ railway.toml or render.yaml exists

Security
✅ .env in .gitignore
✅ No hardcoded secrets in code

API Endpoints
✅ /health endpoint defined
✅ /ready endpoint defined
✅ Authentication implemented
✅ Rate limiting implemented
✅ Graceful shutdown (SIGTERM)
✅ Structured logging (JSON)

Docker
✅ Multi-stage build
✅ Non-root user
✅ HEALTHCHECK instruction
✅ Slim base image
✅ .dockerignore covers .env
✅ .dockerignore covers __pycache__

Result: 20/20 checks passed (100%)
🎉 PRODUCTION READY! Deploy nào!
```

## Conclusion

The final app passed all production readiness checks:

```text
20/20 checks passed (100%)
PRODUCTION READY
```

---

# 9. Screenshots

Screenshots are stored in the `screenshots/` folder.

## Screenshot List

| Screenshot File                    | Description                                                         |
| ---------------------------------- | ------------------------------------------------------------------- |
| `part1-develop-ask.png`            | Develop version responds to `/ask` locally.                         |
| `part2-image-size.png`             | Docker image size comparison between develop and production images. |
| `part3-public-url-test.png`        | Render public URL responds to `/health` and `/ask`.                 |
| `part3-render-blueprint.png`       | Render dashboard showing deployed service.                          |
| `part3-render-logs-success.png`    | Render logs showing successful deployment and live service.         |
| `part4-api-key.png`                | API key authentication test.                                        |
| `part4-rate-limit.png`             | Rate limit test returning HTTP 429 after limit is exceeded.         |
| `part6-final-health-ready-ask.png` | Final app responds to `/health`, `/ready`, and `/ask` with API key. |
| `part6-production-ready.png`       | Final production readiness check passes 20/20 checks.               |

## Recommended Extra Screenshot

If available, include:

```text
part5-stateless-redis.png
```

This screenshot should show:

```text
✅ All requests served despite different instances!
✅ Session history preserved across all instances via Redis!
```

---

# 10. Self-Test Commands

## 10.1 Public Render Health Check

```bash
curl https://day12-agent-chung.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

## 10.2 Public Render Ask Test

```bash
curl -X POST https://day12-agent-chung.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello from Render cloud deployment"}'
```

Expected:

```text
The agent returns a valid answer.
```

---

# 11. Final Local Production Self-Test

## 11.1 Start Final Local Stack

```bash
cd 06-lab-complete
docker compose up --build
```

## 11.2 Health Check

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

## 11.3 Authentication Required

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```

Expected:

```text
401 Unauthorized
```

## 11.4 Ask With API Key

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

## 11.5 Rate Limiting

```bash
for i in {1..15}; do
  curl -X POST http://localhost:8000/ask \
    -H "X-API-Key: chung-day12-secret" \
    -H "Content-Type: application/json" \
    -d "{\"question\":\"rate limit test $i\"}"
done
```

Expected:

```text
The API should eventually return 429 Too Many Requests.
```

---

# 12. Notes About Final Cloud Deployment

The public Render URL currently demonstrates the cloud deployment checkpoint using the Part 3 deployment configuration.

The complete final production app was validated locally in `06-lab-complete` and passed the full production readiness checker with 20/20 checks.

For a stricter production submission, the same final app can also be deployed to Render by setting the Render service root directory to:

```text
06-lab-complete
```

and using the final app's `render.yaml`.

---

# 13. Final Conclusion

The Day 12 deployment requirements were completed successfully.

The project demonstrates:

1. Localhost versus production comparison.
2. Docker containerization.
3. Docker image optimization.
4. Docker Compose multi-service setup.
5. Cloud deployment with Render.
6. API key authentication.
7. JWT authentication.
8. Rate limiting.
9. Cost guard.
10. Redis-based stateless design.
11. Health checks and readiness checks.
12. Metrics endpoint.
13. Production readiness validation.

The final production app passed:

```text
20/20 checks passed (100%)
PRODUCTION READY
```

Therefore, the project is ready for submission.
## Final Production Deployment

### Public URL

```text
https://day12-cloud-deployment-lab.onrender.com
```

### Final App Folder

```text
06-lab-complete
```

### Platform Configuration

```text
Platform: Render
Runtime: Docker
Root Directory: 06-lab-complete
Health Check Path: /health
Redis: Render Key Value
Environment: production
```

### Environment Variables

```env
ENVIRONMENT=production
APP_NAME=day12-agent-chung-final
APP_VERSION=1.0.0
AGENT_API_KEY=***
JWT_SECRET=***
RATE_LIMIT_PER_MINUTE=10
MONTHLY_BUDGET_USD=10.0
REDIS_URL=***
OPENAI_API_KEY=
LLM_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
ALLOWED_ORIGINS=*
```

Real secrets are configured in Render Environment Variables and are not committed to GitHub.

### Public Test Commands

```powershell
$BASE="https://day12-cloud-deployment-lab.onrender.com"
$KEY="chung-day12-secret"

Invoke-RestMethod -Uri "$BASE/health" -Method GET

Invoke-RestMethod -Uri "$BASE/ready" -Method GET

Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -Headers @{"X-API-Key"=$KEY} `
  -ContentType "application/json" `
  -Body '{"user_id":"chung","conversation_id":"render","question":"Hello final Render app"}'
```

### Verified Results

```text
GET /health => status: ok, environment: production
GET /ready => ready: True, redis: ok
POST /ask without X-API-Key => 401 Unauthorized
POST /ask with X-API-Key => successful response
Conversation history => history_turns_used: 1
Rate limiting => 429 after 10 requests/min/user
GET /metrics => monthly cost, monthly budget, budget percentage returned
Production readiness check => 20/20 checks passed
```
