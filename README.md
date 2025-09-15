# 🏋️‍♂️🥗 AI Weight & Meal Planner (Streamlit)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A clean, production-ready Streamlit app that turns a short user profile into a personalized **daily calorie target**, **weekly weight forecast**, **LLM-generated veg/non-veg meal plan** (ingredients + steps), **beginner exercise guidance**, and a **custom Q&A coach**.

> **Disclaimer:** Educational use only. Not medical advice.

---

## Overview

This project helps users plan weight change responsibly:
- Calculate calorie targets from profile + goal
- Forecast weekly weight trend
- Generate structured meal plans (veg/non-veg) with ingredients, cooking steps, and prep time
- Provide simple, safe exercise suggestions
- Answer free-text questions via a built-in coach (LLM)

The code is modular, with clear separation between UI (Streamlit), planning logic, and LLM prompts.

---

## Features

- **Profile inputs**: age, height, current & target weight, activity level, diet (veg/non-veg), weekly goal  
- **Daily targets**: calories (optionally extend to protein/macros)  
- **Weekly forecast**: line chart of projected weight trend  
- **Meal planner**: named meals with ingredients, steps, and notes  
- **Exercise basics**: gentle weekly structure for beginners  
- **Custom Q&A**: ask “how much protein should I take?”, “is this meal okay?”, etc.

---

## Project Structure

```
.
├─ Stream_lit_Chat.py              # Main Streamlit app (UI + navigation)
├─ main.py                         # (Optional) alternate entry point
├─ weight_planner.py               # Targets, calorie math, weekly forecast
├─ meal_planner.py                 # Rule-based meal/snack helpers
├─ gpt_weight_nutrition_planner.py # LLM prompts + generation
├─ GPTCustomPrompt.py              # Custom Q&A coach
├─ Weight_planner.ipynb            # Notebook (experiments / drafts)
├─ requirements.txt
├─ images/                         # Screenshots/assets
├─ Calories/                       # Datasets (use Git LFS for large CSVs)
├─ vector/                         # (optional) vector store or artifacts
├─ .gitattributes                  # LF policy + Git LFS rules
└─ .gitignore
```

---

## Quick Start

### 1) Clone
```bash
git clone https://github.com/chandueddala/Weight_Planner.git
cd Weight_Planner
```

### 2) (If repo uses large files) enable Git LFS
```bash
git lfs install
git lfs pull
```

### 3) Create a virtual environment & install deps
```bash
# Windows (PowerShell)
python -m venv .venv
. .\.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### 4) Configure environment
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-...
# Optional:
# OPENAI_MODEL=gpt-4o-mini
```

### 5) Run
```bash
streamlit run Stream_lit_Chat.py
# or
python -m streamlit run Stream_lit_Chat.py
```
Open the URL Streamlit prints (default: http://localhost:8501).

---

## Configuration & Data

- **Model keys**: `OPENAI_API_KEY` is read from `.env`. You can set `OPENAI_MODEL` to control the default model.
- **Dataset paths**: prefer forward slashes on Windows (e.g., `"Calories/Recipes.csv"`) to avoid `\R` escape warnings.
- **Large files**: this repo tracks big assets with **Git LFS** via `.gitattributes`.  
  If you ever see pointer text files, run:
  ```bash
  git lfs install
  git lfs pull
  ```
- **Sample data**: consider adding a small `Calories/Recipes_sample.csv` so the app runs without fetching full datasets.

---

## Usage Notes

- Start on the **Main Planner** page, fill profile inputs, and submit.  
- Review **daily calories** and the **weekly forecast** chart.  
- Generate **meal plans** (veg/non-veg) with ingredients and steps.  
- Use the **Custom Coach** panel to ask nutrition/fitness questions.  
- Use the **Reset** button to clear state.

---

## Screenshots (placeholders)

Add images to `images/` and update the links:

| Planner | Forecast | Meal Prompt |
|---|---|---|
| ![Planner](images/planner.png) | ![Forecast](images/forecast.png) | ![Prompt](images/prompt.png) |

---

## Troubleshooting

**Large file push blocked (>100 MB)**  
Use Git LFS. Ensure patterns are tracked and `.gitattributes` is committed:
```bash
git lfs track "Calories/*.csv"
git add .gitattributes
git add Calories/*.csv
git commit -m "Track large files via LFS"
git push
```
If large files were already committed earlier, migrate history:
```bash
git lfs migrate import --everything --include="Calories/*.csv"
git push --force-with-lease
```

**Line endings warning on Windows**  
“LF will be replaced by CRLF” is harmless. To normalize:
```bash
git config --global core.autocrlf input
git add --renormalize .
git commit -m "Normalize line endings"
```

**FileNotFoundError for CSVs**  
Run Streamlit from the repo root and confirm `Calories/Recipes.csv` (or sample) exists and the path matches.

**LangChain deprecations**  
Use community imports:
```python
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS

# from langchain.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
```

---

## Roadmap

- Macro breakdown (carbs/fat) & exportable shopping list  
- Multi-day planning with leftovers  
- Unit toggles (kg/lb, cm/in)  
- PDF/CSV export of plans  
- Auth + cloud persistence

---

## Contributing

Contributions welcome!  
- Open an issue for feature requests or non-trivial changes.  
- Include screenshots for UI updates.  
- Keep PRs focused and tested.

---

## License

Licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.
