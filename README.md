# 🏋️‍♂️🥗 AI Weight & Meal Planner (Streamlit)

Personalized weight & meal planning assistant in Streamlit.  
Enter your profile and goal → get **daily macros**, a **weekly weight forecast**, **LLM-generated veg/non-veg meals** (ingredients + steps), simple **exercise suggestions**, and a **custom Q&A coach**.

> ⚠️ For education only — not medical advice.

---

## ✨ Features

- **User profile inputs**: age, height, current/target weight, activity, diet (veg/non-veg), weekly goal
- **Daily targets**: calories 
- **Weekly forecast**: clean weight trend chart
- **Meal planner**: named meals with ingredients, cooking steps, prep time, notes
- **Exercise basics**: beginner-friendly weekly plan
- **Custom coach**: ask free-text questions (e.g., protein timing)

---

## 📦 Repo layout





├─ Stream_lit_Chat.py # Main Streamlit app (UI + navigation)
├─ main.py # (Optional) alt entry point
├─ weight_planner.py # Calorie math, targets, forecasting
├─ meal_planner.py # Rule-based helpers for meals/snacks
├─ gpt_weight_nutrition_planner.py # LLM prompts + generation
├─ GPTCustomPrompt.py # Custom Q&A coach
├─ Weight_planner.ipynb # Notebook (experiments)
├─ requirements.txt
├─ images/ # Screenshots/assets (add yours here)
├─ Calories/ # Datasets (large files likely via LFS)
├─ vector/ # (optional) vector store or assets
├─ .gitattributes # includes Git LFS rules
└─ .gitignore

yaml
Copy code

> Verified from the repository file list on the `main` branch. :contentReference[oaicite:1]{index=1}

---

## 🚀 Quickstart

**1) Clone**
```bash
git clone https://github.com/chandueddala/Weight_Planner.git
cd Weight_Planner
2) (If repo uses large files) fetch with Git LFS

bash
Copy code
git lfs install
git lfs pull
3) Create env & install

bash
Copy code
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
4) Configure API keys
Create .env in the project root:

env
Copy code
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
5) Run the app

bash
Copy code
streamlit run Stream_lit_Chat.py
# or
python -m streamlit run Stream_lit_Chat.py
Open the URL Streamlit prints (usually http://localhost:8501).

🧰 Configuration & data
Models: set OPENAI_API_KEY and optionally OPENAI_MODEL in .env.

Recipes/data: if you’re using local CSVs under Calories/ (e.g., Recipes.csv), keep paths portable:

Use forward slashes on Windows: "Calories/Recipes.csv" (avoids \R escape warnings).

Large files: this repo includes .gitattributes for Git LFS. If you see pointer text files, run:

bash
Copy code
git lfs install
git lfs pull
Sample data: consider adding a small Calories/Recipes_sample.csv for quick tests (keeps the repo lightweight).

📸 Screenshots
Add your images to images/ and link them here. Example:

Planner	Forecast	Meal Prompt

🧱 Tech stack
Streamlit, Python

App modules: Stream_lit_Chat.py, weight_planner.py, meal_planner.py, GPTCustomPrompt.py, gpt_weight_nutrition_planner.py

Data/Assets: Calories/, images/, vector/

See requirements.txt for dependencies

🛠️ Troubleshooting
Line endings (LF ↔ CRLF) on Windows

Harmless warnings like “LF will be replaced by CRLF”. To normalize:

bash
Copy code
git config --global core.autocrlf input
git add --renormalize .
git commit -m "Normalize line endings"
Large file push blocked (>100 MB)

Ensure Git LFS is tracking your data paths and that .gitattributes is committed:

bash
Copy code
git lfs track "Calories/*.csv"
git add .gitattributes
git add Calories/*.csv
git commit -m "Track large files via LFS"
git push
If large files were already committed earlier, migrate history:

bash
Copy code
git lfs migrate import --everything --include="Calories/*.csv"
git push --force-with-lease
FileNotFoundError for CSVs

Confirm the file exists relative to the repo root and you run Streamlit from the project root.

Prefer "Calories/Recipes.csv" (forward slashes) on Windows.

LangChain deprecation warnings

Replace imports:

from langchain.vectorstores import FAISS → from langchain_community.vectorstores import FAISS

from langchain.embeddings import OpenAIEmbeddings → from langchain_community.embeddings import OpenAIEmbeddings

🗺️ Roadmap
 Macro breakdown (carbs/fat) & exportable shopping list

 Multi-day meal planning with leftovers

 Unit toggles (kg/lb, cm/in)

 PDF/CSV export

 Auth + cloud persistence

🤝 Contributing
PRs welcome! Please open an issue first for feature requests or significant changes.
Describe your change clearly and include screenshots for UI tweaks.

📜 License
Apache License 2.0

