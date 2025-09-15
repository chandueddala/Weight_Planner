import pandas as pd
import ast
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class MealPlanner:
    def __init__(self, df, total_calories=2000, diet_type="vegan", api_key=os.getenv("OPENAI_API_KEY")):
        self.df = df.copy()
        self.total_calories = total_calories
        self.diet_type = diet_type
        self.api_key = api_key
        self.selected_meals_df = pd.DataFrame()

    def _safe_parse_list(self, x):
        try:
            parsed = ast.literal_eval(x) if isinstance(x, str) else x
            return parsed if isinstance(parsed, list) else [str(parsed)]
        except:
            return [str(x)]

    def prepare_data(self):
        self.df['ingredients'] = self.df['ingredients'].apply(self._safe_parse_list)
        self.df['steps'] = self.df['steps'].apply(self._safe_parse_list)

    def select_meals(self):
        meal_structure = {
            'breakfast': 0.25,
            'snack': 0.1,
            'lunch': 0.35,
            'dinner': 0.30
        }

        selected_meals = []
        self.prompt = f"Create a personalized 1-day meal plan for a {self.diet_type} diet with a total of {self.total_calories} kcal.\n\nHere is the proposed structure with ingredients and estimated calories:\n\n"

        for meal, ratio in meal_structure.items():
            base_type = 'snack' if 'snack' in meal else meal
            target_kcal = self.total_calories * ratio

            matches = self.df[
                (self.df['meal_type'].str.lower() == base_type.lower()) &
                (self.df['diet_type'].str.lower() == self.diet_type.lower())
            ]

            matches = matches[matches['sugar'] <= 20]

            if not matches.empty:
                matches_sorted = matches.sort_values(by=['total_fat', 'protein', 'calories'], ascending=[True, False, True])
                closest = matches_sorted.iloc[(matches_sorted['calories'] - target_kcal).abs().argsort()[:1]]
                row = closest.iloc[0]
                selected_meals.append(row)
                self.prompt += f"• {base_type.title()} ({int(row['calories'])} kcal): Ingredients: {', '.join(row['ingredients'][:5])}\n"

        self.selected_meals_df = pd.DataFrame(selected_meals).reset_index(drop=True)

    def generate_gpt_annotations(self):
        if "Your task:" not in self.prompt:
          self.prompt += (
            "\nYour task:"
            "\n1. Generate a more appealing name for each meal."
            "\n2. Write a brief 1-line recommendation for each (e.g., reduce oil, boost protein)."
            "\n3. If any ingredient pushes the calories too high, mention that.")

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": self.prompt}],
            max_tokens=500
        )
        gpt_output = response.choices[0].message.content
        gpt_lines = [line for line in gpt_output.strip().split("\n") if line.strip()]
        self.selected_meals_df['gpt_name_and_tip'] = gpt_lines[:len(self.selected_meals_df)]

    def display_plan(self):
        st.subheader("Prompt Sent to Model")
        st.text_area("Prompt", self.prompt, height=200)

        st.subheader("🍉🍓🍒🥝🍌Final Meal Plan🍉🍓🍒🥝🍌")
        for i, row in self.selected_meals_df.iterrows():
            st.subheader(f"**🥣{row['meal_type'].capitalize()}**")
            st.markdown(f"**🍔 Name**:{row['name']} -----------{row['minutes']}Minutes")
            st.markdown(f"**❗Suggestion:** {row['gpt_name_and_tip']}")
            st.write(f"**🥗Ingredients:** {', '.join(row['ingredients'])}")
            st.markdown("**🍝Cooking Steps:**")
            for step in row['steps']:
                st.write(f"➡️{step}")
            st.markdown(f"**Nutrition:** {int(row['calories'])} kcal | Protein: {row['protein']}% | Fat: {row['total_fat']}% | Sugar: {row['sugar']}% | Sodium: {row['sodium']}% | Carbs: {row['carbohydrates']}%")
            st.markdown("---")

        total_nutrition = self.selected_meals_df[['calories', 'protein', 'total_fat', 'sugar', 'sodium', 'carbohydrates']].sum()
        st.subheader("📊Total Nutrition Summary")
        st.dataframe(total_nutrition.to_frame().T)
        cols_to_drop = ['Unnamed:0','id','contributor_id','submitted','tags']
        return self.selected_meals_df.drop(columns=[col for col in cols_to_drop if col in self.selected_meals_df.columns]),total_nutrition
