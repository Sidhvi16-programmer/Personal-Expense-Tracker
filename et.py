import streamlit as st
import mysql.connector
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Expense Tracker")

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
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

    if tracker_menu == "Users":
        st.header("Manage Accounts")
        
        if role == "admin":
            # Admin: Show all users
            st.subheader("All User Information")
            users = execute_query("SELECT user_id, email, role FROM users")
        else:
            # Regular user: Show only their own account info
            st.subheader("Your Account Information")
            users = execute_query("SELECT user_id, email, role FROM users WHERE email = %s", (user_email,))

        user_df = pd.DataFrame(users, columns=["User ID", "Email", "Role"])
        st.dataframe(user_df)

    elif tracker_menu == "Expenses":
        st.header("Manage Expenses")

        user_id_query = "SELECT user_id FROM users WHERE email = %s"
        user_id_result = execute_query(user_id_query, (user_email,))
        if not user_id_result:
            st.error("Unable to retrieve user information. Please log out and log in again.")
        else:
            user_id = user_id_result[0][0]

            # Add a new expense
            st.subheader("Add New Expense")
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            category = st.text_input("Category")
            date = st.date_input("Date")
            description = st.text_area("Description")
            if st.button("Add Expense"):
                if not amount or not category:
                    st.error("Amount and Category are required!")
                else:
                    execute_query(
                        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, amount, category, date, description),
                    )
                    st.success("Expense added successfully!")

            # Display the logged-in user's expenses
            st.subheader("Your Expense List")
            if role == "admin":
                expenses = execute_query("SELECT * FROM expenses")
            else:
                expenses = execute_query(
                    "SELECT expense_id,user_id, amount, category, date, description,created_at FROM expenses WHERE user_id = %s", 
                    (user_id,)
                )
            if expenses:
                expenses_df = pd.DataFrame(expenses, columns=["ID", "User ID","Amount", "Category", "Date", "Description","Created at"])
                st.dataframe(expenses_df)
            else:
                st.info("No expenses found.")

    elif tracker_menu == "Budgets":
        st.header("Manage Budgets")

        user_id_query = "SELECT user_id FROM users WHERE email = %s"
        user_id_result = execute_query(user_id_query, (user_email,))
        if not user_id_result:
            st.error("Unable to retrieve user information. Please log out and log in again.")
        else:
            user_id = user_id_result[0][0]

            # Add a new budget
            st.subheader("Add New Budget")
            budget_amount = st.number_input("Budget Amount", min_value=0.0, format="%.2f")
            period = st.selectbox("Period", ["weekly", "monthly"])
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            if st.button("Add Budget"):
                if not budget_amount or not period:
                    st.error("Budget Amount and Period are required!")
                else:
                    execute_query(
                        "INSERT INTO budgets (user_id, budget_amount, period, start_date, end_date) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, budget_amount, period, start_date, end_date),
                    )
                    st.success("Budget added successfully!")

            # Display the logged-in user's budgets
            st.subheader("Your Budget List")
            if role == "admin":
                budgets = execute_query("SELECT * FROM budgets")
            else:
                budgets = execute_query(
                    "SELECT budget_id,user_id, budget_amount, period, start_date, end_date FROM budgets WHERE user_id = %s", 
                    (user_id,)
                )
            if budgets:
                budgets_df = pd.DataFrame(budgets, columns=["ID","User ID", "Budget Amount", "Period", "Start Date", "End Date"])
                st.dataframe(budgets_df)
            else:
                st.info("No budgets found.")