# Docker Deployment Guide - NotebookUm

## Quick Start

### 1. Build and run with Docker Compose (Recommended)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Build images and start services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### 2. Build Docker image manually

```bash
# Build the image
docker build -t notebookum:latest .

# Run container
docker run -d \
  --name notebookum-app \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DB_HOST=mysql \
  -e DB_NAME=notebookum \
  -e DB_USER=notebookum \
  -e DB_PASSWORD=password \
  -e OPENAI_API_KEY=your-key \
  notebookum:latest
```

## Docker Architecture

### Multi-stage Build Benefits
- **Stage 1 (Builder)**: Installs uv and all dependencies
- **Stage 2 (Runtime)**: Only includes runtime essentials (50% smaller image)
- **Result**: ~300-400MB final image vs 1GB+ without multi-stage

### Services in docker-compose.yml

1. **MySQL 8.0** (Port 3306)
   - Database persistence with volumes
   - Health checks for readiness
   - Environment-configurable credentials

2. **Redis 7** (Port 6379)
   - Message broker for Celery
   - Task result backend
   - Cache support

3. **Flask App + Granian** (Port 5000)
   - ASGI server with 4 workers (adjust for your CPU)
   - Async task processing
   - Health endpoint at `/health`

4. **Celery Worker** (Background)
   - Processes PDF uploads asynchronously
   - Connects to Redis broker
   - Logs available via docker-compose logs

## Performance Tuning

### Granian Configuration (in Dockerfile)
```bash
granian \
  --workers 4            # (2 × CPU_cores) + 1 recommended
  --max-concurrency 1024 # Connections per worker
  --loop auto           # Auto-detect best event loop
  --http auto           # Auto-detect HTTP version
```

### Database Optimization
- MySQL uses Alpine image for smaller footprint
- Health checks prevent app startup before DB ready
- Volume persistence ensures data survives container restart

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | production | Flask environment mode |
| `DB_HOST` | mysql | Database hostname |
| `DB_PORT` | 3306 | Database port |
| `DB_NAME` | notebookum | Database name |
| `DB_USER` | notebookum | Database user |
| `DB_PASSWORD` | - | **CHANGE IN PRODUCTION** |
| `OPENAI_API_KEY` | - | Required for AI features |
| `MAX_UPLOAD_SIZE` | 26214400 | Max file size in bytes (25MB) |
| `CELERY_BROKER_URL` | redis://... | Task queue broker |
| `CELERY_RESULT_BACKEND` | redis://... | Task results storage |

## Deployment Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Change `DB_PASSWORD` in `.env`
- [ ] Add `OPENAI_API_KEY` in `.env`
- [ ] Test app responds at http://localhost:5000/
- [ ] Check database connectivity: `docker-compose exec mysql mysql -unotebookum -p notebookum`
- [ ] Monitor logs: `docker-compose logs -f app`
- [ ] Run database migrations: `docker-compose exec app flask db upgrade`

## Common Commands

```bash
# View running containers
docker-compose ps

# Execute command in container
docker-compose exec app python -m pytest

# View logs for specific service
docker-compose logs app
docker-compose logs mysql
docker-compose logs celery-worker

# Rebuild without cache
docker-compose build --no-cache

# Remove volumes and data
docker-compose down -v

# Push to registry
docker tag notebookum:latest your-registry/notebookum:latest
docker push your-registry/notebookum:latest
```

## Kubernetes Deployment

For Kubernetes, consider:
- ConfigMap for environment variables
- Secret for sensitive data (DB_PASSWORD, OPENAI_API_KEY)
- StatefulSet for MySQL (or use managed database)
- Deployment for Flask app with readiness/liveness probes
- Service for internal networking

## Production Best Practices

1. **Security**
   - Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
   - Don't commit `.env` to version control
   - Enable HTTPS/TLS at load balancer level
   - Run as non-root user (appuser in our Dockerfile)

2. **Monitoring**
   - Enable health endpoint checks
   - Log to stdout (captured by Docker)
   - Use APM tools (DataDog, New Relic)
   - Monitor database connections

3. **Scaling**
   - Use container orchestration (Docker Swarm, Kubernetes)
   - Scale Celery workers independently
   - Use external database (managed RDS, Azure Database)
   - Redis cluster for high availability

4. **Updates**
   - Blue-green deployment strategy
   - Use semantic versioning for images
   - Test in staging first
   - Maintain backward compatibility with DB migrations
