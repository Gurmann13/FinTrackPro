import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.data_utils import save_expense, load_expenses_data, delete_expense


def show_expense_tracker():
    st.header("💳 Expense Tracker")
    st.markdown("Track your daily expenses and manage your spending.")

    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User session not found. Please log in again.")
        return

    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["➕ Add Expense", "📋 View Expenses", "🗑️ Manage Expenses"])

    with tab1:
        add_expense_form(user_id)

    with tab2:
        view_expenses(user_id)

    with tab3:
        manage_expenses(user_id)


def add_expense_form(user_id):
    st.subheader("Add New Expense")

    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            expense_date = st.date_input(
                "Date:",
                value=date.today(),
                max_value=date.today()
            )

            amount = st.number_input(
                "Amount ($):",
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )

        with col2:
            category = st.selectbox(
                "Category:",
                [
                    "Food & Dining",
                    "Transportation",
                    "Shopping",
                    "Entertainment",
                    "Bills & Utilities",
                    "Healthcare",
                    "Travel",
                    "Education",
                    "Groceries",
                    "Other"
                ]
            )

            payment_method = st.selectbox(
                "Payment Method:",
                ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Digital Wallet"]
            )

        description = st.text_input(
            "Description:",
            placeholder="Enter expense description..."
        )

        notes = st.text_area(
            "Notes (Optional):",
            placeholder="Additional notes about this expense...",
            height=100
        )

        submitted = st.form_submit_button("💾 Add Expense", type="primary", use_container_width=True)

        if submitted:
            if amount <= 0:
                st.error("❌ Amount must be greater than 0")
            elif not description.strip():
                st.error("❌ Description is required")
            else:
                try:
                    expense_data = {
                        'user_id': user_id,
                        'date': expense_date.strftime('%Y-%m-%d'),
                        'amount': amount,
                        'category': category,
                        'description': description.strip(),
                        'payment_method': payment_method,
                        'notes': notes.strip(),
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if save_expense(expense_data):
                        st.success("✅ Expense added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save expense. Please try again.")

                except Exception as e:
                    st.error(f"❌ Error adding expense: {str(e)}")


def view_expenses(user_id):
    st.subheader("Your Expenses")

    # Load expenses
    expenses_df = load_expenses_data(user_id)

    if expenses_df.empty:
        st.info("📝 No expenses recorded yet. Add your first expense using the 'Add Expense' tab!")
        return

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        # Date range filter
        date_filter = st.selectbox(
            "Filter by period:",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year"]
        )

    with col2:
        # Category filter
        categories = ["All Categories"] + sorted(expenses_df['category'].unique().tolist())
        category_filter = st.selectbox("Filter by category:", categories)

    with col3:
        # Sort options
        sort_by = st.selectbox(
            "Sort by:",
            ["Date (Newest)", "Date (Oldest)", "Amount (High to Low)", "Amount (Low to High)"]
        )

    # Apply filters
    filtered_df = expenses_df.copy()

    # Date filter
    if date_filter != "All Time":
        today = datetime.now().date()
        if date_filter == "Last 7 Days":
            cutoff_date = today - pd.Timedelta(days=7)
        elif date_filter == "Last 30 Days":
            cutoff_date = today - pd.Timedelta(days=30)
        elif date_filter == "Last 90 Days":
            cutoff_date = today - pd.Timedelta(days=90)
        elif date_filter == "This Year":
            cutoff_date = date(today.year, 1, 1)

        filtered_df = filtered_df[filtered_df['date'] >= cutoff_date.strftime('%Y-%m-%d')]

    # Category filter
    if category_filter != "All Categories":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]

    # Sort
    if sort_by == "Date (Newest)":
        filtered_df = filtered_df.sort_values('date', ascending=False)
    elif sort_by == "Date (Oldest)":
        filtered_df = filtered_df.sort_values('date', ascending=True)
    elif sort_by == "Amount (High to Low)":
        filtered_df = filtered_df.sort_values('amount', ascending=False)
    elif sort_by == "Amount (Low to High)":
        filtered_df = filtered_df.sort_values('amount', ascending=True)

    # Summary statistics
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Expenses", f"${filtered_df['amount'].sum():,.2f}")
        with col2:
            st.metric("Number of Transactions", len(filtered_df))
        with col3:
            st.metric("Average Amount", f"${filtered_df['amount'].mean():,.2f}")
        with col4:
            st.metric("Largest Expense", f"${filtered_df['amount'].max():,.2f}")

        st.divider()

        # Display expenses table
        display_df = filtered_df.copy()
        display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")

        # Select columns to display
        columns_to_show = ['date', 'description', 'category', 'amount', 'payment_method']

        st.dataframe(
            display_df[columns_to_show],
            use_container_width=True,
            hide_index=True,
            column_config={
                'date': 'Date',
                'description': 'Description',
                'category': 'Category',
                'amount': 'Amount',
                'payment_method': 'Payment Method'
            }
        )

    else:
        st.info("No expenses found matching your filters.")


def manage_expenses(user_id):
    st.subheader("Manage Expenses")

    # Load expenses
    expenses_df = load_expenses_data(user_id)

    if expenses_df.empty:
        st.info("📝 No expenses to manage yet.")
        return

    # Search and select expense to manage
    search_term = st.text_input("🔍 Search expenses:", placeholder="Search by description or category...")

    # Filter expenses based on search
    if search_term:
        mask = (
                expenses_df['description'].str.contains(search_term, case=False, na=False) |
                expenses_df['category'].str.contains(search_term, case=False, na=False)
        )
        filtered_expenses = expenses_df[mask]
    else:
        filtered_expenses = expenses_df.head(50)  # Show only recent 50 for performance

    if not filtered_expenses.empty:
        # Create a selection dataframe
        selection_df = filtered_expenses.copy()
        selection_df['Display'] = selection_df.apply(
            lambda row: f"{row['date']} - {row['description']} - ${row['amount']:.2f} ({row['category']})",
            axis=1
        )

        selected_expense = st.selectbox(
            "Select an expense to manage:",
            options=selection_df.index,
            format_func=lambda x: selection_df.loc[x, 'Display']
        )

        if selected_expense is not None:
            expense = expenses_df.loc[selected_expense]

            # Display expense details
            st.subheader("Expense Details")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {expense['date']}")
                st.write(f"**Amount:** ${expense['amount']:.2f}")
                st.write(f"**Category:** {expense['category']}")
                st.write(f"**Payment Method:** {expense['payment_method']}")

            with col2:
                st.write(f"**Description:** {expense['description']}")
                if expense.get('notes'):
                    st.write(f"**Notes:** {expense['notes']}")
                st.write(f"**Created:** {expense.get('created_at', 'N/A')}")

            # Action buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✏️ Edit Expense", use_container_width=True):
                    st.info("📝 Edit functionality will be available in future updates.")

            with col2:
                if st.button("📋 Duplicate", use_container_width=True):
                    # Prepare duplicate data
                    duplicate_data = {
                        'user_id': user_id,
                        'date': datetime.now().date().strftime('%Y-%m-%d'),
                        'amount': expense['amount'],
                        'category': expense['category'],
                        'description': f"Copy of {expense['description']}",
                        'payment_method': expense['payment_method'],
                        'notes': expense.get('notes', ''),
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if save_expense(duplicate_data):
                        st.success("✅ Expense duplicated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to duplicate expense.")

            with col3:
                if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                    st.warning("⚠️ Are you sure you want to delete this expense?")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❌ Yes, Delete", key="confirm_delete"):
                            if delete_expense(selected_expense, user_id):
                                st.success("✅ Expense deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete expense.")

                    with col2:
                        if st.button("↩️ Cancel", key="cancel_delete"):
                            st.rerun()

    else:
        st.info("No expenses found matching your search criteria.")

    # Bulk operations
    st.divider()
    st.subheader("📊 Expense Summary")

    # Category summary
    if not expenses_df.empty:
        category_summary = expenses_df.groupby('category')['amount'].agg(['count', 'sum']).round(2)
        category_summary.columns = ['Count', 'Total Amount']
        category_summary['Average'] = (category_summary['Total Amount'] / category_summary['Count']).round(2)

        st.dataframe(category_summary, use_container_width=True)
