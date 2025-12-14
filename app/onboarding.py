"""
User Onboarding Module
Provides welcome page and application instructions for first-time users.
"""
import streamlit as st
from app.user_store import update_user_profile, get_user_credits


def render_welcome_page():
    """
    Render welcome page for first-time users.
    Shows personalized greeting, initial credits, and app instructions.
    """
    full_name = st.session_state.get('full_name', 'User')
    username = st.session_state.get('username', 'user')
    credits = st.session_state.get('credits_remaining', 20)
    
    st.markdown("""
        <style>
        .welcome-container {
            text-align: center;
            padding: 2rem;
        }
        .welcome-title {
            font-size: 3rem;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .welcome-subtitle {
            font-size: 1.5rem;
            color: #666;
            margin-bottom: 2rem;
        }
        .feature-card {
            background: #f0f8ff;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .credit-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.5rem;
            font-weight: bold;
            display: inline-block;
            margin: 2rem 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
    
    # Welcome message
    st.markdown(f'<h1 class="welcome-title">Welcome, {full_name}! 🎉</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="welcome-subtitle">Username: <strong>{username}</strong></p>', unsafe_allow_html=True)
    
    # Credits badge
    st.markdown(f'<div class="credit-badge">💳 {credits} Free Credits</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Important Disclaimers
    st.warning("""
    ⚠️ **Important Disclaimer:**

    This application is a **prototype developed for educational and demonstration purposes only**.
    It is not intended to provide medical advice, diagnosis, or treatment. Always consult with
    qualified healthcare professionals before making any changes to your diet or exercise routine.
    """)

    st.info("""
    🔒 **Your Data is Secure:**

    This application uses **AWS (Amazon Web Services)** for secure data storage and email handling.
    Your personal information, email, and health data are protected using industry-standard
    security practices and encryption. We take your privacy seriously.
    """)

    st.success("""
    🎉 **Limited Free Access:**

    You are one of the **10 free users** who have early access to this application.
    Please use your **20 free AI consultation credits wisely** - each question to the AI Dietitian costs 1 credit.
    Make the most of your personalized nutrition guidance!
    """)

    st.markdown("---")

    # What are credits section
    st.subheader("💡 What are Credits?")
    st.info("""
    Credits are used each time you ask a question to our AI Dietitian.
    Each conversation with the AI costs **1 credit**. Your free credits allow you to explore
    the full power of personalized nutrition guidance!
    """)
    
    st.markdown("---")
    
    # Features overview
    st.subheader("🚀 What Can You Do Here?")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🏋️ Weight Planner")
        st.write("Get personalized weight loss/gain plans based on your goals, activity level, and preferences.")

    with col2:
        st.markdown("### 🍽️ Meal Planner")
        st.write("Generate daily meal plans tailored to your calorie targets and dietary preferences (veg, non-veg, vegan).")

    with col3:
        st.markdown("### 🧑‍⚕️ AI Dietitian Chat")
        st.write("Ask our AI expert any nutrition or fitness questions. Get evidence-based answers instantly!")
    
    st.markdown("---")
    
    # Quick start guide
    st.subheader("📋 How to Get Started")
    
    st.markdown("""
    ### Step 1: Fill in Your Profile
    - Enter your age, gender, height, current weight, and target weight
    - Choose your activity level (sedentary to super active)
    - Set your weekly weight goal (0.4 - 1.0 lbs per week)
    - Select your diet preference
    
    ### Step 2: Generate Your Plan
    - Click **Submit** to get your personalized weight forecast
    - View your target calories and maintenance calories
    - See your weekly weight projection chart
    
    ### Step 3: Get Your Meal Plan
    - Review your customized daily meal plan
    - See nutritional breakdowns for each meal
    - Get GPT-generated meal annotations
    
    ### Step 4: Chat with AI Dietitian
    - Click "💬 Proceed to GPT Chat" to unlock the AI chat
    - Ask questions like:
      - "What are good protein sources for muscle gain?"
      - "How can I reduce sugar cravings?"
      - "What's the best pre-workout meal?"
    - Each query uses 1 credit
    
    ### Step 5: Track Your Progress
    - Your conversation history is saved
    - Monitor your remaining credits in the sidebar
    - Come back anytime to continue your journey!
    """)
    
    st.markdown("---")
    
    # Tips section
    with st.expander("💡 Tips for Best Results"):
        st.markdown("""
        - **Be specific** in your AI questions for better answers
        - **Update your profile** as you progress towards your goals
        - **Save important meal plans** by taking screenshots
        - **Check your credits** before starting long conversations
        - **Ask follow-up questions** - the AI remembers your context!
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get started button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✨ Let's Get Started!", use_container_width=True, type="primary"):
            # Mark onboarding as complete
            user_id = st.session_state.get('user_id')
            if user_id:
                update_user_profile(user_id, onboarding_completed=True)
                st.session_state.onboarding_completed = True
            st.rerun()


def render_instructions_page():
    """
    Render comprehensive application instructions.
    Can be accessed anytime from the sidebar.
    """
    st.title("📖 Application Guide")
    
    st.markdown("""
    Welcome to your comprehensive guide for using the Weight Planner application!
    """)
    
    # Navigation tip
    st.info("💡 **Tip**: Bookmark this page! You can access it anytime from the sidebar.")
    
    st.markdown("---")
    
    # Detailed instructions
    tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Weight Planner", "🍽️ Meal Planner", "🧑‍⚕️ AI Dietitian", "💳 Credits"])
    
    with tab1:
        st.subheader("Weight Planner Guide")
        st.markdown("""
        The Weight Planner helps you create a science-based plan to reach your weight goals.
        
        #### Input Fields Explained:
        - **Age**: Your current age (affects metabolism calculations)
        - **Gender**: Male or female (impacts calorie needs)
        - **Height**: In centimeters (affects BMR calculation)
        - **Current Weight**: Your present weight in kilograms
        - **Target Weight**: Your goal weight in kilograms
        - **Activity Level**:
          - *Sedentary*: Little to no exercise
          - *Light*: Exercise 1-3 days/week
          - *Moderate*: Exercise 3-5 days/week
          - *Very*: Exercise 6-7 days/week
          - *Super*: Very intense daily exercise or physical job
        - **Weekly Difference**: How many pounds per week to lose/gain (0.4-1.0)
        
        #### Understanding Your Results:
        - **Weekly Weight Forecast**: Chart showing projected weight over time
        - **Target Daily Calories**: How many calories to eat daily to reach your goal
        - **Maintenance Calories**: Calories needed to maintain current weight
        - **Summary**: Personalized analysis and recommendations
        """)
    
    with tab2:
        st.subheader("Meal Planner Guide")
        st.markdown("""
        Get a complete daily meal plan that matches your calorie targets.
        
        #### How It Works:
        1. After generating your weight plan, the meal planner automatically creates a daily menu
        2. Meals are selected from a database of recipes to match your target calories
        3. Each meal shows:
           - Recipe name and description
           - Calories, protein, carbs, and fat
           - Meal category (breakfast, lunch, dinner, snack)
        
        #### Diet Preferences:
        - **Veg**: Vegetarian meals only
        - **Non-Veg**: Includes meat, fish, and vegetarian options
        - **Vegan**: Plant-based meals only
        
        #### Customization Tips:
        - You can regenerate plans by adjusting your preferences and resubmitting
        - Look for GPT annotations for cooking tips and substitutions
        - Note down favorite recipes for future reference
        """)
    
    with tab3:
        st.subheader("AI Dietitian Chat Guide")
        st.markdown("""
        Chat with our AI nutrition expert for personalized guidance!
        
        #### What You Can Ask:
        - Nutrition questions (protein sources, vitamins, supplements)
        - Meal timing and frequency
        - Exercise and diet coordination
        - Food substitutions and alternatives
        - Specific dietary needs (diabetes, allergies, etc.)
        - Weight loss/gain strategies
        - Hydration recommendations
        - Building healthy habits
        
        #### Sample Questions:
        ```
        • What are the best post-workout meals for muscle recovery?
        • How much water should I drink daily?
        • Can you suggest high-protein vegetarian snacks?
        • What foods help with better sleep?
        • How do I calculate my macro split?
        • What's the best breakfast for sustained energy?
        ```
        
        #### Chat Features:
        - **Context Awareness**: The AI remembers your profile and previous questions
        - **Source Documents**: See which research documents informed the answer
        - **Conversation History**: All your chats are saved for reference
        - **Metadata Display**: View credits used, response time, and sources retrieved
        """)
    
    with tab4:
        st.subheader("Credits System Guide")
        st.markdown("""
        Understanding how credits work:
        
        #### Credit Basics:
        - 💳 **Starting Credits**: Every new user gets **20 free credits**
        - 💰 **Cost Per Query**: Each AI Dietitian question costs **1 credit**
        - 📊 **Free Features**: Weight Planner and Meal Planner don't use credits
        
        #### Checking Your Balance:
        - Your current credits are always visible in the sidebar
        - After each AI query, you'll see updated balance
        - Color-coded indicators:
          - 🟢 Green: 10+ credits (healthy)
          - 🟡 Yellow: 5-9 credits (moderate)
          - 🔴 Red: 0-4 credits (low - plan accordingly!)
        
        #### When You Run Out:
        - You'll see a warning when credits reach 0
        - Chat functionality will be disabled
        - Weight and Meal planners remain fully accessible
        - Contact support to add more credits
        
        #### Credit Usage Tips:
        - Ask detailed questions to get comprehensive answers
        - Use follow-up questions to clarify (they remember context!)
        - Save important conversations by taking screenshots
        - Plan your questions to make the most of your credits
        """)
    
    st.markdown("---")
    
    # Troubleshooting
    with st.expander("🔧 Troubleshooting Common Issues"):
        st.markdown("""
        **Q: My meal plan doesn't match my target calories exactly**
        - A: The planner finds the closest match. Small variations (±50 cal) are normal.
        
        **Q: The AI gives generic answers**
        - A: Make sure your profile is filled out. The AI uses your data for personalization.
        
        **Q: I want to change my weight goal**
        - A: Update your profile in the sidebar and click Submit again.
        
        **Q: Can I export my data?**
        - A: Currently, take screenshots. Data export feature coming soon!
        
        **Q: How accurate are the weight projections?**
        - A: Based on scientific formulas, but actual results vary due to individual factors.
        """)
    
    # Contact support
    st.markdown("---")
    st.info("📧 **Need More Help?** Contact support at support@weightplanner.com")


def check_onboarding_status() -> bool:
    """
    Check if user needs to see onboarding.
    
    Returns:
        bool: True if onboarding should be shown
    """
    # New users who haven't completed onboarding
    if st.session_state.get('authenticated', False):
        return not st.session_state.get('onboarding_completed', False)
    return False
