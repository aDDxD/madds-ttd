from sqlalchemy import create_engine, inspect
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
