import pandas as pd
from sqlalchemy import create_engine, inspect, text

from app.core.config import Config
from app.core.logger import get_logger


class DatabaseHandler:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.engine = create_engine(
            Config.DW_DATABASE_URL, connect_args={"timeout": 30}
        )

    def get_schema(self):
        try:
            inspector = inspect(self.engine)
            schema = {}
            schema_names = inspector.get_schema_names()
            for schema_name in schema_names:
                for table_name in inspector.get_table_names(schema=schema_name):
                    columns = [
                        column["name"]
                        for column in inspector.get_columns(
                            table_name, schema=schema_name
                        )
                    ]
                    schema[f"{schema_name}.{table_name}"] = columns
            self.logger.info("Retrieved Schema: %s", schema)
            return schema
        except Exception as e:
            self.logger.error("Error retrieving schema: %s", str(e))
            return {}

    def clean_schema(self, schema):
        cleaned_schema = {
            table.replace('"', ""): [col.replace('"', "") for col in columns]
            for table, columns in schema.items()
        }
        self.logger.info("Cleaned Schema: %s", cleaned_schema)
        return cleaned_schema

    def schema_to_string(self, schema):
        schema_str = [
            f"{table}: {', '.join(columns)}" for table, columns in schema.items()
        ]
        self.logger.info("Schema String: %s", "; ".join(schema_str))
        return "; ".join(schema_str)

    def execute_sql(self, query: str):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            self.logger.info("Executed SQL Query: %s", query)
            self.logger.info("Query Result: %s", df.head())
            return df
        except Exception as e:
            self.logger.error("Error executing SQL query: %s", str(e))
            raise
