import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.utils.logger import get_logger


class DatabaseHandler:
    def __init__(self, database_url: str):
        """
        Initialize the DatabaseHandler with a connection to the database.

        :param database_url: The URL of the database to connect to.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.engine = self._connect_to_database(database_url)

    def _connect_to_database(self, database_url: str):
        """
        Establish a connection to the database.

        :param database_url: The database connection URL.
        :return: A SQLAlchemy engine instance.
        """
        try:
            engine = create_engine(database_url, connect_args={"timeout": 30})
            self.logger.info("Successfully connected to the database.")
            return engine
        except SQLAlchemyError as e:
            self.logger.error("Error connecting to the database: %s", str(e))
            raise

    def _schema_to_string(self, schema: dict) -> str:
        """
        Convert the schema dictionary to a formatted string.

        :param schema: The schema dictionary.
        :return: A string representation of the schema.
        """
        if not schema:
            self.logger.warning("Schema is empty.")
            return ""
        schema_str = "\n".join(
            [f"{table}: {', '.join(columns)}" for table, columns in schema.items()]
        )
        return schema_str

    def get_schema(self) -> str:
        """
        Retrieve the database schema and convert it to a string.

        :return: A string representation of the database schema.
        """
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

            if not schema:
                self.logger.warning("No schema information was retrieved.")
            else:
                self.logger.info(
                    "Schema retrieved successfully with %d tables.", len(schema)
                )

            return self._schema_to_string(schema)
        except SQLAlchemyError as e:
            self.logger.error("Error retrieving schema: %s", str(e))
            raise

    def execute_sql(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the result as a DataFrame.

        :param query: The SQL query to execute.
        :return: A DataFrame containing the query results.
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            if df.empty:
                self.logger.warning("Query executed but returned no results.")
            else:
                self.logger.info(
                    "Query executed successfully and returned %d rows.", len(df)
                )
            return df
        except SQLAlchemyError as e:
            self.logger.error("Error executing SQL query: %s", str(e))
            raise
