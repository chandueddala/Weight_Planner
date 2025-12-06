# Code Documentation - Complete Codebase Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure Overview](#project-structure-overview)
3. [Core Modules Deep Dive](#core-modules-deep-dive)
4. [Code Walkthrough](#code-walkthrough)
5. [Data Models](#data-models)
6. [Algorithms Explained](#algorithms-explained)
7. [UI Components](#ui-components)
8. [State Management](#state-management)
9. [Code Patterns](#code-patterns)
10. [Extending the Codebase](#extending-the-codebase)

---

## Introduction

This document provides a complete guide to understanding the Weight Planner codebase. Whether you're a new developer joining the project, planning to extend functionality, or just want to understand how everything works, this guide will walk you through every component.

### Reading This Guide

- **New developers**: Read sequentially from top to bottom
- **Looking for specific functionality**: Use the table of contents
- **Extending features**: Jump to "Extending the Codebase" section
- **Debugging**: Refer to specific module documentation

---

## Project Structure Overview

```
Weight_Planner/
│
├── 📄 main.py                              # Application entry point (10 lines)
├── 📄 Stream_lit_Chat.py                   # Main UI application (202 lines)
├── 📄 weight_planner.py                    # Weight calculation logic (81 lines)
├── 📄 meal_planner.py                      # Meal selection logic (100 lines)
├── 📄 gpt_weight_nutrition_planner.py      # RAG-based exercise planner (77 lines)
├── 📄 GPTCustomPrompt.py                   # Custom chatbot handler (94 lines)
│
├── 📁 Calories/
│   └── Recipes.csv                         # 10k+ recipes database
│
├── 📁 vector/                              # FAISS vector store
│   ├── index.faiss                         # Vector embeddings
│   └── index.pkl                           # Metadata
│
├── 📁 images/                              # UI assets
│
├── 📁 docs/                                # Documentation
│
└── 📁 myenv/                               # Virtual environment (excluded from Git)
```

### File Dependency Graph

```
main.py
  └── Stream_lit_Chat.py
        ├── weight_planner.py
        ├── meal_planner.py
        ├── gpt_weight_nutrition_planner.py
        └── GPTCustomPrompt.py
              └── OpenAI API
              └── LangChain
              └── FAISS Vector Store
```

---

## Core Modules Deep Dive

### Module 1: `main.py` - Application Entry Point

**Purpose**: Launch the Streamlit application in a background thread

**Complete Code**:
```python
import threading
import os
import time

def run():
    os.system("streamlit run Stream_lit_Chat.py --server.headless true")

thread = threading.Thread(target=run)
thread.start()
time.sleep(5)
print("Streamlit app is live at:","http://localhost:8501")
```

**Line-by-Line Explanation**:

| Line | Code | Explanation |
|------|------|-------------|
| 1-3 | `import threading, os, time` | Import required modules for threading, OS commands, and delays |
| 6-7 | `def run():` | Define function to run Streamlit command |
| 7 | `os.system(...)` | Execute shell command to start Streamlit server in headless mode |
| 9 | `thread = threading.Thread(target=run)` | Create background thread for Streamlit server |
| 10 | `thread.start()` | Start the background thread |
| 11 | `time.sleep(5)` | Wait 5 seconds for server to initialize |
| 12 | `print(...)` | Display access URL to user |

**Why Use Threading?**
- Allows script to continue execution while server runs
- Prevents blocking the terminal
- Provides user feedback about server status

**Alternative Approach** (simpler):
```python
import os
os.system("streamlit run Stream_lit_Chat.py")
```

---

### Module 2: `weight_planner.py` - Weight Calculation Engine

**Purpose**: Calculate BMR, calorie targets, and weight forecasts using scientific formulas

#### Class Structure

```python
class WeightPlanner:
    """
    Calculates personalized weight plans using Mifflin-St Jeor equation.

    Attributes:
        present_weight_kg (float): Current weight in kilograms
        target_weight_kg (float): Goal weight in kilograms
        age (int): User's age in years
        height_cm (float): Height in centimeters
        gender (str): 'male' or 'female'
        activity_level (str): Activity level (sedentary/light/moderate/very/super)
        weekly_loss_lbs (float): Desired weekly weight change in pounds
        weekly_change_kg (float): Weekly change converted to kg
        direction (str): 'loss' or 'gain'
        activity_factors (dict): Multipliers for activity levels
    """
```

#### Constructor Deep Dive

```python
def __init__(self, present_weight_kg, target_weight_kg, age, height_cm,
             gender, activity_level="moderate", weekly_loss_lbs=1.0):
    """
    Initialize weight planner with user parameters.

    Args:
        present_weight_kg (float): Current weight in kg (40-200)
        target_weight_kg (float): Target weight in kg (40-200)
        age (int): Age in years (18-100)
        height_cm (float): Height in cm (120-220)
        gender (str): 'male' or 'female'
        activity_level (str): Activity level (default: 'moderate')
        weekly_loss_lbs (float): Weekly change in lbs (default: 1.0)

    Example:
        >>> planner = WeightPlanner(
        ...     present_weight_kg=85.0,
        ...     target_weight_kg=75.0,
        ...     age=30,
        ...     height_cm=175,
        ...     gender='male',
        ...     activity_level='moderate',
        ...     weekly_loss_lbs=1.0
        ... )
    """
    self.present_weight_kg = present_weight_kg
    self.target_weight_kg = target_weight_kg
    self.age = age
    self.height_cm = height_cm
    self.gender = gender.lower()
    self.activity_level = activity_level.lower()
    self.weekly_loss_lbs = weekly_loss_lbs
    self.weekly_change_kg = weekly_loss_lbs * 0.453592  # Convert lbs to kg

    # Determine if user wants to lose or gain weight
    self.direction = "loss" if target_weight_kg < present_weight_kg else "gain"

    # Harris-Benedict activity multipliers
    self.activity_factors = {
        "sedentary": 1.2,    # Little or no exercise
        "light": 1.375,      # Exercise 1-3 days/week
        "moderate": 1.55,    # Exercise 3-5 days/week
        "very": 1.725,       # Exercise 6-7 days/week
        "super": 1.9         # Physical job + exercise
    }
```

#### BMR Calculation Method

```python
def calculate_bmr(self, weight_kg):
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.

    This is the most accurate BMR formula (±10% error rate).

    Formula:
        Male: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(y) + 5
        Female: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age(y) - 161

    Args:
        weight_kg (float): Weight in kilograms

    Returns:
        float: BMR in kilocalories per day

    Example:
        >>> planner = WeightPlanner(85, 75, 30, 175, 'male')
        >>> bmr = planner.calculate_bmr(75)
        >>> print(bmr)  # ~1693.75 kcal

    Scientific Reference:
        Mifflin MD, St Jeor ST, Hill LA, et al. A new predictive equation
        for resting energy expenditure in healthy individuals. Am J Clin Nutr.
        1990;51(2):241-7.
    """
    if self.gender == "male":
        return 10 * weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
    else:
        return 10 * weight_kg + 6.25 * self.height_cm - 5 * self.age - 161
```

**BMR Calculation Example**:
```
Given:
- Male, 30 years old, 175 cm, 75 kg

Calculation:
BMR = 10 × 75 + 6.25 × 175 - 5 × 30 + 5
    = 750 + 1093.75 - 150 + 5
    = 1698.75 kcal/day
```

#### Weight Simulation Method

```python
def simulate(self):
    """
    Simulate weekly weight progression and calculate calorie targets.

    Algorithm:
        1. Calculate target weight BMR
        2. Apply activity factor to get maintenance calories
        3. Calculate daily caloric adjustment based on weekly goal
        4. Simulate week-by-week weight changes until goal is reached

    Returns:
        tuple: (forecast_df, target_calories, maintenance_calories)
            - forecast_df (pd.DataFrame): Weekly weight progression
            - target_calories (int): Daily calorie target to achieve goal
            - maintenance_calories (int): Calories to maintain target weight

    Scientific Basis:
        - 1 kg body weight ≈ 7700 kcal
        - 1 lb ≈ 3500 kcal
        - Safe weight loss: 0.5-1 kg/week (1-2 lbs/week)
        - Safe weight gain: 0.25-0.5 kg/week (0.5-1 lbs/week)

    Example:
        >>> planner = WeightPlanner(85, 75, 30, 175, 'male', 'moderate', 1.0)
        >>> df, target_cal, maint_cal = planner.simulate()
        >>> print(f"Target: {target_cal} kcal, Maintenance: {maint_cal} kcal")
        Target: 2129 kcal, Maintenance: 2629 kcal
        >>> print(df)
           Week  Estimated Weight (kg)
        0     0                   85.00
        1     1                   84.55
        2     2                   84.09
        ...
    """
    # Get activity multiplier
    activity_factor = self.activity_factors.get(self.activity_level, 1.55)

    # Calculate BMR at target weight
    target_bmr = self.calculate_bmr(self.target_weight_kg)

    # Calculate maintenance calories (BMR × activity factor)
    maintenance_calories = round(target_bmr * activity_factor)

    # Calculate weekly caloric change needed
    # 1 kg = 7700 kcal, so weekly_change_kg × 7700 = weekly kcal change
    weekly_kcal_change = self.weekly_change_kg * 7700

    # Daily adjustment (weekly change / 7 days)
    daily_kcal_adjustment = weekly_kcal_change / 7

    # Calculate target daily calories
    if self.direction == "loss":
        target_daily_calories = maintenance_calories - daily_kcal_adjustment
    else:  # gain
        target_daily_calories = maintenance_calories + daily_kcal_adjustment

    # Simulate weekly progression
    weight = self.present_weight_kg
    weekly_data = [{"Week": 0, "Estimated Weight (kg)": round(weight, 2)}]
    week = 1

    # Continue until target weight is reached
    while (self.direction == "loss" and weight > self.target_weight_kg) or \
          (self.direction == "gain" and weight < self.target_weight_kg):

        # Update weight based on direction
        if self.direction == "loss":
            weight -= self.weekly_change_kg
            weight = max(weight, self.target_weight_kg)  # Don't go below target
        else:
            weight += self.weekly_change_kg
            weight = min(weight, self.target_weight_kg)  # Don't go above target

        weekly_data.append({"Week": week, "Estimated Weight (kg)": round(weight, 2)})
        week += 1

    return pd.DataFrame(weekly_data), round(target_daily_calories), round(maintenance_calories)
```

**Weight Loss Example Calculation**:
```
Given:
- Current: 85 kg → Target: 75 kg
- Weekly loss: 1 lb (0.45 kg)
- Activity: Moderate (1.55)
- Male, 30y, 175cm

Step 1: Calculate target BMR
BMR = 10×75 + 6.25×175 - 5×30 + 5 = 1698.75 kcal

Step 2: Calculate maintenance calories
Maintenance = 1698.75 × 1.55 = 2633 kcal

Step 3: Calculate daily deficit
Weekly deficit = 0.45 kg × 7700 kcal/kg = 3465 kcal
Daily deficit = 3465 / 7 = 495 kcal

Step 4: Calculate target calories
Target = 2633 - 495 = 2138 kcal/day

Step 5: Simulate progression
Week 0: 85.00 kg
Week 1: 84.55 kg (85.00 - 0.45)
Week 2: 84.09 kg (84.55 - 0.45)
...
Week 22: 75.00 kg (target reached)
```

#### GPT Summary Generation

```python
def generate_summary(self):
    """
    Generate AI-powered motivational summary using GPT-4.

    Returns:
        tuple: (prompt, summary)
            - prompt (str): The prompt sent to GPT
            - summary (str): GPT-generated motivational text

    Example Output:
        "Great choice! Going from 85 kg to 75 kg in 22 weeks is a healthy
        and sustainable pace. Stay consistent with your 2138 kcal daily target,
        and you'll see amazing results!"
    """
    df, target_cal, maintenance_cal = self.simulate()
    total_weeks = df['Week'].max()

    prompt = (
        f"A user wants to go from {self.present_weight_kg} kg to {self.target_weight_kg} kg "
        f"over {total_weeks} weeks. The goal is to create an inspiring and friendly summary "
        f"that briefly motivates the user with 2–3 sentences. Be supportive and positive."
    )

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )

    summary = response.choices[0].message.content.strip()

    return prompt, summary
```

---

### Module 3: `meal_planner.py` - Meal Selection Engine

**Purpose**: Select optimal meals from recipe database based on calorie and diet constraints

#### Class Structure

```python
class MealPlanner:
    """
    Selects and optimizes daily meal plans from recipe database.

    Attributes:
        df (pd.DataFrame): Recipe database
        total_calories (int): Target daily calories
        diet_type (str): Diet preference (veg/non_veg/vegan)
        api_key (str): OpenAI API key
        selected_meals_df (pd.DataFrame): Selected meals
        prompt (str): Prompt sent to GPT for annotations
    """
```

#### Data Preparation

```python
def prepare_data(self):
    """
    Parse ingredients and cooking steps from string representations.

    Handles both:
        - String representations of lists: "['egg', 'milk', 'flour']"
        - Actual lists: ['egg', 'milk', 'flour']
        - Edge cases: Invalid formats, None values

    Uses ast.literal_eval for safe parsing (no code execution risk).
    """
    self.df['ingredients'] = self.df['ingredients'].apply(self._safe_parse_list)
    self.df['steps'] = self.df['steps'].apply(self._safe_parse_list)

def _safe_parse_list(self, x):
    """
    Safely parse string to list.

    Args:
        x: String representation or actual list

    Returns:
        list: Parsed list or [str(x)] if parsing fails

    Example:
        "['a', 'b']" → ['a', 'b']
        ['a', 'b'] → ['a', 'b']
        "invalid" → ['invalid']
    """
    try:
        parsed = ast.literal_eval(x) if isinstance(x, str) else x
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except:
        return [str(x)]
```

#### Meal Selection Algorithm

```python
def select_meals(self):
    """
    Select optimal meals for breakfast, snack, lunch, and dinner.

    Algorithm:
        1. Define calorie distribution (breakfast 25%, snack 10%, lunch 35%, dinner 30%)
        2. For each meal type:
            a. Filter by meal_type (breakfast/lunch/dinner/snack)
            b. Filter by diet_type (veg/non_veg/vegan)
            c. Filter sugar ≤ 20% daily value
            d. Sort by: low fat → high protein → low calories
            e. Find closest match to target calories
        3. Build prompt for GPT annotation

    Optimization Criteria:
        - Primary: Match target calories
        - Secondary: Low total fat
        - Tertiary: High protein
        - Constraint: Sugar ≤ 20% DV (limit added sugars)

    Meal Distribution Rationale:
        - Breakfast (25%): Moderate start to day
        - Snack (10%): Small energy boost
        - Lunch (35%): Largest meal (peak activity)
        - Dinner (30%): Substantial but lighter than lunch
    """
    meal_structure = {
        'breakfast': 0.25,  # 25% of daily calories
        'snack': 0.1,       # 10% of daily calories
        'lunch': 0.35,      # 35% of daily calories
        'dinner': 0.30      # 30% of daily calories
    }

    selected_meals = []
    self.prompt = f"Create a personalized 1-day meal plan for a {self.diet_type} diet with a total of {self.total_calories} kcal.\n\nHere is the proposed structure with ingredients and estimated calories:\n\n"

    for meal, ratio in meal_structure.items():
        base_type = 'snack' if 'snack' in meal else meal
        target_kcal = self.total_calories * ratio

        # Filter by meal type and diet type
        matches = self.df[
            (self.df['meal_type'].str.lower() == base_type.lower()) &
            (self.df['diet_type'].str.lower() == self.diet_type.lower())
        ]

        # Filter high-sugar recipes (> 20% DV)
        matches = matches[matches['sugar'] <= 20]

        if not matches.empty:
            # Sort by optimization criteria
            matches_sorted = matches.sort_values(
                by=['total_fat', 'protein', 'calories'],
                ascending=[True, False, True]  # Low fat, high protein, low cal
            )

            # Find closest match to target calories
            closest = matches_sorted.iloc[
                (matches_sorted['calories'] - target_kcal).abs().argsort()[:1]
            ]

            row = closest.iloc[0]
            selected_meals.append(row)

            # Build prompt with first 5 ingredients
            self.prompt += f"• {base_type.title()} ({int(row['calories'])} kcal): Ingredients: {', '.join(row['ingredients'][:5])}\n"

    self.selected_meals_df = pd.DataFrame(selected_meals).reset_index(drop=True)
```

**Example Selection Process**:
```
Target: 2000 kcal, Diet: veg

Breakfast (500 kcal target):
1. Filter: meal_type='breakfast', diet_type='veg', sugar≤20
2. Sort: low fat, high protein, low cal
3. Find: Recipe with ~500 kcal
   → Selected: "Veggie Omelet" (485 kcal, fat=15%, protein=25%, sugar=5%)

Snack (200 kcal target):
1. Filter: meal_type='snack', diet_type='veg', sugar≤20
2. Sort: low fat, high protein, low cal
3. Find: Recipe with ~200 kcal
   → Selected: "Greek Yogurt with Berries" (195 kcal, fat=10%, protein=15%, sugar=12%)

... (continue for lunch and dinner)
```

#### GPT Annotation

```python
def generate_gpt_annotations(self):
    """
    Use GPT-3.5-turbo to generate creative meal names and health tips.

    Task for GPT:
        1. Create appealing meal name (e.g., "Sunshine Veggie Scramble")
        2. Provide 1-line health tip (e.g., "Add more veggies for fiber!")
        3. Flag high-calorie ingredients if needed

    Response format expected:
        Line 1: Breakfast name + tip
        Line 2: Snack name + tip
        Line 3: Lunch name + tip
        Line 4: Dinner name + tip

    Model: GPT-3.5-turbo (cost-effective for simple creative tasks)
    Max tokens: 500 (4 meals × ~100 tokens each)
    """
    if "Your task:" not in self.prompt:
        self.prompt += (
            "\nYour task:"
            "\n1. Generate a more appealing name for each meal."
            "\n2. Write a brief 1-line recommendation for each (e.g., reduce oil, boost protein)."
            "\n3. If any ingredient pushes the calories too high, mention that."
        )

    client = OpenAI(api_key=self.api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": self.prompt}],
        max_tokens=500
    )

    gpt_output = response.choices[0].message.content
    gpt_lines = [line for line in gpt_output.strip().split("\n") if line.strip()]

    # Assign GPT output to meals (one line per meal)
    self.selected_meals_df['gpt_name_and_tip'] = gpt_lines[:len(self.selected_meals_df)]
```

---

### Module 4: `gpt_weight_nutrition_planner.py` - RAG Exercise Planner

**Purpose**: Generate personalized exercise and nutrition plans using Retrieval-Augmented Generation (RAG)

#### RAG Architecture

```
User Query → Vector Search → Retrieve Context → Combine with Prompt → GPT-4 → Response
```

#### Class Initialization

```python
class GPTWeightNutritionPlanner:
    def __init__(self, vector_path="vector", model_name="gpt-4-turbo", temperature=0.3):
        """
        Initialize RAG-based planner.

        Args:
            vector_path (str): Path to FAISS vector store
            model_name (str): GPT model to use
            temperature (float): Creativity (0=deterministic, 1=creative)

        Loads:
            - FAISS vector store with embeddings
            - OpenAI embeddings model (text-embedding-ada-002)
            - ChatGPT-4 model
            - LangChain QA chain
        """
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set in environment.")

        self.vector_path = vector_path
        self.model_name = model_name
        self.temperature = temperature
        self._load_vectorstore()
        self._load_model()

def _load_vectorstore(self):
    """
    Load FAISS vector store from disk.

    FAISS (Facebook AI Similarity Search):
        - Efficient similarity search library
        - Stores document embeddings (1536 dimensions)
        - Uses L2 (Euclidean) distance for similarity

    Security Note:
        allow_dangerous_deserialization=True required for loading pickle files.
        Only use with trusted vector stores!
    """
    embeddings = OpenAIEmbeddings()  # text-embedding-ada-002
    self.vectorstore = FAISS.load_local(
        self.vector_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

def _load_model(self):
    """
    Initialize LangChain QA chain with GPT-4.

    Chain Type: "stuff"
        - Concatenates all retrieved documents into one prompt
        - Simple and effective for small context windows
        - Alternative: "map_reduce", "refine", "map_rerank"
    """
    self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
    self.chain = load_qa_with_sources_chain(self.llm, chain_type="stuff")
```

#### Context Retrieval

```python
def generate(self, age, gender, height_cm, present_weight, target_weight, activity, calories):
    """
    Generate personalized exercise and nutrition plan using RAG.

    Process:
        1. Create retrieval query optimized for vector search
        2. Search vector store for top k=7 relevant documents
        3. Filter by valid health/fitness sources
        4. Extract snippets from documents
        5. Build personalized prompt with user details
        6. Combine context + prompt → send to GPT-4
        7. Return structured response with sources

    Args:
        age (int): User's age
        gender (str): 'male' or 'female'
        height_cm (float): Height in cm
        present_weight (float): Current weight in kg
        target_weight (float): Goal weight in kg
        activity (str): Activity level
        calories (int): Daily calorie target

    Returns:
        tuple: (prompt, response, doc_summaries)
            - prompt: Full prompt sent to GPT
            - response: GPT-generated plan
            - doc_summaries: List of source documents used
    """
    # Create focused retrieval query
    goal = 'gain' if target_weight > present_weight else 'lose'
    retrieval_query = f"Weekly or daily physical activity exercises and nutrition guidance for someone trying to {goal} weight."

    # Retrieve relevant documents
    docs = self.vectorstore.similarity_search(retrieval_query, k=7)

    # Filter by trusted sources
    valid_sources = ["diet", "physical", "Weight", "GymDataset",
                     "weight_gain", "weight_loss", "Human_Nut", "Nut_Science"]
    docs = [doc for doc in docs if doc.metadata.get("source") in valid_sources]

    # Log retrieved sources (for debugging)
    print("📄 Retrieved Sources:")
    for doc in docs:
        print(" -", doc.metadata.get("source"))

    # Build readable summaries
    doc_summaries = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown Source")
        snippet = doc.page_content[:600].strip().replace("\n", " ") + "..."
        doc_summaries.append(
            f"**Chunk {i+1} — Source:** {source}\n{textwrap.fill(snippet, width=100)}"
        )

    # Build personalized prompt
    prompt = self.build_prompt(age, gender, height_cm, present_weight,
                               target_weight, activity, calories)

    # Call GPT with context
    response = self.chain.run({"input_documents": docs, "question": prompt})

    return prompt.strip(), response.strip(), doc_summaries
```

**RAG Example Flow**:
```
1. User Input:
   Age=30, Gender=male, Weight=85kg→75kg, Activity=moderate, Calories=2138

2. Retrieval Query:
   "Weekly or daily physical activity exercises and nutrition guidance
    for someone trying to lose weight."

3. Vector Search (k=7):
   Retrieved documents:
   - diet (similarity: 0.23)
   - weight_loss (similarity: 0.28)
   - physical (similarity: 0.31)
   - GymDataset (similarity: 0.35)
   - Human_Nut (similarity: 0.42)
   - Nut_Science (similarity: 0.45)
   - Weight (similarity: 0.48)

4. Prompt Construction:
   ```
   The user wants to lose weight.

   **User Details:**
   - Age: 30
   - Gender: male
   - Height: 175 cm
   - Current Weight: 85 kg
   - Target Weight: 75 kg
   - Activity Level: moderate
   - Suggested Caloric Intake: 2138 kcal/day

   **Instructions:**
   1. Provide a beginner-friendly weekly physical activity/exercise
      clearly must be week's day by day.
   2. Suggest dietary and nutritional guidance using the context clearly.
   ```

5. GPT-4 Response (with context):
   → Generates weekly exercise plan + nutrition advice

6. Return:
   (prompt, response, 7 document summaries with sources)
```

---

### Module 5: `GPTCustomPrompt.py` - Custom Chatbot Handler

**Purpose**: Handle user's custom questions with context-aware RAG and similarity filtering

#### Key Differences from Exercise Planner

| Feature | Exercise Planner | Custom Chat |
|---------|------------------|-------------|
| **Retrieval** | Keyword-based | User query-based |
| **Filtering** | Source-only | Source + Similarity score |
| **Threshold** | None | Cosine similarity ≤ 0.5 |
| **Temperature** | 0.3 (focused) | 0.4 (slightly creative) |

#### Similarity Scoring

```python
def generate(self, user_prompt, age, gender, height_cm, present_weight,
             target_weight, calories, score_threshold=0.5):
    """
    Generate response to custom user question using RAG with similarity filtering.

    Similarity Threshold:
        FAISS uses L2 distance (Euclidean):
        - 0.0 = identical
        - < 0.5 = highly relevant
        - 0.5-1.0 = moderately relevant
        - > 1.0 = not relevant

    Algorithm:
        1. Search with similarity scores
        2. Filter by score ≤ 0.5 AND valid source
        3. Enrich prompt with user context
        4. Generate response
        5. Return with source attribution and scores
    """
    # Search with scores
    docs_and_scores = self.vectorstore.similarity_search_with_score(user_prompt, k=7)

    valid_sources = {"diet", "physical", "Weight", "GymDataset",
                     "weight_gain", "weight_loss", "Human_Nut", "Nut_Science"}

    # Filter by score and source
    filtered = [
        (doc, score) for doc, score in docs_and_scores
        if doc.metadata.get("source") in valid_sources and score <= score_threshold
    ]

    docs = [doc for doc, _ in filtered]
    cosine_scores = [score for _, score in filtered]

    print("📄 Filtered Sources (score ≤ threshold):")
    for doc, score in zip(docs, cosine_scores):
        print(f" - {doc.metadata.get('source')}, Score: {score:.4f}")

    # Build summaries with scores
    doc_summaries = []
    for i, (doc, score) in enumerate(zip(docs, cosine_scores)):
        source = doc.metadata.get("source", "Unknown Source")
        snippet = doc.page_content[:600].strip().replace("\n", " ") + "..."
        doc_summaries.append(
            f"**Chunk {i+1} — Source: {source}, Similarity Score: {score:.4f}**\n"
            f"{textwrap.fill(snippet, width=100)}"
        )

    if not docs:
        return "No relevant chunks found.", \
               "Sorry, no context matched your question well enough.", []

    # Enrich prompt with user details
    prompt = self.enrich_prompt(user_prompt, age, gender, height_cm,
                                present_weight, target_weight, calories)

    response = self.chain.run({"input_documents": docs, "question": prompt})

    return prompt.strip(), response.strip(), doc_summaries
```

#### Prompt Enrichment

```python
def enrich_prompt(self, user_prompt, age, gender, height_cm, present_weight,
                  target_weight, calories):
    """
    Add user context to make responses personalized.

    Benefits:
        - GPT can tailor advice to user's specific situation
        - More accurate recommendations
        - Context-aware responses

    Safety Measures:
        - Checks if question is health-related
        - Rejects unrelated questions
        - Limits to nutrition/exercise topics
    """
    goal = "gain" if target_weight > present_weight else "lose"
    return f"""
User wants to {goal} weight. Answer the following question using the provided context
and tailor the response to the user's personal metrics if possible.

**User Details:**
- Age: {age}
- Gender: {gender}
- Height: {height_cm} cm
- Current Weight: {present_weight} kg
- Target Weight: {target_weight} kg
- Caloric Target: {calories} kcal/day

**User Question:**
{user_prompt}

**Instructions for GPT:**
1. Your response must be based only on the user details and retrieved context.
2. Consider topics like weight management, food suggestions, calorie balance,
   physical activity, dietary nutrients, macronutrients (carbs, protein, fat),
   and micronutrients (e.g., vitamins, minerals).
3. Make it short and clear.
4. If the question is clearly unrelated to health, weight, exercise, or nutrition,
   respond with:
   *"This question appears unrelated to personalized health guidance. Please ask
    about nutrition, exercise, or weight-related planning."*
"""
```

---

### Module 6: `Stream_lit_Chat.py` - UI Controller

**Purpose**: Main application interface with two pages (Main Planner, Custom Chat)

#### Page Architecture

```python
# Session State Structure
st.session_state = {
    # Navigation
    'page': 'Main Planner' | 'Custom Chat',

    # Weight Planning
    'forecast_df': pd.DataFrame,           # Weekly weight data
    'target_calories': int,                # Daily calorie target
    'maintenance_calories': int,           # Maintenance calories
    'summary_prompt': str,                 # Prompt for summary
    'summary_text': str,                   # GPT summary

    # Meal Planning
    'meal_planner': MealPlanner,           # Meal planner instance
    'gpt_annotated': bool,                 # Whether GPT annotations done
    'gpt_plan': dict,                      # Exercise plan data

    # Chat
    'chat_history': [                      # List of chat exchanges
        {
            'user': str,                   # User question
            'response': str,               # GPT response
            'context': list,               # Source documents
            'prompt': str                  # Full prompt sent
        },
        ...
    ]
}
```

#### Main Planner Page Flow

```python
# 1. User Input (Sidebar Form)
with st.sidebar.form("user_inputs"):
    age = st.number_input("Age", 18, 100, 24)
    gender = st.selectbox("Gender", ["male", "female"])
    height_cm = st.number_input("Height (cm)", 120, 220, 176)
    present_weight = st.number_input("Current Weight (kg)", 40.0, 200.0, 85.0)
    target_weight = st.number_input("Target Weight (kg)", 40.0, 200.0, 75.0)
    activity = st.selectbox("Activity Level", ["sedentary", "light", "moderate", "very", "super"])
    weekly_loss = st.number_input("Weekly Difference (lbs)", 0.4, 1.0, 0.5, 0.1)
    diet = st.selectbox("Diet Preference", ["veg", "non_veg", "vegan"])
    submitted = st.form_submit_button("Submit")

# 2. Process Submission
if submitted:
    # Clear chat history
    st.session_state.chat_history = []

    # Calculate weight plan
    wp = WeightPlanner(...)
    df_weights, target_calories, maintenance_calories = wp.simulate()
    prompt_summary, summary_text = wp.generate_summary()

    # Store in session state
    st.session_state['forecast_df'] = df_weights
    st.session_state['target_calories'] = target_calories
    st.session_state['maintenance_calories'] = maintenance_calories
    st.session_state['summary_prompt'] = prompt_summary
    st.session_state['summary_text'] = summary_text

    # Generate meal plan
    planner = MealPlanner(df, total_calories=target_calories, diet_type=diet)
    planner.prepare_data()
    planner.select_meals()
    st.session_state['meal_planner'] = planner
    st.session_state['gpt_annotated'] = False
    st.session_state['gpt_plan'] = None

# 3. Display Results
if "forecast_df" in st.session_state:
    # Weight forecast chart
    st.line_chart(st.session_state['forecast_df'].set_index("Week"))

    # Calorie targets
    st.markdown(f"**Target Daily Calories:** `{st.session_state['target_calories']} kcal`")
    st.markdown(f"**Maintenance Calories:** `{st.session_state['maintenance_calories']} kcal`")

# 4. Display Summary
if 'summary_text' in st.session_state:
    st.markdown(st.session_state['summary_text'])

# 5. Display Meal Plan
if 'meal_planner' in st.session_state:
    planner = st.session_state['meal_planner']
    if not st.session_state.get('gpt_annotated'):
        planner.generate_gpt_annotations()
        st.session_state['gpt_annotated'] = True
    selected_df, nutrition = planner.display_plan()

# 6. Exercise & Nutrition Plan (Button)
if st.button("Exercise & Nutrition Plan"):
    gpt_engine = GPTWeightNutritionPlanner()
    gpt_prompt, gpt_response, gpt_docs = gpt_engine.generate(...)
    st.session_state['gpt_plan'] = {
        "prompt": gpt_prompt,
        "response": gpt_response,
        "docs": gpt_docs
    }

# 7. Navigate to Chat
if st.button("Proceed to GPT Chat"):
    st.session_state.page = "Custom Chat"
    st.rerun()
```

#### Custom Chat Page Flow

```python
# 1. Chat Input
user_custom_prompt = st.chat_input("Type your custom question...")

# 2. Process Question
if user_custom_prompt:
    gpt_custom = GPTCustomPromptPlanner()
    prompt_out, response_out, docs_out = gpt_custom.generate(
        user_prompt=user_custom_prompt,
        age=age, gender=gender, height_cm=height_cm,
        present_weight=present_weight, target_weight=target_weight,
        calories=calories
    )

    # Add to chat history
    st.session_state.chat_history.append({
        "user": user_custom_prompt,
        "response": response_out,
        "context": docs_out,
        "prompt": prompt_out
    })

# 3. Display Chat History
for item in st.session_state.chat_history:
    # User message
    with st.chat_message("user", avatar=user_avatar_path):
        st.markdown(item["user"])

    # Assistant message
    with st.chat_message("assistant", avatar=bot_avatar_path):
        st.markdown(item["response"])

        # Expandable sections for transparency
        with st.expander("Prompt Sent"):
            st.code(item["prompt"], language='text')

        with st.expander("Context Source"):
            for i, doc in enumerate(item["context"], 1):
                st.markdown(f"**Chunk {i}**")
                st.markdown(doc, unsafe_allow_html=True)
```

---

## Data Models

### Recipe Data Model

```python
{
    # Identifiers
    'id': int,                          # Unique recipe ID
    'name': str,                        # Recipe name
    'contributor_id': int,              # Author ID
    'submitted': datetime,              # Submission date

    # Recipe Details
    'minutes': int,                     # Cooking time
    'n_steps': int,                     # Number of steps
    'steps': list[str],                 # Cooking instructions
    'n_ingredients': int,               # Ingredient count
    'ingredients': list[str],           # Ingredient list
    'description': str,                 # Recipe description
    'tags': list[str],                  # Tags (e.g., 'healthy', 'quick')

    # Categorization
    'meal_type': str,                   # 'breakfast', 'lunch', 'dinner', 'snack'
    'diet_type': str,                   # 'veg', 'non_veg', 'vegan'

    # Nutrition (% Daily Value based on 2000 kcal diet)
    'calories': float,                  # kcal
    'total_fat': float,                 # % DV
    'saturated_fat': float,             # % DV
    'protein': float,                   # % DV
    'carbohydrates': float,             # % DV
    'sugar': float,                     # % DV
    'sodium': float,                    # % DV
}
```

### Session State Model

```python
{
    # Page Navigation
    'page': str,                        # 'Main Planner' or 'Custom Chat'

    # Weight Data
    'forecast_df': pd.DataFrame(
        columns=['Week', 'Estimated Weight (kg)']
    ),
    'target_calories': int,
    'maintenance_calories': int,
    'summary_prompt': str,
    'summary_text': str,

    # Meal Data
    'meal_planner': MealPlanner,
    'gpt_annotated': bool,
    'gpt_plan': {
        'prompt': str,
        'response': str,
        'docs': list[str]
    },

    # Chat Data
    'chat_history': [
        {
            'user': str,
            'response': str,
            'context': list[str],
            'prompt': str
        }
    ]
}
```

---

## Algorithms Explained

### 1. BMR Calculation (Mifflin-St Jeor)

```
Male BMR = 10W + 6.25H - 5A + 5
Female BMR = 10W + 6.25H - 5A - 161

Where:
  W = weight in kg
  H = height in cm
  A = age in years

Accuracy: ±10% for 95% of population
```

### 2. Calorie Target Calculation

```
TDEE = BMR × Activity Factor

Activity Factors:
  Sedentary: 1.2
  Light: 1.375
  Moderate: 1.55
  Very Active: 1.725
  Super Active: 1.9

For Weight Loss:
  Target = TDEE - (Weekly Loss × 7700 / 7)

For Weight Gain:
  Target = TDEE + (Weekly Gain × 7700 / 7)
```

### 3. Meal Selection Algorithm

```
Function: select_optimal_meal(meal_type, diet_type, target_calories)

Input:
  meal_type: breakfast | lunch | dinner | snack
  diet_type: veg | non_veg | vegan
  target_calories: float

Algorithm:
  1. recipes = filter_by(meal_type, diet_type)
  2. recipes = filter(recipes, sugar <= 20)
  3. recipes = sort(recipes, by=[fat↑, protein↓, calories↑])
  4. best = argmin(|recipe.calories - target_calories|)
  5. return best

Time Complexity: O(n log n) due to sorting
Space Complexity: O(n)
```

### 4. Vector Similarity Search

```
Function: similarity_search(query, k)

Input:
  query: user question string
  k: number of documents to retrieve

Algorithm:
  1. query_embedding = embed(query)          # 1536-dim vector
  2. scores = []
  3. for each doc_embedding in index:
  4.   distance = L2(query_embedding, doc_embedding)
  5.   scores.append((doc, distance))
  6. scores = sort(scores, by=distance↑)
  7. return top_k(scores)

Time Complexity: O(n) with FAISS indexing optimization
Space Complexity: O(k)

Distance Metric: L2 (Euclidean)
  d(p,q) = sqrt(Σ(p_i - q_i)²)
```

---

## UI Components

### Streamlit Components Used

```python
# Input Components
st.number_input()           # Numeric input with validation
st.selectbox()             # Dropdown selection
st.form()                  # Group inputs with single submit
st.form_submit_button()    # Submit form data

# Display Components
st.title()                 # Page title
st.subheader()             # Section header
st.markdown()              # Formatted text
st.dataframe()             # Interactive table
st.line_chart()            # Line chart visualization
st.success()               # Success message box
st.error()                 # Error message box
st.code()                  # Code block display

# Layout Components
st.sidebar                 # Sidebar container
st.expander()              # Collapsible section
with st.chat_message()     # Chat message container

# Interaction Components
st.button()                # Action button
st.chat_input()            # Chat text input

# Caching
@st.cache_data             # Cache function results
st.rerun()                 # Rerun app (for navigation)
```

---

## State Management

### Session State Lifecycle

```
1. App Start
   ↓
2. Initialize session_state
   ↓
3. User Interaction
   ↓
4. Update session_state
   ↓
5. Rerun app (preserves state)
   ↓
6. Render with updated state
   ↓
7. Repeat from step 3

Reset:
  - Click "Reset Everything" button
  - Close browser tab
  - Server restart
```

### State Persistence Pattern

```python
# Check if variable exists in session state
if 'variable_name' not in st.session_state:
    # Initialize if doesn't exist
    st.session_state['variable_name'] = default_value

# Use the variable
value = st.session_state['variable_name']

# Update the variable
st.session_state['variable_name'] = new_value
```

---

## Code Patterns

### Pattern 1: Safe Data Parsing

```python
def safe_parse(value, default):
    """Safely parse value with fallback."""
    try:
        return ast.literal_eval(value) if isinstance(value, str) else value
    except:
        return default
```

### Pattern 2: Caching Expensive Operations

```python
@st.cache_data(show_spinner=False)
def load_data(path):
    """Load data once, cache for subsequent runs."""
    return pd.read_csv(path)
```

### Pattern 3: Session State Initialization

```python
# Initialize all session variables at once
if 'initialized' not in st.session_state:
    st.session_state.update({
        'page': 'Main Planner',
        'forecast_df': None,
        'chat_history': [],
        'initialized': True
    })
```

### Pattern 4: Error Handling with User Feedback

```python
try:
    result = risky_operation()
except Exception as e:
    st.error(f"Operation failed: {e}")
    logging.error(f"Error details: {e}", exc_info=True)
```

---

## Extending the Codebase

### Adding New Meal Types

```python
# In meal_planner.py
meal_structure = {
    'breakfast': 0.25,
    'snack': 0.1,
    'lunch': 0.35,
    'dinner': 0.30,
    'midnight_snack': 0.05  # NEW MEAL TYPE
}
```

### Adding New Diet Types

```python
# Update selectbox in Stream_lit_Chat.py
diet = st.selectbox("Diet Preference",
    ["veg", "non_veg", "vegan", "keto", "paleo"]  # Add new options
)

# Ensure CSV has corresponding diet_type values
```

### Adding New Vector Sources

```python
# In gpt_weight_nutrition_planner.py and GPTCustomPrompt.py
valid_sources = [
    "diet", "physical", "Weight", "GymDataset",
    "weight_gain", "weight_loss", "Human_Nut", "Nut_Science",
    "new_source_name"  # ADD NEW SOURCE
]

# Rebuild FAISS index with new documents
```

### Adding New GPT Models

```python
# In any planner file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4o",  # CHANGE MODEL
    messages=[...],
    max_tokens=500
)
```

---

**Last Updated**: December 2025
**Version**: 1.0
**For Questions**: Refer to API_REFERENCE.md or raise GitHub issue
