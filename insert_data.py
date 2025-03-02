import mysql.connector

# Function to insert data
def insert_lead(name, email, phone):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rahul@123",
        database="seo_marketing"
    )
    cursor = conn.cursor()
    
    sql = "INSERT INTO leads (name, email, phone) VALUES (%s, %s, %s)"
    values = (name, email, phone)
    
    cursor.execute(sql, values)
    conn.commit()
    
    print(f"✅ Lead {name} added successfully")
    
    cursor.close()
    conn.close()

# Example Usage
insert_lead("John Doe", "john@example.com", "1234567890")
