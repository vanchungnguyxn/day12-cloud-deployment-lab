# Day 12 Lab - Mission Answers

## Student Information

* Name: Nguyen Van Chung
* Course: AI20K
* Lab: Day 12 - Cloud Infrastructure and Deployment

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

The endpoint returned successfully:

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

# Part 4: API Gateway and Security

# 4.1 API Key Authentication

I tested API key authentication in the develop API Gateway version.

## Server Setup

The server was started with an API key environment variable:

```powershell
$env:AGENT_API_KEY="my-secret-key"
python app.py
```

## Test Without API Key

### Request

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

## Test With Valid API Key

### Request

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

## Conclusion

The API endpoint is protected by API key authentication. Requests without the API key are blocked, while requests with a valid API key are accepted.

---

# 4.2 JWT Authentication

I tested JWT authentication in the production API Gateway version.

## Login Request

```powershell
$token = (Invoke-RestMethod -Uri "http://localhost:8000/auth/token" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"student","password":"demo123"}').access_token

$token
```

## Result

The server returned a JWT token:

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Test With JWT

### Request

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

## Test Without JWT

### Request

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

## Conclusion

JWT authentication works correctly. The `/ask` endpoint requires a valid bearer token. Requests without a token are rejected.

---

# 4.3 Rate Limiting

I tested the rate limit behavior by sending multiple requests quickly.

## Test Command

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

## Result

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

## Conclusion

Rate limiting works correctly. The API allows a limited number of requests in a 60-second window. After the limit is reached, the server returns HTTP 429.

---

# Current Progress Summary

| Part                            | Status       | Evidence                                        |
| ------------------------------- | ------------ | ----------------------------------------------- |
| Part 1: Localhost vs Production | Completed    | Develop and production endpoints tested         |
| Part 2: Docker                  | Completed    | Docker image, Docker run, Docker Compose tested |
| Part 3: Cloud Deployment        | Not yet done | Will be done after final app is ready           |
| Part 4: API Gateway & Security  | Completed    | API key, JWT, and rate limit tested             |
| Part 5: Scaling & Reliability   | Not yet done | Next step                                       |
| Part 6: Final Lab Complete      | Not yet done | Later step                                      |
