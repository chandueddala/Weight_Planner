# Weight Planner - Production RAG Service

A production-grade, stateful RAG (Retrieval-Augmented Generation) service for personalized nutrition and fitness guidance using AWS DynamoDB for state management.

## Features

✅ **Stateful Conversations** - Maintains conversation history and context across queries
✅ **User Preferences Storage** - Automatically saves and loads user health metrics (age, weight goals, etc.)
✅ **Credit Management** - Atomic credit tracking with DynamoDB conditional updates
✅ **Full Audit Trail** - Every query and response logged for compliance
✅ **Streamlit Web Interface** - Interactive chat interface with real-time metadata display

## Quick Start

### Prerequisites

- Python 3.8+
- AWS Account with DynamoDB tables configured
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
# Edit .env with your credentials
```

### AWS DynamoDB Setup

Required tables in `us-east-2`:
- **Users** (PK: user_id)
- **UserSessions** (PK: user_id, SK: session_id)
- **UserMessages** (PK: user_id, SK: ts)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup instructions.

### Running the Application

```bash
# Start Streamlit interface
python main.py

# Or directly
streamlit run Stream_lit_Chat.py
```

Navigate to `http://localhost:8501`

## Project Structure

```
Weight_Planner/
├── app/                      # Core DynamoDB persistence modules
│   ├── aws_session.py        # boto3 session management
│   ├── user_store.py         # User & credit management
│   ├── session_store.py      # Stateful session persistence
│   ├── message_store.py      # Audit logging
│   └── stateful_rag.py       # Production RAG service
├── test/                     # Test suite
├── GPTCustomPrompt.py        # Main RAG planner (DynamoDB-integrated)
├── Stream_lit_Chat.py        # Streamlit UI
└── main.py                   # Application entry point
```

Full architecture documentation: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## Usage

### Python API

```python
from GPTCustomPrompt import GPTCustomPromptPlanner

planner = GPTCustomPromptPlanner()

# First query with preferences
prompt, response, docs, metadata = planner.generate(
    user_prompt="What are good protein sources?",
    user_id="user-123",
    age=28,
    gender="male",
    present_weight=70,
    target_weight=75,
    calories=2500
)

print(f"Response: {response}")
print(f"Credits remaining: {metadata['credits_remaining']}")

# Second query - preferences auto-loaded from DynamoDB!
prompt2, response2, docs2, metadata2 = planner.generate(
    user_prompt="What about carbs?",
    user_id="user-123"
    # No need to pass preferences again!
)
```

### Streamlit Interface

1. Fill in user profile (age, gender, weight goals)
2. Submit to get meal plan and forecast
3. Click "💬 Proceed to GPT Chat"
4. Ask nutrition/fitness questions
5. See conversation history and credits in real-time

## Testing

```bash
# Test DynamoDB connectivity
python test/test_dynamo.py

# Test stateful RAG integration
python test/test_stateful_rag.py

# Test GPTCustomPrompt integration
python test/test_gpt_custom_prompt.py
```

## Key Features Explained

### Conversation History

Every conversation turn is stored in DynamoDB and included in subsequent prompts:

```
**Conversation History:**
1. User: What are good protein sources?
2. Assistant: For muscle gain, focus on lean meats, eggs...
3. User: What about carbs?
4. Assistant: Carbs provide energy, especially whole grains...

**Current User Question:**
How much water should I drink?
```

### Credit System

- New users get 20 free credits
- Each query costs 1 credit
- Atomic deduction prevents double-charging
- Fails fast if insufficient credits

### Metadata Tracking

Every response includes:
- `request_id` - Unique identifier for debugging
- `credits_remaining` - Current credit balance
- `latency_ms` - Response time
- `chunks_retrieved` - Number of RAG sources used
- `session_id` - Session identifier

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- AWS Lambda deployment
- Secrets Manager migration
- Cognito authentication
- CloudWatch monitoring
- Cost optimization

## Documentation

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Complete architecture
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [.env.example](.env.example) - Environment configuration template

## Environment Variables

```bash
AWS_PROFILE=default
AWS_REGION=us-east-2
DDB_USERS_TABLE=Users
DDB_SESSIONS_TABLE=UserSessions
DDB_MESSAGES_TABLE=UserMessages
OPENAI_API_KEY=your-key-here
MODEL_NAME=gpt-4-turbo
```

## License

[Your License]

## Contributing

[Your Contributing Guidelines]
