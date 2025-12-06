# 🏋️‍♂️🥗 AI Weight & Meal Planner

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.49.1-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com/)

A comprehensive, AI-powered weight management and personalized meal planning application that combines scientific nutrition calculations with intelligent GPT-based recommendations. This application provides users with customized weight loss/gain plans, daily meal suggestions, exercise routines, and an interactive AI dietitian chatbot.

> **Disclaimer:** Educational use only. Not medical advice. Consult healthcare professionals before starting any diet or exercise program.

---

## 📚 Complete Documentation

**New to the project?** Check out our comprehensive documentation:

- 📖 **[Documentation Index](docs/INDEX.md)** - Start here! Navigate all docs
- 🚀 **[Setup Guide](docs/SETUP.md)** - Installation for Windows/macOS/Linux
- 🏗️ **[Architecture](docs/ARCHITECTURE.md)** - System design and data flows
- 💻 **[Code Documentation](docs/CODE_DOCUMENTATION.md)** - Complete code walkthrough
- 📚 **[API Reference](docs/API_REFERENCE.md)** - All functions and classes
- ⚙️ **[.env.example](.env.example)** - Environment configuration template

---

## ✨ Features

### 1. **Personalized Weight Planning**
- Scientific BMR (Basal Metabolic Rate) calculation using Mifflin-St Jeor equation
- Customizable weight goals (loss or gain)
- Weekly weight progression forecasting
- Activity level-based calorie adjustments
- Visual weight trajectory charts

### 2. **Intelligent Meal Planning**
- Diet-specific recommendations (Vegetarian, Non-Vegetarian, Vegan)
- Calorie-optimized daily meal plans (Breakfast, Lunch, Dinner, Snacks)
- Complete nutritional breakdown (Protein, Fats, Carbs, Sugar, Sodium)
- Step-by-step cooking instructions
- AI-enhanced meal naming and optimization tips

### 3. **AI-Powered Exercise & Nutrition Guidance**
- RAG (Retrieval-Augmented Generation) based recommendations
- Personalized weekly exercise routines
- Context-aware nutritional advice from curated health databases
- Evidence-based suggestions with source attribution

### 4. **Custom AI Dietitian Chatbot**
- Interactive Q&A interface with persistent chat history
- Context-aware responses based on your profile
- Answers about nutrition, exercise, and diet-related queries
- Source citations for transparency

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/))
- Git (optional, for cloning)

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/chandueddala/Weight_Planner.git
cd Weight_Planner
```

#### 2. (If repo uses large files) Enable Git LFS
```bash
git lfs install
git lfs pull
```

#### 3. Create virtual environment & install dependencies
```bash
# Windows (PowerShell)
python -m venv myenv
myenv\Scripts\activate

# macOS/Linux
python3 -m venv myenv
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Configure environment
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

See [.env.example](.env.example) for all configuration options.

#### 5. Run the application
```bash
# Option 1: Using main.py (recommended)
python main.py

# Option 2: Using Streamlit directly
streamlit run Stream_lit_Chat.py
```

#### 6. Access the app
Open your browser to: **http://localhost:8501**

**Need more help?** See our detailed [Setup Guide](docs/SETUP.md) with troubleshooting.

---

## 📖 Usage

### Step-by-Step Guide

1. **Enter Your Profile** (in the sidebar)
   - Age, gender, height, current/target weight
   - Activity level and diet preference
   - Weekly weight change goal
   - Click **Submit**

2. **View Your Weight Forecast**
   - See weekly weight progression chart
   - Review target daily calories
   - Read AI-generated motivational summary

3. **Explore Your Meal Plan**
   - Complete daily meal plan (breakfast, lunch, dinner, snack)
   - Ingredients and step-by-step cooking instructions
   - Nutritional breakdown and AI suggestions

4. **Get Exercise & Nutrition Guidance**
   - Click **Exercise & Nutrition Plan**
   - Receive personalized weekly exercise routine
   - View evidence-based nutritional recommendations

5. **Chat with AI Dietitian**
   - Click **Proceed to GPT Chat**
   - Ask questions about nutrition, exercise, diet
   - Get context-aware responses with sources

6. **Reset and Start Over**
   - Use **Reset Everything** button to clear all data

---

## 🏗️ Project Structure

```
Weight_Planner/
│
├── README.md                            # This file
├── .env.example                         # Environment configuration template
│
├── main.py                              # Application entry point
├── Stream_lit_Chat.py                   # Main Streamlit UI
├── weight_planner.py                    # Weight calculation & BMR logic
├── meal_planner.py                      # Meal selection & optimization
├── gpt_weight_nutrition_planner.py      # RAG-based exercise planner
├── GPTCustomPrompt.py                   # Custom chatbot handler
│
├── requirements.txt                     # Python dependencies
├── Weight_planner.ipynb                 # Jupyter notebook (development)
│
├── docs/                                # 📚 Complete documentation
│   ├── INDEX.md                         # Documentation navigator
│   ├── SETUP.md                         # Installation guide
│   ├── ARCHITECTURE.md                  # System architecture
│   ├── CODE_DOCUMENTATION.md            # Code walkthrough
│   └── API_REFERENCE.md                 # API reference
│
├── Calories/
│   └── Recipes.csv                      # Recipe database (10k+ recipes)
│
├── vector/                              # FAISS vector store for RAG
│   ├── index.faiss                      # Vector embeddings
│   └── index.pkl                        # Metadata
│
└── images/                              # UI assets (avatars, animations)
```

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Core programming language |
| **Streamlit** | 1.49.1 | Web UI framework |
| **OpenAI GPT-4** | Latest | AI recommendations & chat |
| **GPT-3.5-turbo** | Latest | Meal annotations |
| **LangChain** | 0.3.27+ | RAG framework |
| **FAISS** | 1.12.0 | Vector similarity search |
| **Pandas** | 2.3.2 | Data manipulation |
| **NumPy** | 2.3.3 | Numerical computing |

See [requirements.txt](requirements.txt) for complete dependencies.

---

## 📊 Data Sources

1. **Recipe Database**: 10,000+ recipes with complete nutritional information
2. **Vector Store**: Health & fitness knowledge base including:
   - Dietary guidelines
   - Physical activity recommendations
   - Weight management research
   - Exercise routines
   - Human nutrition science

---

## ⚙️ Configuration & Data

- **Model keys**: `OPENAI_API_KEY` is required. Set in `.env` file.
- **Dataset paths**: Uses `Calories/Recipes.csv` for meal planning.
- **Large files**: Tracked with **Git LFS** via `.gitattributes`.
  ```bash
  git lfs install
  git lfs pull
  ```
- **Vector store**: Pre-built FAISS index in `vector/` directory.

See [.env.example](.env.example) for all configuration options.

---

## 🔧 Troubleshooting

### Common Issues

**"Python not found"**
- Windows: Use `py` instead of `python`
- macOS/Linux: Use `python3` explicitly

**"ModuleNotFoundError"**
- Ensure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

**"API key not found"**
- Create `.env` file in project root
- Add: `OPENAI_API_KEY=sk-your-key-here`
- Restart application

**"Port 8501 already in use"**
- Kill existing Streamlit: `pkill -f streamlit` (macOS/Linux)
- Or use different port: `streamlit run Stream_lit_Chat.py --server.port 8502`

**"FileNotFoundError for Recipes.csv"**
- Run from project root directory
- Ensure Git LFS files are downloaded: `git lfs pull`

**"Large file push blocked"**
- Use Git LFS for files >100 MB:
  ```bash
  git lfs track "Calories/*.csv"
  git add .gitattributes
  git commit -m "Track large files via LFS"
  git push
  ```

**LangChain deprecation warnings**
- Use community imports:
  ```python
  from langchain_community.vectorstores import FAISS
  from langchain_community.embeddings import OpenAIEmbeddings
  ```

**For detailed troubleshooting**, see [docs/SETUP.md](docs/SETUP.md#troubleshooting).

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Make your changes
4. Commit: `git commit -m 'Add some AmazingFeature'`
5. Push: `git push origin feature/AmazingFeature`
6. Open a Pull Request

**Guidelines**:
- Follow PEP 8 style guidelines
- Add docstrings to functions
- Update documentation as needed
- Include tests for new features

See our [Architecture Guide](docs/ARCHITECTURE.md) for design patterns.

---

## 🔮 Roadmap

- [x] Weight forecasting with BMR calculation
- [x] AI-powered meal planning
- [x] Exercise & nutrition guidance with RAG
- [x] Custom chatbot interface
- [ ] Multi-day meal planning (7-day, 14-day, 30-day)
- [ ] Macronutrient customization (carbs/protein/fat targets)
- [ ] Exportable shopping lists
- [ ] PDF/Excel export of plans
- [ ] Unit toggles (kg/lb, cm/in)
- [ ] Integration with fitness trackers (Fitbit, Apple Health)
- [ ] Mobile app version
- [ ] Recipe substitution recommendations
- [ ] Food photo recognition
- [ ] Multi-language support
- [ ] Social features (share plans, progress tracking)
- [ ] Auth + cloud persistence

---

## 📄 License

Licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Mifflin-St Jeor Equation** for BMR calculations ([Source](https://www.leighpeele.com/mifflin-st-jeor-calculator))
- **OpenAI** for GPT-4 and GPT-3.5-turbo models
- **LangChain** for RAG framework
- **Streamlit** for the web framework
- **FAISS** by Meta AI for vector similarity search
- Recipe data curated from public nutrition databases

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/chandueddala/Weight_Planner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chandueddala/Weight_Planner/discussions)
- **Documentation**: [Complete Docs](docs/INDEX.md)

---

**Made with ❤️ for health-conscious individuals seeking AI-powered nutrition guidance**
