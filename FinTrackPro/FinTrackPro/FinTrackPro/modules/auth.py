import streamlit as st
import hashlib
import re
from utils.auth_utils import register_user, authenticate_user, hash_password

def show_auth_page():
    st.markdown("### 🔐 Authentication")
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_register_form()

def show_login_form():
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input(
            "Username:",
            placeholder="Enter your username",
            max_chars=50
        )
        
        password = st.text_input(
            "Password:",
            type="password",
            placeholder="Enter your password"
        )
        
        remember_me = st.checkbox("Remember me")
        
        submitted = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
        
        if submitted:
            if not username.strip() or not password:
                st.error("❌ Please enter both username and password.")
            else:
                try:
                    user_data = authenticate_user(username.strip(), password)
                    
                    if user_data:
                        # Set session state
                        st.session_state.authenticated = True
                        st.session_state.username = user_data['username']
                        st.session_state.user_id = user_data['user_id']
                        
                        st.success(f"✅ Welcome back, {user_data['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Login failed: {str(e)}")
    
    # Additional login options
    st.divider()
    st.markdown("**Demo Account:**")
    st.info("You can create a new account using the Register tab, or login with any existing credentials.")

def show_register_form():
    st.subheader("Create New Account")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "Username:",
                placeholder="Choose a unique username",
                max_chars=50,
                help="Username must be 3-50 characters long"
            )
            
            email = st.text_input(
                "Email:",
                placeholder="Enter your email address",
                help="We'll use this for account recovery"
            )
        
        with col2:
            password = st.text_input(
                "Password:",
                type="password",
                placeholder="Create a strong password",
                help="Password must be at least 8 characters long"
            )
            
            confirm_password = st.text_input(
                "Confirm Password:",
                type="password",
                placeholder="Re-enter your password"
            )
        
        full_name = st.text_input(
            "Full Name (Optional):",
            placeholder="Enter your full name",
            max_chars=100
        )
        
        # Terms and conditions
        terms_accepted = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            help="You must accept the terms to create an account"
        )
        
        submitted = st.form_submit_button("📝 Create Account", type="primary", use_container_width=True)
        
        if submitted:
            # Clear any previous registration errors
            if 'registration_error' in st.session_state:
                st.session_state.registration_error = None
            
            # Validation
            validation_errors = validate_registration_data(
                username, email, password, confirm_password, terms_accepted
            )
            
            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    # Safely handle None values from form fields
                    safe_username = str(username).strip() if username is not None else ''
                    safe_email = str(email).strip().lower() if email is not None else ''
                    safe_full_name = str(full_name).strip() if full_name is not None else ''
                    
                    user_data = {
                        'username': safe_username,
                        'email': safe_email,
                        'password': str(password) if password is not None else '',
                        'full_name': safe_full_name if safe_full_name else None
                    }
                    
                    if register_user(user_data):
                        st.success("✅ Account created successfully! You can now login.")
                        st.balloons()
                        
                        # Clear form by rerunning
                        st.rerun()
                    else:
                        # Show specific error message if available
                        error_msg = st.session_state.get('registration_error', 'Username or email already exists')
                        st.error(f"❌ {error_msg}")
                        
                except Exception as e:
                    import traceback
                    st.error(f"❌ Registration failed: {str(e)}")
                    st.error(f"Full traceback: {traceback.format_exc()}")
    
    # Registration tips
    st.divider()
    st.subheader("🛡️ Security Tips")
    
    tips = [
        "🔒 Use a strong password with at least 8 characters",
        "📧 Use a valid email address for account recovery",
        "👤 Choose a unique username that you'll remember",
        "🔐 Don't share your login credentials with anyone",
        "💾 Your financial data is stored securely and privately"
    ]
    
    for tip in tips:
        st.markdown(f"- {tip}")

def validate_registration_data(username, email, password, confirm_password, terms_accepted):
    """Validate registration form data"""
    errors = []
    
    # Safely handle None values
    safe_username = username.strip() if username else ''
    safe_email = email.strip() if email else ''
    
    # Username validation
    if not safe_username:
        errors.append("Username is required")
    elif len(safe_username) < 3:
        errors.append("Username must be at least 3 characters long")
    elif len(safe_username) > 50:
        errors.append("Username must be less than 50 characters")
    elif not re.match("^[a-zA-Z0-9_-]+$", safe_username):
        errors.append("Username can only contain letters, numbers, hyphens, and underscores")
    
    # Email validation
    if not safe_email:
        errors.append("Email is required")
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', safe_email):
        errors.append("Please enter a valid email address")
    
    # Password validation
    if not password:
        errors.append("Password is required")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif not re.search(r'[A-Za-z]', password):
        errors.append("Password must contain at least one letter")
    elif not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    # Confirm password validation
    if password != confirm_password:
        errors.append("Passwords do not match")
    
    # Terms acceptance validation
    if not terms_accepted:
        errors.append("You must accept the Terms of Service and Privacy Policy")
    
    return errors
