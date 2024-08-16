import logging
import os

import pandas as pd
from sqlalchemy import create_engine, inspect, text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the database URL from environment variables
DATABASE_URL = os.getenv("DW_DATABASE_URL")

# Create the database connection using SQLAlchemy with a timeout
engine = create_engine(DATABASE_URL, connect_args={"timeout": 30})


def get_schema():
    """Retrieve the database schema information from all schemas."""
    try:
        inspector = inspect(engine)
        schema = {}
        # Get all schema names
        schema_names = inspector.get_schema_names()

        for schema_name in schema_names:
            for table_name in inspector.get_table_names(schema=schema_name):
                columns = [
                    column["name"]
                    for column in inspector.get_columns(table_name, schema=schema_name)
                ]
                # Store the schema-qualified table name
                schema[f"{schema_name}.{table_name}"] = columns

        # Log the retrieved schema
        logger.info("Retrieved Schema: %s", schema)

        return schema
    except Exception as e:
        logger.error("Error retrieving schema: %s", str(e))
        return {}


def clean_schema(schema):
    """Clean up schema by removing any unwanted characters."""
    cleaned_schema = {}
    for table, columns in schema.items():
        cleaned_table = table.replace('"', "")
        cleaned_columns = [col.replace('"', "") for col in columns]
        cleaned_schema[cleaned_table] = cleaned_columns

    # Log the cleaned schema
    logger.info("Cleaned Schema: %s", cleaned_schema)

    return cleaned_schema


def schema_to_string(schema):
    """Convert schema dictionary to a string format."""
    schema_str = []
    for table, columns in schema.items():
        columns_str = ", ".join(columns)
        schema_str.append(f"{table}: {columns_str}")

    # Log the schema string
    logger.info("Schema String: %s", "; ".join(schema_str))

    return "; ".join(schema_str)


def execute_sql(query: str):
    """Execute a SQL query and return the result as a DataFrame."""
    try:
        # Directly execute the SQL query without trying to manually parse it
        with engine.connect() as connection:
            result = connection.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Log the executed query and the result
        logger.info("Executed SQL Query: %s", query)
        logger.info(
            "Query Result: %s", df.head()
        )  # Log only the first few rows for brevity

        return df

    except Exception as e:
        logger.error("Error executing SQL query: %s", str(e))
        raise
