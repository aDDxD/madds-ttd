import json
from typing import List

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.data_sources.database_handler import DatabaseHandler
from app.core.utils.config import Config
from app.core.utils.logger import get_logger


class VisualizationItem(BaseModel):
    description: str
    sql_query: str
    visualization: str
    plotly_express_function: str


class DataAnalysisResponse(BaseModel):
    visualizations: List[VisualizationItem]


class LLMService:
    def __init__(self, database_url: str, model_name: str = "gpt-4o-mini"):
        """
        Initialize the LLMService with a database connection and language model.

        :param database_url: The URL of the database to connect to.
        :param model_name: The name of the language model to use. Default is "gpt-4o-mini".
        """
        self.logger = get_logger(self.__class__.__name__)
        self.db_manager = DatabaseHandler(database_url)
        self.llm = ChatOpenAI(model=model_name, openai_api_key=Config.OPENAI_API_KEY)

        # Create an output parser using the Pydantic model
        self.output_parser = PydanticOutputParser(pydantic_object=DataAnalysisResponse)

    def generate_analysis_description(self):
        """
        Generate a concise analysis description based on the database schema.

        :return: A user-friendly description string generated by the LLM.
        """
        schema = self.db_manager.get_schema()
        if not schema:
            self.logger.error(
                "Failed to generate analysis description: Schema is empty."
            )
            raise ValueError(
                "Schema could not be retrieved. Ensure the database is accessible."
            )

        # Template for a more concise, user-friendly description
        prompt_template = ChatPromptTemplate.from_template(
            template=(
                f"You are connected to a database with the following schema:\n{schema}\n"
                "Provide a brief, end-user-friendly description of this database, "
                "such as 'You are connected to the XYZ database, which holds information about ABC.'"
            )
        )

        description_prompt = prompt_template.format()
        response = self.llm.invoke([{"role": "system", "content": description_prompt}])
        self.logger.info("Analysis description generated successfully.")
        return response.content.strip()

    def process_data_analysis(
        self,
        natural_language_query: str,
        db_type: str = "SQL Database",
        schema: str = "",
    ):
        """
        Process the natural language query and return a structured JSON response.
        """
        prompt_template = ChatPromptTemplate.from_template(
            template=(
                f"You are a professional Data Analyst with expertise in {db_type} databases. "
                f"Given the following database schema: {schema} "
                f"your task is to generate meaningful insights from the natural language query: '{{{{query}}}}'. "
                f"Provide as many visualizations as necessary to comprehensively address the query. "
                f"Your response must be structured as a JSON object adhering to the following schema: "
                "{json_schema} "
                f"Each item in the 'visualizations' array should include: "
                f"- 'description': A brief explanation of the suggested data visualization and its purpose. "
                f"- 'sql_query': A valid SQL query that must be compatible with the {db_type} database. Ensure the query only references columns available in the provided schema. "
                f"- 'visualization': Suggested visualization type (e.g., bar, line, pie, etc.). "
                f"- 'plotly_express_function': A complete Plotly Express function call to generate the suggested visualization, e.g., 'px.bar(data, x=\"column_name\", y=\"column_name\")'. "
                "Your analysis should be both accurate and actionable, helping to uncover key trends, comparisons, and insights from the data."
            )
        )
        schema_description = "{'visualizations': [{'description': 'string', 'sql_query': 'string', 'visualization': 'string', 'plotly_express_function': 'string'}]}"

        formatted_prompt = prompt_template.format(
            query=natural_language_query, json_schema=schema_description
        )
        response = self.llm.invoke([{"role": "system", "content": formatted_prompt}])

        # Parse the response using the output parser
        return self.output_parser.parse(response.content)

    def extract_query_visualizations(self, response_content: str):
        """
        Extract the SQL queries, visualizations, and descriptions from the LLM response.

        :param response_content: The JSON-formatted content returned by the LLM.
        :return: A list of dictionaries with cleaned SQL queries, visualization types, and descriptions.
        """
        try:
            self.logger.info("Rsponse content before json loads: %s", response_content)
            # Parse the JSON content
            response_dict = json.loads(response_content)

            # Iterate over the items, clean SQL queries, and store the results
            results = []
            for item in response_dict:
                # Clean the SQL query
                cleaned_sql = item["sql_query"].strip().lower()

                results.append(
                    {
                        "description": item["description"],
                        "sql_query": cleaned_sql,
                        "visualization": item["visualization"],
                    }
                )

            return results

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            raise ValueError(
                "Failed to parse LLM response. Ensure the response is in valid JSON format."
            )
