import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.data_utils import save_backlog_item, load_backlog_data, update_backlog_status, delete_backlog_item

def show_backlog():
    st.header("📋 Financial Task Backlog")
    st.markdown("Keep track of your pending financial tasks and goals.")
    
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("User session not found. Please log in again.")
        return
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["➕ Add Task", "📋 View Tasks", "✅ Manage Tasks"])
    
    with tab1:
        add_task_form(user_id)
    
    with tab2:
        view_tasks(user_id)
    
    with tab3:
        manage_tasks(user_id)

def add_task_form(user_id):
    st.subheader("Add New Financial Task")
    
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Task Title:",
                placeholder="Enter task title..."
            )
            
            category = st.selectbox(
                "Category:",
                [
                    "Budget Planning",
                    "Investment",
                    "Tax Planning", 
                    "Insurance",
                    "Debt Management",
                    "Savings Goal",
                    "Bill Payment",
                    "Financial Review",
                    "Other"
                ]
            )
            
            priority = st.selectbox(
                "Priority:",
                ["Low", "Medium", "High", "Urgent"]
            )
        
        with col2:
            due_date = st.date_input(
                "Due Date:",
                value=None,
                min_value=date.today()
            )
            
            estimated_amount = st.number_input(
                "Estimated Amount ($) - Optional:",
                min_value=0.0,
                step=0.01,
                format="%.2f"
            )
            
            status = st.selectbox(
                "Status:",
                ["Pending", "In Progress", "Completed"],
                index=0
            )
        
        description = st.text_area(
            "Description:",
            placeholder="Describe the task in detail...",
            height=100
        )
        
        notes = st.text_area(
            "Notes (Optional):",
            placeholder="Additional notes or steps...",
            height=80
        )
        
        submitted = st.form_submit_button("📝 Add Task", type="primary", use_container_width=True)
        
        if submitted:
            if not title.strip():
                st.error("❌ Task title is required")
            elif not description.strip():
                st.error("❌ Task description is required")
            else:
                try:
                    task_data = {
                        'user_id': user_id,
                        'title': title.strip(),
                        'description': description.strip(),
                        'category': category,
                        'priority': priority,
                        'status': status,
                        'due_date': due_date.strftime('%Y-%m-%d') if due_date else None,
                        'estimated_amount': estimated_amount if estimated_amount > 0 else None,
                        'notes': notes.strip(),
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    if save_backlog_item(task_data):
                        st.success("✅ Task added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save task. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error adding task: {str(e)}")

def view_tasks(user_id):
    st.subheader("Your Financial Tasks")
    
    # Load tasks
    tasks_df = load_backlog_data(user_id)
    
    if tasks_df.empty:
        st.info("📝 No tasks in your backlog yet. Add your first financial task using the 'Add Task' tab!")
        return
    
    # Filter and sort options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by status:",
            ["All", "Pending", "In Progress", "Completed"]
        )
    
    with col2:
        category_filter = st.selectbox(
            "Filter by category:",
            ["All"] + sorted(tasks_df['category'].unique().tolist())
        )
    
    with col3:
        priority_filter = st.selectbox(
            "Filter by priority:",
            ["All", "Urgent", "High", "Medium", "Low"]
        )
    
    with col4:
        sort_by = st.selectbox(
            "Sort by:",
            ["Due Date", "Priority", "Created Date", "Title"]
        )
    
    # Apply filters
    filtered_df = tasks_df.copy()
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    
    # Apply sorting
    if sort_by == "Due Date":
        # Handle null due dates
        filtered_df['due_date_sort'] = pd.to_datetime(filtered_df['due_date'], errors='coerce')
        filtered_df = filtered_df.sort_values('due_date_sort', na_position='last')
    elif sort_by == "Priority":
        priority_order = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}
        filtered_df['priority_order'] = filtered_df['priority'].map(priority_order)
        filtered_df = filtered_df.sort_values('priority_order')
    elif sort_by == "Created Date":
        filtered_df = filtered_df.sort_values('created_at', ascending=False)
    elif sort_by == "Title":
        filtered_df = filtered_df.sort_values('title')
    
    # Task summary
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tasks = len(filtered_df)
            st.metric("Total Tasks", total_tasks)
        
        with col2:
            pending_tasks = len(filtered_df[filtered_df['status'] == 'Pending'])
            st.metric("Pending Tasks", pending_tasks)
        
        with col3:
            completed_tasks = len(filtered_df[filtered_df['status'] == 'Completed'])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            st.metric("Completed Tasks", completed_tasks, f"{completion_rate:.1f}%")
        
        with col4:
            total_amount = filtered_df['estimated_amount'].fillna(0).sum()
            st.metric("Total Estimated Amount", f"${total_amount:,.2f}")
        
        st.divider()
        
        # Display tasks
        for idx, task in filtered_df.iterrows():
            # Create task card
            with st.container():
                # Header with title and status
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Priority indicator
                    priority_emoji = {"Urgent": "🚨", "High": "🔴", "Medium": "🟡", "Low": "🟢"}
                    st.markdown(f"### {priority_emoji.get(task['priority'], '⚪')} {task['title']}")
                
                with col2:
                    status_color = {
                        "Pending": "🟠",
                        "In Progress": "🔵", 
                        "Completed": "✅"
                    }
                    st.markdown(f"**Status:** {status_color.get(task['status'], '⚪')} {task['status']}")
                
                with col3:
                    st.markdown(f"**Category:** {task['category']}")
                
                # Task details
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {task['description']}")
                    if pd.notna(task['notes']) and task['notes'].strip():
                        st.write(f"**Notes:** {task['notes']}")
                
                with col2:
                    if pd.notna(task['due_date']):
                        due_date = pd.to_datetime(task['due_date']).date()
                        days_left = (due_date - date.today()).days
                        
                        if days_left < 0:
                            st.write(f"**Due Date:** ⚠️ {task['due_date']} (Overdue)")
                        elif days_left == 0:
                            st.write(f"**Due Date:** 🔥 {task['due_date']} (Today!)")
                        elif days_left <= 7:
                            st.write(f"**Due Date:** ⏰ {task['due_date']} ({days_left} days)")
                        else:
                            st.write(f"**Due Date:** 📅 {task['due_date']} ({days_left} days)")
                    else:
                        st.write("**Due Date:** Not set")
                    
                    if pd.notna(task['estimated_amount']) and task['estimated_amount'] > 0:
                        st.write(f"**Estimated Amount:** ${task['estimated_amount']:,.2f}")
                    
                    st.write(f"**Priority:** {task['priority']}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"✏️ Edit", key=f"edit_{idx}", use_container_width=True):
                        st.info("📝 Edit functionality will be available in future updates.")
                
                with col2:
                    if task['status'] != 'Completed':
                        if st.button(f"✅ Complete", key=f"complete_{idx}", use_container_width=True):
                            if update_backlog_status(idx, user_id, 'Completed'):
                                st.success("✅ Task marked as completed!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update task status.")
                
                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{idx}", use_container_width=True):
                        if delete_backlog_item(idx, user_id):
                            st.success("✅ Task deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete task.")
                
                st.divider()
    
    else:
        st.info("No tasks found matching your filters.")

def manage_tasks(user_id):
    st.subheader("Task Management & Analytics")
    
    tasks_df = load_backlog_data(user_id)
    
    if tasks_df.empty:
        st.info("📝 No tasks to manage yet.")
        return
    
    # Task analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Task Status Distribution")
        status_counts = tasks_df['status'].value_counts()
        
        # Create a pie chart
        import plotly.express as px
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Task Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Tasks by Category")
        category_counts = tasks_df['category'].value_counts()
        
        fig = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            title="Tasks by Category",
            labels={'x': 'Number of Tasks', 'y': 'Category'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Priority analysis
    st.subheader("🎯 Priority Analysis")
    priority_counts = tasks_df['priority'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    
    colors = {"Urgent": "🚨", "High": "🔴", "Medium": "🟡", "Low": "🟢"}
    for i, (priority, count) in enumerate(priority_counts.items()):
        with [col1, col2, col3, col4][i % 4]:
            st.metric(f"{colors.get(priority, '⚪')} {priority}", count)
    
    # Overdue tasks
    st.subheader("⚠️ Overdue Tasks")
    
    today = date.today()
    overdue_tasks = tasks_df[
        (pd.notna(tasks_df['due_date'])) & 
        (pd.to_datetime(tasks_df['due_date']).dt.date < today) &
        (tasks_df['status'] != 'Completed')
    ]
    
    if not overdue_tasks.empty:
        st.warning(f"You have {len(overdue_tasks)} overdue tasks!")
        
        for idx, task in overdue_tasks.iterrows():
            due_date = pd.to_datetime(task['due_date']).date()
            days_overdue = (today - due_date).days
            
            st.markdown(f"""
            **{task['title']}** - {task['category']}  
            Due: {task['due_date']} ({days_overdue} days overdue)  
            Priority: {task['priority']} | Status: {task['status']}
            """)
    else:
        st.success("✅ No overdue tasks!")
    
    # Upcoming tasks
    st.subheader("📅 Upcoming Tasks (Next 7 Days)")
    
    next_week = today + pd.Timedelta(days=7)
    upcoming_tasks = tasks_df[
        (pd.notna(tasks_df['due_date'])) & 
        (pd.to_datetime(tasks_df['due_date']).dt.date >= today) &
        (pd.to_datetime(tasks_df['due_date']).dt.date <= next_week) &
        (tasks_df['status'] != 'Completed')
    ]
    
    if not upcoming_tasks.empty:
        st.info(f"You have {len(upcoming_tasks)} tasks due in the next 7 days.")
        
        for idx, task in upcoming_tasks.iterrows():
            due_date = pd.to_datetime(task['due_date']).date()
            days_left = (due_date - today).days
            
            if days_left == 0:
                urgency = "🔥 Due Today!"
            elif days_left == 1:
                urgency = "⏰ Due Tomorrow"
            else:
                urgency = f"📅 Due in {days_left} days"
            
            st.markdown(f"""
            **{task['title']}** - {task['category']}  
            {urgency} ({task['due_date']})  
            Priority: {task['priority']} | Status: {task['status']}
            """)
    else:
        st.info("📅 No tasks due in the next 7 days.")
    
    # Bulk actions
    st.divider()
    st.subheader("🔧 Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Mark All Pending as In Progress", use_container_width=True):
            pending_tasks = tasks_df[tasks_df['status'] == 'Pending']
            success_count = 0
            
            for idx in pending_tasks.index:
                if update_backlog_status(idx, user_id, 'In Progress'):
                    success_count += 1
            
            if success_count > 0:
                st.success(f"✅ Updated {success_count} tasks to 'In Progress'!")
                st.rerun()
            else:
                st.error("❌ No tasks were updated.")
    
    with col2:
        if st.button("🗑️ Delete All Completed", use_container_width=True):
            completed_tasks = tasks_df[tasks_df['status'] == 'Completed']
            
            if not completed_tasks.empty:
                st.warning(f"⚠️ This will delete {len(completed_tasks)} completed tasks. Are you sure?")
                
                if st.button("❌ Yes, Delete All Completed", key="confirm_bulk_delete"):
                    success_count = 0
                    
                    for idx in completed_tasks.index:
                        if delete_backlog_item(idx, user_id):
                            success_count += 1
                    
                    if success_count > 0:
                        st.success(f"✅ Deleted {success_count} completed tasks!")
                        st.rerun()
                    else:
                        st.error("❌ No tasks were deleted.")
            else:
                st.info("No completed tasks to delete.")
    
    with col3:
        # Export functionality placeholder
        if st.button("📄 Export Tasks", use_container_width=True):
            st.info("📤 Export functionality will be available in future updates.")
