import pandas as pd

from app.core.data_sources.data_source import DataSource
from app.core.utils.logger import Logger


class FileDataSource(DataSource):
    def __init__(self, source: str):
        self.logger = Logger(self.__class__.__name__).get_logger()
        self.source = source

    def get_schema(self) -> dict:
        try:
            df = pd.read_csv(self.source)
            schema = {col: str(df[col].dtype) for col in df.columns}
            self.logger.info("File schema retrieved successfully.")
            return schema
        except Exception as e:
            self.logger.error(f"Error retrieving schema from file: {str(e)}")
            raise

    def schema_to_string(self, schema: dict) -> str:
        if not schema:
            self.logger.warning("Schema is empty.")
            return ""

        schema_str = "File Schema:\n"
        for column, dtype in schema.items():
            schema_str += f"  - {column}: {dtype}\n"
        return schema_str

    def execute_sql(self, query: str) -> pd.DataFrame:
        raise NotImplementedError(
            "SQL execution is not supported for file-based data sources."
        )
