import streamlit as st
import sqlite3
import pandas as pd

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "securepassword"

# Function to fetch data from the database
def fetch_data(query, db_path="user_data.db"):
    try:
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Admin login function
def admin_login():
    st.title("PredictMe Admin Login")

    # Input fields for username and password
    username = st.text_input("Username", placeholder="Enter your admin username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")

    # Check credentials
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.success("Login successful! Redirecting to the Control Panel...")
            st.session_state["page"] = "control_panel"
        else:
            st.error("Invalid username or password. Please try again.")

# Admin control panel
def control_panel():
    st.title("PredictMe Admin Control Panel")
    
    # User insights
    st.header("User Insights")
    
    # Query to count total users
    query_total_users = "SELECT COUNT(*) as users FROM users;"
    result_total_users = fetch_data(query_total_users)
    if result_total_users is not None:
        total_users = result_total_users["users"].iloc[0]
        st.subheader(f"Total Users: {total_users}")
    
    # Show user details
    st.subheader("User Details")
    query_user_details = "SELECT * FROM users;"
    user_details = fetch_data(query_user_details)
    if user_details is not None:
        st.dataframe(user_details)
    
    # Additional insights
    st.header("Additional Insights")
    # Query for insights like gender distribution
    query_gender_distribution = """
        SELECT gender, COUNT(*) as count
        FROM users
        GROUP BY gender;
    """
    gender_distribution = fetch_data(query_gender_distribution)
    if gender_distribution is not None:
        st.subheader("Gender Distribution")
        st.bar_chart(gender_distribution.set_index("gender"))

# Function to clean the users table based on a condition
def clean_users_table(condition):
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        query = f"DELETE FROM users WHERE {condition}"
        cursor.execute(query)
        conn.commit()
        st.success(f"Successfully deleted rows where {condition}.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        conn.close()

    # Query for date-wise activity
#    query_date_activity = """
#        SELECT DATE(creation_date) as date, COUNT(*) as user_count
#        FROM users
#        GROUP BY DATE(creation_date);
#    """
#    date_activity = fetch_data(query_date_activity)
#    if date_activity is not None:
#        st.subheader("Date-wise User Activity")
#        st.line_chart(date_activity.set_index("date"))

# Main function for the control panel app
def main():
    # Use session state for navigation
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    # Navigate based on the current session state
    if st.session_state["page"] == "control_panel":
        control_panel()
        # Admin Control Section
        st.header("Admin Control")
        st.subheader("Clean Users Table")

        # Text input for the condition
        condition = st.text_input(
            "Enter the SQL condition to clean the users table (e.g., gender = 'NA'):",
            placeholder="gender = 'NA'",
        )

        # Trigger the function on button click
        if st.button("Clean Table"):
            if condition:
                clean_users_table(condition)
            else:
                st.warning("Please provide a valid condition.")
    else:
        admin_login()

# Run the app
if __name__ == "__main__":
    main()
