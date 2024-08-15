import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Database connection parameters
credentials = {
    "database": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5432,
}

# Create the table in PostgreSQL
query = """
CREATE TABLE IF NOT EXISTS online_sales_data (
    transaction_id INT,
    date DATE,
    product_category TEXT,
    product_name TEXT,
    units_sold INT,
    unit_price FLOAT,
    total_revenue FLOAT,
    region TEXT,
    payment_method TEXT
);
"""


def create_table(credential, query):
    # Connect to the database and create the table
    conn = psycopg2.connect(**credential)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def rename_cols_and_write_dataset_to_table(credentials):
    # Load the CSV file into a DataFrame
    df = pd.read_csv("app/data/Online Sales Data.csv")

    # Rename Columns
    df.rename(
        columns={
            "Transaction ID": "transaction_id",
            "Date": "date",
            "Product Category": "product_category",
            "Product Name": "product_name",
            "Units Sold": "units_sold",
            "Unit Price": "unit_price",
            "Total Revenue": "total_revenue",
            "Region": "region",
            "Payment Method": "payment_method",
        },
        inplace=True,
    )

    # Adjust date data type
    df["date"] = pd.to_datetime(df["date"])

    # Create the database connection
    engine = create_engine(
        f"postgresql://{credentials['user']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/{credentials['database']}"
    )

    # Insert the DataFrame into the PostgreSQL table
    df.to_sql("online_sales_data", engine, if_exists="replace", index=False)


if __name__ == "__main__":
    create_table(credentials, query)
    rename_cols_and_write_dataset_to_table(credentials)
