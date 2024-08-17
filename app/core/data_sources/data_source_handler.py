from abc import ABC, abstractmethod

import pandas as pd


class DataSourceHandler(ABC):
    @abstractmethod
    def get_schema(self) -> dict:
        pass

    @abstractmethod
    def execute_sql(self, query: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def schema_to_string(self, schema: dict) -> str:
        pass

    @staticmethod
    def create(data_source_url: str) -> "DataSourceHandler":
        if (
            data_source_url.startswith("postgresql://")
            or data_source_url.startswith("mysql://")
            or data_source_url.startswith("sqlite://")
            or data_source_url.startswith("mssql+pyodbc://")
        ):
            from app.core.data_sources.database_handler import DatabaseHandler

            return DatabaseHandler(data_source_url)
        else:
            raise ValueError(f"Unsupported data source URL: {data_source_url}")
