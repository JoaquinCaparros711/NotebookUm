# Docker Deployment Guide

This guide explains how to build and run NotebookUm using Docker.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+ (for compose commands)

## Quick Start with Docker Compose

The easiest way to run the application locally:

```bash
# Build and start the application
docker-compose up --build

# Access the application
open http://localhost:5000

# Stop the application
docker-compose down
```

## Building the Docker Image

### Build locally:

```bash
docker build -t notebookum:latest .
```

### Build with custom tag:

```bash
docker build -t notebookum:1.0.0 .
```

## Running the Container

### Using Docker CLI:

```bash
# Basic run (with environment file)
docker run -p 5000:5000 --env-file .env notebookum:latest

# Interactive with mounted code (for development)
docker run -it -p 5000:5000 -v $(pwd):/app --env-file .env notebookum:latest python -m flask run --host=0.0.0.0 --reload

# With custom environment variables
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  notebookum:latest
```

### Using Docker Compose:

```bash
# Start in foreground (ctrl+c to stop)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down
```

## Environment Configuration

Create a `.env` file with required variables:

```bash
FLASK_ENV=development
SECRET_KEY=change-me-in-production
GEMMA_API_KEY=your-api-key-here
GEMMA_API_URL=your-api-url-here
```

Or pass them at runtime:

```bash
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e GEMMA_API_KEY=your-key \
  notebookum:latest
```

## Production Deployment

### With Gunicorn (recommended for production):

Modify the Dockerfile to use Gunicorn instead of Flask dev server:

```dockerfile
# Change this line:
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]

# To this:
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "sync", "main:app"]
```

Then add gunicorn to dependencies in pyproject.toml:

```toml
dependencies = [
    "flask>=3.1",
    "gunicorn>=21.0",
    "openai>=2.29.0",
    "python-dotenv>=1.0",
]
```

### Using Docker with Kubernetes:

```bash
kubectl apply -f deployment.yaml
```

## Troubleshooting

### Port already in use:

```bash
# Use a different port
docker run -p 8000:5000 notebookum:latest
```

### Permission denied when mounting volumes:

```bash
# Run with user ID mapping
docker run -u $(id -u):$(id -g) -v $(pwd):/app notebookum:latest
```

### Container exits immediately:

```bash
# View the logs
docker logs <container-id>

# Run interactively to debug
docker run -it notebookum:latest /bin/bash
```

### Build cache issues:

```bash
# Rebuild without using cached layers
docker build --no-cache -t notebookum:latest .
```

## Image Optimization

The Dockerfile uses a multi-stage build to:
- Keep the final image size small (~200MB)
- Only include runtime dependencies
- Exclude build tools from the production image

### Estimated sizes:
- Builder stage: ~600MB (includes build dependencies)
- Final runtime image: ~200MB (production-ready)

## Security Features

The Docker setup includes:

✓ **Non-root user**: Application runs as `appuser` (UID 1000)
✓ **Health checks**: Built-in `HEALTHCHECK` endpoint
✓ **Slim base image**: Uses `python:3.12-slim` to reduce surface area
✓ **.dockerignore**: Excludes unnecessary files from the image
✓ **Environment variables**: Secrets passed at runtime, not baked into image

## Docker Compose Features

The `docker-compose.yml` includes:

- **Automatic rebuilds**: `--build` flag rebuilds on changes
- **Volume mounts**: Code changes reflect immediately (development)
- **Environment file**: Loads `.env` automatically
- **Health checks**: Container health monitoring
- **Restart policy**: Automatic restart unless stopped manually
- **Auto-reload**: Flask development server with `--reload`
- **Commented database**: PostgreSQL ready for future use (uncomment to enable)

## Advanced Usage

### Multi-container setup with database:

Uncomment the `db` service in `docker-compose.yml` and add to your `.env`:

```env
DATABASE_URL=postgresql://notebookum:change-me@db:5432/notebookum
```

Then start both services:

```bash
docker-compose up
```

### Push to Docker Registry:

```bash
# Tag for Docker Hub
docker tag notebookum:latest youruser/notebookum:latest

# Login to Docker Hub
docker login

# Push the image
docker push youruser/notebookum:latest
```

### Run multiple instances with load balancing:

```bash
docker run -p 5001:5000 --name app1 notebookum:latest &
docker run -p 5002:5000 --name app2 notebookum:latest &
# Use nginx or similar for load balancing
```

## Verification

### Check that the image was built correctly:

```bash
docker images notebookum

# Output should show:
# REPOSITORY          TAG       IMAGE ID       CREATED        SIZE
# notebookum          latest    abc123def456   2 minutes ago  200MB
```

### Verify the application is running:

```bash
# Check health
curl http://localhost:5000/

# View running containers
docker ps

# Check logs
docker logs <container-id>
```

## Related Documentation

- [Docker Documentation](https://docs.docker.com/)
- [Flask with Docker](https://flask.palletsprojects.com/en/latest/deploying/docker/)
- [Best Practices for Python Docker Images](https://docs.docker.com/language/python/build-images/)
