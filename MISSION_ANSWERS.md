# Day 12 Lab - Mission Answers

## Student Information

* Name: Nguyen Van Chung
* Course: AI20K
* Lab: Day 12 - Cloud Infrastructure and Deployment
* Repository: https://github.com/vanchungnguyxn/day12-cloud-deployment-lab
* Public URL: https://day12-agent-chung.onrender.com

---

# Part 1: Localhost vs Production

## 1.1 Develop Version Test

I ran the develop version of the AI agent locally.

### Command

```bash
cd 01-localhost-vs-production/develop
python app.py
```

### Test Request

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask?question=Hello" -Method POST
```

### Result

```text
answer
------
Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.
```

### Evidence from Server Log

```text
[DEBUG] Got question: Hello
[DEBUG] Using key: sk-hardcoded-fake-key-never-do-this
[DEBUG] Response: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.
```

## 1.2 Anti-patterns Found in Develop Version

The develop version contains several production anti-patterns:

1. API key is hardcoded in source code.
2. Secret value is printed in debug logs.
3. The app runs directly on localhost.
4. Development reload mode is enabled.
5. Configuration is not loaded from environment variables.
6. There is no proper production configuration.
7. There is no clear separation between development and production environments.

These issues are risky because secrets can be leaked, the app is harder to deploy on cloud platforms, and the service is not production-ready.

---

## 1.3 Production Version Test

I ran the production version of the AI agent.

### Command

```bash
cd 01-localhost-vs-production/production
python app.py
```

### Server Log

```text
WARNING:root:OPENAI_API_KEY not set — using mock LLM
INFO:     Uvicorn running on http://0.0.0.0:8000
```

This shows the app can run on `0.0.0.0`, which is suitable for containers and cloud deployment.

### Health Check Test

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

### Result

```text
status         : ok
uptime_seconds : 8.1
version        : 1.0.0
environment    : development
```

### Ask Endpoint Test

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"Explain production deployment"}'
```

### Result

```text
question                      answer
--------                      ------
Explain production deployment Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được.
```

## 1.4 Part 1 Conclusion

The production version is better than the develop version because:

| Aspect            | Develop Version          | Production Version             |
| ----------------- | ------------------------ | ------------------------------ |
| Secret management | Hardcoded API key        | Uses environment variable      |
| Logging           | Debug logs expose secret | Safer logging                  |
| Host              | localhost                | 0.0.0.0                        |
| Health check      | Not production-oriented  | Has `/health` endpoint         |
| Cloud readiness   | Not ready                | More suitable for Docker/cloud |

---

# Part 2: Docker

## 2.1 Develop Docker Image

I built and ran the develop Docker image.

### Build Command

```bash
docker build -f 02-docker/develop/Dockerfile -t day12-agent-develop .
```

### Run Command

```bash
docker run -p 8000:8000 --name day12-agent-dev day12-agent-develop
```

### Test Request

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask?question=What is Docker" -Method POST
```

### Result

```text
answer
------
Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!
```

This proves the agent can run inside a Docker container.

---

## 2.2 Docker Image Size Comparison

### Develop Image

```text
IMAGE                        ID             DISK USAGE   CONTENT SIZE
day12-agent-develop:latest   fb6a085953fc       1.66GB          424MB
```

### Production Image

```text
IMAGE                           ID             DISK USAGE   CONTENT SIZE
day12-agent-production:latest   167852b7c56d        236MB         56.6MB
```

### Analysis

The production image is much smaller than the develop image.

* Develop image disk usage: 1.66GB
* Production image disk usage: 236MB
* Develop content size: 424MB
* Production content size: 56.6MB

The production image is smaller because it uses a more optimized Dockerfile, a slimmer Python base image, and production-oriented dependency installation. This reduces deployment time, storage usage, and security attack surface.

---

## 2.3 Docker Compose Production Test

I ran the production stack using Docker Compose.

### Command

```bash
cd 02-docker/production
docker compose up --build
```

The stack started multiple services:

* Agent
* Nginx
* Redis
* Qdrant

### Health Check Test

```powershell
Invoke-RestMethod -Uri "http://localhost/health" -Method GET
```

### Result

```text
status uptime_seconds version timestamp
------ -------------- ------- ---------
ok               8.70 2.0.0   6/12/2026 4:20:11 AM
```

### Ask Endpoint Test

```powershell
Invoke-RestMethod -Uri "http://localhost/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"Explain Docker Compose"}'
```

### Result

```text
answer
------
Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!
```

## 2.4 Docker Compose Analysis

Docker Compose is useful because it allows multiple services to run together as one production-like system.

In this lab, the architecture is:

```text
Client → Nginx → Agent → Redis / Qdrant
```

* Nginx acts as the reverse proxy.
* Agent handles AI requests.
* Redis can be used for shared state/cache.
* Qdrant can be used for vector database/RAG workloads.

## 2.5 Part 2 Conclusion

Part 2 shows that the app can be packaged and run in Docker. The production image is significantly smaller than the develop image, and Docker Compose successfully runs a multi-service production-like stack.

---
## Dockerfile Questions

1. **Base image:** `python:3.11-slim`  
   This provides a lightweight Linux environment with Python runtime.

2. **Working directory:** `/app`  
   This is where the application code is copied and executed inside the container.

3. **Why copy `requirements.txt` before source code?**  
   Docker can cache the dependency installation layer. If only source code changes, Docker does not need to reinstall all packages.

4. **CMD vs ENTRYPOINT:**  
   `CMD` provides the default command and can be overridden. `ENTRYPOINT` defines the fixed executable for the container.

5. **Why use multi-stage build?**  
   Multi-stage build keeps build tools in the builder stage and copies only required runtime files to the final image. This reduces image size and attack surface.
---

# Part 3: Cloud Deployment

## 3.1 Railway Deployment Attempt

I first attempted to deploy the agent using Railway CLI.

### Commands

```bash
cd 03-cloud-deployment/railway
railway login
railway init
railway up
railway up --detach
```

### Result

Railway created the project, but the deployment failed because the workspace was restricted:

```text
Your workspace has been restricted. Please attach a payment method or contact support to resolve this.
```

This issue was related to the Railway trial/workspace status, not the application code. Therefore, I switched to Render to complete the cloud deployment checkpoint.

---

## 3.2 Render Deployment

I deployed the AI agent to Render using a Blueprint with `render.yaml`.

### Public URL

```text
https://day12-agent-chung.onrender.com
```

### Deployment Configuration

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

### Health Check Test

```powershell
$BASE="https://day12-agent-chung.onrender.com"

Invoke-RestMethod -Uri "$BASE/health" -Method GET
```

### Result

```text
status uptime_seconds platform timestamp
------ -------------- -------- ---------
ok              129.50 Render   6/12/2026 12:03:05 PM
```

### Agent Endpoint Test

```powershell
Invoke-RestMethod -Uri "$BASE/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"Hello from Render cloud deployment"}'
```

### Result

```text
question                           answer                                                          platform
--------                           ------                                                          --------
Hello from Render cloud deployment Deployment là quá trình đưa code từ máy bạn lên server để người khác dùng được. Render
```

---

## 3.3 Comparison: railway.toml vs render.yaml

| Item                  | railway.toml                         | render.yaml                                              |
| --------------------- | ------------------------------------ | -------------------------------------------------------- |
| Platform              | Railway                              | Render                                                   |
| Format                | TOML                                 | YAML                                                     |
| Purpose               | Configure Railway build/deploy       | Define Render infrastructure as code                     |
| Start command         | `startCommand` under deploy config   | `startCommand` under web service                         |
| Health check          | `healthcheckPath`                    | `healthCheckPath`                                        |
| Environment variables | Set through Railway CLI or dashboard | Set through `envVars` or Render dashboard                |
| Multi-service support | Usually service-level config         | Can define web services, databases, Redis, workers, etc. |

Conclusion: `railway.toml` is simpler and mainly configures how Railway runs one service. `render.yaml` is more infrastructure-oriented and can define complete cloud resources using a Blueprint.

---

## 3.4 Optional Cloud Run Reading

I reviewed the Cloud Run deployment files.

### cloudbuild.yaml

This file defines the CI/CD pipeline:

1. Run tests.
2. Build Docker image.
3. Push the image to a container registry.
4. Deploy the image to Google Cloud Run.

### service.yaml

This file defines the Cloud Run service:

1. Public ingress.
2. Autoscaling configuration.
3. CPU and memory limits.
4. Environment variables.
5. Secret Manager integration.
6. Health probes.

Cloud Run is more production-oriented because it supports autoscaling, managed deployment, secrets, health checks, and CI/CD integration.

## 3.5 Part 3 Conclusion

The cloud deployment checkpoint was completed successfully using Render. Railway was attempted first, but the workspace was restricted. The Render public URL works, and both `/health` and `/ask` endpoints return successful responses.

---

# Part 4: API Gateway and Security

## 4.1 API Key Authentication

I tested API key authentication in the develop API Gateway version.

### Server Setup

```powershell
$env:AGENT_API_KEY="my-secret-key"
python app.py
```

### Test Without API Key

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"hello"}'
```

### Result

```json
{
  "detail": "Missing API key. Include header: X-API-Key: <your-key>"
}
```

This request was rejected because it did not include the required API key.

### Test With Valid API Key

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -Headers @{"X-API-Key"="my-secret-key"} `
  -ContentType "application/json" `
  -Body '{"question":"hello"}'
```

### Result

```text
question answer
-------- ------
hello    Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.
```

## 4.2 JWT Authentication

I tested JWT authentication in the production API Gateway version.

### Login Request

```powershell
$token = (Invoke-RestMethod -Uri "http://localhost:8000/auth/token" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"student","password":"demo123"}').access_token

$token
```

### Result

The server returned a JWT token:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Test With JWT

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -Headers @{"Authorization"="Bearer $token"} `
  -ContentType "application/json" `
  -Body '{"question":"Explain JWT authentication"}'
```

### Result

```text
question                   answer
--------                   ------
Explain JWT authentication Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.
```

### Test Without JWT

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"Explain JWT authentication"}'
```

### Result

```json
{
  "detail": "Authentication required. Include: Authorization: Bearer <token>"
}
```

## 4.3 Rate Limiting

I tested the rate limit behavior by sending multiple requests quickly.

### Test Command

```powershell
1..20 | ForEach-Object {
  try {
    Invoke-RestMethod -Uri "http://localhost:8000/ask" `
      -Method POST `
      -Headers @{"Authorization"="Bearer $token"} `
      -ContentType "application/json" `
      -Body ('{"question":"Rate limit test ' + $_ + '"}') | Out-Null
    "Request $_ OK"
  } catch {
    "Request $_ ERROR: $($_.Exception.Response.StatusCode.value__)"
  }
}
```

### Result

```text
Request 1 OK
Request 2 OK
Request 3 OK
Request 4 OK
Request 5 OK
Request 6 OK
Request 7 OK
Request 8 OK
Request 9 OK
Rate limit exceeded ERROR: 429
Rate limit exceeded ERROR: 429
Rate limit exceeded ERROR: 429
```

The server returned:

```json
{
  "detail": {
    "error": "Rate limit exceeded",
    "limit": 10,
    "window_seconds": 60,
    "retry_after_seconds": 26
  }
}
```

## 4.4 Cost Guard

The production security version also includes cost guard logic. The app tracks request usage and limits usage based on configured budget or usage threshold.

This matters because AI APIs can become expensive when exposed publicly. A cost guard helps prevent unexpected spending and abuse.

## 4.5 Part 4 Conclusion

Part 4 shows that the API can be protected with authentication and rate limiting. API key authentication, JWT authentication, and rate limiting all worked correctly.

---

# Part 5: Scaling and Reliability

## 5.1 Production Scaling with Docker Compose

I ran the production scaling setup with three agent instances.

### Command

```bash
cd 05-scaling-reliability/production
docker compose up --build --scale agent=3
```

### Result

The Docker Compose stack successfully started three agent containers:

```text
agent-1: Starting instance instance-0c6711
agent-2: Starting instance instance-5bdca5
agent-3: Starting instance instance-5df3f6
Storage: Redis ✅
Connected to Redis
```

This proves that multiple agent instances can run at the same time and connect to the same Redis storage.

---

## 5.2 Health Check

I tested the health check endpoint through Nginx.

### Request

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET
```

### Result

```text
status          : ok
instance_id     : instance-0c6711
uptime_seconds  : 178.5
storage         : redis
redis_connected : True
```

The `/health` endpoint confirms that the service is alive and connected to Redis.

---

## 5.3 Load Balancing Test

I sent multiple chat requests through Nginx.

### Request

```powershell
1..5 | ForEach-Object {
  Invoke-RestMethod -Uri "http://localhost:8080/chat" `
    -Method POST `
    -ContentType "application/json" `
    -Body ('{"question":"hello-' + $_ + '","session_id":null}')
}
```

### Result

The requests were handled by different instances:

```text
hello-1 served_by instance-5df3f6
hello-2 served_by instance-0c6711
hello-3 served_by instance-5bdca5
hello-4 served_by instance-5df3f6
hello-5 served_by instance-0c6711
```

This proves that Nginx successfully load balances traffic across multiple agent containers.

---

## 5.4 Stateless Session Test

I ran the stateless test script.

### Command

```bash
python test_stateless.py
```

### Result

```text
Total requests: 5
Instances used: {'instance-5df3f6', 'instance-0c6711', 'instance-5bdca5'}
✅ All requests served despite different instances!
✅ Session history preserved across all instances via Redis!
```

The same session was served by different agent instances, but the conversation history was preserved.

This proves that the application is stateless at the container level because session state is stored in Redis instead of local memory.

---

## 5.5 Part 5 Conclusion

The production scaling setup supports reliability and scaling through:

1. Health checks.
2. Multiple agent instances.
3. Nginx load balancing.
4. Redis shared state.
5. Stateless container design.

This makes the agent more suitable for production deployment.

---

# Part 6: Complete Production Agent

## 6.1 Final Docker Compose Test

I ran the final production app using Docker Compose.

### Command

```bash
cd 06-lab-complete
docker compose up --build
```

The stack started successfully with:

* Agent service
* Redis service

Redis became healthy and the agent started on port 8000.

---

## 6.2 Health Check

### Request

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

### Result

```text
status         : ok
version        : 1.0.0
environment    : staging
uptime_seconds : 10.3
total_requests : 0
checks         : @{llm=mock}
timestamp      : 6/12/2026 2:30:35 PM
```

The `/health` endpoint confirms that the service is alive and running.

---

## 6.3 Readiness Check

### Request

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ready" -Method GET
```

### Result

```text
ready
-----
True
```

The `/ready` endpoint confirms that the service is ready to receive traffic.

---

## 6.4 API Key Authentication

### Request Without API Key

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"question":"Hello final app without key"}'
```

### Result

```json
{
  "detail": "Invalid or missing API key. Include header: X-API-Key: <key>"
}
```

The request was rejected because it did not include a valid API key.

### Request With Valid API Key

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ask" `
  -Method POST `
  -Headers @{"X-API-Key"="chung-day12-secret"} `
  -ContentType "application/json" `
  -Body '{"question":"Hello final production app"}'
```

### Result

```text
question  : Hello final production app
answer    : Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.
model     : gpt-4o-mini
usage     :
timestamp : 6/12/2026 2:30:46 PM
```

This proves that the final production agent can receive authenticated requests and return AI responses.

---

## 6.5 Metrics Endpoint

### Request

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/metrics" `
  -Method GET `
  -Headers @{"X-API-Key"="chung-day12-secret"}
```

### Result

```text
uptime_seconds   : 74.2
total_requests   : 0
error_count      : 0
daily_cost_usd   : 0
daily_budget_usd : 5
budget_used_pct  : 0
```

The metrics endpoint returns basic operational data such as uptime, total requests, error count, daily cost, and budget usage percentage.

---

## 6.6 Production Readiness Check

I ran the production readiness checker.

### Command

```bash
python check_production_ready.py
```

### Result

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

## 6.7 Part 6 Conclusion

The final app is production-ready. It includes:

1. Docker deployment.
2. Redis dependency.
3. Environment-based configuration.
4. Health check endpoint.
5. Readiness endpoint.
6. API key authentication.
7. Metrics endpoint.
8. Rate limiting.
9. Cost guard.
10. Structured logging.
11. Non-root Docker user.
12. Docker healthcheck.
13. Mock LLM fallback when `OPENAI_API_KEY` is not set.

---

# Screenshots / Evidence

The following screenshots are included as evidence for the Day 12 lab completion.

## Screenshot List

| Screenshot File                    | Related Part                     | Evidence                                                                                      |
| ---------------------------------- | -------------------------------- | --------------------------------------------------------------------------------------------- |
| `part1-develop-ask.png`            | Part 1: Localhost vs Production  | Shows the develop version responding to `/ask` successfully on localhost.                     |
| `part2-image-size.png`             | Part 2: Docker                   | Shows Docker image size comparison between develop and production images.                     |
| `part3-public-url-test.png`        | Part 3: Cloud Deployment         | Shows the public Render URL responding successfully to `/health` and `/ask`.                  |
| `part3-render-blueprint.png`       | Part 3: Cloud Deployment         | Shows the Render web service `day12-agent-chung` deployed from the GitHub repository.         |
| `part3-render-logs-success.png`    | Part 3: Cloud Deployment         | Shows Render deployment logs with successful startup and live service URL.                    |
| `part4-api-key.png`                | Part 4: API Gateway and Security | Shows API key authentication working: valid API key is accepted, missing API key is rejected. |
| `part4-rate-limit.png`             | Part 4: API Gateway and Security | Shows rate limiting working, with HTTP 429 returned after exceeding the request limit.        |
| `part6-final-health-ready-ask.png` | Part 6: Final Production Agent   | Shows the final app responding successfully to `/health`, `/ready`, and `/ask` with API key.  |
| `part6-production-ready.png`       | Part 6: Final Production Agent   | Shows `check_production_ready.py` passing all 20/20 checks with 100% production readiness.    |

## Evidence Summary

These screenshots prove that the lab requirements were completed:

1. The agent runs locally and responds to requests.
2. The Docker production image is optimized and smaller than the develop image.
3. The application was deployed successfully to Render with a working public URL.
4. API key authentication works correctly.
5. Rate limiting works correctly and returns HTTP 429 when the limit is exceeded.
6. Scaling and stateless session storage were tested with Redis.
7. The final production app supports health checks, readiness checks, authentication, metrics, and mock LLM fallback.
8. The final production readiness checker passed all checks with 100%.

## Screenshot Note for Part 5

The current screenshot set does not include a separate screenshot for Part 5: Scaling and Reliability. However, Part 5 was tested successfully using Docker Compose scaling and Redis stateless session storage.

Recommended additional screenshot if available:

```text
part5-stateless-redis.png
```

This screenshot should show:

```text
✅ All requests served despite different instances!
✅ Session history preserved across all instances via Redis!
```

---

# Final Progress Summary

| Part                            | Status    | Evidence                                                                                   |
| ------------------------------- | --------- | ------------------------------------------------------------------------------------------ |
| Part 1: Localhost vs Production | Completed | `part1-develop-ask.png`                                                                    |
| Part 2: Docker                  | Completed | `part2-image-size.png`                                                                     |
| Part 3: Cloud Deployment        | Completed | `part3-public-url-test.png`, `part3-render-blueprint.png`, `part3-render-logs-success.png` |
| Part 4: API Gateway & Security  | Completed | `part4-api-key.png`, `part4-rate-limit.png`                                                |
| Part 5: Scaling & Reliability   | Completed | Redis/stateless test output; recommended screenshot: `part5-stateless-redis.png`           |
| Part 6: Final Lab Complete      | Completed | `part6-final-health-ready-ask.png`, `part6-production-ready.png`                           |

---

# Final Conclusion

The Day 12 lab was completed successfully. The project demonstrates the full deployment lifecycle of an AI agent application:

1. Local development and production comparison.
2. Docker packaging.
3. Docker Compose multi-service deployment.
4. Cloud deployment with Render.
5. API key and JWT authentication.
6. Rate limiting and cost guard.
7. Scaling with multiple agent instances.
8. Stateless design using Redis.
9. Final production readiness validation.

The final production readiness checker passed all required checks with a score of 20/20, confirming that the application is production-ready for the scope of this lab.
