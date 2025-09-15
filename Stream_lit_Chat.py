
import streamlit as st
import pandas as pd
from weight_planner import WeightPlanner
from meal_planner import MealPlanner
from gpt_weight_nutrition_planner import GPTWeightNutritionPlanner
from GPTCustomPrompt import GPTCustomPromptPlanner

st.set_page_config(page_title="AI Weight & Meal Planner", layout="wide")

# --- Navigation State ---
if "page" not in st.session_state:
    st.session_state.page = "Main Planner"

if st.session_state.page == "Main Planner":
    st.sidebar.title("Navigation")
    st.sidebar.markdown("*Custom Dietitian Bot will unlock after completing the planner.*")
else:
    st.sidebar.title("Navigation")
    if st.sidebar.button("🔙Back to Planner"):
        st.session_state.page = "Main Planner"


st.sidebar.image(
    "images/CHi6.gif",
)
if st.sidebar.button("🔁Reset Everything"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Shared Inputs Form ---
with st.sidebar.form("user_inputs"):
    st.header("User Profile")
    age = st.number_input("Age", 18, 100, 24)
    gender = st.selectbox("Gender", ["male", "female"])
    height_cm = st.number_input("Height (cm)", 120, 220, 176)
    present_weight = st.number_input("Current Weight (kg)", 40.0, 200.0, 85.0)
    target_weight = st.number_input("Target Weight (kg)", 40.0, 200.0, 75.0)
    activity = st.selectbox("Activity Level", ["sedentary", "light", "moderate", "very", "super"])
    weekly_loss = st.number_input("Weekly Difference (lbs)", min_value=0.4, max_value=1.0, value=0.5, step=0.1)
    diet=st.selectbox("Diet Preference", ["veg", "non_veg", "vegan"])
    submitted = st.form_submit_button("🥙Submit")
    

@st.cache_data(show_spinner=False)
def load_recipes_direct(path):
    return pd.read_csv(path)

csv_path = "Calories\Recipes.csv"
df = load_recipes_direct(csv_path)

# --- Main Planner Page ---
if st.session_state.page == "Main Planner":
    st.title("🏋️🏋️‍♂️ Personalized Weight & Meal Planner Assistant🏋️🏋️‍♂️")

    if submitted:
        
        st.session_state.chat_history = []

        wp = WeightPlanner(
            present_weight_kg=present_weight,
            target_weight_kg=target_weight,
            age=age,
            height_cm=height_cm,
            gender=gender,
            activity_level=activity,
            weekly_loss_lbs=weekly_loss
        )
        df_weights, target_calories, maintenance_calories = wp.simulate()
        prompt_summary, summary_text = wp.generate_summary()

        st.session_state['forecast_df'] = df_weights
        st.session_state['target_calories'] = target_calories
        st.session_state['maintenance_calories'] = maintenance_calories
        st.session_state['summary_prompt'] = prompt_summary
        st.session_state['summary_text'] = summary_text

        planner = MealPlanner(df, total_calories=target_calories, diet_type=diet)
        planner.prepare_data()
        planner.select_meals()
        st.session_state['meal_planner'] = planner
        st.session_state['gpt_annotated'] = False
        st.session_state['gpt_plan'] = None

    if "forecast_df" in st.session_state:
        st.subheader("📈Weekly Weight Forecast")
        st.line_chart(st.session_state['forecast_df'].set_index("Week"))

        if 'target_calories' in st.session_state:
            st.markdown(f"**🎯 Target Daily Calories:** `{st.session_state['target_calories']} kcal`")
        if 'maintenance_calories' in st.session_state:
            st.markdown(f"**🥙 Maintenance Calories:** `{st.session_state['maintenance_calories']} kcal`")

    if 'summary_prompt' in st.session_state and 'summary_text' in st.session_state:
        st.subheader("🧑‍⚕️Summary")
        st.markdown(st.session_state['summary_text'])
        with st.expander("Prompt Used"):
            st.code(st.session_state['summary_prompt'], language='text')

    if 'meal_planner' in st.session_state:
        st.subheader("🍽️🧑‍🍳 Daily Meal Plan")
        planner = st.session_state['meal_planner']
        if not st.session_state.get('gpt_annotated', False):
            planner.generate_gpt_annotations()
            st.session_state['gpt_annotated'] = True
        selected_df, nutrition = planner.display_plan()
        st.dataframe(selected_df)

    if st.button("(Exercise & Nutrition Plan)"):
        if 'target_calories' not in st.session_state:
            st.error("Please generate forecast first.")
        else:
            st.subheader("🧑‍⚕️(Exercise & Nutrition Plan)")
            if not st.session_state.get("gpt_plan"):
                try:
                    gpt_engine = GPTWeightNutritionPlanner()
                    gpt_prompt, gpt_response, gpt_docs = gpt_engine.generate(
                        age=age,
                        gender=gender,
                        height_cm=height_cm,
                        present_weight=present_weight,
                        target_weight=target_weight,
                        activity=activity,
                        calories=st.session_state['target_calories']
                    )
                    st.session_state['gpt_plan'] = {
                        "prompt": gpt_prompt,
                        "response": gpt_response,
                        "docs": gpt_docs
                    }
                except Exception as e:
                    st.error(f"GPT generation failed: {e}")

            plan = st.session_state.get('gpt_plan', {})
            if plan:
                with st.expander("Prompt Sent to GPT"):
                    st.code(plan["prompt"], language='text')

                st.subheader("Response")
                st.success(plan["response"])

                with st.expander("Retrieved Context Chunks"):
                    for i, doc in enumerate(plan["docs"], 1):
                        st.markdown(f"**Chunk {i}**")
                        st.markdown(doc, unsafe_allow_html=True)

    if 'meal_planner' in st.session_state and 'target_calories' in st.session_state:
        if st.button("💬 Proceed to GPT Chat"):
            st.session_state.page = "Custom Chat"
            st.rerun()


elif st.session_state.page == "Custom Chat":
    st.title("🧑‍⚕️Custom Dietitian Bot")

    
    if(gender=="male"):
      user_avatar_path = "images/Male.png"
    else:
      user_avatar_path = "images/Female.png"
    bot_avatar_path = "images/nutritionist_dietitian_occupation_profession_male_avatar_doctor-512.webp"

    calories = st.session_state.get('target_calories', 1800)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_custom_prompt = st.chat_input("Type your custom question...")
    if user_custom_prompt:
        try:
            gpt_custom = GPTCustomPromptPlanner()
            prompt_out, response_out, docs_out = gpt_custom.generate(
                user_prompt=user_custom_prompt,
                age=age,
                gender=gender,
                height_cm=height_cm,
                present_weight=present_weight,
                target_weight=target_weight,
                calories=calories
            )
            st.session_state.chat_history.append({
                "user": user_custom_prompt,
                "response": response_out,
                "context": docs_out,
                "prompt": prompt_out 
            })

        except Exception as e:
            st.error(f"Custom GPT prompt failed: {e}")

    for item in st.session_state.chat_history:
        with st.chat_message("user", avatar=user_avatar_path):
            st.markdown(item["user"])
        with st.chat_message("assistant", avatar=bot_avatar_path):
            st.markdown(item["response"])
            with st.expander("📄Prompt Sent"):
                st.code(item["prompt"], language='text')
            with st.expander("📄 Context Source"):
                for i, doc in enumerate(item["context"], 1):
                    st.markdown(f"**Chunk {i}**")
                    st.markdown(doc, unsafe_allow_html=True)
