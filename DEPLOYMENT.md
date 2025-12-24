
## Docker Deployment

### 1. Build the Image
```bash
docker build -t weight-planner .
```

### 2. Run with Docker Compose
Ensure your `.env` file is configured, then run:
```bash
docker-compose up -d
```
The application will be available at `http://localhost:8501`.

### 3. AWS Credentials in Docker
The `docker-compose.yml` is configured to use your local AWS credentials if you uncomment the volume mount:
```yaml
    volumes:
      - ~/.aws:/root/.aws:ro
```
Alternatively, pass `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as environment variables.

### 4. Production Docker
For production, push the image to Amazon ECR and deploy to ECS or App Runner.
```bash
# Login to ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-2.amazonaws.com

# Tag and Push
docker tag weight-planner:latest <aws_account_id>.dkr.ecr.us-east-2.amazonaws.com/weight-planner:latest
docker push <aws_account_id>.dkr.ecr.us-east-2.amazonaws.com/weight-planner:latest
```

## Running with Docker (Local)

### Option 1: Docker Compose (Recommended)
This method automatically loads your `.env` file and handles port mapping.

```bash
# Build and run
docker-compose up --build

# Run in background (detached)
docker-compose up -d

# Stop
docker-compose down
```

### Option 2: Docker CLI
If you prefer running the container directly without Compose, you can pass the env file:

```bash
# Build
docker build -t weight-planner .

# Run with .env file
docker run -p 8501:8501 --env-file .env weight-planner
```

### Testing Lambda Docker Locally
To test the Lambda-compatible image locally (mimicking Lambda environment):

```bash
# Build Lambda image
docker build -f Dockerfile.lambda -t weight-planner-lambda .

# Run (maps port 8501 so you can see it)
docker run -p 8501:8501 --env-file .env weight-planner-lambda
```
Note: Since the Lambda image uses the Web Adapter, it behaves like a normal web app when run locally, listening on port 8501.

