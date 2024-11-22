import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Expense Tracker")

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sidhu@1416",
        database="project",
    )

# Function to execute SQL queries
def execute_query(query, params=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            if query.strip().lower().startswith("select"):
                return cursor.fetchall()
            connection.commit()
    finally:
        connection.close()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "role" not in st.session_state:
    st.session_state.role = "user"

# Helper function to navigate between states
def navigate_to(page):
    st.session_state["page"] = page

# Main Application
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    # Login Page
    st.title("Expense Tracker App")
    st.subheader("Login")
    email = st.text_input("Enter Your Email")
    password = st.text_input("Enter Your Password", type="password")
    if st.button("Login"):
        if not email or not password:
            st.error("Email and password are required!")
        else:
            query = "SELECT user_id, email, role FROM users WHERE email = %s AND password = %s"
            result = execute_query(query, (email, password))
            if result:
                user_id, user_email, role = result[0]
                st.session_state.logged_in = True
                st.session_state.user_email = user_email
                st.session_state.role = role
                st.success("Login successful!")
                navigate_to("tracker")
            else:
                st.error("Invalid email or password!")

    # Sign-Up Option
    st.markdown("Don't have an account? [Sign Up Here](#)", unsafe_allow_html=True)
    if st.button("Go to Sign Up"):
        navigate_to("signup")

elif st.session_state.page == "signup":
    # Sign-Up Page
    st.title("Sign Up")
    email = st.text_input("Enter Your Email")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Your Password", type="password")
    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not email or not password:
            st.error("All fields are required!")
        else:
            existing_user_query = "SELECT * FROM users WHERE email = %s"
            existing_user = execute_query(existing_user_query, (email,))
            if existing_user:
                st.error("Email already registered!")
            else:
                insert_query = "INSERT INTO users (email, password, role) VALUES (%s, %s, 'user')"
                execute_query(insert_query, (email, password))
                st.success("Account created successfully! Please log in.")
                navigate_to("login")

elif st.session_state.logged_in and st.session_state.page == "tracker":
    # Expense Tracker
    st.title(f"Welcome, {st.session_state.get('user_email', 'User')}!")
    st.sidebar.title("Navigation")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.role = "user"
        navigate_to("login")

    # Get the logged-in user's role
    role = st.session_state.role
    user_email = st.session_state.user_email

    # Sidebar menu for tracker
    tracker_menu = st.sidebar.selectbox("Tracker Menu", ["Users", "Expenses", "Budgets"])

    # Users Management
    if tracker_menu == "Users":
        st.header("Manage Users")
        if role == "admin":
            users = execute_query("SELECT user_id, email, role FROM users")
            user_df = pd.DataFrame(users, columns=["User ID", "Email", "Role"])
            st.dataframe(user_df)

            # Add a New User
            st.subheader("Add New User")
            new_email = st.text_input("New User Email")
            new_password = st.text_input("New User Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            if st.button("Add User"):
                execute_query("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", 
                              (new_email, new_password, new_role))
                st.success("User added successfully!")

            # Update a User
            user_to_edit = st.selectbox("Select User to Edit", [u[0] for u in users])
            if user_to_edit:
                selected_user = next(u for u in users if u[0] == user_to_edit)
                updated_email = st.text_input("Updated Email", value=selected_user[1])
                updated_role = st.selectbox("Updated Role", ["user", "admin"], index=["user", "admin"].index(selected_user[2]))
                if st.button("Update User"):
                    execute_query(
                        "UPDATE users SET email = %s, role = %s WHERE user_id = %s",
                        (updated_email, updated_role, user_to_edit)
                    )
                    st.success("User updated successfully!")

            # Delete a User
            user_to_delete = st.selectbox("Select User to Delete", [u[0] for u in users])
            if st.button("Delete User"):
                execute_query("DELETE FROM users WHERE user_id = %s", (user_to_delete,))
                st.success("User deleted successfully!")

        else:
            # Regular users: View their own account
            user_info = execute_query("SELECT user_id, email, role FROM users WHERE email = %s", (user_email,))
            user_df = pd.DataFrame(user_info, columns=["User ID", "Email", "Role"])
            st.dataframe(user_df)

    # Expenses Management
    elif tracker_menu == "Expenses":
        st.header("Manage Expenses")
        if role == "admin":
            expenses = execute_query("SELECT expense_id, user_id, amount, category, date, description FROM expenses")
        else:
            user_id_result = execute_query("SELECT user_id FROM users WHERE email = %s", (user_email,))
            user_id = user_id_result[0][0]
            expenses = execute_query("SELECT expense_id, user_id, amount, category, date, description FROM expenses WHERE user_id = %s", (user_id,))
        
        expense_df = pd.DataFrame(expenses, columns=["Expense ID", "User ID", "Amount", "Category", "Date", "Description"])
        st.dataframe(expense_df)

        # Add a New Expense
        st.subheader("Add New Expense")
        expense_amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        expense_category = st.text_input("Category")
        expense_date = st.date_input("Date")
        expense_description = st.text_area("Description")
        if st.button("Add Expense"):
            execute_query(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (%s, %s, %s, %s, %s)",
                (user_id, expense_amount, expense_category, expense_date, expense_description)
            )
            st.success("Expense added successfully!")

        # Update an Expense
        expense_to_edit = st.selectbox("Select Expense to Edit", [e[0] for e in expenses])
        if expense_to_edit:
            selected_expense = next(e for e in expenses if e[0] == expense_to_edit)
            
            # Handle invalid dates gracefully
            try:
                updated_date = datetime.strptime(selected_expense[3], '%Y-%m-%d').date() if isinstance(selected_expense[3], str) else selected_expense[3]
            except ValueError:
                updated_date = st.date_input("Updated Date")

            updated_amount = st.number_input("Updated Amount", value=float(selected_expense[2]), format="%.2f")
            updated_category = st.text_input("Updated Category", value=selected_expense[2])
            updated_description = st.text_area("Updated Description", value=selected_expense[4])
            if st.button("Update Expense"):
                execute_query(
                    "UPDATE expenses SET amount = %s, category = %s, date = %s, description = %s WHERE expense_id = %s",
                    (updated_amount, updated_category, updated_date, updated_description, expense_to_edit)
                )
                st.success("Expense updated successfully!")

        # Delete an Expense
        expense_to_delete = st.selectbox("Select Expense to Delete", [e[0] for e in expenses])
        if st.button("Delete Expense"):
            execute_query("DELETE FROM expenses WHERE expense_id = %s", (expense_to_delete,))
            st.success("Expense deleted successfully!")

    # Budgets Management
    elif tracker_menu == "Budgets":
        st.header("Manage Budgets")
        if role == "admin":
            budgets = execute_query("SELECT budget_id, user_id, budget_amount, period, start_date, end_date FROM budgets")
        else:
            user_id_result = execute_query("SELECT user_id FROM users WHERE email = %s", (user_email,))
            user_id = user_id_result[0][0]
            budgets = execute_query("SELECT budget_id, user_id, budget_amount, period, start_date, end_date FROM budgets WHERE user_id = %s", (user_id,))
        
        budget_df = pd.DataFrame(budgets, columns=["Budget ID", "User ID", "Amount", "Period", "Start Date", "End Date"])
        st.dataframe(budget_df)

        # Add a New Budget
        st.subheader("Add New Budget")
        budget_amount = st.number_input("Budget Amount", min_value=0.0, format="%.2f")
        budget_period = st.selectbox("Period", ["weekly", "monthly"])
        budget_start_date = st.date_input("Start Date")
        budget_end_date = st.date_input("End Date")
        if st.button("Add Budget"):
            execute_query(
                "INSERT INTO budgets (user_id, budget_amount, period, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
                (user_id, budget_amount, budget_period, budget_start_date, budget_end_date)
            )
            st.success("Budget added successfully!")

        # Update a Budget
        budget_to_edit = st.selectbox("Select Budget to Edit", [b[0] for b in budgets])
        if budget_to_edit:
            selected_budget = next(b for b in budgets if b[0] == budget_to_edit)
            updated_amount = st.number_input("Updated Budget Amount", value=float(selected_budget[2]), format="%.2f")
            updated_period = st.selectbox("Updated Period", ["weekly", "monthly"], index=["weekly", "monthly"].index(selected_budget[3]))
            updated_start_date = st.date_input(
                "Updated Start Date",
                value=datetime.strptime(selected_budget[4], '%Y-%m-%d').date() if isinstance(selected_budget[4], str) else selected_budget[4]
            )
            updated_end_date = st.date_input(
                "Updated End Date",
                value=datetime.strptime(selected_budget[5], '%Y-%m-%d').date() if isinstance(selected_budget[5], str) else selected_budget[5]
            )
            if st.button("Update Budget"):
                execute_query(
                    "UPDATE budgets SET budget_amount = %s, period = %s, start_date = %s, end_date = %s WHERE budget_id = %s",
                    (updated_amount, updated_period, updated_start_date, updated_end_date, budget_to_edit)
                )
                st.success("Budget updated successfully!")

        # Delete a Budget
        budget_to_delete = st.selectbox("Select Budget to Delete", [b[0] for b in budgets])
        if st.button("Delete Budget"):
            execute_query("DELETE FROM budgets WHERE budget_id = %s", (budget_to_delete,))
            st.success("Budget deleted successfully!")
