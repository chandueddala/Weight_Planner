# 🏋️‍♂️🥗 AI Weight & Meal Planner (Streamlit)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Personalized weight & meal planning assistant built with Streamlit.  
Enter your profile and goal → get **daily calories/macros**, a **weekly weight forecast**, **LLM-generated veg/non-veg meals** (ingredients + steps), simple **exercise suggestions**, and a **custom Q&A coach**.

> ⚠️ For education only — not medical advice.

---

## ✨ Features

- **User profile inputs**: age, height, current/target weight, activity level, diet (veg/non-veg), weekly goal  
- **Daily targets**: calories (and protein guidance, if enabled)  
- **Weekly forecast**: clean weight trend chart  
- **Meal planner (LLM or rules)**: named meals with ingredients, cooking steps, prep time, notes  
- **Exercise basics**: beginner-friendly weekly plan  
- **Custom coach**: ask free-text questions (e.g., “protein timing?”)

---

## 📦 Repository Layout

├─ Stream_lit_Chat.py # Main Streamlit app (UI + navigation)
├─ main.py # (Optional) alternate entry point
├─ weight_planner.py # Calorie math, targets, forecasting
├─ meal_planner.py # Rule-based meal/snack helpers
├─ gpt_weight_nutrition_planner.py # LLM prompts + generation
├─ GPTCustomPrompt.py # Custom Q&A coach
├─ Weight_planner.ipynb # Notebook (experiments)
├─ requirements.txt
├─ images/ # Screenshots/assets
├─ Calories/ # Datasets (large files → use Git LFS)
├─ vector/ # (optional) vector store or assets
├─ .gitattributes # includes Git LFS rules
└─ .gitignore

---

## 🚀 Quickstart

**1) Clone**
```bash
git clone https://github.com/chandueddala/Weight_Planner.git
cd Weight_Planner

2) (If repo uses large files) fetch with Git LFS

git lfs install
git lfs pull
