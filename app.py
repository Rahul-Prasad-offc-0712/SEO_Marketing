import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql 
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Database Connection
from sqlalchemy import create_engine
from urllib.parse import quote_plus

def get_db_connection():
    try:
        # Encode special characters in password
        password = quote_plus("Seo@123")
        
        # Cloud SQL Database details
        user = "seo_user"
        host = "34.139.108.200"  # Replace with your Cloud SQL Public IP
        port = 3306  # MySQL default port
        database = "seo"

        # Create SQLAlchemy engine
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

        # Establish connection
        connection = engine.connect()
        print("✅ Connected to Cloud SQL MySQL successfully!")
        return connection

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None


# Fetch Table Names
def get_table_names():
    engine = get_db_connection()
    if engine is None:
        return []
    try:
        query = "SHOW TABLES"
        tables = pd.read_sql(query, engine)
        return tables.iloc[:, 0].tolist()
    except Exception as e:
        st.error(f"Error fetching table names: {e}")
        return []

# Fetch Data from Table
def fetch_data_from_db(table_name):
    engine = get_db_connection()
    if engine is None:
        return None
    try:
        query = f"SELECT * FROM `{table_name}`"  # Use backticks for table names
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Upload and Store Data in Database
def upload_data(file, table_name):
    if file is not None:
        try:
            df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
            df.columns = [col.strip().replace(" ", "_").replace("/", "_") for col in df.columns]
            engine = get_db_connection()
            if engine is not None:
                df.to_sql(table_name, engine, if_exists='append', index=False)
                st.success(f"Data uploaded successfully to {table_name}")
        except Exception as e:
            st.error(f"Error uploading data: {e}")

# Streamlit UI
st.title("📊 SEO Data Dashboard")

# Dropdown to select a table
tables = get_table_names()
selected_table = st.selectbox("Select a Table", tables)

if selected_table:
    df = fetch_data_from_db(selected_table)
    if df is not None:
        st.write("### 🗃️ Data Preview")
        st.dataframe(df.head())

        # Visualization Section
        st.write("## 📈 Data Visualization")
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        if numeric_cols:
            # 📊 **Bar Chart**
            st.write("### 📊 Bar Chart")
            bar_x = st.selectbox("Select X-axis (Categorical Column)", categorical_cols, key="bar_x")
            bar_y = st.selectbox("Select Y-axis (Numeric Column)", numeric_cols, key="bar_y")

            if bar_x and bar_y:
                fig, ax = plt.subplots(figsize=(14, 6))  
                sns.barplot(x=df[bar_x], y=df[bar_y], ax=ax)

                # Improve x-axis label visibility
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
                step = max(1, len(df[bar_x].unique()) // 10)  
                ax.set_xticks(range(0, len(df[bar_x]), step))
                ax.set_xticklabels(df[bar_x][::step], rotation=45, ha="right")

                plt.xlabel(bar_x, fontsize=12)
                plt.ylabel(bar_y, fontsize=12)
                plt.tight_layout()
                st.pyplot(fig)

            # 📈 **Line Chart**
            st.write("### 📈 Line Chart")
            line_x = st.selectbox("Select X-axis (Time or Numeric Column)", numeric_cols, key="line_x")
            line_y = st.selectbox("Select Y-axis (Numeric Column)", numeric_cols, key="line_y")

            if line_x and line_y:
                fig, ax = plt.subplots(figsize=(14, 6))
                sampled_df = df.iloc[::max(1, len(df) // 100)]  # Downsample for readability
                sns.lineplot(x=sampled_df[line_x], y=sampled_df[line_y], ax=ax)

                plt.xlabel(line_x, fontsize=12)
                plt.ylabel(line_y, fontsize=12)
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig)

            # 🥧 **Pie Chart**
            st.write("### 🥧 Pie Chart")
            pie_col = st.selectbox("Select Column for Pie Chart", categorical_cols, key="pie_col")

            if pie_col:
                pie_data = df[pie_col].value_counts().nlargest(10)
                fig, ax = plt.subplots()
                ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("pastel"))
                ax.axis("equal")
                st.pyplot(fig)

            # 📊 **Histogram**
            st.write("### 📊 Histogram")
            hist_col = st.selectbox("Select Column for Distribution", numeric_cols, key="hist_col")

            if hist_col:
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.histplot(df[hist_col], bins=min(50, len(df[hist_col].unique())), kde=True, ax=ax)
                plt.xlabel(hist_col, fontsize=12)
                plt.tight_layout()
                st.pyplot(fig)

            # 🔥 **Correlation Heatmap**
            st.write("### 🔥 Correlation Heatmap")
            fig, ax = plt.subplots(figsize=(10, 6))
            correlation_matrix = df[numeric_cols].corr()
            sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
            plt.xticks(rotation=45, ha="right")
            plt.yticks(rotation=0)
            plt.title("Correlation Heatmap", fontsize=14)
            plt.tight_layout()
            st.pyplot(fig)

        else:
            st.warning("⚠️ No numeric columns available for visualization.")

# File Upload Section
st.write("### 📤 Upload Data to Database")
file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
if file and selected_table:
    if st.button("Upload Data"):
        upload_data(file, selected_table)
