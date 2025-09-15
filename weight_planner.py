import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class WeightPlanner:
    def __init__(self, present_weight_kg, target_weight_kg, age, height_cm, gender, activity_level="moderate", weekly_loss_lbs=1.0):
        self.present_weight_kg = present_weight_kg
        self.target_weight_kg = target_weight_kg
        self.age = age
        self.height_cm = height_cm
        self.gender = gender.lower()
        self.activity_level = activity_level.lower()
        self.weekly_loss_lbs = weekly_loss_lbs
        self.weekly_change_kg = weekly_loss_lbs * 0.453592
        self.direction = "loss" if target_weight_kg < present_weight_kg else "gain"
        self.activity_factors = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "very": 1.725,
            "super": 1.9
        }
##Mifflin:https://www.leighpeele.com/mifflin-st-jeor-calculator
    def calculate_bmr(self, weight_kg):
        if self.gender == "male":
            return 10 * weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            return 10 * weight_kg + 6.25 * self.height_cm - 5 * self.age - 161

    def simulate(self):
        activity_factor = self.activity_factors.get(self.activity_level, 1.55)
        target_bmr = self.calculate_bmr(self.target_weight_kg)
        maintenance_calories = round(target_bmr * activity_factor)

        weekly_kcal_change = self.weekly_change_kg * 7700
        daily_kcal_adjustment = weekly_kcal_change / 7

        if self.direction == "loss":
            target_daily_calories = maintenance_calories - daily_kcal_adjustment
        else:
            target_daily_calories = maintenance_calories + daily_kcal_adjustment

        weight = self.present_weight_kg
        weekly_data = [{"Week": 0, "Estimated Weight (kg)": round(weight, 2)}]
        week = 1

        while (self.direction == "loss" and weight > self.target_weight_kg) or \
              (self.direction == "gain" and weight < self.target_weight_kg):
            weight -= self.weekly_change_kg if self.direction == "loss" else -self.weekly_change_kg
            weight = max(weight, self.target_weight_kg) if self.direction == "loss" else min(weight, self.target_weight_kg)
            weekly_data.append({"Week": week, "Estimated Weight (kg)": round(weight, 2)})
            week += 1

        return pd.DataFrame(weekly_data), round(target_daily_calories), round(maintenance_calories)

    def generate_summary(self):
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

        return prompt,summary
