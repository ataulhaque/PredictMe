import sqlite3

def admin_login(username, password):
    # Check admin credentials
    if username == "admin" and password == "admin_password":  # Replace with secure method
        print("Login successful!")
        return query_users_table()
    else:
        print("Invalid credentials.")
        return None

def query_users_table():
    # Connect to the database
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    # Query the users table
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    # Close the connection
    conn.close()
    
    return users

# Example usage
# admin_login("admin", "admin_password")
