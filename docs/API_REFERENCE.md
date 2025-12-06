# API Reference Documentation

Complete reference for all classes, methods, and functions in the Weight Planner application.

## Table of Contents
1. [WeightPlanner Class](#weightplanner-class)
2. [MealPlanner Class](#mealplanner-class)
3. [GPTWeightNutritionPlanner Class](#gptweightnutritionplanner-class)
4. [GPTCustomPromptPlanner Class](#gptcustompromptplanner-class)
5. [Utility Functions](#utility-functions)
6. [Constants and Configuration](#constants-and-configuration)

---

## WeightPlanner Class

**Module**: `weight_planner.py`

**Purpose**: Calculate BMR, calorie targets, and weight forecasts using the Mifflin-St Jeor equation.

### Constructor

```python
WeightPlanner(present_weight_kg, target_weight_kg, age, height_cm, gender,
              activity_level="moderate", weekly_loss_lbs=1.0)
```

**Parameters**:

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| `present_weight_kg` | float | Yes | - | 40-200 | Current weight in kilograms |
| `target_weight_kg` | float | Yes | - | 40-200 | Desired weight in kilograms |
| `age` | int | Yes | - | 18-100 | User's age in years |
| `height_cm` | float | Yes | - | 120-220 | Height in centimeters |
| `gender` | str | Yes | - | 'male', 'female' | User's biological gender |
| `activity_level` | str | No | "moderate" | See below | Activity level |
| `weekly_loss_lbs` | float | No | 1.0 | 0.4-1.0 | Weekly weight change in pounds |

**Activity Levels**:
- `"sedentary"`: Little or no exercise (1.2x multiplier)
- `"light"`: Exercise 1-3 days/week (1.375x)
- `"moderate"`: Exercise 3-5 days/week (1.55x)
- `"very"`: Exercise 6-7 days/week (1.725x)
- `"super"`: Physical job + daily exercise (1.9x)

**Returns**: WeightPlanner instance

**Raises**:
- `ValueError`: If parameters are out of valid range
- `TypeError`: If parameter types are incorrect

**Example**:
```python
from weight_planner import WeightPlanner

# Create weight loss plan
planner = WeightPlanner(
    present_weight_kg=85.0,
    target_weight_kg=75.0,
    age=30,
    height_cm=175,
    gender='male',
    activity_level='moderate',
    weekly_loss_lbs=1.0
)
```

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `present_weight_kg` | float | Current weight |
| `target_weight_kg` | float | Goal weight |
| `age` | int | User's age |
| `height_cm` | float | Height in cm |
| `gender` | str | Gender (lowercase) |
| `activity_level` | str | Activity level (lowercase) |
| `weekly_loss_lbs` | float | Weekly change in lbs |
| `weekly_change_kg` | float | Weekly change in kg (calculated) |
| `direction` | str | "loss" or "gain" (calculated) |
| `activity_factors` | dict | Activity level multipliers |

---

### calculate_bmr()

Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.

```python
calculate_bmr(weight_kg: float) -> float
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `weight_kg` | float | Yes | Weight in kilograms |

**Returns**: `float` - BMR in kilocalories per day

**Formula**:
- **Male**: `BMR = 10W + 6.25H - 5A + 5`
- **Female**: `BMR = 10W + 6.25H - 5A - 161`

Where: W=weight(kg), H=height(cm), A=age(years)

**Example**:
```python
planner = WeightPlanner(85, 75, 30, 175, 'male')
bmr = planner.calculate_bmr(75)
print(f"BMR: {bmr:.2f} kcal/day")  # Output: BMR: 1698.75 kcal/day
```

**Scientific Reference**:
> Mifflin MD, St Jeor ST, Hill LA, et al. *A new predictive equation for resting energy expenditure in healthy individuals.* Am J Clin Nutr. 1990;51(2):241-7.

---

### simulate()

Simulate weekly weight progression and calculate calorie targets.

```python
simulate() -> tuple[pd.DataFrame, int, int]
```

**Parameters**: None

**Returns**: `tuple` containing:
1. `pd.DataFrame`: Weekly weight forecast with columns:
   - `Week` (int): Week number (0 = start)
   - `Estimated Weight (kg)` (float): Projected weight
2. `int`: Target daily calories to achieve goal
3. `int`: Maintenance calories at target weight

**Algorithm**:
1. Calculate target weight BMR
2. Apply activity factor → maintenance calories
3. Calculate daily caloric adjustment (weekly change × 7700 ÷ 7)
4. Determine target calories (maintenance ± adjustment)
5. Simulate week-by-week progression

**Example**:
```python
planner = WeightPlanner(85, 75, 30, 175, 'male', 'moderate', 1.0)
forecast_df, target_cal, maint_cal = planner.simulate()

print(f"Target Calories: {target_cal} kcal/day")
print(f"Maintenance Calories: {maint_cal} kcal/day")
print(f"Estimated Duration: {forecast_df['Week'].max()} weeks")
print("\nWeekly Forecast:")
print(forecast_df.head(10))

# Output:
# Target Calories: 2129 kcal/day
# Maintenance Calories: 2629 kcal/day
# Estimated Duration: 22 weeks
#
# Weekly Forecast:
#    Week  Estimated Weight (kg)
# 0     0                  85.00
# 1     1                  84.55
# 2     2                  84.09
# ...
```

---

### generate_summary()

Generate AI-powered motivational summary using GPT-4.

```python
generate_summary() -> tuple[str, str]
```

**Parameters**: None

**Returns**: `tuple` containing:
1. `str`: Prompt sent to GPT-4
2. `str`: Generated motivational summary (2-3 sentences)

**API Usage**:
- Model: `gpt-4-turbo`
- Max tokens: 100
- Temperature: Default (1.0)

**Example**:
```python
planner = WeightPlanner(85, 75, 30, 175, 'male')
prompt, summary = planner.generate_summary()

print("Prompt:", prompt)
print("\nSummary:", summary)

# Output:
# Prompt: A user wants to go from 85 kg to 75 kg over 22 weeks...
# Summary: Great choice! Going from 85 kg to 75 kg in 22 weeks is a
#          healthy and sustainable pace. Stay consistent with your
#          calorie target, and you'll see amazing results!
```

**Raises**:
- `ValueError`: If OPENAI_API_KEY not set
- `openai.OpenAIError`: If API call fails

---

## MealPlanner Class

**Module**: `meal_planner.py`

**Purpose**: Select and optimize daily meal plans from recipe database.

### Constructor

```python
MealPlanner(df, total_calories=2000, diet_type="vegan",
            api_key=os.getenv("OPENAI_API_KEY"))
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `df` | pd.DataFrame | Yes | - | Recipe database (from CSV) |
| `total_calories` | int | No | 2000 | Target daily calories |
| `diet_type` | str | No | "vegan" | Diet preference |
| `api_key` | str | No | From .env | OpenAI API key |

**Diet Types**:
- `"veg"`: Vegetarian (no meat/fish)
- `"non_veg"`: Non-vegetarian (all foods)
- `"vegan"`: Vegan (no animal products)

**Returns**: MealPlanner instance

**Example**:
```python
import pandas as pd
from meal_planner import MealPlanner

# Load recipe database
df = pd.read_csv("Calories/Recipes.csv")

# Create meal planner for 2200 kcal veg diet
planner = MealPlanner(
    df=df,
    total_calories=2200,
    diet_type="veg"
)
```

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `df` | pd.DataFrame | Copy of recipe database |
| `total_calories` | int | Daily calorie target |
| `diet_type` | str | Diet preference |
| `api_key` | str | OpenAI API key |
| `selected_meals_df` | pd.DataFrame | Selected meals (after selection) |
| `prompt` | str | Prompt built for GPT (after selection) |

---

### prepare_data()

Parse ingredients and cooking steps from string representations.

```python
prepare_data() -> None
```

**Parameters**: None

**Returns**: None (modifies `self.df` in place)

**Side Effects**:
- Converts `ingredients` column from string to list
- Converts `steps` column from string to list

**Example**:
```python
planner = MealPlanner(df, total_calories=2000, diet_type="veg")
planner.prepare_data()

# Before: df['ingredients'] = "['egg', 'milk', 'flour']"
# After:  df['ingredients'] = ['egg', 'milk', 'flour']
```

---

### select_meals()

Select optimal meals for breakfast, snack, lunch, and dinner.

```python
select_meals() -> None
```

**Parameters**: None

**Returns**: None (populates `self.selected_meals_df` and `self.prompt`)

**Algorithm**:
1. Define calorie distribution:
   - Breakfast: 25%
   - Snack: 10%
   - Lunch: 35%
   - Dinner: 30%
2. For each meal type:
   - Filter by `meal_type` and `diet_type`
   - Remove high-sugar recipes (>20% DV)
   - Sort by: low fat ↑, high protein ↓, low calories ↑
   - Select closest match to target calories
3. Build prompt for GPT annotation

**Side Effects**:
- Sets `self.selected_meals_df` with 4 rows (4 meals)
- Sets `self.prompt` with meal details

**Example**:
```python
planner = MealPlanner(df, total_calories=2000, diet_type="veg")
planner.prepare_data()
planner.select_meals()

print(f"Selected {len(planner.selected_meals_df)} meals")
print(planner.selected_meals_df[['meal_type', 'name', 'calories']])

# Output:
# Selected 4 meals
#   meal_type                name  calories
# 0 breakfast    Veggie Scramble     498.0
# 1     snack  Greek Yogurt Bowl     195.0
# 2     lunch  Quinoa Power Bowl     702.0
# 3    dinner    Lentil Stir Fry     605.0
```

---

### generate_gpt_annotations()

Use GPT-3.5-turbo to generate creative meal names and health tips.

```python
generate_gpt_annotations() -> None
```

**Parameters**: None

**Returns**: None (adds `gpt_name_and_tip` column to `self.selected_meals_df`)

**API Usage**:
- Model: `gpt-3.5-turbo`
- Max tokens: 500
- Temperature: Default (1.0)

**Side Effects**:
- Adds column `gpt_name_and_tip` with GPT suggestions

**Example**:
```python
planner.generate_gpt_annotations()

print(planner.selected_meals_df[['meal_type', 'gpt_name_and_tip']])

# Output:
#   meal_type                          gpt_name_and_tip
# 0 breakfast  Sunshine Veggie Scramble - Add spinach for extra iron!
# 1     snack  Berry Bliss Bowl - Use low-fat yogurt to reduce calories.
# 2     lunch  Power Quinoa Bowl - Great protein balance!
# 3    dinner  Hearty Lentil Stir Fry - Reduce oil for lower fat content.
```

**Raises**:
- `ValueError`: If API key not set
- `openai.OpenAIError`: If API call fails

---

### display_plan()

Display complete meal plan in Streamlit UI.

```python
display_plan() -> tuple[pd.DataFrame, pd.Series]
```

**Parameters**: None

**Returns**: `tuple` containing:
1. `pd.DataFrame`: Selected meals with cleaned columns
2. `pd.Series`: Total nutrition summary

**Side Effects**:
- Displays meal plan in Streamlit UI
- Shows ingredients, steps, nutrition, GPT tips

**Example** (in Streamlit context):
```python
# In Stream_lit_Chat.py
planner = st.session_state['meal_planner']
selected_df, total_nutrition = planner.display_plan()

# Displays in UI:
# - Prompt used
# - Each meal with name, ingredients, steps, nutrition, tips
# - Total nutrition summary table
```

---

## GPTWeightNutritionPlanner Class

**Module**: `gpt_weight_nutrition_planner.py`

**Purpose**: Generate personalized exercise and nutrition plans using RAG (Retrieval-Augmented Generation).

### Constructor

```python
GPTWeightNutritionPlanner(vector_path="vector", model_name="gpt-4-turbo",
                          temperature=0.3)
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `vector_path` | str | No | "vector" | Path to FAISS vector store |
| `model_name` | str | No | "gpt-4-turbo" | OpenAI model to use |
| `temperature` | float | No | 0.3 | Creativity (0=focused, 1=creative) |

**Returns**: GPTWeightNutritionPlanner instance

**Raises**:
- `ValueError`: If OPENAI_API_KEY not set
- `FileNotFoundError`: If vector store not found

**Example**:
```python
from gpt_weight_nutrition_planner import GPTWeightNutritionPlanner

# Initialize with defaults
planner = GPTWeightNutritionPlanner()

# Or customize
planner = GPTWeightNutritionPlanner(
    vector_path="custom_vector_path",
    model_name="gpt-4-turbo",
    temperature=0.2  # More focused responses
)
```

**Attributes**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `vector_path` | str | Path to vector store |
| `model_name` | str | GPT model name |
| `temperature` | float | Response creativity |
| `vectorstore` | FAISS | Loaded vector store |
| `llm` | ChatOpenAI | GPT model instance |
| `chain` | Chain | LangChain QA chain |

---

### build_prompt()

Build personalized prompt for GPT-4 with user details.

```python
build_prompt(age, gender, height_cm, present_weight, target_weight,
             activity, calories) -> str
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `age` | int | Yes | User's age |
| `gender` | str | Yes | User's gender |
| `height_cm` | float | Yes | Height in cm |
| `present_weight` | float | Yes | Current weight in kg |
| `target_weight` | float | Yes | Goal weight in kg |
| `activity` | str | Yes | Activity level |
| `calories` | int | Yes | Daily calorie target |

**Returns**: `str` - Formatted prompt for GPT-4

**Example**:
```python
planner = GPTWeightNutritionPlanner()
prompt = planner.build_prompt(
    age=30,
    gender='male',
    height_cm=175,
    present_weight=85,
    target_weight=75,
    activity='moderate',
    calories=2138
)

print(prompt)
# Output:
# The user wants to lose weight.
#
# **User Details:**
# - Age: 30
# - Gender: male
# - Height: 175 cm
# - Current Weight: 85 kg
# - Target Weight: 75 kg
# - Activity Level: moderate
# - Suggested Caloric Intake: 2138 kcal/day
#
# **Instructions:**
# 1. Provide a beginner-friendly weekly physical activity/exercise...
# 2. Suggest dietary and nutritional guidance using the context...
```

---

### generate()

Generate personalized exercise and nutrition plan using RAG.

```python
generate(age, gender, height_cm, present_weight, target_weight,
         activity, calories) -> tuple[str, str, list[str]]
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `age` | int | Yes | User's age |
| `gender` | str | Yes | User's gender |
| `height_cm` | float | Yes | Height in cm |
| `present_weight` | float | Yes | Current weight in kg |
| `target_weight` | float | Yes | Goal weight in kg |
| `activity` | str | Yes | Activity level |
| `calories` | int | Yes | Daily calorie target |

**Returns**: `tuple` containing:
1. `str`: Full prompt sent to GPT-4
2. `str`: GPT-4 generated exercise & nutrition plan
3. `list[str]`: Retrieved document summaries with sources

**Process**:
1. Create retrieval query based on user goal
2. Search vector store for top k=7 documents
3. Filter by valid health/fitness sources
4. Build personalized prompt
5. Combine context + prompt → GPT-4
6. Return response with sources

**Example**:
```python
planner = GPTWeightNutritionPlanner()

prompt, response, docs = planner.generate(
    age=30,
    gender='male',
    height_cm=175,
    present_weight=85,
    target_weight=75,
    activity='moderate',
    calories=2138
)

print("Generated Plan:")
print(response)

print("\nSources Used:")
for i, doc in enumerate(docs, 1):
    print(f"{i}. {doc[:100]}...")

# Output:
# Generated Plan:
# **Weekly Exercise Plan:**
# Monday: 30min cardio + strength training (upper body)
# Tuesday: Rest or light yoga
# Wednesday: 45min cardio (running/cycling)
# ...
#
# Sources Used:
# 1. **Chunk 1 — Source:** physical
#    Physical activity recommendations for adults include...
# 2. **Chunk 2 — Source:** weight_loss
#    Effective weight loss strategies combine calorie deficit...
# ...
```

**Raises**:
- `ValueError`: If API key not set
- `openai.OpenAIError`: If API call fails

---

## GPTCustomPromptPlanner Class

**Module**: `GPTCustomPrompt.py`

**Purpose**: Handle custom user queries with context-aware RAG and similarity filtering.

### Constructor

```python
GPTCustomPromptPlanner(vector_path="vector", model_name="gpt-4-turbo",
                       temperature=0.4)
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `vector_path` | str | No | "vector" | Path to FAISS vector store |
| `model_name` | str | No | "gpt-4-turbo" | OpenAI model |
| `temperature` | float | No | 0.4 | Response creativity |

**Returns**: GPTCustomPromptPlanner instance

**Differences from GPTWeightNutritionPlanner**:
- Higher temperature (0.4 vs 0.3) for more conversational responses
- Includes similarity score filtering
- Enriches prompts with user context

**Example**:
```python
from GPTCustomPrompt import GPTCustomPromptPlanner

planner = GPTCustomPromptPlanner()
```

---

### enrich_prompt()

Add user context to make responses personalized.

```python
enrich_prompt(user_prompt, age, gender, height_cm, present_weight,
              target_weight, calories) -> str
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_prompt` | str | Yes | User's question |
| `age` | int | Yes | User's age |
| `gender` | str | Yes | User's gender |
| `height_cm` | float | Yes | Height in cm |
| `present_weight` | float | Yes | Current weight |
| `target_weight` | float | Yes | Goal weight |
| `calories` | int | Yes | Daily calorie target |

**Returns**: `str` - Enriched prompt with user context

**Example**:
```python
planner = GPTCustomPromptPlanner()
enriched = planner.enrich_prompt(
    user_prompt="What are good protein sources for weight loss?",
    age=30,
    gender='male',
    height_cm=175,
    present_weight=85,
    target_weight=75,
    calories=2138
)

print(enriched)
# Output:
# User wants to lose weight. Answer the following question...
#
# **User Details:**
# - Age: 30
# - Gender: male
# ...
#
# **User Question:**
# What are good protein sources for weight loss?
#
# **Instructions for GPT:**
# 1. Your response must be based only on user details and retrieved context.
# 2. Consider topics like weight management, food suggestions...
# ...
```

---

### generate()

Generate response to custom user question using RAG with similarity filtering.

```python
generate(user_prompt, age, gender, height_cm, present_weight, target_weight,
         calories, score_threshold=0.5) -> tuple[str, str, list[str]]
```

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `user_prompt` | str | Yes | - | User's question |
| `age` | int | Yes | - | User's age |
| `gender` | str | Yes | - | User's gender |
| `height_cm` | float | Yes | - | Height in cm |
| `present_weight` | float | Yes | - | Current weight |
| `target_weight` | float | Yes | - | Goal weight |
| `calories` | int | Yes | - | Daily calorie target |
| `score_threshold` | float | No | 0.5 | Similarity threshold |

**Returns**: `tuple` containing:
1. `str`: Enriched prompt sent to GPT-4
2. `str`: GPT-4 response
3. `list[str]`: Retrieved document summaries with similarity scores

**Similarity Threshold**:
- Uses L2 (Euclidean) distance in FAISS
- Lower score = higher similarity
- Default threshold: 0.5
- Only documents with score ≤ threshold are used

**Example**:
```python
planner = GPTCustomPromptPlanner()

prompt, response, docs = planner.generate(
    user_prompt="What exercises burn the most calories?",
    age=30,
    gender='male',
    height_cm=175,
    present_weight=85,
    target_weight=75,
    calories=2138,
    score_threshold=0.5
)

print("Response:", response)
print(f"\nRetrieved {len(docs)} relevant documents")

# Output:
# Response: Based on your profile and retrieved context, high-intensity
#           exercises like running, swimming, and HIIT burn the most
#           calories. For your weight loss goal...
#
# Retrieved 5 relevant documents
```

**Special Cases**:
- If no documents match threshold: Returns apologetic message
- If question is unrelated to health/nutrition: GPT responds with redirect message

---

## Utility Functions

### _safe_parse_list()

Safely parse string representations to lists.

**Module**: `meal_planner.py`

```python
_safe_parse_list(x: Any) -> list
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `x` | Any | Yes | Value to parse |

**Returns**: `list` - Parsed list or `[str(x)]` if parsing fails

**Example**:
```python
result1 = planner._safe_parse_list("['a', 'b', 'c']")
# Returns: ['a', 'b', 'c']

result2 = planner._safe_parse_list(['x', 'y', 'z'])
# Returns: ['x', 'y', 'z']

result3 = planner._safe_parse_list("invalid syntax")
# Returns: ['invalid syntax']

result4 = planner._safe_parse_list(None)
# Returns: ['None']
```

---

### load_recipes_direct()

Load recipe CSV with caching.

**Module**: `Stream_lit_Chat.py`

```python
@st.cache_data(show_spinner=False)
def load_recipes_direct(path: str) -> pd.DataFrame
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | str | Yes | Path to CSV file |

**Returns**: `pd.DataFrame` - Recipe database

**Caching**: Results cached by Streamlit to avoid re-loading on each rerun

**Example**:
```python
df = load_recipes_direct("Calories/Recipes.csv")
print(f"Loaded {len(df)} recipes")
```

---

## Constants and Configuration

### Activity Factors

**Module**: `weight_planner.py`

```python
ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "very": 1.725,
    "super": 1.9
}
```

### Meal Distribution

**Module**: `meal_planner.py`

```python
MEAL_STRUCTURE = {
    'breakfast': 0.25,  # 25% of daily calories
    'snack': 0.1,       # 10%
    'lunch': 0.35,      # 35%
    'dinner': 0.30      # 30%
}
```

### Valid Vector Sources

**Modules**: `gpt_weight_nutrition_planner.py`, `GPTCustomPrompt.py`

```python
VALID_SOURCES = [
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

### Model Configuration

```python
# GPT Models Used
GPT_4_TURBO = "gpt-4-turbo"       # Weight summary, exercise plans, chat
GPT_35_TURBO = "gpt-3.5-turbo"    # Meal annotations

# Embedding Model
EMBEDDING_MODEL = "text-embedding-ada-002"

# Temperature Settings
TEMP_FOCUSED = 0.3      # For exercise plans (deterministic)
TEMP_CONVERSATIONAL = 0.4  # For chat (slightly creative)
TEMP_DEFAULT = 1.0      # For summaries and annotations

# Token Limits
MAX_TOKENS_SUMMARY = 100
MAX_TOKENS_ANNOTATIONS = 500
```

### Data Paths

```python
RECIPES_CSV_PATH = "Calories/Recipes.csv"
VECTOR_STORE_PATH = "vector/"
IMAGES_PATH = "images/"
```

---

## Error Handling

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `ValueError` | API key not set | Set OPENAI_API_KEY in .env |
| `FileNotFoundError` | Data files missing | Verify file paths, run `git lfs pull` |
| `openai.OpenAIError` | API call failed | Check API key, internet, OpenAI status |
| `KeyError` | Missing session state variable | Initialize session state properly |
| `TypeError` | Wrong parameter type | Check parameter types in function calls |
| `RuntimeError` | FAISS index error | Rebuild vector store or check permissions |

### Error Handling Pattern

```python
try:
    result = api_call()
except ValueError as e:
    st.error(f"Configuration error: {e}")
except openai.OpenAIError as e:
    st.error(f"API error: {e}")
except Exception as e:
    st.error(f"Unexpected error: {e}")
    logging.error(f"Details: {e}", exc_info=True)
```

---

## Version Information

- **API Version**: 1.0
- **Last Updated**: December 2025
- **Python Version**: 3.8+
- **OpenAI API Version**: v1 (2023+)
- **LangChain Version**: 0.3.27+

---

## Usage Examples

### Complete Workflow Example

```python
import pandas as pd
from weight_planner import WeightPlanner
from meal_planner import MealPlanner
from gpt_weight_nutrition_planner import GPTWeightNutritionPlanner
from GPTCustomPrompt import GPTCustomPromptPlanner

# Step 1: Calculate weight plan
planner = WeightPlanner(
    present_weight_kg=85.0,
    target_weight_kg=75.0,
    age=30,
    height_cm=175,
    gender='male',
    activity_level='moderate',
    weekly_loss_lbs=1.0
)

forecast_df, target_cal, maint_cal = planner.simulate()
prompt, summary = planner.generate_summary()

print(f"Target Calories: {target_cal} kcal/day")
print(f"Duration: {forecast_df['Week'].max()} weeks")
print(f"Summary: {summary}")

# Step 2: Generate meal plan
df = pd.read_csv("Calories/Recipes.csv")
meal_planner = MealPlanner(df, total_calories=target_cal, diet_type="veg")
meal_planner.prepare_data()
meal_planner.select_meals()
meal_planner.generate_gpt_annotations()

print("\nSelected Meals:")
print(meal_planner.selected_meals_df[['meal_type', 'name', 'calories']])

# Step 3: Get exercise plan
exercise_planner = GPTWeightNutritionPlanner()
ex_prompt, ex_response, ex_docs = exercise_planner.generate(
    age=30, gender='male', height_cm=175,
    present_weight=85, target_weight=75,
    activity='moderate', calories=target_cal
)

print("\nExercise & Nutrition Plan:")
print(ex_response)

# Step 4: Ask custom question
chat_planner = GPTCustomPromptPlanner()
chat_prompt, chat_response, chat_docs = chat_planner.generate(
    user_prompt="What are the best snacks for my weight loss goal?",
    age=30, gender='male', height_cm=175,
    present_weight=85, target_weight=75,
    calories=target_cal
)

print("\nCustom Q&A:")
print(chat_response)
```

---

## Deprecated Features

None currently.

---

## Future API Changes

Planned for v2.0:
- Multi-day meal planning support
- Recipe filtering by allergens
- Macronutrient customization
- Integration with fitness tracker APIs

---

**For Questions or Issues**:
- GitHub Issues: https://github.com/yourusername/Weight_Planner/issues
- Documentation: See README.md and CODE_DOCUMENTATION.md

**Last Updated**: December 2025
**Maintained By**: Development Team
