# Weight Planner - AI-Powered Nutrition & Fitness Assistant

A production-grade RAG (Retrieval-Augmented Generation) application for personalized nutrition and fitness guidance with AWS DynamoDB persistence and user authentication.

## Overview

Weight Planner helps users achieve their weight goals through AI-powered personalized nutrition and fitness advice. The system maintains conversation history, tracks user metrics, and provides contextual recommendations based on scientific nutrition data.

## Key Features

✅ **User Authentication** - Secure signup/login with bcrypt password hashing
✅ **Personalized Plans** - Custom meal and workout plans based on user metrics
✅ **AI Chat Assistant** - RAG-powered chat for nutrition and fitness questions
✅ **Conversation History** - Context-aware responses using turn-based chat format
✅ **Credit System** - 20 free credits per user, atomic credit tracking
✅ **AWS DynamoDB** - Persistent storage for users, sessions, and messages
✅ **Email Validation** - Valid email format required for signup

## Quick Start

### Prerequisites

- Python 3.8+
- AWS Account with DynamoDB access
- OpenAI API key

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd Weight_Planner

# Create virtual environment
python -m venv myenv
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials and OpenAI API key
```

### AWS DynamoDB Setup

Create these tables in your AWS region (default: `us-east-2`):

**Required Tables:**
- `Users` - Primary Key: `user_id` (String)
- `UserSessions` - Primary Key: `user_id` (String), Sort Key: `session_id` (String)
- `UserMessages` - Primary Key: `user_id` (String), Sort Key: `ts` (String)

See [SETUP.md](SETUP.md) for detailed AWS configuration.

### Run the Application

```bash
# Start Streamlit app
streamlit run Stream_lit_Chat.py
```

Navigate to `http://localhost:8501`

## Usage

### 1. Sign Up / Login

- Create account with valid email and strong password
- Email format validated (user@example.com)
- Password requirements: 8+ chars, uppercase, lowercase, number

### 2. Complete Onboarding

- Enter your age, gender, height
- Set current weight and target weight
- System calculates caloric target

### 3. Get Your Plan

- Receive personalized meal plan
- View weight loss/gain forecast
- See macronutrient breakdown

### 4. Chat with AI Assistant

- Ask nutrition questions
- Get fitness recommendations
- Context-aware responses based on your metrics
- Conversation history tracked in turns

## Project Structure

```
Weight_Planner/
├── app/                       # Core modules
│   ├── auth_pages.py          # Login/signup UI
│   ├── cognito_auth.py        # Authentication logic
│   ├── onboarding.py          # User onboarding flow
│   ├── user_store.py          # User & credit management
│   ├── session_store.py       # Session persistence
│   └── message_store.py       # Message logging
├── GPTCustomPrompt.py         # RAG planner with turn-based prompts
├── Stream_lit_Chat.py         # Main Streamlit interface
├── weight_planner.py          # Weight loss calculations
├── meal_planner.py            # Meal plan generator
└── vector/                    # FAISS embeddings (nutrition data)
```

## Environment Configuration

Edit `.env` file:

```bash
# AWS Configuration
AWS_PROFILE=default
AWS_REGION=us-east-2

# DynamoDB Tables
DDB_USERS_TABLE=Users
DDB_SESSIONS_TABLE=UserSessions
DDB_MESSAGES_TABLE=UserMessages

# OpenAI API
OPENAI_API_KEY=your-openai-key-here
MODEL_NAME=gpt-4-turbo

# Application Settings
DEFAULT_STARTING_CREDITS=20
DEFAULT_CREDIT_COST=1
```

## Features

### Turn-Based Chat Display

Conversations displayed as clear turns (not individual numbered messages):

```
💬 Conversation Turn 1
  User: What measurements to take?
  Assistant: For a 24-year-old male...
─────────────────────────────

💬 Conversation Turn 2
  User: How much protein?
  Assistant: Based on your weight...
```

See [FEATURES.md](FEATURES.md) for complete feature documentation.

## Credit System

- **New users**: 20 free credits
- **Cost per query**: 1 credit
- **Atomic tracking**: Prevents double-charging
- **Real-time display**: Credits shown after each response

## Testing

```bash
# Test authentication
python -c "from app.cognito_auth import validate_email; print(validate_email('test@example.com'))"

# Test DynamoDB connection
python test/test_dynamo.py

# Test RAG integration
python test/test_gpt_custom_prompt.py
```

## Documentation

- [SETUP.md](SETUP.md) - Detailed setup and configuration
- [FEATURES.md](FEATURES.md) - Complete feature documentation
- [.env.example](.env.example) - Environment variable template

## Support

For issues or questions:
1. Check [SETUP.md](SETUP.md) for configuration help
2. Check [FEATURES.md](FEATURES.md) for feature details
3. Review console logs for error messages

## Security

- ✅ Bcrypt password hashing (cost factor 12)
- ✅ Email format validation
- ✅ AWS IAM for DynamoDB access
- ✅ Session-based authentication
- ✅ Environment variables for secrets

## License

[Your License Here]

## Version

**Last Updated**: December 14, 2025
**Status**: Production Ready
