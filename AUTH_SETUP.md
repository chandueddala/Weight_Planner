# Authentication Setup Guide

This guide explains how to set up and use the authentication system for the Weight Planner application.

## Quick Start (Local Development)

The application is configured to use **local authentication** with bcrypt password hashing by default. This allows you to start developing and testing immediately without AWS Cognito setup.

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New authentication dependencies added:
- `bcrypt==4.2.1` - Password hashing
- `email-validator==2.2.0` - Email validation
- `boto3==1.35.90` - AWS SDK (for DynamoDB)

### 2. Configure Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key authentication variables:
```bash
AUTH_MODE=local              # Use local auth (no Cognito required)
MIN_USERNAME_LENGTH=3        # Minimum username length
MAX_USERNAME_LENGTH=20       # Maximum username length
DEFAULT_STARTING_CREDITS=20  # Credits for new users
```

### 3. Run the Application

```bash
streamlit run Stream_lit_Chat.py
```

### 4. Create Your First User

1. Navigate to http://localhost:8501
2. Click "Sign Up"
3. Fill in:
   - Full Name: Your Name
   - Email: your.email@example.com
   - Password: At least 8 characters with uppercase, lowercase, and number
   - Confirm Password
4. Check "I agree to the Terms of Service"
5. Click "Create Account"

Your unique username will be auto-generated and displayed!

## Features

### ✅ Implemented

- **User Registration** - Sign up with email, password, and name
- **User Login** - Secure bcrypt password hashing
- **Unique Usernames** - Auto-generated from name or email
- **Welcome Page** - First-time user onboarding with instructions
- **Credits System** - 20 free credits per new user
- **Session Management** - Stay logged in across pages
- **Protected Routes** - Chat requires authentication and credits
- **User Profile Sidebar** - Shows username, email, and credits
- **Real-time Credit Updates** - Credits update after each AI query

### 📊 User Profile Schema

DynamoDB Users table schema:

```python
{
  "user_id": str,              # Primary key (UUID)
  "email": str,                # User email (indexed for lookups)
  "full_name": str,            # User's full name
  "username": str,             # Unique username (indexed)
  "password_hash": str,        # Bcrypt hashed password
  "email_verified": bool,      # Email verification status
  "auth_provider": str,        # "local" or "cognito"
  "credits_remaining": int,    # Current credit balance
  "plan": str,                 # User plan type
  "created_at": str,           # ISO timestamp
  "last_login": str,           # ISO timestamp
  "onboarding_completed": bool # Onboarding status
}
```

## DynamoDB Setup

### Required Tables

1. **Users** table
   - Primary Key: `user_id` (String)
   - Recommended GSI: `email-index` on `email` field
   - Recommended GSI: `username-index` on `username` field

2. **UserSessions** table (already exists)
   - Primary Key: `user_id` (String)
   - Sort Key: `session_id` (String)

3. **UserMessages** table (already exists)
   - Primary Key: `user_id` (String)
   - Sort Key: `ts` (String)

### Adding Global Secondary Indexes (Optional but Recommended)

For efficient email and username lookups, add GSIs:

```bash
# Email index
aws dynamodb update-table \
  --table-name Users \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --global-secondary-index-updates \
    "[{\"Create\":{\"IndexName\":\"email-index\",\"KeySchema\":[{\"AttributeName\":\"email\",\"KeyType\":\"HASH\"}],\"Projection\":{\"ProjectionType\":\"ALL\"},\"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}}}]" \
  --region us-east-2

# Username index
aws dynamodb update-table \
  --table-name Users \
  --attribute-definitions AttributeName=username,AttributeType=S \
  --global-secondary-index-updates \
    "[{\"Create\":{\"IndexName\":\"username-index\",\"KeySchema\":[{\"AttributeName\":\"username\",\"KeyType\":\"HASH\"}],\"Projection\":{\"ProjectionType\":\"ALL\"},\"ProvisionedThroughput\":{\"ReadCapacityUnits\":5,\"WriteCapacityUnits\":5}}}]" \
  --region us-east-2
```

**Note**: If GSIs are not created, the system will fall back to table scans (less efficient but functional for development).

## Password Security

### Local Auth Mode

- Passwords are hashed using **bcrypt** with cost factor 12
- Passwords stored in DynamoDB are hashed and cannot be reversed
- Password requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number

### Security Best Practices

✅ **For Production**:
- Migrate to AWS Cognito for enhanced security features
- Enable MFA (Multi-Factor Authentication)
- Implement email verification
- Use HTTPS for all connections
- Rotate database credentials regularly

## Testing the Authentication Flow

### 1. Test Signup

```
1. Navigate to signup page
2. Enter valid details
3. Verify username is auto-generated
4. Confirm user created in DynamoDB
5. Check that 20 credits are assigned
```

### 2. Test Login

```
1. Navigate to login page
2. Enter email and password from signup
3. Verify successful login
4. Check sidebar shows username and credits
```

### 3. Test Onboarding

```
1. After first signup, verify welcome page appears
2. Review features, credits, and instructions
3. Click "Let's Get Started"
4. Verify redirected to main app
5. On next login, verify onboarding is skipped
```

### 4. Test Credit System

```
1. Complete weight planning form
2. Navigate to GPT Chat
3. Ask a question (costs 1 credit)
4. Verify credits decrease from 20 to 19
5. Check sidebar updates immediately
6. Deplete all credits
7. Verify chat access is blocked
```

### 5. Test Session Persistence

```
1. Log in
2. Navigate through different pages
3. Refresh browser
4. Verify still logged in
5. Click logout
6. Verify redirected to login
7. Verify cannot access protected pages
```

## Migrating to AWS Cognito (Optional)

For production deployment with AWS Cognito:

### 1. Create Cognito User Pool

```bash
aws cognito-idp create-user-pool \
  --pool-name weight-planner-users \
  --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true}" \
  --auto-verified-attributes email \
  --region us-east-2
```

### 2. Create App Client

```bash
aws cognito-idp create-user-pool-client \
  --user-pool-id <your-pool-id> \
  --client-name weight-planner-app \
  --no-generate-secret \
  --region us-east-2
```

### 3. Update Environment

```bash
AUTH_MODE=cognito
COGNITO_USER_POOL_ID=your-pool-id
COGNITO_CLIENT_ID=your-client-id
COGNITO_REGION=us-east-2
```

### 4. Update cognito_auth.py

The `cognito_auth.py` module is designed to support both local and Cognito modes. To enable Cognito:

1. Install additional dependency: `pip install pycognito`
2. Implement Cognito signup/login functions in `cognito_auth.py`
3. Update auth flow to use Cognito SDK

## Troubleshooting

### Issue: "Email already registered"
- **Solution**: Email is already in use. Try logging in or use a different email.

### Issue: "Invalid email or password"
- **Solution**: Check email spelling and password. Passwords are case-sensitive.

### Issue: GSI warnings in logs
- **Solution**: This is normal if GSIs aren't created. System uses table scans as fallback.

### Issue: Credits not updating
- **Solution**: Refresh the page or check that `update_credits_in_session()` is called after queries.

### Issue: Can't access chat even with credits
- **Solution**: Verify you've completed the weight planner form first to unlock chat.

## File Structure

```
Weight_Planner/
├── app/
│   ├── cognito_auth.py      # Authentication logic
│   ├── auth_pages.py        # Streamlit login/signup UI
│   ├── onboarding.py        # Welcome page and instructions
│   ├── user_store.py        # User management (extended)
│   └── ...
├── Stream_lit_Chat.py       # Main app (with auth integration)
├── requirements.txt         # Dependencies (updated)
└── .env.example            # Environment template (updated)
```

## Support

For questions or issues:
- Check the [README.md](README.md)
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Contact development team

---

**Last Updated**: December 2025
