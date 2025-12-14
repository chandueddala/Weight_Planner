"""
Streamlit Authentication Pages
Provides login, signup, and authentication management UI components.
"""
import streamlit as st
from app.cognito_auth import signup_user, login_user, logout_user


def render_login_page():
    """
    Render the login page with email and password fields.

    Returns:
        bool: True if login successful
    """
    st.markdown("""
        <style>
        .auth-container {
            max-width: 550px;
            margin: 0 auto;
            padding: 1.5rem;
        }
        .auth-title {
            text-align: center;
            color: #1f77b4;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .auth-subtitle {
            text-align: center;
            color: #e0e0e0;
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="auth-title">🏋️ Weight Planner</h1>', unsafe_allow_html=True)
    st.markdown('<p class="auth-subtitle">AI-Powered Nutrition & Fitness Assistant</p>', unsafe_allow_html=True)

    # Medical Disclaimer
    st.warning("""
    ⚠️ **Important Disclaimer**

    This application is a **prototype developed for educational and demonstration purposes only**.
    It is not intended to provide medical advice, diagnosis, or treatment. Always consult with qualified
    healthcare professionals before making any changes to your diet or exercise routine.
    """)

    # AWS Security Notice
    st.info("""
    🔒 **Your Data is Secure**

    This application uses **AWS (Amazon Web Services)** for secure data storage and email handling.
    Your information is protected using industry-standard security practices.
    """)

    # Login form
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="your.email@example.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Login", use_container_width=True)
        with col2:
            signup_btn = st.form_submit_button("Sign Up", use_container_width=True, type="secondary")
    
    # Handle login
    if submit:
        if not email or not password:
            st.error("Please enter both email and password")
            return False
        
        with st.spinner("Logging in..."):
            success, message, user_data = login_user(email, password)
        
        if success:
            # Set session state
            st.session_state.authenticated = True
            st.session_state.user_id = user_data['user_id']
            st.session_state.email = user_data['email']
            st.session_state.full_name = user_data['full_name']
            st.session_state.username = user_data['username']
            st.session_state.credits_remaining = user_data['credits_remaining']
            st.session_state.onboarding_completed = user_data.get('onboarding_completed', False)
            st.session_state.email_verified = user_data.get('email_verified', False)

            st.success(message)
            st.rerun()
            return True
        else:
            st.error(message)
            return False
    
    # Handle switch to signup
    if signup_btn:
        st.session_state.auth_page = "signup"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False


def render_signup_page():
    """
    Render the signup page with name, email, and password fields.

    Returns:
        bool: True if signup successful
    """
    st.markdown("""
        <style>
        .auth-container {
            max-width: 550px;
            margin: 0 auto;
            padding: 1.5rem;
        }
        .auth-title {
            text-align: center;
            color: #1f77b4;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .auth-subtitle {
            text-align: center;
            color: #e0e0e0;
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
        }
        .password-hint {
            font-size: 0.85rem;
            color: #888;
            margin-top: -0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="auth-title">🏋️ Weight Planner</h1>', unsafe_allow_html=True)
    st.markdown('<p class="auth-subtitle">Create Your Free Account</p>', unsafe_allow_html=True)

    # Medical Disclaimer
    st.warning("""
    ⚠️ **Important Disclaimer**

    This application is a **prototype developed for educational and demonstration purposes only**.
    It is not intended to provide medical advice, diagnosis, or treatment. Always consult with qualified
    healthcare professionals before making any changes to your diet or exercise routine.
    """)

    # Free Tier Notice
    st.success("""
    🎉 **Limited Free Access**

    We currently have **10 free user slots available**. Sign up now to claim your spot and receive
    **20 free AI consultation credits**. Use them wisely!
    """)

    # AWS Security Notice
    st.info("""
    🔒 **Your Data is Secure**

    This application uses **AWS (Amazon Web Services)** for secure data storage and email handling.
    Your information is protected using industry-standard security practices and encryption.
    """)

    # Signup form
    st.subheader("Sign Up")
    
    with st.form("signup_form"):
        full_name = st.text_input("👤 Full Name", placeholder="John Doe")
        email = st.text_input("📧 Email", placeholder="your.email@example.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")
        st.markdown('<p class="password-hint">Password must be at least 8 characters with uppercase, lowercase, and number</p>', unsafe_allow_html=True)
        password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password")
        
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Create Account", use_container_width=True)
        with col2:
            login_btn = st.form_submit_button("Back to Login", use_container_width=True, type="secondary")
    
    # Handle signup
    if submit:
        # Validation
        if not full_name or not email or not password or not password_confirm:
            st.error("Please fill in all fields")
            return False
        
        if not agree_terms:
            st.error("Please agree to the Terms of Service")
            return False
        
        if password != password_confirm:
            st.error("Passwords do not match")
            return False
        
        with st.spinner("Creating your account..."):
            success, message, user_data = signup_user(email, password, full_name)
        
        if success:
            st.success(message)

            # Automatically log in the user
            st.session_state.authenticated = True
            st.session_state.user_id = user_data['user_id']
            st.session_state.email = user_data['email']
            st.session_state.full_name = user_data['full_name']
            st.session_state.username = user_data['username']
            st.session_state.credits_remaining = user_data['credits_remaining']
            st.session_state.onboarding_completed = False
            st.session_state.email_verified = True

            st.balloons()

            import time
            time.sleep(2)
            st.rerun()
            return True
        else:
            st.error(message)
            return False
    
    # Handle switch to login
    if login_btn:
        st.session_state.auth_page = "login"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False


def check_authentication():
    """
    Check if user is authenticated. Redirect to login if not.
    Call this at the top of protected pages.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    # Initialize auth page state
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "login"
    
    # Check if authenticated
    if not st.session_state.get('authenticated', False):
        # Show login or signup page
        if st.session_state.auth_page == "signup":
            render_signup_page()
        else:
            render_login_page()
        
        st.stop()  # Stop execution of the rest of the app
        return False
    
    return True


def render_user_sidebar():
    """
    Render user information and credits in the sidebar.
    Call this after check_authentication() in the sidebar section.
    """
    if st.session_state.get('authenticated', False):
        st.sidebar.markdown("---")
        st.sidebar.subheader("👤 Your Account")
        
        # User info
        username = st.session_state.get('username', 'User')
        email = st.session_state.get('email', '')
        credits = st.session_state.get('credits_remaining', 0)
        
        st.sidebar.markdown(f"**{username}**")
        st.sidebar.caption(email)
        
        # Credits display with color coding
        if credits > 10:
            credit_color = "🟢"
        elif credits > 5:
            credit_color = "🟡"
        else:
            credit_color = "🔴"
        
        st.sidebar.markdown(f"### {credit_color} Credits: **{credits}**")
        
        if credits == 0:
            st.sidebar.error("⚠️ No credits remaining!")
            st.sidebar.info("Contact support to add more credits")
        elif credits < 5:
            st.sidebar.warning(f"Running low on credits!")
        
        # Logout button
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout_user(st.session_state)
            st.session_state.page = "Main Planner"  # Reset page
            st.rerun()


def update_credits_in_session(new_credits: int):
    """
    Update credits in session state.
    Call this after any operation that changes credits.
    
    Args:
        new_credits: New credit balance
    """
    if st.session_state.get('authenticated', False):
        st.session_state.credits_remaining = new_credits
