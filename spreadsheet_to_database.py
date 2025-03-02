import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import mysql.connector

# MySQL Connection
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Rahul@123",
            database="seo_marketing"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"❌ Error: {err}")
        return None

# Mapping of file types to database tables
TABLE_MAP = {
    "leads": "leads",
    "traffic": "traffic_analysis",  # Updated name
    "seo_pages": "seo_pages",
    "seo_queries": "seo_queries",
}

# Data type conversion
def convert_data_types(df, table_name):
    type_map = {
        "traffic_analysis": {
            "items_viewed": int, "items_added_to_cart": int, "items_purchased": int,
            "item_revenue": int, "total_purchasers": int, "month_year": str, "sessions": str
        },
        "seo_pages": {
            "Clicks": int, "Impressions": int, "CTR": float, "Position": float, "Mon_Year": str, "Top_pages": str
        },
        "seo_queries": {
            "Top_pages": str, "Clicks": int, "Impressions": int, "CTR": float, "Position": float, "Mon_Year": str
        }
    }

    if table_name in type_map:
        for col, dtype in type_map[table_name].items():
            if col in df.columns:
                df[col] = df[col].astype(dtype, errors='ignore')

    return df

# Upload file and detect type
def upload_file():
    global df, table_name

    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")])
    if not file_path:
        return

    try:
        df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)

        # Detect which table to use based on file name
        for key in TABLE_MAP:
            if key in file_path.lower():
                table_name = TABLE_MAP[key]
                break
        else:
            messagebox.showerror("Error", "❌ Unknown file type! Please rename file correctly (e.g., leads.xlsx).")
            return

        # Convert Data Types
        df = convert_data_types(df, table_name)

        # Display Data in Table Preview
        tree.delete(*tree.get_children())
        tree["column"] = list(df.columns)
        tree["show"] = "headings"

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        messagebox.showinfo("Success", f"✅ {file_path} loaded as '{table_name}' table!")

    except Exception as e:
        messagebox.showerror("Error", f"❌ Error loading file: {e}")

# Insert data into MySQL
def insert_data():
    global df, table_name

    if df is None or df.empty:
        messagebox.showwarning("Warning", "⚠ No data to insert!")
        return

    conn = connect_db()
    if conn is None:
        return

    cursor = conn.cursor()

    # Get actual column names from MySQL database
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
    db_columns = [col[0].strip().lower().replace(" ", "_") for col in cursor.fetchall()]  # Normalize column names

    # **Normalize column names in DataFrame**
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Identify missing columns
    missing_columns = [col for col in db_columns if col not in df.columns]
    
    if missing_columns:
        messagebox.showwarning("Warning", f"⚠ Missing columns in Excel file: {missing_columns}\nThese columns will be skipped.")
    
    # **Only keep matching columns**
    common_columns = [col for col in db_columns if col in df.columns]
    df = df[common_columns]

    # **Handle NaN values**
    for col in df.columns:
        if df[col].dtype == 'float64' or df[col].dtype == 'int64':  # If column is numeric
            df[col].fillna(0, inplace=True)  # Replace NaN with 0
        else:
            df[col].fillna('', inplace=True)  # Replace NaN with empty string for text columns

    # **Construct SQL query**
    columns = ", ".join([f"`{col}`" for col in common_columns])
    placeholders = ", ".join(["%s"] * len(common_columns))
    insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

    try:
        for _, row in df.iterrows():
            cursor.execute(insert_query, tuple(row))

        conn.commit()
        messagebox.showinfo("Success", f"✅ Data inserted successfully into '{table_name}' table!")

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Insert Error", f"❌ Error inserting data: {e}")

    finally:
        cursor.close()
        conn.close()



# GUI Setup
root = tk.Tk()
root.title("Spreadsheet to MySQL")
root.geometry("700x500")

frame = tk.Frame(root)
frame.pack(pady=10)

upload_btn = tk.Button(frame, text="📂 Upload File", command=upload_file)
upload_btn.pack(side=tk.LEFT, padx=10)

insert_btn = tk.Button(frame, text="💾 Insert into MySQL", command=insert_data)
insert_btn.pack(side=tk.LEFT, padx=10)

# Table for previewing data
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10)

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
tree.pack()

tree_scroll.config(command=tree.yview)

df = None
table_name = None

root.mainloop()
