import mysql.connector

# Function to fetch data
def fetch_leads():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rahul@123",
        database="seo_marketing"
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM leads")
    results = cursor.fetchall()
    
    for row in results:
        print(row)
    
    cursor.close()
    conn.close()

# Example Usage
fetch_leads()
