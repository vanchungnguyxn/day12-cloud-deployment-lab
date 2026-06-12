## Exercise 1.1: Anti-patterns in develop/app.py

1. Hardcoded API key directly in source code.
2. Hardcoded database/config values.
3. Hardcoded port 8000 instead of reading from environment variables.
4. Uses development mode/reload, not suitable for production.
5. No health check endpoint.
6. No readiness check endpoint.
7. Uses print/basic logging instead of structured JSON logging.
8. No graceful shutdown handling.
9. No authentication or rate limiting.
10. Secrets/config are not managed through environment variables.