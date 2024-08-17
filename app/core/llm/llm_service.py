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
        try:
            self.logger.info("Starting to retrieve the database schema.")
            raw_schema = self.db_manager.get_schema()
            self.logger.info(
                "Raw schema retrieved successfully with %d tables.", len(raw_schema)
            )

            formatted_schema = self.db_manager.schema_to_string(raw_schema)
            self.logger.info("Formatted schema generated successfully.")

            if not formatted_schema:
                self.logger.error(
                    "Failed to generate analysis description: Schema is empty."
                )
                raise ValueError(
                    "Schema could not be retrieved. Ensure the database is accessible."
                )

            # Template for a more concise, user-friendly description
            prompt_template = ChatPromptTemplate.from_template(
                template=(
                    f"You are connected to a database with the following schema:\n{formatted_schema}\n"
                    "Provide a brief, end-user-friendly description of this database, "
                    "such as 'You are connected to the XYZ database, which holds information about ABC.'"
                )
            )

            self.logger.info("Prompt template created successfully.")

            description_prompt = prompt_template.format()
            self.logger.debug("Formatted description prompt:\n%s", description_prompt)

            response = self.llm.invoke(
                [{"role": "system", "content": description_prompt}]
            )
            self.logger.info("Response from LLM received successfully.")

            return response.content.strip()

        except Exception as e:
            self.logger.error(
                f"Error generating analysis description: {str(e)}", exc_info=True
            )
            raise

    def process_data_analysis(
        self,
        natural_language_query: str,
        db_type: str = "SQL Server",
    ):
        """
        Process the natural language query and return a structured JSON response.
        """
        raw_schema = self.db_manager.get_schema()
        self.logger.info("Schema retrieved with %d tables.", len(raw_schema))

        formatted_schema = self.db_manager.schema_to_string(raw_schema)
        self.logger.info(f"Formatted schema generated for prompt. {formatted_schema}")

        # Log schema summary instead of the whole schema
        self.logger.info("Schema contains %d tables.", len(raw_schema))
        for table_name in list(raw_schema.keys())[:5]:  # Log first 5 table names
            self.logger.info("Table: %s", table_name)
        if len(raw_schema) > 5:
            self.logger.info("...and %d more tables.", len(raw_schema) - 5)

        prompt_template = ChatPromptTemplate.from_template(
            template=(
                f"You are an elite Data Analyst with profound expertise in {db_type} databases. "
                f"Your task is to deliver highly accurate, contextually relevant, and insightful visualizations based on the natural language query: '{{{{query}}}} based on the provided database schema'. "
                f"You are given the following database schema: {formatted_schema}. Use it to ensure the integrity and relevance of your analysis. "
                f"Your focus should be on extracting and presenting insights that are directly aligned with the user's query. Follow these detailed guidelines to achieve the best results: \n\n"
                f"1. **Understand the User's Intent**: Thoroughly analyze the natural language query to grasp the exact information the user is seeking. Consider whether the query is asking for trends, comparisons, distributions, correlations, or specific data points. Tailor your visualizations accordingly.\n"
                f"2. **Respect the Query's Specificity**: If the user asks for insights about a specific entity (e.g., products, regions, time periods), ensure your analysis focuses precisely on that entity. Avoid generalizing to broader categories unless explicitly requested.\n"
                f"3. **Prioritize Relevance Over Quantity**: Deliver only the most relevant visualizations. Avoid unnecessary or redundant charts. If the user requests a specific number of visualizations, adhere strictly to that number.\n"
                f"4. **Contextual Precision**: Ensure that each visualization addresses a different aspect of the query. For example, if the query is about sales trends, consider time-based analyses like line charts or trend analyses. If the query is about product performance, use bar charts or scatter plots to compare metrics like sales or customer ratings.\n"
                f"5. **Avoid Repetition**: Ensure that each visualization offers unique insights. Do not create multiple visualizations that convey the same information unless the query explicitly requests different perspectives (e.g., by region and by product).\n"
                f"6. **Minimize Unnecessary Visualizations**: Keep the analysis concise. If a single visualization sufficiently answers the query, do not create additional visualizations. Focus on depth and accuracy rather than volume.\n"
                f"7. **Use the Correct Visualization Types**: Choose the most appropriate visualization type for the data being analyzed. For example:\n"
                f"   - Use **line charts** for trends over time.\n"
                f"   - Use **bar charts** for comparing quantities across different categories.\n"
                f"   - Use **pie charts** for showing proportions of a whole.\n"
                f"   - Use **scatter plots** for identifying relationships between variables.\n"
                f"   - Use **heatmaps** for showing data density or correlations.\n"
                f"8. **Craft Clear and Insightful Descriptions**: Each visualization should include a brief yet informative description that explains what the visualization reveals in relation to the query. The description should focus on why the visualization was chosen and what insights it provides.\n"
                f"9. **Precision in SQL Queries**: Generate SQL queries that are not only accurate but also optimized to retrieve exactly the data needed for the visualization. Ensure the query references only relevant columns and tables as per the provided schema.\n"
                f"10. **Adhere to Output Format**: Your response must be structured as a JSON object adhering to the following schema:"
                "{json_schema}"
                f"Each item in the 'visualizations' array should include:\n"
                f"   - 'description': A clear explanation of the suggested data visualization, emphasizing its relevance to the query.\n"
                f"   - 'sql_query': A precise SQL query that retrieves the necessary data, fully compatible with the {db_type} database and schema provided.\n"
                f"   - 'visualization': The most appropriate visualization type for the data being analyzed.\n"
                f"   - 'plotly_express_function': A complete Plotly Express function call that generates the visualization, e.g., 'px.bar(data, x=\"column_name\", y=\"column_name\")'.\n"
                f"Your analysis should be exceptionally accurate, directly aligned with the query, and provide deep, actionable insights that the user can immediately leverage."
            )
        )
        schema_description = "{'visualizations': [{'description': 'string', 'sql_query': 'string', 'visualization': 'string', 'plotly_express_function': 'string'}]}"

        formatted_prompt = prompt_template.format(
            query=natural_language_query, json_schema=schema_description
        )
        self.logger.debug("Formatted data analysis prompt:\n%s", formatted_prompt)

        response = self.llm.invoke([{"role": "system", "content": formatted_prompt}])

        # Parse the response using the output parser
        return self.output_parser.parse(response.content)
