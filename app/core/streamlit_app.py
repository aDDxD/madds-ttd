import json
import streamlit as st
import plotly.express as px

from app.core.llm.llm_service import LLMService
from app.core.utils.config import Config
from app.core.utils.logger import Logger


class StreamlitApp:
    def __init__(self):
        st.set_page_config(layout="wide")

        self.logger = Logger(self.__class__.__name__).get_logger()
        self.database_url = Config().DW_DATABASE_URL
        self.llm_service = LLMService(data_source_url=self.database_url)

        if "analysis_description" not in st.session_state:
            st.session_state["analysis_description"] = None

    def show_database_overview(self):
        """Displays the database overview in the sidebar."""
        st.sidebar.title("Database Overview")
        try:
            if st.session_state["analysis_description"] is None:
                analysis_description = self.llm_service.generate_analysis_description()
                st.session_state["analysis_description"] = analysis_description

            st.sidebar.markdown(
                f"<div style='width: auto; word-wrap: break-word;'>{st.session_state['analysis_description']}</div>",
                unsafe_allow_html=True,
            )
        except Exception as e:
            self.logger.error(f"Error generating analysis description: {str(e)}")
            st.sidebar.error(f"Error generating analysis description: {str(e)}")

    def run(self):
        """Runs the main Streamlit application."""
        st.title("Talk to Your Data")
        st.subheader("Interact with your data using natural language queries")

        self.show_database_overview()

        prompt = st.text_input(
            "Enter Your Query:",
            placeholder="e.g., Show total sales by product category",
        )

        if st.button("Submit Query"):
            if prompt:
                try:
                    structured_response = self.llm_service.process_data_analysis(prompt)
                    self.logger.debug(f"Structured Response: {structured_response}")

                    structured_response_json = json.dumps(
                        structured_response.dict(), indent=2
                    )

                    with st.expander("Inspect LLM Response"):
                        st.text_area(
                            "LLM Response", structured_response_json, height=400
                        )

                    st.write("## Generated Visualizations")
                    for i, item in enumerate(structured_response.visualizations):
                        st.write(f"### **Visualization {i + 1}:**")
                        st.write(f"- **Description:** {item.description}")

                        df = self.llm_service.data_handler.execute_sql(item.sql_query)
                        plotly_code = item.plotly_express_function.replace("data", "df")
                        chart = eval(plotly_code, {"df": df, "px": px})
                        st.plotly_chart(chart)

                        with st.expander("Show Data Used for the Chart"):
                            st.dataframe(df)

                except Exception as e:
                    self.logger.error(
                        f"Error processing query: {str(e)}", exc_info=True
                    )
                    st.error(f"Error processing query: {str(e)}")
            else:
                st.warning("Please enter a query.")
