# AI Weight & Meal Planner 🏋️‍♂️🥗

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.49.1-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com/)

A comprehensive, AI-powered weight management and personalized meal planning application that combines scientific nutrition calculations with intelligent GPT-based recommendations. This application provides users with customized weight loss/gain plans, daily meal suggestions, exercise routines, and an interactive AI dietitian chatbot.

## 🌟 Features

### 1. **Personalized Weight Planning**
- Scientific BMR (Basal Metabolic Rate) calculation using the Mifflin-St Jeor equation
- Customizable weight goals (loss or gain)
- Weekly weight progression forecasting
- Activity level-based calorie adjustments
- Visual weight trajectory charts

### 2. **Intelligent Meal Planning**
- Diet-specific meal recommendations (Vegetarian, Non-Vegetarian, Vegan)
- Calorie-optimized daily meal plans (Breakfast, Lunch, Dinner, Snacks)
- Nutritional breakdown for each meal (Protein, Fats, Carbs, Sugar, Sodium)
- Step-by-step cooking instructions
- AI-enhanced meal naming and optimization tips

### 3. **AI-Powered Exercise & Nutrition Guidance**
- RAG (Retrieval-Augmented Generation) based recommendations
- Personalized weekly exercise routines
- Context-aware nutritional advice
- Evidence-based suggestions from curated health databases

### 4. **Custom AI Dietitian Chatbot**
- Interactive Q&A interface with persistent chat history
- Context-aware responses based on user profile
- Nutrition, exercise, and diet-related queries
- Source citations for all recommendations
- Cosine similarity-based relevant context retrieval

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Architecture](#-architecture)
- [API Keys & Environment](#-api-keys--environment)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Git (for cloning the repository)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Weight_Planner.git
cd Weight_Planner
```

2. **Create and activate virtual environment**
```bash
# On Windows
python -m venv myenv
myenv\Scripts\activate

# On macOS/Linux
python3 -m venv myenv
source myenv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file in the root directory
echo OPENAI_API_KEY=your_openai_api_key_here > .env
```

5. **Run the application**
```bash
# Option 1: Using main.py (recommended)
python main.py

# Option 2: Using Streamlit directly
streamlit run Stream_lit_Chat.py
```

6. **Access the application**
- Open your browser and navigate to `http://localhost:8501`

## 🔧 Installation

### Detailed Setup Guide

#### Step 1: System Requirements
Ensure you have the following installed:
- **Python**: Version 3.8 or higher
- **pip**: Latest version (upgrade using `pip install --upgrade pip`)
- **Git**: For version control
- **Internet connection**: For downloading dependencies and API calls

#### Step 2: Environment Setup

**Windows:**
```bash
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Data Requirements
The application requires:
- **Recipe Database**: Located in `Calories/Recipes.csv`
- **Vector Store**: Pre-built FAISS index in `vector/` directory
- **Images**: UI assets in `images/` folder

All these are included in the repository.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Application Settings

You can customize the following parameters in the Streamlit sidebar:

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| Age | User's age | 18-100 | 24 |
| Gender | User's gender | Male/Female | Male |
| Height | Height in centimeters | 120-220 cm | 176 cm |
| Current Weight | Present weight | 40-200 kg | 85 kg |
| Target Weight | Desired weight | 40-200 kg | 75 kg |
| Activity Level | Daily activity | Sedentary/Light/Moderate/Very/Super | Moderate |
| Weekly Change | Weight change per week | 0.4-1.0 lbs | 0.5 lbs |
| Diet Preference | Dietary restrictions | Veg/Non-Veg/Vegan | Veg |

## 📖 Usage

### Step-by-Step User Guide

#### 1. Launch the Application
```bash
python main.py
```
Navigate to `http://localhost:8501` in your browser.

#### 2. Enter Your Profile
- Fill in the **User Profile** form in the left sidebar
- Select your age, gender, height, and weight details
- Choose your activity level and diet preference
- Click **Submit** to generate your personalized plan

#### 3. View Weight Forecast
- Review the **Weekly Weight Forecast** chart
- Check your **Target Daily Calories** and **Maintenance Calories**
- Read the AI-generated motivational summary

#### 4. Explore Meal Plans
- View your personalized daily meal plan with:
  - Breakfast, Lunch, Dinner, and Snacks
  - Complete ingredient lists
  - Step-by-step cooking instructions
  - Nutritional breakdowns
  - AI-enhanced meal suggestions

#### 5. Get Exercise & Nutrition Guidance
- Click the **Exercise & Nutrition Plan** button
- Receive a personalized weekly exercise routine
- Get evidence-based nutritional recommendations
- Review retrieved context sources for transparency

#### 6. Chat with AI Dietitian
- Click **Proceed to GPT Chat** to unlock the custom chatbot
- Ask questions about:
  - Specific food recommendations
  - Exercise modifications
  - Nutrition-related queries
  - Diet adjustments
- View the context sources and prompts used for each response

#### 7. Reset and Start Over
- Use the **Reset Everything** button to clear all data and start fresh

## 📁 Project Structure

```
Weight_Planner/
│
├── main.py                              # Application entry point
├── Stream_lit_Chat.py                   # Main Streamlit UI application
├── weight_planner.py                    # Weight calculation & BMR logic
├── meal_planner.py                      # Meal selection & optimization
├── gpt_weight_nutrition_planner.py      # RAG-based exercise/nutrition planner
├── GPTCustomPrompt.py                   # Custom chatbot handler
│
├── requirements.txt                     # Python dependencies
├── .env                                 # Environment variables (not in repo)
├── .gitignore                          # Git ignore rules
├── .gitattributes                      # Git LFS configuration
│
├── Calories/
│   └── Recipes.csv                      # Recipe database (10k+ recipes)
│
├── vector/                              # FAISS vector store for RAG
│   ├── index.faiss                      # Vector embeddings
│   └── index.pkl                        # Metadata
│
├── images/                              # UI assets
│   ├── CHi6.gif                        # Sidebar animation
│   ├── Male.png                        # Male user avatar
│   ├── Female.png                      # Female user avatar
│   └── nutritionist_dietitian_*.webp   # Bot avatar
│
├── myenv/                               # Virtual environment (not in repo)
│
├── __pycache__/                         # Python cache (not in repo)
│
├── docs/                                # Documentation
│   ├── ARCHITECTURE.md                  # System architecture
│   ├── SETUP.md                         # Installation guide
│   └── API_REFERENCE.md                 # API documentation
│
└── Weight_planner.ipynb                 # Jupyter notebook (development/testing)
```

## 🛠️ Technologies Used

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Core programming language |
| **Streamlit** | 1.49.1 | Web UI framework |
| **OpenAI GPT-4** | Latest | AI text generation & recommendations |
| **GPT-3.5-turbo** | Latest | Meal annotations |
| **LangChain** | 0.3.27+ | RAG framework & chain orchestration |
| **FAISS** | 1.12.0 | Vector similarity search |
| **Pandas** | 2.3.2 | Data manipulation |

### Key Libraries

**AI & ML:**
- `openai==1.107.2` - OpenAI API client
- `langchain==0.3.27` - LangChain framework
- `langchain-community==0.3.29` - Community integrations
- `faiss-cpu==1.12.0` - Facebook AI Similarity Search
- `tiktoken==0.11.0` - OpenAI tokenizer

**Data Processing:**
- `pandas==2.3.2` - Data analysis
- `numpy==2.3.3` - Numerical computing
- `pyarrow==21.0.0` - Columnar data format

**Web Framework:**
- `streamlit==1.49.1` - Web application framework
- `altair==5.5.0` - Declarative visualization
- `pydeck==0.9.1` - Deck.gl bindings

**Utilities:**
- `python-dotenv==1.1.1` - Environment variable management
- `requests==2.32.5` - HTTP library
- `Pillow==11.3.0` - Image processing

## 🏗️ Architecture

The application follows a modular, component-based architecture. For detailed architecture documentation, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (Streamlit Web App)                       │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   Weight Planner Module  │    │   Meal Planner Module    │
│  - BMR Calculation       │    │  - Recipe Selection      │
│  - Calorie Computation   │    │  - Nutrition Balancing   │
│  - Weight Forecasting    │    │  - GPT Meal Annotation   │
└──────────┬───────────────┘    └─────────┬────────────────┘
           │                              │
           └──────────────┬───────────────┘
                          ▼
           ┌──────────────────────────────┐
           │      GPT Integration Layer   │
           │  - Exercise Planner (RAG)    │
           │  - Custom Chat (RAG)         │
           │  - Context Retrieval         │
           └──────────┬───────────────────┘
                      │
         ┌────────────┴────────────┐
         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│  OpenAI API     │      │  FAISS Vector   │
│  (GPT-4/3.5)    │      │  Store          │
└─────────────────┘      └─────────────────┘
```

### Core Components

1. **WeightPlanner** (`weight_planner.py`)
   - Calculates BMR using Mifflin-St Jeor equation
   - Computes maintenance and target calories
   - Generates weekly weight forecasts
   - Creates motivational summaries via GPT-4

2. **MealPlanner** (`meal_planner.py`)
   - Filters recipes by diet type and calorie targets
   - Optimizes meal selection (low fat, high protein, low sugar)
   - Generates AI-enhanced meal names and tips
   - Provides complete nutritional breakdowns

3. **GPTWeightNutritionPlanner** (`gpt_weight_nutrition_planner.py`)
   - Implements RAG (Retrieval-Augmented Generation)
   - Retrieves relevant health/fitness context from vector store
   - Generates personalized exercise routines
   - Provides evidence-based nutritional guidance

4. **GPTCustomPromptPlanner** (`GPTCustomPrompt.py`)
   - Handles user-initiated chat queries
   - Uses cosine similarity for context filtering
   - Enriches prompts with user profile data
   - Maintains conversation context

## 🔑 API Keys & Environment

### Getting Your OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key and add it to your `.env` file

### Environment File Example

Create a `.env` file:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Security Best Practices

- ✅ **Never commit** `.env` to version control
- ✅ Use `.gitignore` to exclude sensitive files
- ✅ Rotate API keys periodically
- ✅ Set usage limits on your OpenAI account
- ✅ Use environment-specific `.env` files for dev/prod

## 📊 Data Sources

The application uses curated health and nutrition data:

1. **Recipe Database** (`Calories/Recipes.csv`)
   - 10,000+ recipes with complete nutritional information
   - Categorized by meal type and diet preference
   - Includes ingredients, steps, and macro/micronutrients

2. **Vector Store** (`vector/`)
   - Embeddings from authoritative health sources:
     - `diet` - Dietary guidelines
     - `physical` - Physical activity recommendations
     - `Weight` - Weight management research
     - `GymDataset` - Exercise routines
     - `weight_gain` - Weight gain strategies
     - `weight_loss` - Weight loss protocols
     - `Human_Nut` - Human nutrition science
     - `Nut_Science` - Nutritional science research

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Mifflin-St Jeor Equation** for BMR calculations ([Source](https://www.leighpeele.com/mifflin-st-jeor-calculator))
- **OpenAI** for GPT-4 and GPT-3.5-turbo models
- **LangChain** for RAG framework
- **Streamlit** for the amazing web framework
- **FAISS** by Meta AI for efficient similarity search
- Recipe data curated from public nutrition databases

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Weight_Planner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Weight_Planner/discussions)
- **Email**: your.email@example.com

## 🔮 Roadmap

- [ ] Multi-day meal planning (7-day, 14-day, 30-day)
- [ ] Integration with fitness trackers (Fitbit, Apple Health)
- [ ] Mobile app version (React Native)
- [ ] Food photo recognition & calorie estimation
- [ ] Social features (share plans, progress tracking)
- [ ] Support for more languages
- [ ] Offline mode with local LLM support
- [ ] Export plans to PDF/Excel
- [ ] Recipe substitution recommendations
- [ ] Grocery shopping list generator

---

**Made with ❤️ for health-conscious individuals seeking AI-powered nutrition guidance**
