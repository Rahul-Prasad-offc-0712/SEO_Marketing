import mysql.connector

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="host.docker.internal",
            user="seo_user",  # Change this if using a different user
            password="Seo@123",  # Replace with your actual password
            database="seo"
        )
        if conn.is_connected():
            print("✅ Connected to MySQL database")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")  # <-- This will print any error
        return None

# Run the function
connect_db()
