
# AWS Lambda Deployment (Streamlit)

To deploy the entire Streamlit application serverless on AWS Lambda, we use the **AWS Lambda Web Adapter**.

### 1. Build the Lambda Image
```bash
docker build -f Dockerfile.lambda -t weight-planner-lambda .
```

### 2. Push to Amazon ECR
```bash
# Set variables
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-2
REPO_NAME=weight-planner-lambda

# Create Repo (if not exists)
aws ecr create-repository --repository-name $REPO_NAME --region $REGION

# Login
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Tag and Push
docker tag weight-planner-lambda:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:latest
```

### 3. Deploy to Lambda (via Console)
1. Create a new Lambda function.
2. Select **Container Image**.
3. Choose the image you pushed to ECR.
4. **Configuration**:
   - **Architecture**: x86_64
   - **Timeout**: 60-120 seconds (Streamlit needs time).
   - **Memory**: 1024MB or 2048MB (recommended for RAG/Pandas).
   - **Environment Variables**: Add your `.env` variables here (OPENAI_API_KEY, AWS_REGION, etc.).
5. **Enable Function URL**:
   - Go to Configuration > Function URL.
   - Create Function URL (Auth type: NONE for public access, or IAM).
   - This URL will map to your Streamlit app.

### Notes
- The `Dockerfile.lambda` includes the AWS Lambda Web Adapter extension.
- This adapter acts as a proxy, translating Lambda events to HTTP requests for Streamlit.
- No code changes are required in `Stream_lit_Chat.py`!
