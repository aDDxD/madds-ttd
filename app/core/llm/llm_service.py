import re

from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from app.core.data_sources.data_source_handler import DataSourceHandler
from app.core.llm.models import DataAnalysisResponse
from app.core.llm.prompts import Prompts
from app.core.utils.config import Config
from app.core.utils.logger import Logger


class LLMService:
    def __init__(self, data_source_url: str, model_name: str = "gpt-4o-mini"):
        self.logger = Logger(self.__class__.__name__).get_logger()
        self.data_handler = DataSourceHandler.create(data_source_url)
        self.llm = ChatOpenAI(model=model_name, openai_api_key=Config().OPENAI_API_KEY)
        self.output_parser = PydanticOutputParser(pydantic_object=DataAnalysisResponse)

    def generate_analysis_description(self):
        """Generate a concise analysis description based on the data source schema."""
        try:
            self.logger.info("Retrieving schema from data source...")
            raw_schema = self.data_handler.get_schema()
            self.logger.info(f"Schema retrieved: {len(raw_schema)} tables found.")

            formatted_schema = self.data_handler.schema_to_string(raw_schema)
            self.logger.info("Schema formatted successfully.")

            if not formatted_schema:
                self.logger.error(
                    "Schema is empty. Unable to generate analysis description."
                )
                raise ValueError(
                    "Schema could not be retrieved. Ensure the data source is accessible."
                )

            prompt_template = Prompts.data_source_overview_prompt(formatted_schema)
            self.logger.info("Generating description using the language model...")
            description_prompt = prompt_template.format()
            self.logger.debug(f"Prompt for LLM:\n{description_prompt}")

            response = self.llm.invoke(
                [{"role": "system", "content": description_prompt}]
            )
            self.logger.info("Description generated successfully.")
            return response.content.strip()

        except Exception as e:
            self.logger.error(f"Error generating analysis description: {str(e)}")
            raise

    def process_data_analysis(
        self, natural_language_query: str, db_type: str = "SQL Server"
    ) -> str:
        """Process the natural language query and return the pure Python code needed to generate the dashboard."""
        try:
            # Step 1: Clarify user intent
            clarification_prompt = Prompts.clarification_prompt(natural_language_query)
            clarification_response = self.llm.invoke(
                [{"role": "system", "content": clarification_prompt.format()}]
            )
            self.logger.info(
                f"Clarification response: {clarification_response.content}"
            )

            # Step 2: Retrieve and format the schema
            raw_schema = self.data_handler.get_schema()
            self.logger.info(f"Schema retrieved with {len(raw_schema)} tables.")
            formatted_schema = self.data_handler.schema_to_string(raw_schema)

            # Step 3: Process the query with initial analysis
            prompt_template = Prompts.data_analysis_prompt(formatted_schema, db_type)
            formatted_prompt = prompt_template.format(
                query=natural_language_query,
                json_schema=Prompts.JSON_SCHEMA_DESCRIPTION,
            )
            self.logger.debug(
                f"Formatted prompt for data analysis:\n{formatted_prompt}"
            )

            response = self.llm.invoke(
                [{"role": "system", "content": formatted_prompt}]
            )
            self.logger.info("Received initial response from LLM.")

            # Step 4: Generate the dashboard code
            dashboard_prompt = Prompts.dashboard_creation_prompt(
                formatted_schema, db_type
            )
            dashboard_response = self.llm.invoke(
                [
                    {
                        "role": "system",
                        "content": dashboard_prompt.format(
                            query=natural_language_query
                        ),
                    }
                ]
            )
            self.logger.info(
                f"Dashboard creation response: {dashboard_response.content}"
            )

            # Step 5: Remove any markdown or extraneous text from the response
            final_code = dashboard_response.content.strip()

            # Remove markdown formatting like ```python and ```
            final_code = re.sub(r"```(?:python)?\n", "", final_code)
            final_code = re.sub(r"```", "", final_code)

            return final_code

        except Exception as e:
            self.logger.error(
                f"Error processing data analysis: {str(e)}", exc_info=True
            )
            raise
