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
    prompt_template = ChatPromptTemplate.from_template(
        template=(
            f"Based on the following schema information: {schema_str}, "
            f"generate a SQL query for the given natural language query: {{query}}, "
            f"and suggest the best types of visualizations for the data. Provide the SQL query and the visualization suggestions in the following format:\n\n"
            f"SQL Query: ```\n{{query}}\n```\nVisualization Suggestions: {{visualizations}}"
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

    # Clean up the SQL query to remove any unwanted text, such as "sql"
    if sql_query.lower().startswith("sql"):
        sql_query = sql_query[sql_query.lower().index("select") :].strip()

    result_df = execute_sql(sql_query)

    return result_df, sql_query, visualization_suggestions


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
