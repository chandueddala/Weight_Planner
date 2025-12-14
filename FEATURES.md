# Features Documentation - Weight Planner

Complete guide to all features in the Weight Planner application.

## Table of Contents

1. [User Authentication](#user-authentication)
2. [Onboarding & Profile Setup](#onboarding--profile-setup)
3. [Personalized Meal Plans](#personalized-meal-plans)
4. [AI Chat Assistant](#ai-chat-assistant)
5. [Turn-Based Conversations](#turn-based-conversations)
6. [Credit System](#credit-system)
7. [Data Persistence](#data-persistence)

---

## User Authentication

### Sign Up

**Features:**
- Email format validation
- Strong password requirements
- Automatic username generation
- Unique email enforcement

**Email Validation:**
- ✅ Valid: `user@example.com`, `test@gmail.com`
- ❌ Invalid: `invalid-email`, `user@`, `@domain.com`

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)

**Example:**
- ✅ Valid: `SecurePass123`, `MyPassword1`
- ❌ Invalid: `weak`, `nodigits`, `12345678`

**Security:**
- Bcrypt password hashing (cost factor 12)
- Email stored in plaintext for login
- Password never stored in plaintext
- Email verified set to `true` automatically

### Login

**Features:**
- Email and password authentication
- Professional error messages
- Session management
- Last login tracking

**Error Messages:**
- "We couldn't find an account with this email address..."
- "The password you entered is incorrect..."
- "This account is not configured for password login..."

### Session Management

**Features:**
- Streamlit session state
- Persistent across page reloads
- Automatic logout option
- User data cached in session

**Session Data:**
```python
{
    "authenticated": True,
    "user_id": "uuid-string",
    "email": "user@example.com",
    "full_name": "John Doe",
    "username": "johndoe123",
    "credits_remaining": 20,
    "onboarding_completed": True,
    "email_verified": True
}
```

---

## Onboarding & Profile Setup

### Welcome Screen

**Information Displayed:**
- Available free credits (20)
- Features overview
- Important disclaimers

**Disclaimers:**
- Prototype for educational purposes only
- Not for medical advice
- Consult healthcare professionals

**Security Notices:**
- AWS secure data storage
- Email validation completed
- Password encryption active

### Profile Input

**Required Fields:**
1. **Age**: 18-100 years
2. **Gender**: Male/Female/Other
3. **Height**: Centimeters
4. **Current Weight**: Kilograms
5. **Target Weight**: Kilograms
6. **Activity Level**: Sedentary to Very Active

**Calculations:**
- BMI calculation
- Caloric target (TDEE-based)
- Weight change per week
- Time to reach goal

---

## Personalized Meal Plans

### Meal Plan Generation

**Features:**
- Custom calorie distribution
- Macronutrient breakdown
- Sample meals for each time
- Portion sizes

**Meal Times:**
- Breakfast (7:00 AM)
- Mid-Morning Snack (10:00 AM)
- Lunch (1:00 PM)
- Evening Snack (4:00 PM)
- Dinner (7:00 PM)
- Post-Dinner (Optional)

**Example Meal:**
```
Breakfast (Target: 458 kcal)
- 2 slices whole wheat toast
- 1 boiled egg
- 1 glass milk
- 1 small banana
```

### Weight Forecast

**Display:**
- Weekly weight progression
- Target achievement timeline
- Line chart visualization
- Healthy weight loss rate (0.5-1 kg/week)

**Example:**
```
Week 1: 85.0 kg
Week 2: 84.5 kg
Week 3: 84.0 kg
...
Week 20: 75.0 kg (TARGET REACHED!)
```

### Macronutrient Breakdown

**Percentages:**
- Carbohydrates: 50-55%
- Protein: 20-25%
- Fats: 20-25%

**Display:**
- Pie chart visualization
- Grams per day
- Calories per gram

---

## AI Chat Assistant

### RAG-Powered Responses

**Features:**
- Retrieval-Augmented Generation
- FAISS vector search
- Scientific nutrition data
- Context-aware answers

**Knowledge Sources:**
- Diet guidelines
- Physical activity recommendations
- Weight management science
- Gym workout data
- Nutrition science
- Human nutrition facts

**Similarity Threshold:**
- Default: 0.5 (adjustable in .env)
- Lower = more similar required
- Filters irrelevant content

### Personalized Responses

**User Context Included:**
- Age, gender, height
- Current weight, target weight
- Caloric target
- Conversation history

**Example Prompt to LLM:**
```
User wants to lose weight. Answer using provided context.

User Details:
- Age: 24
- Gender: male
- Height: 176 cm
- Current Weight: 85.0 kg
- Target Weight: 75.0 kg
- Caloric Target: 1833 kcal/day

Conversation History:
Turn 1:
- User: What measurements to take?
- Assistant: For a 24-year-old male...

Current User Question:
How much protein should I consume?
```

### Response Metadata

**Displayed After Each Response:**
- 💳 Credits Remaining
- ⏱️ Response Time (milliseconds)
- 📄 Chunks Retrieved (RAG sources)

**Example:**
```
💳 Credits Remaining: 19 | ⏱️ Response Time: 1234 ms | 📄 Chunks: 5
```

### Expandable Sections

**📄 Prompt Sent:**
- Full prompt sent to LLM
- Shows user context
- Shows conversation history
- Shows instructions

**📄 Context Source:**
- Retrieved document chunks
- Source identification
- Similarity scores
- Original text snippets

---

## Turn-Based Conversations

### Display Format

**Structure:**
```
💬 Conversation Turn 1
  👤 User: [question]
  🤖 Assistant: [response]
  💳 [metadata]
─────────────────────────

💬 Conversation Turn 2
  👤 User: [question]
  🤖 Assistant: [response]
  💳 [metadata]
```

**Benefits:**
- Clear conversation flow
- Easy to reference specific turns
- No confusion with numbering
- Visual separation between turns

### LLM Context Format

**Before (Confusing):**
```
1. User: question 1
2. Assistant: answer 1
3. User: question 2
4. Assistant: answer 2
```
❌ Looks like 4 separate items

**After (Clear):**
```
Turn 1:
- User: question 1
- Assistant: answer 1

Turn 2:
- User: question 2
- Assistant: answer 2
```
✅ Clearly shows 2 conversation turns

### History Limit

**Configuration:**
- Last 6 messages = 3 turns
- Adjustable via `MAX_SESSION_TURNS=6` in .env
- Prevents context overflow
- Maintains recent relevance

---

## Credit System

### Credit Allocation

**New Users:**
- Starting credits: 20 (configurable)
- Set via `DEFAULT_STARTING_CREDITS=20` in .env

**Cost Per Query:**
- Default: 1 credit per question
- Set via `DEFAULT_CREDIT_COST=1` in .env

### Credit Tracking

**Features:**
- Atomic DynamoDB updates
- Prevents double-charging
- Conditional check-and-set
- Fail-fast on insufficient credits

**Implementation:**
```python
# Atomic credit deduction
charge_credits(user_id, cost=1, request_id="uuid")
```

**Error Handling:**
- Returns error if credits < cost
- No LLM call if insufficient credits
- Clear error message to user

### Credit Display

**Locations:**
1. **Sidebar**: User profile shows remaining credits
2. **After Each Response**: Metadata line
3. **Insufficient Credits Warning**: Before chat input

**Example Display:**
```
User: johndoe123
Email: john@example.com
Credits: 15
```

### Credit Warnings

**Low Credits:**
```
⚠️ You have 3 credits remaining
```

**No Credits:**
```
⚠️ You have no credits remaining. Please contact support.
```

---

## Data Persistence

### DynamoDB Tables

**Users Table:**
```python
{
    "user_id": "uuid",
    "email": "user@example.com",
    "password_hash": "bcrypt-hash",
    "full_name": "John Doe",
    "username": "johndoe123",
    "credits_remaining": 20,
    "email_verified": True,
    "onboarding_completed": True,
    "created_at": "2025-12-14T10:30:00Z",
    "last_login": "2025-12-14T11:00:00Z"
}
```

**UserSessions Table:**
```python
{
    "user_id": "uuid",
    "session_id": "default",
    "recent_turns": [
        {"role": "user", "text": "question"},
        {"role": "assistant", "text": "answer"}
    ],
    "preferences": {
        "age": 24,
        "gender": "male",
        "height_cm": 176,
        "present_weight": 85.0,
        "target_weight": 75.0,
        "calories": 1833
    },
    "last_retrieval": [...],
    "updated_at": "2025-12-14T11:15:00Z"
}
```

**UserMessages Table:**
```python
{
    "user_id": "uuid",
    "ts": "2025-12-14T11:15:30.123456",
    "request_id": "uuid",
    "session_id": "default",
    "role": "user",
    "text": "How much protein?",
    "retrieval_meta": [...]
}
```

### Auto-Save Features

**What's Saved Automatically:**
- User preferences (age, weight, goals)
- Conversation history (last 6 messages)
- All messages (full audit trail)
- Credit transactions
- Last login timestamps

**When It's Saved:**
- After each chat query
- On preference updates
- On credit deduction
- On session state changes

---

## Additional Features

### Reset Button

**Function:** Clears all session state except authentication
**Preserves:**
- Login session
- User ID, email, credits
- Onboarding status

**Clears:**
- Chat history
- Meal plans
- Weight forecasts
- Form inputs

### Instructions Page

**Content:**
- How to use the planner
- Chat assistant tips
- Credit management info
- Troubleshooting help

### Navigation

**Sidebar Buttons:**
- 📖 View Instructions
- 🔁 Reset Everything
- 💬 Proceed to GPT Chat

**Page States:**
- Main Planner
- GPT Chat
- Instructions

---

## Feature Comparison

### Before vs After Improvements

**Email Verification:**
- Before: Complex verification flow with codes
- After: Simple email format validation

**Chat Display:**
- Before: Messages numbered 1, 2, 3, 4, 5, 6
- After: Turns numbered 1, 2, 3 (grouped User + Assistant)

**UI Components:**
- Before: Custom HTML with theme issues
- After: Native Streamlit components (theme-aware)

---

## Coming Soon

**Potential Future Features:**
- Password reset functionality
- Profile editing
- Credit purchase system
- Export meal plans
- Share plans with others
- Mobile responsive design

---

**Last Updated**: December 14, 2025
**Status**: Complete Feature Documentation
