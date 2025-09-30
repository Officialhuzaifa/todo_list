import streamlit as st
from cli import create_task, read_tasks, update_task, delete_task

# --- PATCH for st.rerun ---
if not hasattr(st, "rerun"):
    try:
        from streamlit.runtime.scriptrunner import RerunException, RerunData
        def rerun():
            raise RerunException(RerunData())
        st.rerun = rerun
    except Exception:
        pass

st.set_page_config(page_title="To-Do App", layout="wide")

# --- Global CSS (shadcn-inspired) ---
st.markdown("""
    <style>
    /* Card Style */
    .shadcn-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }
    .shadcn-card:hover {
        transform: scale(1.01);
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    }
    /* Buttons */
    div[data-testid="stButton"] > button {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stButton"] > button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
    }
    /* Add/Update = Green */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background-color: #16a34a !important;
        color: white !important;
    }
    /* Delete = Red */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #dc2626 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)


st.title("✅ To-Do List Application")

# --- Sidebar ---
menu = ["Dashboard", "View Tasks"]
choice = st.sidebar.radio("Navigation", menu)

# ---------------- Dashboard ---------------
if choice == "Dashboard":
    st.subheader("📊 Dashboard Overview")
    tasks = read_tasks()
    total_tasks = len(tasks) if tasks else 0
    completed_tasks = len([t for t in tasks if t['status'] == "completed"]) if tasks else 0
    pending_tasks = total_tasks - completed_tasks
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    import pandas as pd
    import numpy as np

    # --- Top KPI Cards with trend arrows ---
    col1, col2, col3 = st.columns(3)
    trend_completed = "↑" if completed_tasks >= (total_tasks - completed_tasks) else "↓"
    trend_pending = "↑" if pending_tasks > 0 else "↓"

    with col1:
        st.markdown(f"""
        <div class='shadcn-card'>
            <h3>📝 Total Tasks</h3>
            <p style="font-size:24px">{total_tasks}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='shadcn-card'>
            <h3>✅ Completed</h3>
            <p style="font-size:24px">{completed_tasks} <span style="color:green">{trend_completed}</span></p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='shadcn-card'>
            <h3>⏳ Pending</h3>
            <p style="font-size:24px">{pending_tasks} <span style="color:red">{trend_pending}</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Progress")
    st.progress(progress)
    st.markdown(f"**{progress}%** of tasks completed")
    
# ---------------- View Tasks ----------------
elif choice == "View Tasks":
    st.subheader("📋 View and Manage Your Tasks")

    # Add Task Button at top-right
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button(" Add Task", type="secondary"):
            st.session_state["show_add_task"] = not st.session_state.get("show_add_task", False)
            st.rerun()

    if st.session_state.get("show_add_task"):
        with st.container():
            st.markdown("<div class='shadcn-card'>", unsafe_allow_html=True)
            st.markdown("### ➕ Add New Task")
            new_title = st.text_input("Task Title", key="new_task_title")
            new_description = st.text_area("Task Description", key="new_task_desc")
            if st.button("✅ Save Task", key="add_btn", type="secondary"):
                if new_title and new_description:
                    create_task(new_title, new_description)
                    st.toast("✅ Task added successfully!")
                    st.session_state["show_add_task"] = False
                    st.rerun()
                else:
                    st.error("Please provide both title and description.")
            st.markdown("</div>", unsafe_allow_html=True)
        st.divider()

    # ✅ Show tasks ONLY in "View Tasks"
    tasks = read_tasks()
    if tasks:
        for task in tasks[::-1]:
            is_completed = task['status'] == "completed"

            # Card for task
            st.markdown("<div class='shadcn-card'>", unsafe_allow_html=True)

            # Checkbox
            completed_checkbox = st.checkbox("Mark Completed", value=is_completed, key=f"complete_{task['id']}")
            if completed_checkbox and not is_completed:
                update_task(task['id'], task['title'], task['description'], "completed")
                st.rerun()
            elif not completed_checkbox and is_completed:
                update_task(task['id'], task['title'], task['description'], "pending")
                st.rerun()

            # Title & description
            title_display = f"~~{task['title']}~~" if completed_checkbox else task['title']
            st.markdown(f"**📌 {title_display}**")
            if not completed_checkbox:
                st.markdown(f"**Description:** {task['description']}")

            # Action buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.popover("✏️ Update Task"):
                    upd_title = st.text_input("New Title", value=task['title'], key=f"upd_title_{task['id']}")
                    upd_description = st.text_area("New Description", value=task['description'], key=f"upd_desc_{task['id']}")
                    if st.button("💾 Save", key=f"upd_save_{task['id']}", type="secondary"):
                        if upd_title and upd_description:
                            update_task(task['id'], upd_title, upd_description, task['status'])
                            st.toast("✅ Task updated successfully!")
                            st.rerun()
                        else:
                            st.error("Please fill in all fields.")

            with col2:
                if st.button("🗑️ Delete", key=f"delete_btn_{task['id']}", type="primary"):
                    delete_task(task['id'])
                    st.toast("🗑️ Task deleted successfully!")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No tasks found.")
