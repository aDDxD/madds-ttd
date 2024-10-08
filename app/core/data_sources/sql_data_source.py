from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.data_sources.data_source import DataSource
from app.core.utils.logger import Logger


class SQLDataSource(DataSource):
    def __init__(self, source: str):
        self.logger = Logger(self.__class__.__name__).get_logger()
        self.engine = self._connect_to_database(source)

    def _connect_to_database(self, source: str):
        try:
            engine = create_engine(source)
            self.logger.info("Connected to database successfully.")
            return engine
        except SQLAlchemyError as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise ValueError(f"Failed to connect to the database. Error: {e}")

    def get_schema(self) -> dict:
        try:
            inspector = inspect(self.engine)
            schema = {}
            schema_names = inspector.get_schema_names()

            # Filter out system or default schemas for 'SQL Server' and 'PostgreSQL'
            filtered_schemas = [
                schema_name
                for schema_name in schema_names
                if not (
                    (
                        self.engine.dialect.name == "mssql"
                        and schema_name in ["master", "model", "msdb", "tempdb"]
                    )
                    or (
                        self.engine.dialect.name == "postgresql"
                        and (
                            schema_name == "information_schema"
                            or schema_name.startswith("pg_")
                        )
                    )
                )
            ]

            for schema_name in filtered_schemas:
                for table_name in inspector.get_table_names(schema=schema_name):
                    columns_info = inspector.get_columns(table_name, schema=schema_name)
                    foreign_keys = self._get_foreign_keys(schema_name, table_name)
                    indexes = self._get_indexes(schema_name, table_name)
                    constraints = self._get_constraints(schema_name, table_name)
                    data_summary = self._get_data_summary(
                        schema_name, table_name, columns_info
                    )

                    schema[f"{schema_name}.{table_name}"] = {
                        "columns": [
                            {
                                "name": column["name"],
                                "type": str(column["type"]),
                                "nullable": column["nullable"],
                                "default": column.get("default"),
                            }
                            for column in columns_info
                        ],
                        "foreign_keys": foreign_keys,
                        "indexes": indexes,
                        "constraints": constraints,
                        "data_summary": data_summary,
                    }

            if not schema:
                self.logger.warning("No schema information was retrieved.")
            else:
                self.logger.info(f"Schema retrieved with {len(schema)} tables.")

            return schema
        except SQLAlchemyError as e:
            self.logger.error(f"Error retrieving schema: {str(e)}")
            raise

    def schema_to_string(self, schema: dict) -> str:
        if not schema:
            self.logger.warning("Schema is empty.")
            return ""

        schema_str = []
        for table, details in schema.items():
            table_str = f"Table: {table}\n"

            columns = details.get("columns", [])
            table_str += "  Columns:\n"
            for column in columns:
                table_str += f"    - {column['name']} ({column['type']})"
                if column.get("nullable"):
                    table_str += " [NULLABLE]"
                if column.get("default") is not None:
                    table_str += f" [DEFAULT: {column['default']}]"
                table_str += "\n"

            foreign_keys = details.get("foreign_keys", [])
            if foreign_keys:
                table_str += "  Foreign Keys:\n"
                for fk in foreign_keys:
                    table_str += f"    - {fk['name']} -> {fk['referred_schema']}.{fk['referred_table']}({', '.join(fk['referred_columns'])})\n"

            indexes = details.get("indexes", [])
            if indexes:
                table_str += "  Indexes:\n"
                for idx in indexes:
                    table_str += f"    - {idx['name']} on {', '.join(idx['column_names'])} [UNIQUE: {idx['unique']}]\n"

            constraints = details.get("constraints", {})
            if constraints:
                pk = constraints.get("primary_key", {})
                if pk:
                    table_str += f"  Primary Key:\n    - {', '.join(pk['constrained_columns'])}\n"
                unique_constraints = constraints.get("unique_constraints", [])
                if unique_constraints:
                    table_str += "  Unique Constraints:\n"
                    for uc in unique_constraints:
                        table_str += (
                            f"    - {uc['name']} on {', '.join(uc['column_names'])}\n"
                        )

            data_summary = details.get("data_summary", {})
            if data_summary:
                table_str += "  Data Summary:\n"
                for col_name, summary in data_summary.items():
                    table_str += f"    - {col_name}: "
                    if "min" in summary and "max" in summary:
                        table_str += f"Min: {summary['min']}, Max: {summary['max']}\n"
                    if "distinct_values" in summary:
                        table_str += f"Distinct Values: {', '.join(map(str, summary['distinct_values']))}\n"

            schema_str.append(table_str)

        return "\n".join(schema_str)

    def _get_foreign_keys(self, schema_name, table_name):
        try:
            inspector = inspect(self.engine)
            foreign_keys = inspector.get_foreign_keys(table_name, schema=schema_name)
            return [
                {
                    "name": fk["name"],
                    "constrained_columns": fk["constrained_columns"],
                    "referred_schema": fk["referred_schema"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
                for fk in foreign_keys
            ]
        except SQLAlchemyError as e:
            self.logger.error(
                f"Error retrieving foreign keys for {schema_name}.{table_name}: {str(e)}"
            )
            return []

    def _get_indexes(self, schema_name, table_name):
        try:
            inspector = inspect(self.engine)
            indexes = inspector.get_indexes(table_name, schema=schema_name)
            return [
                {
                    "name": idx["name"],
                    "column_names": idx["column_names"],
                    "unique": idx.get("unique", False),
                }
                for idx in indexes
            ]
        except SQLAlchemyError as e:
            self.logger.error(
                f"Error retrieving indexes for {schema_name}.{table_name}: {str(e)}"
            )
            return []

    def _get_constraints(self, schema_name, table_name):
        try:
            inspector = inspect(self.engine)
            pk_constraint = inspector.get_pk_constraint(table_name, schema=schema_name)
            try:
                unique_constraints = inspector.get_unique_constraints(
                    table_name, schema=schema_name
                )
            except NotImplementedError:
                unique_constraints = []

            return {
                "primary_key": pk_constraint,
                "unique_constraints": unique_constraints,
            }
        except SQLAlchemyError as e:
            self.logger.error(
                f"Error retrieving constraints for {schema_name}.{table_name}: {str(e)}"
            )
            return {}

    def _get_data_summary(self, schema_name, table_name, columns_info):
        """Get data summary for each column in the table."""
        data_summary = {}
        try:
            with self.engine.connect() as connection:
                for column in columns_info:
                    column_name = column["name"]
                    column_type = str(column["type"])

                    quoted_column_name = self.engine.dialect.identifier_preparer.quote(
                        column_name
                    )

                    if (
                        "INT" in column_type
                        or "NUMERIC" in column_type
                        or "FLOAT" in column_type
                        or "DECIMAL" in column_type
                    ):
                        # Numeric columns: Get min and max values
                        min_max_query = text(
                            f"SELECT MIN({quoted_column_name}) AS min_value, MAX({quoted_column_name}) AS max_value FROM {schema_name}.{table_name}"
                        )
                        result = connection.execute(min_max_query).fetchone()
                        # Use integer indexing because result is a tuple
                        data_summary[column_name] = {
                            "min": result[0],
                            "max": result[1],
                        }
                    elif "CHAR" in column_type or "TEXT" in column_type:
                        if self.engine.dialect.name == "postgresql":
                            # PostgreSQL uses LIMIT
                            distinct_query = text(
                                f"SELECT DISTINCT {quoted_column_name} FROM {schema_name}.{table_name} LIMIT 10"
                            )
                        elif self.engine.dialect.name == "mssql":
                            # SQL Server uses TOP
                            distinct_query = text(
                                f"SELECT DISTINCT TOP 10 {quoted_column_name} FROM {schema_name}.{table_name}"
                            )
                        else:
                            # Default fallback, if needed
                            distinct_query = text(
                                f"SELECT DISTINCT {quoted_column_name} FROM {schema_name}.{table_name} LIMIT 10"
                            )

                        result = connection.execute(distinct_query).fetchall()
                        # Use integer indexing for each row
                        data_summary[column_name] = {
                            "distinct_values": [row[0] for row in result],
                        }

        except SQLAlchemyError as e:
            self.logger.error(
                f"Error retrieving data summary for {schema_name}.{table_name}: {str(e)}"
            )

        return data_summary
