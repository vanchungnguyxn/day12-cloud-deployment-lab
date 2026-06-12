## Exercise 2.1: Dockerfile Analysis

1. The base image is `python:3.11-slim`.

2. The working directory is `/app`.

3. `requirements.txt` is copied before the application source code so Docker can cache the dependency installation layer. This speeds up rebuilds when only source code changes.

4. CMD provides a default command that can be overridden when running the container. ENTRYPOINT defines the main executable and is harder to override.
