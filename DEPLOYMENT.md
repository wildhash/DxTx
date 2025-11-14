# DxTx Deployment Guide

This guide provides instructions for deploying the DxTx AI voice agent system in various environments.

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)
- Valid API keys for:
  - Telnyx
  - TwinMind (or configure Deepgram only)
  - ElevenLabs
  - Deepgram
  - OpenAI

## Production Deployment

### 1. Environment Configuration

Create a `.env` file from the template:
```bash
cp .env.example .env
```

Edit `.env` with your production values:

```bash
# Database - Use strong credentials
DATABASE_URL=postgresql://secure_user:secure_password@postgres:5432/dxtx_production

# API Security - Generate strong keys
API_SECRET_KEY=<generate-a-strong-random-key-here>
ENCRYPTION_KEY=<32-character-minimum-encryption-key>

# Telnyx Configuration
TELNYX_API_KEY=<your-telnyx-api-key>
TELNYX_PUBLIC_KEY=<your-telnyx-public-key>
TELNYX_APP_ID=<your-telnyx-app-id>
TELNYX_PHONE_NUMBER=<your-phone-number-e164-format>

# TwinMind (Primary Transcription)
TWINMIND_API_KEY=<your-twinmind-api-key>
TWINMIND_API_URL=https://api.twinmind.ai/v1

# Deepgram (Fallback Transcription & TTS)
DEEPGRAM_API_KEY=<your-deepgram-api-key>

# ElevenLabs (Primary TTS)
ELEVENLABS_API_KEY=<your-elevenlabs-api-key>
ELEVENLABS_VOICE_ID=<your-preferred-voice-id>

# OpenAI (LLM for dialogue)
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_MODEL=gpt-4-turbo-preview

# NextAuth
NEXTAUTH_URL=https://your-domain.com
NEXTAUTH_SECRET=<generate-a-strong-secret>

# CORS - Update with your domain
ALLOWED_ORIGINS=https://your-domain.com

# Monitoring (Optional)
SENTRY_DSN=<your-sentry-dsn>
```

### 2. SSL Certificates

For production, set up SSL certificates:

```bash
# Using Let's Encrypt with Certbot
sudo certbot certonly --standalone -d your-domain.com -d api.your-domain.com
```

Update `docker-compose.yml` to include SSL:

```yaml
services:
  api:
    # ... existing config ...
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
    environment:
      - SSL_CERT_PATH=/etc/letsencrypt/live/api.your-domain.com/fullchain.pem
      - SSL_KEY_PATH=/etc/letsencrypt/live/api.your-domain.com/privkey.pem
```

### 3. Database Setup

For production, use managed PostgreSQL or external database:

```bash
# Create production database
psql -U postgres -c "CREATE DATABASE dxtx_production;"
psql -U postgres -c "CREATE USER dxtx_user WITH ENCRYPTED PASSWORD 'secure_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE dxtx_production TO dxtx_user;"
```

### 4. Build and Deploy

```bash
# Build Docker images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f

# Run database migrations
docker-compose exec api alembic upgrade head
```

### 5. Health Checks

Verify all services are running:

```bash
# API health check
curl https://api.your-domain.com/health

# Check stats
curl https://api.your-domain.com/stats

# Web dashboard
curl https://your-domain.com
```

## Docker Compose Production Override

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    restart: always
    volumes:
      - /var/lib/dxtx/postgres:/var/lib/postgresql/data

  redis:
    restart: always
    volumes:
      - /var/lib/dxtx/redis:/data

  api:
    restart: always
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    environment:
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    restart: always
    command: npm start
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Cloud Deployment

### AWS (ECS/Fargate)

1. **Push images to ECR**:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag dxtx-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dxtx-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dxtx-api:latest

docker tag dxtx-web:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/dxtx-web:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/dxtx-web:latest
```

2. **Create RDS PostgreSQL instance**
3. **Create ElastiCache Redis cluster**
4. **Deploy ECS task definitions**
5. **Set up Application Load Balancer**

### Google Cloud (Cloud Run)

1. **Build and push images**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/dxtx-api api/
gcloud builds submit --tag gcr.io/PROJECT_ID/dxtx-web web/
```

2. **Deploy services**:
```bash
gcloud run deploy dxtx-api \
  --image gcr.io/PROJECT_ID/dxtx-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy dxtx-web \
  --image gcr.io/PROJECT_ID/dxtx-web \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure (Container Apps)

1. **Create resource group**:
```bash
az group create --name dxtx-rg --location eastus
```

2. **Deploy containers**:
```bash
az containerapp create \
  --name dxtx-api \
  --resource-group dxtx-rg \
  --image your-registry/dxtx-api:latest \
  --target-port 8000 \
  --ingress external

az containerapp create \
  --name dxtx-web \
  --resource-group dxtx-rg \
  --image your-registry/dxtx-web:latest \
  --target-port 3000 \
  --ingress external
```

## Monitoring & Logging

### Application Monitoring

1. **Sentry Integration** (already configured):
   - Set `SENTRY_DSN` in environment variables
   - Errors automatically reported

2. **Prometheus Metrics**:
```bash
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
```

### Log Aggregation

Use ELK Stack or CloudWatch:

```yaml
# Add to docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Backup & Disaster Recovery

### Database Backups

Automated PostgreSQL backups:

```bash
# Daily backup cron job
0 2 * * * docker exec dxtx-postgres pg_dump -U dxtx_user dxtx_production | gzip > /backups/dxtx-$(date +\%Y\%m\%d).sql.gz

# Retain 30 days
0 3 * * * find /backups -name "dxtx-*.sql.gz" -mtime +30 -delete
```

### Restore from Backup

```bash
# Restore database
gunzip < /backups/dxtx-20240101.sql.gz | docker exec -i dxtx-postgres psql -U dxtx_user dxtx_production
```

## Scaling

### Horizontal Scaling

1. **API Service**:
```yaml
api:
  deploy:
    replicas: 3
  # Use load balancer
```

2. **Database**: Use read replicas for PostgreSQL

3. **Redis**: Use Redis Cluster for session storage

### Auto-scaling

Configure based on CPU/memory:

```yaml
# AWS ECS
TaskCount:
  Type: AWS::ApplicationAutoScaling::ScalableTarget
  Properties:
    MinCapacity: 2
    MaxCapacity: 10
    TargetTrackingScalingPolicyConfiguration:
      TargetValue: 70.0
      PredefinedMetricSpecification:
        PredefinedMetricType: ECSServiceAverageCPUUtilization
```

## Security Checklist

- [ ] Use HTTPS/WSS only in production
- [ ] Enable PostgreSQL SSL connections
- [ ] Rotate encryption keys regularly
- [ ] Set up firewall rules (only allow necessary ports)
- [ ] Enable rate limiting on API endpoints
- [ ] Implement IP whitelisting for admin endpoints
- [ ] Regular security updates for dependencies
- [ ] Enable audit logging in production
- [ ] Backup encryption keys securely
- [ ] Set up intrusion detection (fail2ban, etc.)
- [ ] Regular HIPAA compliance audits

## Troubleshooting

### API Not Starting

```bash
# Check logs
docker-compose logs api

# Common issues:
# - Missing environment variables
# - Database connection failed
# - Port already in use
```

### Database Connection Issues

```bash
# Test database connection
docker-compose exec api python -c "from app.database import engine; engine.connect()"

# Check PostgreSQL logs
docker-compose logs postgres
```

### Call Webhook Issues

```bash
# Test webhook endpoint
curl -X POST https://api.your-domain.com/webhooks/telnyx \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test"}'

# Verify Telnyx webhook URL configuration in Telnyx portal
```

## Maintenance

### Database Migrations

```bash
# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback
docker-compose exec api alembic downgrade -1
```

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Review this deployment guide
4. Contact support team

## HIPAA Compliance Notes

For HIPAA compliance in production:
1. Enable audit logging (already implemented)
2. Encrypt data at rest (PostgreSQL encryption)
3. Use secure connections (HTTPS/WSS)
4. Implement access controls
5. Regular security audits
6. Business Associate Agreements with third-party services
7. Data retention policies (configured via `DATA_RETENTION_DAYS`)
