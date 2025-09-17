import streamlit as st
import os
from utils.auth_utils import check_authentication, initialize_session_state
from utils.data_utils import initialize_data_files

# Page configuration
st.set_page_config(
    page_title="Finance Manager Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data files and session state
initialize_data_files()
initialize_session_state()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #e2e3e5;
        border: 1px solid #d6d8db;
        margin: 1rem 0;
    }

</style>
""", unsafe_allow_html=True)

def main():
    # Check if user is authenticated
    if not check_authentication():
        st.markdown('<h1 class="main-header">🏦 Finance Manager Pro</h1>', unsafe_allow_html=True)
        
        # Show login/register page
        import modules.auth as auth_page
        auth_page.show_auth_page()
        return

    # Main application for authenticated users
    st.markdown('<h1 class="main-header">🏦 Finance Manager Pro</h1>', unsafe_allow_html=True)
    
    # Welcome message
    if 'username' in st.session_state:
        st.markdown(f"**Welcome back, {st.session_state.username}!** 👋")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        
        # User info
        if 'username' in st.session_state:
            st.info(f"Logged in as: **{st.session_state.username}**")
        
        # Navigation menu
        page = st.selectbox(
            "Select a page:",
            [
                "Dashboard",
                "Currency Converter", 
                "Finance Calculators",
                "Expense Tracker",
                "Charts & Analytics",
                "Task Backlog"
            ]
        )
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            for key in ['authenticated', 'username', 'user_id']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # Display selected page
    if page == "Dashboard":
        import modules.dashboard as dashboard
        dashboard.show_dashboard()
    elif page == "Currency Converter":
        import modules.currency_converter as currency
        currency.show_currency_converter()
    elif page == "Finance Calculators":
        import modules.calculators as calc
        calc.show_calculators()
    elif page == "Expense Tracker":
        import modules.expense_tracker as expense
        expense.show_expense_tracker()
    elif page == "Charts & Analytics":
        import modules.charts as charts
        charts.show_charts()
    elif page == "Task Backlog":
        import modules.backlog as backlog
        backlog.show_backlog()

if __name__ == "__main__":
    main()
