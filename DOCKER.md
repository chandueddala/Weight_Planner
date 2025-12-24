# Docker Deployment Guide - Weight Planner

Complete guide for building and running Weight Planner in Docker containers.

## Quick Start

### Prerequisites

- Docker installed (version 20.10+)
- Docker Compose installed (version 1.29+)
- AWS credentials configured
- OpenAI API key

### 1. Configure Environment

```bash
# Copy environment template
cp .env.docker .env

# Edit .env with your credentials
nano .env  # or use any text editor
```

**Required variables:**
```bash
AWS_ACCESS_KEY_ID=your-actual-key
AWS_SECRET_ACCESS_KEY=your-actual-secret
OPENAI_API_KEY=sk-your-openai-key
```

### 2. Build and Run

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Access the app
# Open browser to http://localhost:8501
```

### 3. Stop the Container

```bash
# Stop the container
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Docker Commands

### Build Image

```bash
# Build the Docker image
docker build -t weight-planner:latest .

# Build with no cache
docker build --no-cache -t weight-planner:latest .
```

### Run Container

```bash
# Run with docker-compose (recommended)
docker-compose up -d

# Or run with docker directly
docker run -d \
  --name weight-planner \
  -p 8501:8501 \
  --env-file .env \
  weight-planner:latest
```

### Container Management

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View logs
docker logs weight-planner-app
docker logs -f weight-planner-app  # Follow logs

# Restart container
docker-compose restart

# Stop container
docker-compose stop

# Start stopped container
docker-compose start

# Remove container
docker-compose down
```

### Access Container Shell

```bash
# Access bash shell
docker exec -it weight-planner-app bash

# Run commands inside container
docker exec weight-planner-app python -c "from app.cognito_auth import validate_email; print(validate_email('test@example.com'))"
```

---

## Docker Image Details

### Base Image

- **Image**: `python:3.11-slim`
- **Size**: ~200 MB (base) + ~500 MB (dependencies)
- **OS**: Debian-based

### Installed Dependencies

From `requirements.txt`:
- streamlit
- boto3
- langchain-community
- openai
- bcrypt
- pandas
- matplotlib
- faiss-cpu
- python-dotenv

### Container Structure

```
/app/
├── Stream_lit_Chat.py       # Main application
├── GPTCustomPrompt.py        # RAG planner
├── app/                      # Core modules
├── vector/                   # FAISS embeddings
├── requirements.txt          # Dependencies
└── .env                      # Environment variables
```

### Exposed Ports

- **8501**: Streamlit web interface

### Health Check

- **Endpoint**: `http://localhost:8501/_stcore/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

---

## Environment Variables

### Required Variables

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
AWS_REGION=us-east-2

# OpenAI API
OPENAI_API_KEY=sk-your-key-here

# DynamoDB Tables
DDB_USERS_TABLE=Users
DDB_SESSIONS_TABLE=UserSessions
DDB_MESSAGES_TABLE=UserMessages
```

### Optional Variables

```bash
# Application Settings
DEFAULT_STARTING_CREDITS=20
DEFAULT_CREDIT_COST=1
MAX_SESSION_TURNS=6
SIMILARITY_THRESHOLD=0.5

# Authentication
AUTH_MODE=local
MIN_USERNAME_LENGTH=3
MAX_USERNAME_LENGTH=20

# Email (not required)
USE_SES_EMAIL=false
```

---

## Volume Mounts

### FAISS Vector Store

Mount your pre-built FAISS vector store:

```yaml
volumes:
  - ./vector:/app/vector:ro
```

This mounts the local `vector/` directory as read-only inside the container.

**Note**: The vector store must be built before running the container.

### Persistent Data

DynamoDB handles all data persistence, so no additional volumes needed for:
- User data
- Session state
- Message history
- Credit tracking

---

## Docker Compose Configuration

### Service Definition

```yaml
services:
  weight-planner:
    build: .
    image: weight-planner:latest
    container_name: weight-planner-app
    ports:
      - "8501:8501"
    environment:
      # Variables from .env file
    volumes:
      - ./vector:/app/vector:ro
    restart: unless-stopped
    networks:
      - weight-planner-network
```

### Network

Uses bridge network for container isolation:

```yaml
networks:
  weight-planner-network:
    driver: bridge
```

### Restart Policy

```yaml
restart: unless-stopped
```

Container automatically restarts unless manually stopped.

---

## Building for Production

### Multi-Stage Build

For smaller image size, use multi-stage build:

```dockerfile
# Builder stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["streamlit", "run", "Stream_lit_Chat.py"]
```

### Optimize Image Size

```bash
# Use slim base image (already done)
FROM python:3.11-slim

# Remove build dependencies after install
RUN apt-get purge -y gcc g++ && apt-get autoremove -y

# Use .dockerignore to exclude unnecessary files
```

### Security Best Practices

```dockerfile
# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Read-only root filesystem
docker run --read-only --tmpfs /tmp weight-planner
```

---

## Troubleshooting

### Issue: Container exits immediately

**Check logs:**
```bash
docker logs weight-planner-app
```

**Common causes:**
- Missing environment variables
- Invalid AWS credentials
- Invalid OpenAI API key

### Issue: Cannot connect to AWS

**Solutions:**

1. Verify credentials in .env:
   ```bash
   docker exec weight-planner-app env | grep AWS
   ```

2. Test AWS connection:
   ```bash
   docker exec weight-planner-app python -c "import boto3; client = boto3.client('dynamodb', region_name='us-east-2'); print(client.list_tables())"
   ```

3. Check IAM permissions

### Issue: Port 8501 already in use

**Solutions:**

1. Stop conflicting service
2. Change port mapping:
   ```yaml
   ports:
     - "8502:8501"  # Use different host port
   ```

### Issue: Vector store not found

**Solutions:**

1. Verify vector directory exists:
   ```bash
   ls -la vector/
   ```

2. Rebuild FAISS embeddings before running container

3. Check volume mount in docker-compose.yml

### Issue: Container is unhealthy

**Check health:**
```bash
docker inspect weight-planner-app | grep -A 10 Health
```

**Solutions:**
- Increase health check start period
- Check if Streamlit is running
- Verify port 8501 is accessible

---

## Monitoring

### View Resource Usage

```bash
# Container stats
docker stats weight-planner-app

# Resource limits
docker run -d \
  --memory="2g" \
  --cpus="1.5" \
  weight-planner:latest
```

### View Logs

```bash
# View last 100 lines
docker logs --tail 100 weight-planner-app

# Follow logs in real-time
docker logs -f weight-planner-app

# Logs with timestamps
docker logs -t weight-planner-app
```

### Health Monitoring

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' weight-planner-app

# View health check logs
docker inspect --format='{{json .State.Health}}' weight-planner-app | jq
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t weight-planner:latest .

      - name: Run tests
        run: docker run weight-planner:latest python -m pytest

      - name: Push to Docker Hub
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push weight-planner:latest
```

---

## Deployment Options

### AWS ECS

1. Push image to ECR
2. Create ECS task definition
3. Configure environment variables
4. Deploy service

### AWS EC2

```bash
# Install Docker on EC2
sudo yum install docker -y
sudo service docker start

# Pull and run
docker pull weight-planner:latest
docker-compose up -d
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weight-planner
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: weight-planner
        image: weight-planner:latest
        ports:
        - containerPort: 8501
        env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
```

---

## Performance Optimization

### Memory Limits

```yaml
services:
  weight-planner:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### CPU Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
    reservations:
      cpus: '1.0'
```

### Connection Pooling

Already implemented in boto3 for DynamoDB connections.

---

## Cleanup

### Remove Everything

```bash
# Stop and remove containers
docker-compose down

# Remove image
docker rmi weight-planner:latest

# Remove unused images
docker image prune -a

# Remove all unused resources
docker system prune -a
```

---

## Quick Reference

### Common Commands

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Rebuild
docker-compose up -d --build

# Access shell
docker exec -it weight-planner-app bash
```

### Access Application

- **Local**: http://localhost:8501
- **Remote**: http://YOUR_SERVER_IP:8501

---

**Last Updated**: December 14, 2025
**Status**: Docker Configuration Complete
