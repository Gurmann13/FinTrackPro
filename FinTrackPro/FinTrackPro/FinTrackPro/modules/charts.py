import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_utils import load_expenses_data

def show_charts():
    st.header("📊 Charts & Analytics")
    st.markdown("Visualize your spending patterns and financial trends.")
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User session not found. Please log in again.")
        return
    
    # Load expense data
    expenses_df = load_expenses_data(user_id)
    
    if expenses_df.empty:
        st.info("📝 No expense data available. Start by adding some expenses to see your analytics!")
        return
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🥧 Categories", "📅 Time Analysis", "💳 Payment Methods"])
    
    with tab1:
        show_trend_analysis(expenses_df)
    
    with tab2:
        show_category_analysis(expenses_df)
    
    with tab3:
        show_time_analysis(expenses_df)
    
    with tab4:
        show_payment_analysis(expenses_df)

def show_trend_analysis(expenses_df):
    st.subheader("📈 Spending Trends")
    
    # Time period selection
    period = st.selectbox(
        "Select time period:",
        ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year", "All Time"]
    )
    
    # Filter data based on period
    today = datetime.now().date()
    if period == "Last 30 Days":
        cutoff_date = today - timedelta(days=30)
    elif period == "Last 90 Days":
        cutoff_date = today - timedelta(days=90)
    elif period == "Last 6 Months":
        cutoff_date = today - timedelta(days=180)
    elif period == "Last Year":
        cutoff_date = today - timedelta(days=365)
    else:
        cutoff_date = None
    
    if cutoff_date:
        filtered_df = expenses_df[expenses_df['date'] >= cutoff_date.strftime('%Y-%m-%d')]
    else:
        filtered_df = expenses_df
    
    if filtered_df.empty:
        st.warning("No data available for the selected period.")
        return
    
    # Daily spending trend
    st.subheader("📅 Daily Spending Trend")
    daily_spending = filtered_df.groupby('date')['amount'].sum().reset_index()
    daily_spending['date'] = pd.to_datetime(daily_spending['date'])
    
    fig = px.line(
        daily_spending,
        x='date',
        y='amount',
        title='Daily Spending Over Time',
        labels={'amount': 'Amount ($)', 'date': 'Date'}
    )
    fig.update_traces(line_color='#1f77b4', line_width=3)
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Weekly and monthly averages
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Weekly Average")
        weekly_avg = daily_spending['amount'].mean() * 7
        st.metric("Weekly Average Spending", f"${weekly_avg:.2f}")
        
        # Weekly spending chart
        weekly_spending = filtered_df.copy()
        weekly_spending['date'] = pd.to_datetime(weekly_spending['date'])
        weekly_spending['week'] = weekly_spending['date'].dt.to_period('W')
        weekly_data = weekly_spending.groupby('week')['amount'].sum().reset_index()
        weekly_data['week'] = weekly_data['week'].astype(str)
        
        fig = px.bar(
            weekly_data,
            x='week',
            y='amount',
            title='Weekly Spending',
            labels={'amount': 'Amount ($)', 'week': 'Week'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Monthly Average")
        monthly_avg = daily_spending['amount'].mean() * 30
        st.metric("Monthly Average Spending", f"${monthly_avg:.2f}")
        
        # Monthly spending chart
        monthly_spending = filtered_df.copy()
        monthly_spending['date'] = pd.to_datetime(monthly_spending['date'])
        monthly_spending['month'] = monthly_spending['date'].dt.to_period('M')
        monthly_data = monthly_spending.groupby('month')['amount'].sum().reset_index()
        monthly_data['month'] = monthly_data['month'].astype(str)
        
        fig = px.bar(
            monthly_data,
            x='month',
            y='amount',
            title='Monthly Spending',
            labels={'amount': 'Amount ($)', 'month': 'Month'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Spending momentum
    st.subheader("⚡ Spending Momentum")
    
    if len(daily_spending) >= 7:
        # Calculate 7-day moving average
        daily_spending['moving_avg'] = daily_spending['amount'].rolling(window=7).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_spending['date'],
            y=daily_spending['amount'],
            mode='lines',
            name='Daily Spending',
            line=dict(color='lightblue', width=1),
            opacity=0.7
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_spending['date'],
            y=daily_spending['moving_avg'],
            mode='lines',
            name='7-Day Average',
            line=dict(color='red', width=3)
        ))
        
        fig.update_layout(
            title='Daily Spending with 7-Day Moving Average',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_category_analysis(expenses_df):
    st.subheader("🥧 Category Analysis")
    
    # Category spending pie chart
    category_totals = expenses_df.groupby('category')['amount'].sum().reset_index()
    category_totals = category_totals.sort_values('amount', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            category_totals,
            values='amount',
            names='category',
            title='Spending by Category'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category bar chart
        fig = px.bar(
            category_totals,
            x='amount',
            y='category',
            orientation='h',
            title='Category Spending (Horizontal)',
            labels={'amount': 'Amount ($)', 'category': 'Category'}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Category details table
    st.subheader("📋 Category Details")
    
    category_stats = expenses_df.groupby('category').agg({
        'amount': ['count', 'sum', 'mean', 'std']
    }).round(2)
    
    category_stats.columns = ['Transactions', 'Total ($)', 'Average ($)', 'Std Dev ($)']
    category_stats = category_stats.sort_values('Total ($)', ascending=False)
    
    st.dataframe(category_stats, use_container_width=True)
    
    # Category trends over time
    st.subheader("📈 Category Trends")
    
    selected_categories = st.multiselect(
        "Select categories to compare:",
        expenses_df['category'].unique(),
        default=category_totals.head(3)['category'].tolist()
    )
    
    if selected_categories:
        category_trends = expenses_df[expenses_df['category'].isin(selected_categories)]
        category_trends['date'] = pd.to_datetime(category_trends['date'])
        
        # Group by date and category
        daily_category = category_trends.groupby(['date', 'category'])['amount'].sum().reset_index()
        
        fig = px.line(
            daily_category,
            x='date',
            y='amount',
            color='category',
            title='Category Spending Trends Over Time',
            labels={'amount': 'Amount ($)', 'date': 'Date'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_time_analysis(expenses_df):
    st.subheader("📅 Time-based Analysis")
    
    # Convert date column to datetime
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    expenses_df['day_of_week'] = expenses_df['date'].dt.day_name()
    expenses_df['month'] = expenses_df['date'].dt.month_name()
    expenses_df['hour'] = pd.to_datetime(expenses_df.get('created_at', '12:00:00'), errors='coerce').dt.hour
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Day of week analysis
        st.subheader("📆 Spending by Day of Week")
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_spending = expenses_df.groupby('day_of_week')['amount'].sum().reindex(day_order).reset_index()
        
        fig = px.bar(
            dow_spending,
            x='day_of_week',
            y='amount',
            title='Total Spending by Day of Week',
            labels={'amount': 'Amount ($)', 'day_of_week': 'Day of Week'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly analysis
        st.subheader("📅 Spending by Month")
        
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_spending = expenses_df.groupby('month')['amount'].sum().reindex(month_order).fillna(0).reset_index()
        
        fig = px.bar(
            monthly_spending,
            x='month',
            y='amount',
            title='Total Spending by Month',
            labels={'amount': 'Amount ($)', 'month': 'Month'}
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap of spending patterns
    st.subheader("🔥 Spending Heatmap")
    
    # Create a pivot table for heatmap
    heatmap_data = expenses_df.groupby(['day_of_week', 'month'])['amount'].sum().unstack(fill_value=0)
    
    if not heatmap_data.empty:
        fig = px.imshow(
            heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            title='Spending Heatmap: Day of Week vs Month',
            labels={'color': 'Amount ($)'},
            color_continuous_scale='Blues'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Time-based statistics
    st.subheader("⏰ Time Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        most_expensive_day = dow_spending.loc[dow_spending['amount'].idxmax(), 'day_of_week']
        max_day_amount = dow_spending['amount'].max()
        st.metric("Most Expensive Day", most_expensive_day, f"${max_day_amount:.2f}")
    
    with col2:
        least_expensive_day = dow_spending.loc[dow_spending['amount'].idxmin(), 'day_of_week']
        min_day_amount = dow_spending['amount'].min()
        st.metric("Least Expensive Day", least_expensive_day, f"${min_day_amount:.2f}")
    
    with col3:
        total_transactions = len(expenses_df)
        st.metric("Total Transactions", total_transactions)

def show_payment_analysis(expenses_df):
    st.subheader("💳 Payment Method Analysis")
    
    # Payment method distribution
    payment_totals = expenses_df.groupby('payment_method')['amount'].sum().reset_index()
    payment_counts = expenses_df.groupby('payment_method').size().reset_index(name='count')
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            payment_totals,
            values='amount',
            names='payment_method',
            title='Spending by Payment Method ($)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(
            payment_counts,
            values='count',
            names='payment_method',
            title='Transaction Count by Payment Method'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Payment method details
    st.subheader("💳 Payment Method Details")
    
    payment_stats = expenses_df.groupby('payment_method').agg({
        'amount': ['count', 'sum', 'mean']
    }).round(2)
    
    payment_stats.columns = ['Transactions', 'Total ($)', 'Average ($)']
    payment_stats = payment_stats.sort_values('Total ($)', ascending=False)
    
    st.dataframe(payment_stats, use_container_width=True)
    
    # Payment method trends
    st.subheader("📊 Payment Method Trends")
    
    payment_trends = expenses_df.copy()
    payment_trends['date'] = pd.to_datetime(payment_trends['date'])
    
    # Group by date and payment method
    daily_payment = payment_trends.groupby(['date', 'payment_method'])['amount'].sum().reset_index()
    
    fig = px.line(
        daily_payment,
        x='date',
        y='amount',
        color='payment_method',
        title='Payment Method Usage Over Time',
        labels={'amount': 'Amount ($)', 'date': 'Date'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Payment insights
    st.subheader("💡 Payment Insights")
    
    if not payment_stats.empty:
        most_used_payment = payment_stats.index[0]
        most_used_amount = payment_stats.loc[most_used_payment, 'Total ($)']
        most_used_count = payment_stats.loc[most_used_payment, 'Transactions']
        
        highest_avg_payment = payment_stats['Average ($)'].idxmax()
        highest_avg_amount = payment_stats.loc[highest_avg_payment, 'Average ($)']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Most Used Payment Method",
                most_used_payment,
                f"${most_used_amount:.2f} total"
            )
        
        with col2:
            st.metric(
                "Highest Average Transaction",
                highest_avg_payment,
                f"${highest_avg_amount:.2f} avg"
            )
        
        with col3:
            st.metric(
                "Total Payment Methods",
                len(payment_stats),
                f"{most_used_count} transactions (top method)"
            )
