import logging
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.models.db.utils import clean_schema, execute_sql, get_schema, schema_to_string

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Prepare schema information
schema = clean_schema(get_schema())
schema_str = schema_to_string(schema)


def process_query(natural_language_query: str):
    # Retrieve and clean the schema
    schema = clean_schema(get_schema())
    schema_str = schema_to_string(schema)

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

    llm = ChatOpenAI(model="gpt-3.5-turbo")

    sql_query_prompt = prompt_template.format(
        query=natural_language_query, visualizations=""
    )
    response = llm.invoke([{"role": "system", "content": sql_query_prompt}])
    response_content = response.content

    # Extract SQL query and visualization suggestions
    sql_query, visualization_suggestions = extract_query_and_visualizations(
        response_content
    )

    # Clean up any unintended prefixes or keywords in the SQL query
    sql_query = clean_sql_query(sql_query)

    result_df = execute_sql(sql_query)

    return result_df, sql_query, visualization_suggestions


def clean_sql_query(sql_query: str) -> str:
    """Clean the SQL query to remove any unintended prefixes or keywords."""
    # Remove the 'sql' keyword if it mistakenly appears at the beginning
    sql_query = sql_query.lstrip().lower().replace("sql\n", "").replace("sql ", "")

    # Post-process the SQL query to replace LIMIT with TOP for SQL Server
    if "LIMIT" in sql_query.upper():
        limit_value = sql_query.split("LIMIT")[1].strip().rstrip(";")
        sql_query = sql_query.split("LIMIT")[0].strip()
        sql_query = sql_query.replace("SELECT", f"SELECT TOP {limit_value}")

    return sql_query.strip()


def extract_query_and_visualizations(response_content):
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
            s.strip() for s in visualization_suggestions_part.split("\n") if s.strip()
        ]
    else:
        sql_query = response_content.split("```")[1].strip()
        visualization_suggestions = ["bar"]

    return sql_query, visualization_suggestions
