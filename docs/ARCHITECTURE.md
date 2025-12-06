# System Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture Diagram](#system-architecture-diagram)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Module Descriptions](#module-descriptions)
6. [Database Schema](#database-schema)
7. [AI/ML Pipeline](#aiml-pipeline)
8. [Security Architecture](#security-architecture)
9. [Deployment Architecture](#deployment-architecture)

---

## Overview

The AI Weight & Meal Planner is built using a modular, layered architecture that separates concerns into distinct components. The application follows the **MVC (Model-View-Controller)** pattern with additional AI/ML integration layers.

### Architecture Principles

1. **Modularity**: Each component has a single responsibility
2. **Scalability**: Designed to handle multiple concurrent users
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: Easy to add new features and data sources
5. **Security**: API keys and sensitive data are protected

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                           │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Streamlit Web Interface                         │   │
│  │  - User Input Forms                                          │   │
│  │  - Data Visualization (Charts, Tables)                       │   │
│  │  - Chat Interface                                            │   │
│  │  - Session State Management                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────┬───────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                             │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Weight Planner  │  │   Meal Planner   │  │  Chat Handler    │  │
│  │  Module          │  │   Module         │  │  Module          │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                     │              │
│           └──────────┬──────────┴──────────┬──────────┘              │
│                      │                     │                         │
└──────────────────────┼─────────────────────┼─────────────────────────┘
                       │                     │
                       ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         AI/ML LAYER                                  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              GPT Integration Layer                            │  │
│  │                                                                │  │
│  │  ┌────────────────────┐    ┌─────────────────────────────┐  │  │
│  │  │ GPTWeightNutrition │    │  GPTCustomPromptPlanner     │  │  │
│  │  │ Planner (RAG)      │    │  (RAG + Conversation)       │  │  │
│  │  └──────┬─────────────┘    └──────────┬──────────────────┘  │  │
│  │         │                               │                     │  │
│  │         └───────────┬───────────────────┘                     │  │
│  │                     │                                         │  │
│  │         ┌───────────▼──────────────┐                         │  │
│  │         │   LangChain Framework    │                         │  │
│  │         │  - QA with Sources Chain │                         │  │
│  │         │  - Prompt Templates      │                         │  │
│  │         └───────────┬──────────────┘                         │  │
│  └─────────────────────┼────────────────────────────────────────┘  │
│                        │                                            │
└────────────────────────┼────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌──────────────────┐           ┌──────────────────┐
│   OpenAI API     │           │  FAISS Vector DB │
│                  │           │                  │
│  - GPT-4-turbo   │           │  - Embeddings    │
│  - GPT-3.5-turbo │           │  - Similarity    │
│  - Embeddings    │           │    Search        │
└──────────────────┘           └──────────────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                  │
│                                                                       │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐            │
│  │  Recipes.csv │   │ Vector Store │   │ User Session │            │
│  │  (10k+ rows) │   │  (FAISS)     │   │    State     │            │
│  └──────────────┘   └──────────────┘   └──────────────┘            │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Presentation Layer

**File**: `Stream_lit_Chat.py`

**Responsibilities**:
- Render UI components (forms, charts, tables)
- Manage user interactions
- Handle session state
- Display chat interface
- Route between different pages

**Key Components**:
```python
├── Navigation System
│   ├── Main Planner Page
│   └── Custom Chat Page
├── User Input Form (Sidebar)
├── Data Visualization
│   ├── Weight Forecast Chart
│   ├── Meal Plan Display
│   └── Nutrition Summary
└── Chat Interface
    ├── Message Display
    ├── Input Handler
    └── Context Expanders
```

### 2. Application Layer

#### 2.1 Weight Planner Module

**File**: `weight_planner.py`

**Class**: `WeightPlanner`

**Purpose**: Calculate and forecast weight changes based on scientific formulas

**Key Methods**:
```python
class WeightPlanner:
    def __init__(self, present_weight_kg, target_weight_kg, age,
                 height_cm, gender, activity_level, weekly_loss_lbs)

    def calculate_bmr(self, weight_kg)
        # Mifflin-St Jeor Equation
        # Male: BMR = 10W + 6.25H - 5A + 5
        # Female: BMR = 10W + 6.25H - 5A - 161

    def simulate(self)
        # Returns: (forecast_df, target_calories, maintenance_calories)
        # Calculates weekly weight progression

    def generate_summary(self)
        # Uses GPT-4 to create motivational summary
```

**Algorithm Flow**:
```
1. Calculate BMR using Mifflin-St Jeor
2. Apply activity factor (1.2 - 1.9)
3. Calculate maintenance calories
4. Determine caloric deficit/surplus
5. Simulate weekly weight changes
6. Generate AI summary
```

#### 2.2 Meal Planner Module

**File**: `meal_planner.py`

**Class**: `MealPlanner`

**Purpose**: Select and optimize daily meal plans

**Key Methods**:
```python
class MealPlanner:
    def __init__(self, df, total_calories, diet_type, api_key)

    def prepare_data(self)
        # Parse ingredients and steps from CSV

    def select_meals(self)
        # Select breakfast, snack, lunch, dinner
        # Optimize by: low fat, high protein, low sugar

    def generate_gpt_annotations(self)
        # Use GPT-3.5 for meal naming and tips

    def display_plan(self)
        # Render complete meal plan with nutrition
```

**Selection Algorithm**:
```
For each meal type:
1. Filter by diet_type (veg/non_veg/vegan)
2. Filter by meal_type (breakfast/lunch/dinner/snack)
3. Filter sugar <= 20%
4. Sort by: low total_fat, high protein, low calories
5. Find closest match to target calories
6. Add to meal plan
```

#### 2.3 Chat Handler Module

**File**: `GPTCustomPrompt.py`

**Class**: `GPTCustomPromptPlanner`

**Purpose**: Handle custom user queries with RAG

**Key Methods**:
```python
class GPTCustomPromptPlanner:
    def __init__(self, vector_path, model_name, temperature)

    def _load_vectorstore(self)
        # Load FAISS index

    def _load_model(self)
        # Initialize GPT-4 and QA chain

    def enrich_prompt(self, user_prompt, age, gender, ...)
        # Add user context to prompt

    def generate(self, user_prompt, ...)
        # Retrieve context, generate response
        # Returns: (prompt, response, doc_summaries)
```

---

## Data Flow

### Weight Planning Flow

```
User Input
    ↓
[Age, Gender, Height, Weight, Activity, Goals]
    ↓
WeightPlanner.simulate()
    ↓
[Calculate BMR] → [Apply Activity Factor] → [Calculate Calories]
    ↓
[Simulate Weekly Progression]
    ↓
WeightPlanner.generate_summary()
    ↓
[GPT-4 API Call]
    ↓
[Display: Chart, Calories, Summary]
```

### Meal Planning Flow

```
Target Calories + Diet Type
    ↓
Load Recipes.csv
    ↓
MealPlanner.prepare_data()
    ↓
[Parse Ingredients & Steps]
    ↓
MealPlanner.select_meals()
    ↓
For each meal type:
    [Filter by diet] → [Filter sugar] → [Sort & Select Best Match]
    ↓
[Selected Meals DataFrame]
    ↓
MealPlanner.generate_gpt_annotations()
    ↓
[GPT-3.5 API Call for Naming & Tips]
    ↓
[Display: Ingredients, Steps, Nutrition, Tips]
```

### RAG-Based Exercise & Nutrition Flow

```
User Profile Data
    ↓
GPTWeightNutritionPlanner.build_prompt()
    ↓
[Create Retrieval Query]
    ↓
FAISS.similarity_search(query, k=7)
    ↓
[Retrieve Context from Vector Store]
    ↓
[Filter by Valid Sources]
    ↓
LangChain QA Chain
    ↓
[Combine: Context + User Profile + Prompt]
    ↓
[GPT-4 API Call]
    ↓
[Display: Exercise Plan, Nutrition Guidance, Sources]
```

### Custom Chat Flow

```
User Question
    ↓
GPTCustomPromptPlanner.generate()
    ↓
[Enrich with User Profile]
    ↓
FAISS.similarity_search_with_score(query, k=7)
    ↓
[Filter by Similarity Score <= 0.5]
    ↓
[Filter by Valid Sources]
    ↓
[Build Enriched Prompt]
    ↓
LangChain QA Chain
    ↓
[GPT-4 Response]
    ↓
[Display: Answer + Prompt + Context Sources]
```

---

## Module Descriptions

### Entry Point: `main.py`

**Purpose**: Application launcher

**Flow**:
```python
1. Create background thread
2. Run: streamlit run Stream_lit_Chat.py --server.headless true
3. Wait 5 seconds
4. Print: "Streamlit app is live at: http://localhost:8501"
```

### UI Controller: `Stream_lit_Chat.py`

**Architecture Pattern**: Page-based routing with session state

**Pages**:
1. **Main Planner**: Weight forecast, meal plan, exercise guidance
2. **Custom Chat**: AI dietitian chatbot

**Session State Variables**:
```python
st.session_state = {
    'page': 'Main Planner' | 'Custom Chat',
    'forecast_df': DataFrame,
    'target_calories': int,
    'maintenance_calories': int,
    'summary_prompt': str,
    'summary_text': str,
    'meal_planner': MealPlanner object,
    'gpt_annotated': bool,
    'gpt_plan': dict,
    'chat_history': list[dict]
}
```

### Core Logic: `weight_planner.py`

**Scientific Basis**: Mifflin-St Jeor Equation (most accurate BMR formula)

**Activity Factors**:
| Level | Factor | Description |
|-------|--------|-------------|
| Sedentary | 1.2 | Little/no exercise |
| Light | 1.375 | Exercise 1-3 days/week |
| Moderate | 1.55 | Exercise 3-5 days/week |
| Very | 1.725 | Exercise 6-7 days/week |
| Super | 1.9 | Physical job + exercise |

**Calorie Calculation**:
```
1 kg body weight = 7700 kcal
Weekly change (kg) × 7700 = Weekly kcal change
Daily adjustment = Weekly kcal change / 7

If weight loss:
    Target calories = Maintenance - Daily adjustment
If weight gain:
    Target calories = Maintenance + Daily adjustment
```

### Recipe Manager: `meal_planner.py`

**Data Structure**:
```python
Recipe = {
    'name': str,
    'meal_type': 'breakfast' | 'lunch' | 'dinner' | 'snack',
    'diet_type': 'veg' | 'non_veg' | 'vegan',
    'ingredients': list[str],
    'steps': list[str],
    'calories': float,
    'protein': float,
    'total_fat': float,
    'sugar': float,
    'sodium': float,
    'carbohydrates': float,
    'minutes': int
}
```

**Meal Distribution**:
- Breakfast: 25% of daily calories
- Snack: 10% of daily calories
- Lunch: 35% of daily calories
- Dinner: 30% of daily calories

### RAG Engine: `gpt_weight_nutrition_planner.py`

**Vector Store Sources**:
```python
valid_sources = [
    "diet",           # Dietary guidelines
    "physical",       # Physical activity recommendations
    "Weight",         # Weight management
    "GymDataset",     # Exercise routines
    "weight_gain",    # Weight gain strategies
    "weight_loss",    # Weight loss protocols
    "Human_Nut",      # Human nutrition science
    "Nut_Science"     # Nutritional science
]
```

**Retrieval Strategy**:
1. Convert user query to retrieval-optimized query
2. Search vector store for top k=7 documents
3. Filter by valid sources
4. Extract snippets (600 chars each)
5. Combine with user profile
6. Send to GPT-4 with context

### Chatbot Engine: `GPTCustomPrompt.py`

**Similarity Filtering**:
```python
# Cosine similarity threshold
score_threshold = 0.5

# Lower score = higher similarity (in FAISS L2 distance)
filtered_docs = [doc for doc, score in docs_and_scores
                 if score <= 0.5]
```

**Context Enrichment**:
- User age, gender, height, weight
- Current and target weight
- Caloric target
- Retrieved document snippets
- Source attribution

---

## Database Schema

### CSV Data: `Calories/Recipes.csv`

**Schema**:
```
Columns: 28 total
├── id (int): Unique recipe ID
├── name (str): Recipe name
├── minutes (int): Cooking time
├── contributor_id (int): Recipe author ID
├── submitted (datetime): Submission date
├── tags (list): Recipe tags
├── nutrition (list): Nutritional values
├── n_steps (int): Number of cooking steps
├── steps (list): Cooking instructions
├── description (str): Recipe description
├── ingredients (list): Ingredient list
├── n_ingredients (int): Ingredient count
├── meal_type (str): breakfast/lunch/dinner/snack
├── diet_type (str): veg/non_veg/vegan
├── calories (float): kcal
├── total_fat (float): % daily value
├── sugar (float): % daily value
├── sodium (float): % daily value
├── protein (float): % daily value
├── saturated_fat (float): % daily value
└── carbohydrates (float): % daily value
```

**Statistics**:
- Total recipes: 10,000+
- Diet types: 3 (veg, non_veg, vegan)
- Meal types: 4 (breakfast, lunch, dinner, snack)

### Vector Store: `vector/`

**Structure**:
```
vector/
├── index.faiss          # FAISS binary index file
└── index.pkl            # Metadata pickle file
```

**Embedding Model**: OpenAI text-embedding-ada-002

**Metadata Structure**:
```python
{
    'source': str,        # Document source name
    'page_content': str   # Original text chunk
}
```

---

## AI/ML Pipeline

### Embedding Generation

```python
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
# Uses: text-embedding-ada-002
# Dimension: 1536
```

### Vector Search

```python
# Similarity search
docs = vectorstore.similarity_search(query, k=7)

# Similarity search with scores
docs_and_scores = vectorstore.similarity_search_with_score(query, k=7)
```

### GPT Models Used

| Model | Use Case | Temperature | Max Tokens |
|-------|----------|-------------|------------|
| GPT-4-turbo | Weight summary | 0.3 | 100 |
| GPT-4-turbo | Exercise & nutrition plan | 0.3 | Default |
| GPT-4-turbo | Custom chat | 0.4 | Default |
| GPT-3.5-turbo | Meal annotations | Default | 500 |

### LangChain Integration

```python
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

chain = load_qa_with_sources_chain(llm, chain_type="stuff")

response = chain.run({
    "input_documents": docs,
    "question": prompt
})
```

**Chain Type**: "stuff"
- Combines all documents into a single prompt
- Suitable for small context windows
- Provides source attribution

---

## Security Architecture

### API Key Management

```python
# Environment-based configuration
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

**Best Practices**:
1. ✅ API keys stored in `.env` (not in code)
2. ✅ `.env` excluded from version control
3. ✅ Environment variables validated at runtime
4. ✅ No hardcoded secrets

### Data Privacy

- **User data**: Stored only in session state (ephemeral)
- **No persistence**: Data cleared on reset/close
- **No logging**: Personal data not logged to files
- **API calls**: Data sent only to OpenAI (encrypted HTTPS)

### Input Validation

```python
# Streamlit number inputs with bounds
age = st.number_input("Age", 18, 100, 24)
height_cm = st.number_input("Height (cm)", 120, 220, 176)
present_weight = st.number_input("Weight (kg)", 40.0, 200.0, 85.0)
```

---

## Deployment Architecture

### Local Deployment

```
User Browser
    ↓ (HTTP)
localhost:8501
    ↓
Streamlit Server (Python)
    ↓
Application Code
    ↓ (HTTPS API Calls)
OpenAI API
```

### Production Deployment (Recommended)

```
User Browser
    ↓ (HTTPS)
Load Balancer
    ↓
Streamlit Cloud / AWS EC2 / Docker Container
    ↓
Application Instance(s)
    ↓
OpenAI API
```

**Deployment Options**:
1. **Streamlit Cloud**: Easiest (free tier available)
2. **AWS EC2**: Full control, scalable
3. **Docker**: Containerized, portable
4. **Heroku**: Simple PaaS deployment

### Scalability Considerations

**Current Limitations**:
- Single-threaded Streamlit app
- Session state per user (RAM intensive)
- No database (stateless)

**Improvements for Scale**:
1. Add Redis for session storage
2. Implement connection pooling for OpenAI API
3. Cache frequently accessed data
4. Use async API calls
5. Implement rate limiting

---

## Performance Optimization

### Caching Strategy

```python
@st.cache_data(show_spinner=False)
def load_recipes_direct(path):
    return pd.read_csv(path)
```

**Cached Components**:
- Recipe CSV loading
- Vector store initialization
- Embedding models

### API Cost Optimization

**Token Usage**:
- Prompts kept concise
- Context limited to k=7 documents
- Max tokens capped where appropriate

**Model Selection**:
- GPT-3.5-turbo for simple tasks (cheaper)
- GPT-4-turbo only for complex reasoning

---

## Error Handling

### Exception Management

```python
try:
    gpt_engine = GPTWeightNutritionPlanner()
    response = gpt_engine.generate(...)
except Exception as e:
    st.error(f"GPT generation failed: {e}")
```

**Error Cases Handled**:
- Missing API keys
- API rate limits
- Network failures
- Invalid user inputs
- Missing data files

---

## Future Architecture Enhancements

### Planned Improvements

1. **Database Layer**
   - PostgreSQL for user profiles
   - Recipe versioning
   - Progress tracking

2. **Authentication**
   - User login/signup
   - OAuth integration
   - Profile management

3. **Microservices**
   - Separate services for:
     - Weight calculation
     - Meal planning
     - Chat handling
   - API Gateway for routing

4. **Real-time Features**
   - WebSocket for live updates
   - Push notifications
   - Progress tracking

5. **Analytics**
   - User behavior tracking
   - A/B testing
   - Performance monitoring

---

**Last Updated**: December 2025
**Version**: 1.0
**Maintained By**: Development Team
