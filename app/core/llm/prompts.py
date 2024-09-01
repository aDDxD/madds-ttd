class Prompts:

    @staticmethod
    def data_source_overview_prompt(relevant_schema_text: str) -> list:
        return [
            {
                "role": "system",
                "content": (
                    "CONTEXT: "
                    "You are a highly skilled database analyst using RAG to understand the structure and purpose "
                    "of a given data source schema and your goal is to provide insightful and concise analysis based "
                    "on the schema details provided. "
                    "RULES: "
                    "- Introduction/Summary must be one to two sentences long. "
                    "- Example questions/prompts must be 3 to 5 suggestions. "
                    "- Do not include markdown formatting or code in your response. "
                ),
            },
            {
                "role": "user",
                "content": (
                    "Based on the retrieved schema details, please provide a brief introduction about the data source schema "
                    "and suggest 3 to 5 example questions/prompt suggestions that an end-user might ask to gain insights "
                    "or perform analyses using this data source. "
                    "The schema details below provide insight into the structure and content of the data source:"
                ),
            },
            {"role": "system", "content": relevant_schema_text},
        ]

    @staticmethod
    def dashboard_creation_prompt(
        formatted_schema: str, db_type: str, query: str
    ) -> list:
        return [
            {
                "role": "system",
                "content": (
                    "CONTEXT: "
                    "You are a highly skilled data analyst with expertise in creating dashboards using data from various databases. "
                    "Your goal is to generate Python code for a comprehensive, interactive, and user-friendly dashboard that leverages the provided schema and the user's query. "
                    "The dashboard should be designed to provide meaningful insights, be easy to navigate, and visually appealing."
                    "\n\nRULES: "
                    "- The code must include SQL queries that directly fetch data from the provided schema, ensuring accurate and relevant data retrieval. "
                    "- Do not use or create any tables, columns, or data structures not explicitly mentioned in the schema. "
                    "- All visualizations must be created using Plotly Express, taking care to use appropriate chart types that best represent the data and insights. "
                    "- Use SQLAlchemy for all database connections. Always connect to the database using:\n"
                    "  ```python\n"
                    "  DATABASE_URL = os.getenv('DW_DATABASE_URL')\n"
                    "  engine = create_engine(DATABASE_URL)\n"
                    "  ```"
                    "- Ensure all SQL queries are fully compatible with the specified database type, such as using 'TOP' instead of 'LIMIT' for SQL Server. "
                    "- The dashboard should not include interactive elements since it's being executred inside a exec() method. "
                    "- Design the layout to be clear and organized, with distinct sections for different types of data or analyses. Avoid clutter and ensure all elements are easily readable. "
                    "- Include appropriate titles, labels, and legends for all visualizations to make them understandable at a glance. "
                    "- Ensure that all code is suitable for execution inside a Streamlit app. Use `st.plotly_chart()` to render Plotly figures. "
                    "- Add conditional formatting or color-coding to highlight important trends or anomalies in the data. "
                    "- Avoid using deprecated functions like 'st.cache'. Instead, use 'st.cache_data' or other up-to-date caching methods if needed for performance optimization. "
                    "- Do not use `set_page_config()` as the Python code will run inside an existing Streamlit app where the page configuration is already set. "
                    "- Focus on creating a visually appealing dashboard with a consistent color theme and style to enhance user experience. "
                    "- Write concise and well-structured code without any markdown, comments, or unnecessary text—only provide the executable Python code. "
                    "- Include try/except blocks to ignore charts that may cause errors and still render the other suggested charts"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Based on the following user query, generate the Python code required to create a comprehensive, interactive dashboard: '{query}'. "
                    f"The dashboard should leverage the schema details provided and be fully compatible with a {db_type} database. "
                    "The schema details below provide insight into the structure and content of the data source:"
                ),
            },
            {"role": "system", "content": formatted_schema},
        ]
