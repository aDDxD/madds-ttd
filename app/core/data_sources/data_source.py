from abc import ABC, abstractmethod

import pandas as pd


class DataSource(ABC):
    @abstractmethod
    def get_schema(self) -> dict:
        pass

    @abstractmethod
    def schema_to_string(self, schema: dict) -> str:
        pass

    @abstractmethod
    def execute_sql(self, query: str) -> pd.DataFrame:
        pass

    @staticmethod
    def create(source: str) -> "DataSource":
        if source.startswith(("postgresql://", "mssql+pyodbc://")):
            from app.core.data_sources.sql_data_source import SQLDataSource

            return SQLDataSource(source)
        elif source.lower().endswith((".csv")):
            from app.core.data_sources.file_data_source import FileDataSource

            return FileDataSource(source)
        else:
            raise ValueError(f"Unsupported data source: {source}")
