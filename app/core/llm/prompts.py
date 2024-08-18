from langchain_core.prompts import ChatPromptTemplate


class Prompts:
    JSON_SCHEMA_DESCRIPTION = (
        "{'visualizations': [{'description': 'string', 'sql_query': 'string', "
        "'visualization': 'string', 'plotly_express_function': 'string'}]}"
    )

    @staticmethod
    def data_source_overview_prompt(formatted_schema: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template(
            template=(
                f"You are connected to a database with the following schema:\n{formatted_schema}\n"
                "Your task is to provide a clear and concise overview of this database, suitable for an end user. "
                "The description should highlight the primary purpose and content of the database, including key tables and their relationships. "
                "Ensure that the overview is easy to understand, even for users without technical expertise."
            )
        )

    @staticmethod
    def clarification_prompt(query: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template(
            template=(
                f"The user has provided the following query: '{query}'. "
                "Please clarify the intent of this query by specifying the type of insights they might be looking for, "
                "such as trend analysis, comparison, distribution, correlation, or a specific data point. "
                "Also, consider any contextual details that could help tailor the analysis to the user's needs."
            )
        )

    @staticmethod
    def data_analysis_prompt(formatted_schema: str, db_type: str) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template(
            template=(
                f"You are a highly skilled data analyst with deep expertise in {db_type} databases. "
                f"Your task is to generate insightful and accurate Python code based on the user's query: '{{{{query}}}}'. "
                f"You have access to the following database schema:\n{formatted_schema}\n"
                "Ensure that any SQL queries you generate reference tables and columns exactly as they appear in the schema. "
                "Use only the table names and columns from the schema provided—do not invent or assume any tables or columns. "
                f"Make sure the SQL queries are compatible with {db_type}, such as using 'TOP' instead of 'LIMIT' when working with SQL Server. "
                "Your code should focus on providing the most relevant insights through data analysis and visualizations, specifically tailored to the user's query. "
                "All visualizations should be created using Plotly Express, and the code must be suitable for execution in a Streamlit app. "
                "Only return the executable Python code without any explanations, comments, or markdown. "
                "Make sure the code is efficient, accurate, and directly aligned with the user's intent."
            )
        )

    @staticmethod
    def dashboard_creation_prompt(
        formatted_schema: str, db_type: str
    ) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_template(
            template=(
                f"Based on the query '{{{{query}}}}', your task is to generate the final Python code necessary to create a comprehensive dashboard using the provided schema. "
                f"The code should include SQL queries that directly fetch data from the schema and use Plotly Express for all visualizations. "
                f"Here is the schema again to ensure accuracy:\n{formatted_schema}\n"
                "Ensure that the code references tables and columns accurately according to the provided schema and is fully prepared for execution in a Streamlit app. "
                f"Ensure that the SQL queries are fully compatible with {db_type}, avoiding syntax errors (e.g., using 'TOP' instead of 'LIMIT' for SQL Server). "
                "Use `os.getenv('DW_DATABASE_URL')` to connect to the database. "
                "Always use SQLAlchemy to connect to the database. "
                "Do not use or create any tables, columns, or data structures that are not explicitly mentioned in the schema provided. "
                "The code should be concise, focused, and contain no extraneous text, comments, or markdown—only the executable Python code."
            )
        )
