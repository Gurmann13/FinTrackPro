import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_utils import load_expenses_data, get_user_summary

def show_dashboard():
    st.header("📊 Financial Dashboard")
    
    # Get user data
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User session not found. Please log in again.")
        return
    
    # Load expense data
    expenses_df = load_expenses_data(user_id)
    
    # Quick stats in columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
    monthly_expenses = expenses_df[
        expenses_df['date'] >= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    ]['amount'].sum() if not expenses_df.empty else 0
    
    weekly_expenses = expenses_df[
        expenses_df['date'] >= (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    ]['amount'].sum() if not expenses_df.empty else 0
    
    avg_daily = monthly_expenses / 30 if monthly_expenses > 0 else 0
    
    with col1:
        st.metric(
            label="💰 Total Expenses",
            value=f"${total_expenses:,.2f}",
            delta=f"${weekly_expenses:.2f} this week"
        )
    
    with col2:
        st.metric(
            label="📅 Monthly Expenses", 
            value=f"${monthly_expenses:,.2f}",
            delta=f"${avg_daily:.2f}/day avg"
        )
    
    with col3:
        transactions_count = len(expenses_df) if not expenses_df.empty else 0
        st.metric(
            label="📝 Total Transactions",
            value=transactions_count,
            delta="All time"
        )
    
    with col4:
        categories_count = expenses_df['category'].nunique() if not expenses_df.empty else 0
        st.metric(
            label="🏷️ Categories Used",
            value=categories_count,
            delta="Active categories"
        )
    
    st.divider()
    
    # Charts section
    if not expenses_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Expense Trends (Last 30 Days)")
            
            # Filter last 30 days
            recent_expenses = expenses_df[
                expenses_df['date'] >= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            ].copy()
            
            if not recent_expenses.empty:
                # Group by date and sum amounts
                daily_expenses = recent_expenses.groupby('date')['amount'].sum().reset_index()
                daily_expenses['date'] = pd.to_datetime(daily_expenses['date'])
                
                fig = px.line(
                    daily_expenses, 
                    x='date', 
                    y='amount',
                    title="Daily Spending Trend",
                    labels={'amount': 'Amount ($)', 'date': 'Date'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expenses recorded in the last 30 days.")
        
        with col2:
            st.subheader("🥧 Spending by Category")
            
            # Category breakdown
            category_totals = expenses_df.groupby('category')['amount'].sum().reset_index()
            
            fig = px.pie(
                category_totals,
                values='amount',
                names='category',
                title="Expense Distribution by Category"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent transactions
        st.subheader("📋 Recent Transactions")
        recent_df = expenses_df.head(10).copy()
        recent_df['amount'] = recent_df['amount'].apply(lambda x: f"${x:.2f}")
        st.dataframe(
            recent_df[['date', 'description', 'category', 'amount']],
            use_container_width=True,
            hide_index=True
        )
        
    else:
        st.info("📝 No expense data found. Start by adding some transactions in the Expense Tracker!")
        
        # Call to action message
        st.info("💡 **Get Started:** Use the navigation menu in the sidebar to access different features like Expense Tracker, Currency Converter, and Calculators!")
    
    # Quick actions section
    st.divider()
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Add Expenses", "Track spending", help="Use Expense Tracker from sidebar")
    
    with col2:
        st.metric("📊 Analytics", "View trends", help="Use Charts & Analytics from sidebar")
    
    with col3:
        st.metric("🔢 Calculate", "EMI & Interest", help="Use Finance Calculators from sidebar")
    
    with col4:
        st.metric("💱 Convert", "Currency rates", help="Use Currency Converter from sidebar")
    
    # Financial tips section
    st.divider()
    st.subheader("💡 Financial Tips")
    
    tips = [
        "💰 Track every expense, no matter how small - it adds up!",
        "📈 Aim to save at least 20% of your income each month.",
        "🏦 Emergency fund should cover 3-6 months of expenses.",
        "📊 Review your spending patterns monthly to identify areas for improvement.",
        "🎯 Set specific financial goals and track your progress regularly."
    ]
    
    for tip in tips:
        st.markdown(f"- {tip}")
