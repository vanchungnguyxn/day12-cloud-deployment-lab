## Exercise 2.3: Multi-stage Build

The production Dockerfile uses a multi-stage build process.

Stage 1 (builder stage) installs dependencies and prepares the application environment.

Stage 2 (runtime stage) copies only the necessary files required to run the application.

Build results from my environment:

| Image             | Size    |
| ----------------- | ------- |
| my-agent:develop  | 1.66 GB |
| my-agent:advanced | 236 MB  |

The production image is approximately 86% smaller than the develop image.

This reduction is achieved because the final image excludes build tools, cache files, temporary artifacts, and unnecessary dependencies.

A smaller image provides:

* Faster deployment
* Lower storage usage
* Faster container startup
* Reduced attack surface
* Better production readiness
