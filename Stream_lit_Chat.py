
import streamlit as st
import pandas as pd
from weight_planner import WeightPlanner
from meal_planner import MealPlanner
from gpt_weight_nutrition_planner import GPTWeightNutritionPlanner
from GPTCustomPrompt import GPTCustomPromptPlanner

# Authentication imports
from app.auth_pages import check_authentication, render_user_sidebar, update_credits_in_session
from app.onboarding import render_welcome_page, check_onboarding_status
from app.user_store import get_user_credits

st.set_page_config(page_title="AI Weight & Meal Planner", layout="wide")

# --- AUTHENTICATION CHECK (MUST BE FIRST) ---
check_authentication()

# --- ONBOARDING CHECK (FOR NEW USERS) ---
if check_onboarding_status():
    render_welcome_page()
    st.stop()  # Don't show main app until onboarding is complete

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

# --- User Account Sidebar ---
render_user_sidebar()

st.sidebar.image(
    "images/CHi6.gif",
)

# Add Help/Instructions button
if st.sidebar.button("📖 View Instructions"):
    st.session_state.page = "Instructions"
    st.rerun()

if st.sidebar.button("🔁Reset Everything"):
    # Preserve authentication
    auth_data = {
        'authenticated': st.session_state.get('authenticated', False),
        'user_id': st.session_state.get('user_id'),
        'email': st.session_state.get('email'),
        'full_name': st.session_state.get('full_name'),
        'username': st.session_state.get('username'),
        'credits_remaining': st.session_state.get('credits_remaining'),
        'onboarding_completed': st.session_state.get('onboarding_completed')
    }
    
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Restore authentication
    for key, value in auth_data.items():
        if value is not None:
            st.session_state[key] = value
    
    st.session_state.page = "Main Planner"
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

csv_path = "Calories/Recipes.csv"
df = load_recipes_direct(csv_path)

# --- Main Planner Page ---
if st.session_state.page == "Main Planner":
    st.title("🏋️🏋️‍♂️ Personalized Weight & Meal Planner Assistant🏋️🏋️‍♂️")

    # Display important disclaimer
    st.warning("""
    ⚠️ **Medical Disclaimer:** This application is a prototype for educational purposes only and does not provide medical advice.
    Always consult qualified healthcare professionals before making dietary or exercise changes.
    """)

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
                    gpt_prompt, gpt_response, gpt_docs, _ = gpt_engine.generate(
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
        # Check credits before allowing chat access
        current_credits = st.session_state.get('credits_remaining', 0)
        
        if current_credits > 0:
            if st.button("💬 Proceed to GPT Chat"):
                st.session_state.page = "Custom Chat"
                st.rerun()
        else:
            st.error("⚠️ You need credits to access the AI Dietitian Chat. Please contact support to add more credits.")


elif st.session_state.page == "Custom Chat":
    st.title("🧑‍⚕️Custom Dietitian Bot")

    # Display important disclaimer
    st.info("""
    🔒 **Secure & Private:** Your conversations are stored securely using AWS infrastructure.
    Each question costs 1 credit from your balance.
    """)

    st.warning("""
    ⚠️ **Important:** This AI provides educational information only, not medical advice.
    Consult healthcare professionals for medical decisions.
    """)

    # Get authenticated user_id
    user_id = st.session_state.get('user_id', 'anonymous')
    
    if(gender=="male"):
      user_avatar_path = "images/Male.png"
    else:
      user_avatar_path = "images/Female.png"
    bot_avatar_path = "images/nutritionist_dietitian_occupation_profession_male_avatar_doctor-512.webp"

    calories = st.session_state.get('target_calories', 1800)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Check credits before allowing input
    current_credits = st.session_state.get('credits_remaining', 0)
    
    if current_credits > 0:
        user_custom_prompt = st.chat_input("Type your custom question...")
        if user_custom_prompt:
            try:
                gpt_custom = GPTCustomPromptPlanner()
                prompt_out, response_out, docs_out, metadata = gpt_custom.generate(
                    user_prompt=user_custom_prompt,
                    user_id=user_id,  # Use authenticated user_id
                    age=age,
                    gender=gender,
                    height_cm=height_cm,
                    present_weight=present_weight,
                    target_weight=target_weight,
                    calories=calories
                )
                
                # Update credits in session
                new_credits = metadata.get('credits_remaining', current_credits - 1)
                update_credits_in_session(new_credits)
                
                st.session_state.chat_history.append({
                    "user": user_custom_prompt,
                    "response": response_out,
                    "context": docs_out,
                    "prompt": prompt_out,
                    "metadata": metadata  # Include metadata (credits, latency, etc.)
                })
                
                st.rerun()  # Refresh to show updated credits

            except Exception as e:
                st.error(f"Custom GPT prompt failed: {e}")
    else:
        st.warning("⚠️ You have no credits remaining. Please contact support to add more credits.")

    # Display chat history with turn numbers
    for turn_idx, item in enumerate(st.session_state.chat_history, 1):
        # Turn header
        st.markdown(f"### 💬 Conversation Turn {turn_idx}")

        # User message
        with st.chat_message("user", avatar=user_avatar_path):
            st.markdown(f"**User:**\n\n{item['user']}")

        # Assistant response
        with st.chat_message("assistant", avatar=bot_avatar_path):
            st.markdown(f"**Assistant:**\n\n{item['response']}")

            # Display metadata if available
            if "metadata" in item and item["metadata"]:
                meta = item["metadata"]
                st.caption(
                    f"💳 Credits Remaining: **{meta.get('credits_remaining', 'N/A')}** | "
                    f"⏱️ Response Time: **{meta.get('latency_ms', 'N/A')} ms** | "
                    f"📄 Chunks: **{meta.get('chunks_retrieved', 'N/A')}**"
                )

            with st.expander("📄 Prompt Sent"):
                st.code(item["prompt"], language='text')
            with st.expander("📄 Context Source"):
                for i, doc in enumerate(item["context"], 1):
                    st.markdown(f"**Chunk {i}**")
                    st.markdown(doc, unsafe_allow_html=True)

        # Add divider between turns
        if turn_idx < len(st.session_state.chat_history):
            st.divider()

elif st.session_state.page == "Instructions":
    from app.onboarding import render_instructions_page
    render_instructions_page()

    if st.button("🔙 Back to Main App"):
        st.session_state.page = "Main Planner"
        st.rerun()
