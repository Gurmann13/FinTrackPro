import streamlit as st
import pandas as pd
import hashlib
import os
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def register_user(user_data):
    """Register a new user"""
    try:
        users_file = 'data/users.csv'
        
        # Check if user already exists
        if os.path.exists(users_file):
            existing_users = pd.read_csv(users_file)
            
            # Check for duplicate username or email (case-insensitive)
            if not existing_users.empty:
                # Convert to lowercase for comparison
                existing_usernames = existing_users['username'].str.lower().values
                existing_emails = existing_users['email'].str.lower().values
                
                if user_data['username'].lower() in existing_usernames:
                    st.session_state.registration_error = "Username already exists"
                    return False
                if user_data['email'].lower() in existing_emails:
                    st.session_state.registration_error = "Email already exists"
                    return False
        else:
            existing_users = pd.DataFrame()
        
        # Generate user ID - use max + 1 for better ID generation
        if not existing_users.empty and 'user_id' in existing_users.columns:
            user_id = existing_users['user_id'].max() + 1
        else:
            user_id = 1
        
        # Prepare user record
        new_user = {
            'user_id': user_id,
            'username': user_data['username'].strip(),
            'email': user_data['email'].strip().lower(),
            'password_hash': hash_password(user_data['password']),
            'full_name': user_data.get('full_name', '').strip(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_login': None,
            'is_active': True
        }
        
        # Add to dataframe
        if existing_users.empty:
            users_df = pd.DataFrame([new_user])
        else:
            users_df = pd.concat([existing_users, pd.DataFrame([new_user])], ignore_index=True)
        
        # Save to CSV
        users_df.to_csv(users_file, index=False)
        st.session_state.registration_error = None
        return True
        
    except Exception as e:
        error_msg = f"Registration error: {str(e)}"
        st.session_state.registration_error = error_msg
        st.error(error_msg)
        return False

def authenticate_user(username, password):
    """Authenticate user login"""
    try:
        users_file = 'data/users.csv'
        
        if not os.path.exists(users_file):
            return None
        
        users_df = pd.read_csv(users_file)
        
        if users_df.empty:
            return None
        
        # Find user by username
        user_match = users_df[users_df['username'] == username]
        
        if user_match.empty:
            return None
        
        user = user_match.iloc[0]
        
        # Check password
        password_hash = hash_password(password)
        
        if user['password_hash'] == password_hash:
            # Update last login
            users_df.loc[users_df['username'] == username, 'last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            users_df.to_csv(users_file, index=False)
            
            return {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user.get('full_name', ''),
                'last_login': user.get('last_login')
            }
        
        return None
        
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return None

def get_user_data(user_id):
    """Get user data by user ID"""
    try:
        users_file = 'data/users.csv'
        
        if not os.path.exists(users_file):
            return None
        
        users_df = pd.read_csv(users_file)
        
        if users_df.empty:
            return None
        
        user_match = users_df[users_df['user_id'] == user_id]
        
        if user_match.empty:
            return None
        
        user = user_match.iloc[0]
        
        return {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user.get('full_name', ''),
            'created_at': user.get('created_at'),
            'last_login': user.get('last_login')
        }
        
    except Exception as e:
        st.error(f"Error getting user data: {str(e)}")
        return None

def update_user_profile(user_id, profile_data):
    """Update user profile data"""
    try:
        users_file = 'data/users.csv'
        
        if not os.path.exists(users_file):
            return False
        
        users_df = pd.read_csv(users_file)
        
        if users_df.empty:
            return False
        
        # Update user data
        user_index = users_df[users_df['user_id'] == user_id].index
        
        if len(user_index) == 0:
            return False
        
        for key, value in profile_data.items():
            if key in users_df.columns:
                users_df.loc[user_index[0], key] = value
        
        # Save updated data
        users_df.to_csv(users_file, index=False)
        return True
        
    except Exception as e:
        st.error(f"Error updating profile: {str(e)}")
        return False

def change_password(user_id, old_password, new_password):
    """Change user password"""
    try:
        users_file = 'data/users.csv'
        
        if not os.path.exists(users_file):
            return False
        
        users_df = pd.read_csv(users_file)
        
        if users_df.empty:
            return False
        
        # Find user
        user_match = users_df[users_df['user_id'] == user_id]
        
        if user_match.empty:
            return False
        
        user = user_match.iloc[0]
        
        # Verify old password
        old_password_hash = hash_password(old_password)
        
        if user['password_hash'] != old_password_hash:
            return False
        
        # Update password
        new_password_hash = hash_password(new_password)
        users_df.loc[users_df['user_id'] == user_id, 'password_hash'] = new_password_hash
        
        # Save updated data
        users_df.to_csv(users_file, index=False)
        return True
        
    except Exception as e:
        st.error(f"Error changing password: {str(e)}")
        return False
