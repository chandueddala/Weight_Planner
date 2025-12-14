# Setup Guide - Weight Planner

Complete setup instructions for the Weight Planner application.

## Prerequisites

### Required Software

- **Python**: Version 3.8 or higher
- **pip**: Python package manager
- **AWS Account**: For DynamoDB access
- **OpenAI Account**: For API access

### Required Accounts

1. **AWS Account**
   - Sign up at https://aws.amazon.com
   - Free tier available (25 GB storage, 200M requests/month)

2. **OpenAI Account**
   - Sign up at https://platform.openai.com
   - Get API key from dashboard
   - GPT-4 Turbo access required

## Installation Steps

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd Weight_Planner
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv myenv
myenv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages installed:**
- `streamlit` - Web interface
- `boto3` - AWS SDK
- `langchain-community` - RAG framework
- `openai` - OpenAI API client
- `bcrypt` - Password hashing
- `python-dotenv` - Environment variables

### 4. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Required variables:**

```bash
# AWS Configuration
AWS_PROFILE=default
AWS_REGION=us-east-2

# DynamoDB Tables
DDB_USERS_TABLE=Users
DDB_SESSIONS_TABLE=UserSessions
DDB_MESSAGES_TABLE=UserMessages

# Session Configuration
DEFAULT_SESSION_ID=default

# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
MODEL_NAME=gpt-4-turbo

# Application Settings
DEFAULT_STARTING_CREDITS=20
DEFAULT_CREDIT_COST=1
MAX_SESSION_TURNS=6
SIMILARITY_THRESHOLD=0.5

# Authentication Configuration
AUTH_MODE=local
MIN_USERNAME_LENGTH=3
MAX_USERNAME_LENGTH=20

# Email Configuration (optional)
USE_SES_EMAIL=false
```

## AWS DynamoDB Setup

### Option 1: AWS Console (Recommended for Beginners)

1. **Login to AWS Console**
   - Go to https://console.aws.amazon.com
   - Select your region (e.g., `us-east-2`)

2. **Create Users Table**
   - Navigate to DynamoDB service
   - Click "Create table"
   - Table name: `Users`
   - Partition key: `user_id` (String)
   - Use default settings
   - Click "Create table"

3. **Create UserSessions Table**
   - Click "Create table"
   - Table name: `UserSessions`
   - Partition key: `user_id` (String)
   - Sort key: `session_id` (String)
   - Use default settings
   - Click "Create table"

4. **Create UserMessages Table**
   - Click "Create table"
   - Table name: `UserMessages`
   - Partition key: `user_id` (String)
   - Sort key: `ts` (String)
   - Use default settings
   - Click "Create table"

### Option 2: AWS CLI (For Advanced Users)

```bash
# Configure AWS CLI
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-2), Output format (json)

# Create Users table
aws dynamodb create-table \
    --table-name Users \
    --attribute-definitions AttributeName=user_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-2

# Create UserSessions table
aws dynamodb create-table \
    --table-name UserSessions \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=session_id,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=session_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-2

# Create UserMessages table
aws dynamodb create-table \
    --table-name UserMessages \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=S \
        AttributeName=ts,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=ts,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-2
```

### Verify Tables Created

```bash
aws dynamodb list-tables --region us-east-2
```

Should show: `Users`, `UserSessions`, `UserMessages`

## AWS Credentials Setup

### Option 1: AWS CLI Configuration (Recommended)

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: From AWS IAM Console
- **AWS Secret Access Key**: From AWS IAM Console
- **Default region**: `us-east-2`
- **Default output format**: `json`

### Option 2: Environment Variables

Add to `.env`:
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-2
```

### Create IAM User (If Needed)

1. Go to AWS IAM Console
2. Click "Users" → "Create user"
3. Username: `weight-planner-app`
4. Attach policy: `AmazonDynamoDBFullAccess`
5. Create user
6. Go to "Security credentials"
7. Create access key
8. Save Access Key ID and Secret Access Key

## OpenAI API Setup

1. **Get API Key**
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)
   - Save it securely

2. **Add to .env**
   ```bash
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Check Balance**
   - Go to https://platform.openai.com/usage
   - Ensure you have credits available

## Testing Setup

### Test 1: Environment Variables

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING'); print('AWS Region:', os.getenv('AWS_REGION', 'MISSING'))"
```

Expected output:
```
OpenAI Key: SET
AWS Region: us-east-2
```

### Test 2: AWS Connection

```bash
python -c "import boto3; client = boto3.client('dynamodb', region_name='us-east-2'); tables = client.list_tables()['TableNames']; print('Tables:', tables)"
```

Expected output:
```
Tables: ['Users', 'UserMessages', 'UserSessions']
```

### Test 3: Authentication Module

```bash
python -c "from app.cognito_auth import validate_email, validate_password; print('Email valid:', validate_email('test@example.com')); valid, msg = validate_password('TestPass123'); print('Password valid:', valid)"
```

Expected output:
```
Email valid: True
Password valid: True
```

### Test 4: User Store

```bash
python test/test_dynamo.py
```

Should show successful user creation and credit operations.

## Running the Application

### Start the App

```bash
streamlit run Stream_lit_Chat.py
```

### Access the Interface

Open browser to: `http://localhost:8501`

### First-Time Setup

1. Click "Sign Up"
2. Enter:
   - Email: valid format (user@example.com)
   - Password: 8+ chars, uppercase, lowercase, number
   - Full Name: your name
3. Click "Create Account"
4. Complete onboarding:
   - Age, gender, height
   - Current weight, target weight
5. View your personalized plan
6. Start chatting with AI assistant

## Troubleshooting

### Issue: "No module named 'streamlit'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Could not connect to DynamoDB"

**Solutions:**
1. Check AWS credentials:
   ```bash
   aws sts get-caller-identity
   ```
2. Verify region in `.env` matches table region
3. Check IAM permissions

### Issue: "OpenAI API key is invalid"

**Solutions:**
1. Verify key starts with `sk-`
2. Check for extra spaces in `.env`
3. Regenerate key in OpenAI dashboard

### Issue: "Table does not exist"

**Solution:**
```bash
# List tables
aws dynamodb list-tables --region us-east-2

# If missing, create them (see AWS DynamoDB Setup above)
```

### Issue: "Invalid email format"

**Solution:**
- Email must match pattern: `user@domain.com`
- Examples: ✅ `test@gmail.com` ❌ `testgmail.com`

### Issue: "Password too weak"

**Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

## Directory Structure

After setup, your directory should look like:

```
Weight_Planner/
├── .env                    # Your configuration (gitignored)
├── .env.example            # Template
├── requirements.txt        # Dependencies
├── app/                    # Core modules
├── GPTCustomPrompt.py      # RAG planner
├── Stream_lit_Chat.py      # Main app
├── vector/                 # FAISS embeddings
└── test/                   # Test files
```

## Configuration Options

### Credit Settings

Adjust in `.env`:
```bash
DEFAULT_STARTING_CREDITS=20    # Credits for new users
DEFAULT_CREDIT_COST=1          # Cost per query
```

### Conversation History

Adjust in `.env`:
```bash
MAX_SESSION_TURNS=6            # Messages to include in context (3 turns)
```

### RAG Settings

Adjust in `.env`:
```bash
SIMILARITY_THRESHOLD=0.5       # Lower = more similar (0.0-1.0)
```

### Model Selection

Adjust in `.env`:
```bash
MODEL_NAME=gpt-4-turbo         # Options: gpt-4-turbo, gpt-4, gpt-3.5-turbo
```

## Next Steps

After successful setup:

1. ✅ Test signup/login flow
2. ✅ Complete onboarding
3. ✅ Try the meal planner
4. ✅ Chat with AI assistant
5. ✅ Check credit tracking
6. ✅ Review conversation history

## Support

For additional help:
- Check [README.md](README.md) for overview
- Check [FEATURES.md](FEATURES.md) for feature details
- Review AWS DynamoDB Console for table status
- Check OpenAI dashboard for API usage

---

**Last Updated**: December 14, 2025
**Status**: Complete Setup Guide
