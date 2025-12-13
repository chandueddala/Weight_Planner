# Production RAG Service - Project Structure

## Directory Layout

```
Weight_Planner/
├── app/                              # Core application modules
│   ├── __init__.py                   # Package initialization
│   ├── aws_session.py                # boto3 session & DynamoDB table mgmt
│   ├── user_store.py                 # User management with atomic credits
│   ├── session_store.py              # Stateful session management
│   ├── message_store.py              # Idempotent message logging
│   └── stateful_rag.py               # Production RAG service (main entry)
│
├── test/                             # Test suite
│   ├── test_dynamo.py                # Basic DynamoDB connectivity test
│   └── test_stateful_rag.py          # End-to-end RAG service test
│
├── vector/                           # FAISS vector store
│   ├── index.faiss
│   └── index.pkl
│
├── docs/                             # Documentation PDFs
├── .env                              # Local environment config (gitignored)
├── .env.example                      # Environment template
├── requirements.txt                  # Python dependencies
├── DEPLOYMENT.md                     # Production deployment guide
└── README.md                         # Project documentation
```

## Module Overview

### `app/aws_session.py`
- **Purpose**: Centralized boto3 session management
- **Functions**:
  - `get_boto3_session()` - Returns configured boto3 session
  - `get_ddb_tables()` - Returns Users, UserSessions, UserMessages table resources
- **Configuration**: Uses `AWS_PROFILE`, `AWS_REGION` from environment

### `app/user_store.py`
- **Purpose**: User CRUD and credit management
- **Functions**:
  - `get_or_create_user(user_id, email, starting_credits)` - User provisioning
  - `charge_credits(user_id, cost, request_id)` - Atomic credit deduction
  - `get_user_credits(user_id)` - Query current balance
- **Key Features**: 
  - Atomic updates with `ConditionExpression`
  - Prevents negative credits
  - Structured JSON logging

### `app/session_store.py`
- **Purpose**: Stateful conversation session management
- **Functions**:
  - `load_state(user_id, session_id)` - Load session state
  - `save_state(user_id, session_id, state)` - Persist session state
  - `append_turn(state, user_text, assistant_text, max_turns)` - Add conversation turn
  - `update_retrieval_context(state, retrieval_results)` - Track retrieval history
  - `update_preferences(state, preferences)` - Store user preferences
  - `build_context_prompt(state)` - Generate context for RAG query
- **State Structure**:
  ```python
  {
    "summary": str,              # Conversation summary
    "recent_turns": [            # Recent conversation history
      {"role": "user", "text": "..."},
      {"role": "assistant", "text": "..."}
    ],
    "preferences": {             # User preferences
      "age": 28,
      "gender": "male",
      "height_cm": 175,
      ...
    },
    "last_retrieval": [          # Last retrieval results
      {"source": "...", "chunk_id": "...", "score": 0.23}
    ]
  }
  ```

### `app/message_store.py`
- **Purpose**: Audit logging for all user/assistant messages
- **Functions**:
  - `log_message(...)` - Idempotent message logging
  - `get_user_message_history(user_id, session_id, limit)` - Query message history
- **Key Features**:
  - Deterministic timestamp keys: `{iso_ts}#{request_id}#{role}`
  - Prevents duplicate logging on retries
  - Captures retrieval metadata, model, latency, tokens

### `app/stateful_rag.py`
- **Purpose**: Main RAG service orchestrating all components
- **Class**: `StatefulRAGPlanner`
- **Key Method**: `generate(user_prompt, user_id, session_id, preferences...)`
- **Workflow**:
  1. Generate unique `request_id`
  2. Get/create user
  3. Charge credits (fail-fast if insufficient)
  4. Load session state
  5. Update preferences
  6. Build context-aware retrieval query
  7. Run FAISS similarity search
  8. Generate LLM response
  9. Log user message
  10. Log assistant response
  11. Update session state
  12. Save session
  13. Return response + metadata

## Data Flow

```
User Request
    ↓
[StatefulRAGPlanner.generate()]
    ↓
┌─────────────────────────────────┐
│ 1. User Management              │
│    - get_or_create_user()       │
│    - charge_credits()           │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 2. Session Management           │
│    - load_state()               │
│    - update_preferences()       │
│    - build_context_prompt()     │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 3. RAG Pipeline                 │
│    - FAISS retrieval            │
│    - Build enriched prompt      │
│    - Call ChatOpenAI            │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 4. Audit Logging                │
│    - log_message(user)          │
│    - log_message(assistant)     │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│ 5. State Persistence            │
│    - append_turn()              │
│    - update_retrieval_context() │
│    - save_state()               │
└─────────────────────────────────┘
    ↓
Response + Metadata
```

## Environment Configuration

Required environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_PROFILE` | AWS CLI profile | `default` |
| `AWS_REGION` | AWS region | `us-east-2` |
| `DDB_USERS_TABLE` | Users table name | `Users` |
| `DDB_SESSIONS_TABLE` | Sessions table name | `UserSessions` |
| `DDB_MESSAGES_TABLE` | Messages table name | `UserMessages` |
| `DEFAULT_SESSION_ID` | Default session ID | `default` |
| `OPENAI_API_KEY` | OpenAI API key (local) | - |
| `OPENAI_SECRET_ID` | Secrets Manager ID (prod) | - |
| `MODEL_NAME` | OpenAI model | `gpt-4-turbo` |

## Testing

### Run Basic DynamoDB Test
```bash
python test/test_dynamo.py
```
Expected output:
- STS caller identity
- List of DynamoDB tables
- Successful put_item to Users table

### Run End-to-End RAG Test
```bash
python test/test_stateful_rag.py
```
Expected output:
- User created with 20 credits
- RAG response generated
- Credits deducted (19 remaining)
- 2 messages logged (user + assistant)
- Session state updated with preferences and conversation history
- Second query processed with session continuity

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- AWS Secrets Manager migration
- Cognito JWT integration
- Lambda configuration
- Monitoring & logging setup
- Cost optimization strategies

## Key Design Decisions

1. **Atomic Credit Operations**: Uses DynamoDB `ConditionExpression` to prevent race conditions and negative credits
2. **Idempotent Logging**: Deterministic timestamp keys prevent duplicate messages on retries
3. **Stateful Sessions**: Maintains conversation history, preferences, and retrieval context per user session
4. **Separation of Concerns**: DB logic separated from RAG logic for testability and maintainability
5. **Structured Logging**: All operations emit JSON logs with `request_id` for tracing
6. **Environment-Based Config**: No hardcoded credentials; uses boto3 profiles locally, IAM roles in production

## Next Steps

1. **Add Cognito Integration**: Replace `user_id = "test-user-1"` with JWT sub
2. **Implement Summary Generation**: Add periodic conversation summarization
3. **Add Rate Limiting**: Track requests per user per time window
4. **Add Retry Logic**: Exponential backoff for transient failures
5. **Optimize FAISS**: Implement index sharding for large document sets
6. **Add Metrics**: Custom CloudWatch metrics for business KPIs
