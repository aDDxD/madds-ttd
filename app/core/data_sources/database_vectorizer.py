import json
import os
from datetime import datetime, timedelta
from decimal import Decimal

import pandas as pd

from app.core.data_sources.database_handler import DatabaseHandler
from app.core.utils.config import Config


# Run command:  python -m app.core.data_sources.database_vectorizer


class DatabaseVectorizer:
    def __init__(self, database_url: str):
        self.db_handler = DatabaseHandler(database_url=database_url)
        self.chunks_dir = Config.VECTORIZED_DATA_PATH
        os.makedirs(self.chunks_dir, exist_ok=True)
        self.type_serializers = {
            pd.Timestamp: lambda x: x.isoformat(),
            datetime: lambda x: x.isoformat(),
            pd.Timedelta: str,
            timedelta: str,
            int: lambda x: x,
            float: lambda x: x,
            Decimal: float,
            pd.Categorical: str,
            bytes: lambda x: x.decode("utf-8", errors="ignore"),
            bool: lambda x: bool(x),
        }

    def json_serialize(self, value):
        """Helper function to serialize different data types to JSON-compatible formats."""
        if pd.isna(value):
            return None  # Handle NaN and other NA values
        for dtype, serializer in self.type_serializers.items():
            if isinstance(value, dtype):
                return serializer(value)
        return str(value)  # Fallback for any other types

    def replace_nan_after_serialization(self, obj):
        """Recursively replace NaN with None in the serialized data."""
        if isinstance(obj, list):
            return [self.replace_nan_after_serialization(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self.replace_nan_after_serialization(v) for k, v in obj.items()}
        elif isinstance(obj, float) and pd.isna(obj):
            return None
        return obj

    def get_relationships(self, schema):
        """Retrieve relationships and other metadata for the schema."""
        relationships = {}
        for full_table_name in schema.keys():
            schema_name, table_name = full_table_name.split(".")
            relationships[full_table_name] = {
                "foreign_keys": self.db_handler.get_foreign_keys(
                    schema_name, table_name
                ),
                "indexes": self.db_handler.get_indexes(schema_name, table_name),
                "constraints": self.db_handler.get_constraints(schema_name, table_name),
            }
        return relationships

    def prepare_database_for_vectorization(self):
        """Extract and prepare the database data and schema for vectorization."""
        schema = self.db_handler.get_schema()
        relationships = self.get_relationships(schema)

        for table_name, columns in schema.items():
            # Extract full data for each table
            data = self.db_handler.execute_sql(f"SELECT * FROM {table_name}")

            # Convert various data types to JSON-serializable formats
            data = data.map(self.json_serialize)

            # Combine schema, data, and relationships into chunks
            for i in range(0, len(data), 100):  # Example chunking by 100 rows
                chunk_data = data.iloc[i : i + 100].to_dict(orient="records")
                chunk = {
                    "table_name": table_name,
                    "columns": columns,
                    "data": chunk_data,
                    "relationships": relationships.get(table_name, {}),
                }

                # Replace NaN with None after serialization
                chunk = self.replace_nan_after_serialization(chunk)

                # Save chunk as a JSON file
                chunk_filename = f"{table_name}_chunk_{i//100}.json"
                with open(os.path.join(self.chunks_dir, chunk_filename), "w") as f:
                    json.dump(chunk, f)

    def run_job(self):
        """Run the full vectorization process."""
        self.prepare_database_for_vectorization()


if __name__ == "__main__":
    vectorizer = DatabaseVectorizer(database_url=Config.DW_DATABASE_URL)
    vectorizer.run_job()
