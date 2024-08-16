import logging
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import Config
from app.core.database_handler import DatabaseHandler
from app.core.logger import get_logger


class LLMService:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.db_manager = DatabaseHandler()
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", openai_api_key=Config.OPENAI_API_KEY
        )  # Using Config for the API key

    def process_query(self, natural_language_query: str):
        schema = self.db_manager.clean_schema(self.db_manager.get_schema())
        schema_str = self.db_manager.schema_to_string(schema)

        if not schema:
            raise ValueError(
                "Schema could not be retrieved. Ensure the database is accessible and try again."
            )

        prompt_template = ChatPromptTemplate.from_template(
            template=(
                f"Based on the following SQL Server schema information: {schema_str}, "
                f"generate a SQL query for the given natural language query: {{query}}, "
                f"and suggest the best types of visualizations for the data. "
                f"Ensure the SQL query is compatible with Microsoft SQL Server."
            )
        )

        sql_query_prompt = prompt_template.format(
            query=natural_language_query, visualizations=""
        )
        response = self.llm.invoke([{"role": "system", "content": sql_query_prompt}])
        response_content = response.content

        sql_query, visualization_suggestions = self.extract_query_and_visualizations(
            response_content
        )
        sql_query = self.clean_sql_query(sql_query)
        result_df = self.db_manager.execute_sql(sql_query)

        return result_df, sql_query, visualization_suggestions

    def clean_sql_query(self, sql_query: str) -> str:
        sql_query = sql_query.lstrip().lower().replace("sql\n", "").replace("sql ", "")
        if "LIMIT" in sql_query.upper():
            limit_value = sql_query.split("LIMIT")[1].strip().rstrip(";")
            sql_query = sql_query.split("LIMIT")[0].strip()
            sql_query = sql_query.replace("SELECT", f"SELECT TOP {limit_value}")
        return sql_query.strip()

    def extract_query_and_visualizations(self, response_content):
        if (
            "SQL Query:" in response_content
            and "Visualization Suggestions:" in response_content
        ):
            sql_query_part = (
                response_content.split("SQL Query:")[1]
                .split("Visualization Suggestions:")[0]
                .strip()
            )
            sql_query = sql_query_part.split("```")[1].strip()
            visualization_suggestions_part = response_content.split(
                "Visualization Suggestions:"
            )[1].strip()
            visualization_suggestions = [
                s.strip()
                for s in visualization_suggestions_part.split("\n")
                if s.strip()
            ]
        else:
            sql_query = response_content.split("```")[1].strip()
            visualization_suggestions = ["bar"]

        return sql_query, visualization_suggestions
