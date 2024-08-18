import json

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

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
                    # Get the pure Python code from the LLM response
                    python_code = self.llm_service.process_data_analysis(prompt)

                    st.write("## Generated Python Code")
                    st.code(python_code, language="python")

                    # Execute the generated Python code
                    exec(python_code)

                except Exception as e:
                    self.logger.error(
                        f"Error processing query: {str(e)}", exc_info=True
                    )
                    st.error(f"Error processing query: {str(e)}")
            else:
                st.warning("Please enter a query.")
