#!/usr/bin/env python3
"""
Debug script to test registration functionality
"""
import pandas as pd
import os
import sys
import traceback
from datetime import datetime

# Add the current directory to Python path
sys.path.append('.')

def test_registration():
    """Test registration with debug output"""
    try:
        from utils.auth_utils import register_user, hash_password
        from pages.auth import validate_registration_data
        
        print("=== Registration Debug Test ===")
        
        # Check current users
        users_file = 'data/users.csv'
        if os.path.exists(users_file):
            existing_users = pd.read_csv(users_file)
            print(f"Current users count: {len(existing_users)}")
            print("Existing usernames:", existing_users['username'].tolist())
            print("Existing emails:", existing_users['email'].tolist())
        else:
            print("No users file found")
            
        # Test with completely new user data
        test_username = f"NewUser{datetime.now().strftime('%H%M%S')}"
        test_email = f"newuser{datetime.now().strftime('%H%M%S')}@test.com"
        
        print(f"\nTesting registration with:")
        print(f"Username: {test_username}")
        print(f"Email: {test_email}")
        
        # Test validation first
        validation_errors = validate_registration_data(
            test_username, test_email, "TestPass123", "TestPass123", True
        )
        
        if validation_errors:
            print("Validation errors found:")
            for error in validation_errors:
                print(f"  - {error}")
            return False
        else:
            print("Validation passed!")
            
        # Test registration
        user_data = {
            'username': test_username,
            'email': test_email,
            'password': 'TestPass123',
            'full_name': 'Test User'
        }
        
        result = register_user(user_data)
        print(f"Registration result: {result}")
        
        if result:
            # Verify user was added
            updated_users = pd.read_csv(users_file)
            print(f"Users count after registration: {len(updated_users)}")
            return True
        else:
            print("Registration failed!")
            return False
            
    except Exception as e:
        print(f"Error during registration test: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_registration()