# Production RAG Service - Deployment Guide

## AWS Secrets Manager Migration

For production Lambda deployment, migrate OpenAI API key from `.env` to AWS Secrets Manager.

### Step 1: Store Secret in AWS Secrets Manager

```bash
# Create secret in Secrets Manager
aws secretsmanager create-secret \
  --name prod/openai/api-key \
  --description "OpenAI API Key for RAG service" \
  --secret-string "sk-your-actual-api-key-here" \
  --region us-east-2 \
  --profile default
```

### Step 2: Grant Lambda IAM Role Access

Add this policy to your Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-2:*:secret:prod/openai/api-key-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-2:*:table/Users",
        "arn:aws:dynamodb:us-east-2:*:table/UserSessions",
        "arn:aws:dynamodb:us-east-2:*:table/UserMessages"
      ]
    }
  ]
}
```

### Step 3: Update Code to Fetch Secret

Add this helper to `app/aws_session.py`:

```python
import json
import boto3

def get_openai_api_key() -> str:
    """
    Get OpenAI API key from environment or Secrets Manager.
    
    For local dev: uses OPENAI_API_KEY env var
    For production: fetches from Secrets Manager using OPENAI_SECRET_ID
    """
    # Local development
    local_key = os.getenv("OPENAI_API_KEY")
    if local_key:
        return local_key
    
    # Production - fetch from Secrets Manager
    secret_id = os.getenv("OPENAI_SECRET_ID", "prod/openai/api-key")
    session = get_boto3_session()
    client = session.client("secretsmanager")
    
    response = client.get_secret_value(SecretId=secret_id)
    
    # Secret can be string or JSON
    if "SecretString" in response:
        secret = response["SecretString"]
        try:
            secret_dict = json.loads(secret)
            return secret_dict.get("api_key", secret)
        except json.JSONDecodeError:
            return secret
    
    raise ValueError(f"Could not retrieve secret: {secret_id}")
```

Update `app/stateful_rag.py` initialization:

```python
from app.aws_session import get_openai_api_key

# In StatefulRAGPlanner.__init__():
os.environ["OPENAI_API_KEY"] = get_openai_api_key()
```

### Step 4: Lambda Environment Variables

Set these environment variables in your Lambda configuration:

```
AWS_REGION=us-east-2
DDB_USERS_TABLE=Users
DDB_SESSIONS_TABLE=UserSessions
DDB_MESSAGES_TABLE=UserMessages
DEFAULT_SESSION_ID=default
MODEL_NAME=gpt-4-turbo
OPENAI_SECRET_ID=prod/openai/api-key
```

**Note:** Do NOT set `AWS_PROFILE` in Lambda - it will use the Lambda execution role automatically.

## Cognito Integration

For production user authentication, replace hardcoded `user_id` with Cognito sub from JWT token.

### Lambda Handler Example

```python
import json
from app.stateful_rag import StatefulRAGPlanner

# Initialize once (outside handler for warm starts)
rag = StatefulRAGPlanner()

def lambda_handler(event, context):
    """
    API Gateway Lambda handler with Cognito authentication.
    """
    # Extract user ID from Cognito JWT (API Gateway authorizer)
    user_id = event['requestContext']['authorizer']['claims']['sub']
    
    # Parse request body
    body = json.loads(event['body'])
    question = body.get('question')
    session_id = body.get('session_id', 'default')
    
    # User preferences (from body or user profile)
    preferences = body.get('preferences', {})
    
    try:
        prompt, response, docs, metadata = rag.generate(
            user_prompt=question,
            user_id=user_id,
            session_id=session_id,
            **preferences
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': response,
                'metadata': metadata,
                'documents': docs[:3]  # Return top 3 sources
            })
        }
    
    except ValueError as e:
        # Insufficient credits
        return {
            'statusCode': 402,
            'body': json.dumps({'error': str(e)})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
```

## Monitoring & Logging

All operations use structured JSON logging. Configure CloudWatch log groups:

- Log Group: `/aws/lambda/rag-service`
- Retention: 30 days (production), 7 days (dev)

### Key Metrics to Monitor

1. **Credit Management**
   - Filter: `action = "charge_credits_failed"`
   - Alert: Spike in insufficient credit errors

2. **Errors**
   - Filter: `level = "ERROR"`
   - Alert: Error rate > 1% of requests

3. **Latency**
   - Metric: `latency_ms`
   - Alarm: p99 > 5000ms

4. **DynamoDB Throttling**
   - CloudWatch Metrics: `ConsumedReadCapacityUnits`, `ConsumedWriteCapacityUnits`
   - Alarm: Throttled requests > 0

### CloudWatch Insights Queries

**Top users by query volume:**
```
fields user_id, request_id
| filter action = "generate_start"
| stats count() as query_count by user_id
| sort query_count desc
| limit 20
```

**Average latency by user:**
```
fields user_id, latency_ms
| filter action = "generate_complete"
| stats avg(latency_ms) as avg_latency by user_id
| sort avg_latency desc
```

## Cost Optimization

1. **DynamoDB On-Demand Pricing**
   - Use on-demand billing for unpredictable workloads
   - Switch to provisioned capacity if traffic is consistent

2. **Lambda Memory Tuning**
   - Test with 512MB, 1024MB, 2048MB
   - Find optimal memory/cost balance

3. **FAISS Index Optimization**
   - Use S3 for FAISS index storage
   - Load once per Lambda cold start
   - Consider Lambda EFS for large indexes

4. **Connection Pooling**
   - DynamoDB connections are pooled automatically by boto3
   - Monitor connection metrics in CloudWatch

## Backup & Disaster Recovery

**DynamoDB Point-in-Time Recovery:**
```bash
# Enable PITR for all tables
aws dynamodb update-continuous-backups \
  --table-name Users \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
  --region us-east-2

aws dynamodb update-continuous-backups \
  --table-name UserSessions \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
  --region us-east-2

aws dynamodb update-continuous-backups \
  --table-name UserMessages \
  --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
  --region us-east-2
```

## Performance Tuning

1. **Batch DynamoDB Writes**
   - Current implementation writes 2 messages per turn
   - Consider `batch_write_item` for high-volume scenarios

2. **Session State Compression**
   - If session state grows large, compress `state_json` with gzip
   - DynamoDB item size limit: 400KB

3. **Asynchronous Logging**
   - Move message logging to async queue (SQS) for faster response times
   - Trade-off: eventual consistency in audit logs

4. **FAISS Index Sharding**
   - For large document collections, shard FAISS by source/category
   - Parallel retrieval across shards
