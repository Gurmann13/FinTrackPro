import streamlit as st
import pandas as pd
import os
from datetime import datetime

def initialize_data_files():
    """Initialize CSV data files if they don't exist"""
    # Create data directory
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialize users.csv
    users_file = 'data/users.csv'
    if not os.path.exists(users_file):
        users_df = pd.DataFrame(columns=[
            'user_id', 'username', 'email', 'password_hash', 'full_name',
            'created_at', 'last_login', 'is_active'
        ])
        users_df.to_csv(users_file, index=False)
    
    # Initialize expenses.csv
    expenses_file = 'data/expenses.csv'
    if not os.path.exists(expenses_file):
        expenses_df = pd.DataFrame(columns=[
            'expense_id', 'user_id', 'date', 'amount', 'category', 'description',
            'payment_method', 'notes', 'created_at'
        ])
        expenses_df.to_csv(expenses_file, index=False)
    
    # Initialize backlog.csv
    backlog_file = 'data/backlog.csv'
    if not os.path.exists(backlog_file):
        backlog_df = pd.DataFrame(columns=[
            'task_id', 'user_id', 'title', 'description', 'category', 'priority',
            'status', 'due_date', 'estimated_amount', 'notes', 'created_at', 'updated_at'
        ])
        backlog_df.to_csv(backlog_file, index=False)

def save_expense(expense_data):
    """Save expense data to CSV"""
    try:
        expenses_file = 'data/expenses.csv'
        
        # Load existing data
        if os.path.exists(expenses_file):
            expenses_df = pd.read_csv(expenses_file)
        else:
            expenses_df = pd.DataFrame()
        
        # Generate expense ID
        expense_id = len(expenses_df) + 1
        expense_data['expense_id'] = expense_id
        
        # Add to dataframe
        if expenses_df.empty:
            expenses_df = pd.DataFrame([expense_data])
        else:
            expenses_df = pd.concat([expenses_df, pd.DataFrame([expense_data])], ignore_index=True)
        
        # Save to CSV
        expenses_df.to_csv(expenses_file, index=False)
        return True
        
    except Exception as e:
        st.error(f"Error saving expense: {str(e)}")
        return False

def load_expenses_data(user_id):
    """Load expenses data for a specific user"""
    try:
        expenses_file = 'data/expenses.csv'
        
        if not os.path.exists(expenses_file):
            return pd.DataFrame()
        
        expenses_df = pd.read_csv(expenses_file)
        
        if expenses_df.empty:
            return pd.DataFrame()
        
        # Filter by user ID
        user_expenses = expenses_df[expenses_df['user_id'] == user_id].copy()
        
        # Sort by date (newest first)
        if not user_expenses.empty:
            user_expenses = user_expenses.sort_values('date', ascending=False)
        
        return user_expenses
        
    except Exception as e:
        st.error(f"Error loading expenses: {str(e)}")
        return pd.DataFrame()

def delete_expense(expense_index, user_id):
    """Delete an expense"""
    try:
        expenses_file = 'data/expenses.csv'
        
        if not os.path.exists(expenses_file):
            return False
        
        expenses_df = pd.read_csv(expenses_file)
        
        if expenses_df.empty:
            return False
        
        # Verify ownership
        if expense_index in expenses_df.index:
            expense = expenses_df.loc[expense_index]
            if expense['user_id'] == user_id:
                # Remove the expense
                expenses_df = expenses_df.drop(expense_index)
                expenses_df.to_csv(expenses_file, index=False)
                return True
        
        return False
        
    except Exception as e:
        st.error(f"Error deleting expense: {str(e)}")
        return False

def save_backlog_item(task_data):
    """Save backlog item to CSV"""
    try:
        backlog_file = 'data/backlog.csv'
        
        # Load existing data
        if os.path.exists(backlog_file):
            backlog_df = pd.read_csv(backlog_file)
        else:
            backlog_df = pd.DataFrame()
        
        # Generate task ID
        task_id = len(backlog_df) + 1
        task_data['task_id'] = task_id
        
        # Add to dataframe
        if backlog_df.empty:
            backlog_df = pd.DataFrame([task_data])
        else:
            backlog_df = pd.concat([backlog_df, pd.DataFrame([task_data])], ignore_index=True)
        
        # Save to CSV
        backlog_df.to_csv(backlog_file, index=False)
        return True
        
    except Exception as e:
        st.error(f"Error saving task: {str(e)}")
        return False

def load_backlog_data(user_id):
    """Load backlog data for a specific user"""
    try:
        backlog_file = 'data/backlog.csv'
        
        if not os.path.exists(backlog_file):
            return pd.DataFrame()
        
        backlog_df = pd.read_csv(backlog_file)
        
        if backlog_df.empty:
            return pd.DataFrame()
        
        # Filter by user ID
        user_tasks = backlog_df[backlog_df['user_id'] == user_id].copy()
        
        # Sort by created date (newest first)
        if not user_tasks.empty:
            user_tasks = user_tasks.sort_values('created_at', ascending=False)
        
        return user_tasks
        
    except Exception as e:
        st.error(f"Error loading tasks: {str(e)}")
        return pd.DataFrame()

def update_backlog_status(task_index, user_id, new_status):
    """Update backlog item status"""
    try:
        backlog_file = 'data/backlog.csv'
        
        if not os.path.exists(backlog_file):
            return False
        
        backlog_df = pd.read_csv(backlog_file)
        
        if backlog_df.empty:
            return False
        
        # Verify ownership and update
        if task_index in backlog_df.index:
            task = backlog_df.loc[task_index]
            if task['user_id'] == user_id:
                backlog_df.loc[task_index, 'status'] = new_status
                backlog_df.loc[task_index, 'updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                backlog_df.to_csv(backlog_file, index=False)
                return True
        
        return False
        
    except Exception as e:
        st.error(f"Error updating task status: {str(e)}")
        return False

def delete_backlog_item(task_index, user_id):
    """Delete a backlog item"""
    try:
        backlog_file = 'data/backlog.csv'
        
        if not os.path.exists(backlog_file):
            return False
        
        backlog_df = pd.read_csv(backlog_file)
        
        if backlog_df.empty:
            return False
        
        # Verify ownership
        if task_index in backlog_df.index:
            task = backlog_df.loc[task_index]
            if task['user_id'] == user_id:
                # Remove the task
                backlog_df = backlog_df.drop(task_index)
                backlog_df.to_csv(backlog_file, index=False)
                return True
        
        return False
        
    except Exception as e:
        st.error(f"Error deleting task: {str(e)}")
        return False

def get_user_summary(user_id):
    """Get summary statistics for a user"""
    try:
        expenses_df = load_expenses_data(user_id)
        tasks_df = load_backlog_data(user_id)
        
        summary = {
            'total_expenses': expenses_df['amount'].sum() if not expenses_df.empty else 0,
            'total_transactions': len(expenses_df),
            'total_tasks': len(tasks_df),
            'pending_tasks': len(tasks_df[tasks_df['status'] == 'Pending']) if not tasks_df.empty else 0,
            'completed_tasks': len(tasks_df[tasks_df['status'] == 'Completed']) if not tasks_df.empty else 0,
            'categories_used': expenses_df['category'].nunique() if not expenses_df.empty else 0
        }
        
        return summary
        
    except Exception as e:
        st.error(f"Error getting user summary: {str(e)}")
        return {}

def export_user_data(user_id, data_type='all'):
    """Export user data to CSV"""
    try:
        exported_files = []
        
        if data_type in ['all', 'expenses']:
            expenses_df = load_expenses_data(user_id)
            if not expenses_df.empty:
                filename = f'user_{user_id}_expenses_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                expenses_df.to_csv(filename, index=False)
                exported_files.append(filename)
        
        if data_type in ['all', 'tasks']:
            tasks_df = load_backlog_data(user_id)
            if not tasks_df.empty:
                filename = f'user_{user_id}_tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                tasks_df.to_csv(filename, index=False)
                exported_files.append(filename)
        
        return exported_files
        
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return []
