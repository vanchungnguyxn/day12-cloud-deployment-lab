## Exercise 1.3: Basic vs Advanced

| Feature         | Basic                 | Advanced                  | Why important?                            |
| --------------- | --------------------- | ------------------------- | ----------------------------------------- |
| Config          | Hardcoded values      | Environment variables     | Easier deployment across environments     |
| Secrets         | Stored in source code | Loaded from .env          | Prevent secret leakage                    |
| Host            | localhost             | Configurable              | Works in containers and cloud             |
| Port            | Fixed port            | Dynamic from env          | Railway/Render assign ports automatically |
| Logging         | print()               | Structured logging        | Easier monitoring and debugging           |
| Health Check    | Missing               | /health endpoint          | Cloud platform can verify service health  |
| Readiness Check | Missing               | /ready endpoint           | Load balancer knows when service is ready |
| Shutdown        | Abrupt stop           | Graceful shutdown         | Prevent losing active requests            |
| Debug Mode      | Always enabled        | Controlled by environment | More secure in production                 |
| Reliability     | Local only            | Production-ready          | Better scalability and maintainability    |

### Why production version is better

The production version follows several 12-Factor App principles. It separates configuration from code, supports health and readiness checks, uses structured logging, and handles shutdown signals properly. These features make the application safer, easier to deploy, and more reliable in real cloud environments.
