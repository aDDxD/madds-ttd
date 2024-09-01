import pandas as pd
import streamlit as st

from app.core.llm.llm_service import LLMService
from app.core.utils.config import Config
from app.core.utils.logger import Logger


class StreamlitApp:
    def __init__(self):
        # Set Streamlit page configuration
        st.set_page_config(layout="wide")

        # Initialize logger and services
        self.logger = Logger(self.__class__.__name__).get_logger()
        self.source = Config().DW_DATABASE_URL
        self.llm_service = LLMService(source=self.source)

        # Initialize session state for analysis description
        if "analysis_description" not in st.session_state:
            st.session_state["analysis_description"] = None

    def show_database_overview(self):
        """Display the database overview in the sidebar."""
        st.sidebar.title("Database Overview")
        try:
            if st.session_state["analysis_description"] is None:
                analysis_description = self.llm_service.generate_analysis_description()
                st.session_state["analysis_description"] = analysis_description

            with st.sidebar.expander("Details and suggested prompts", expanded=False):
                st.markdown(
                    f"<div style='width: auto; word-wrap: break-word;'>{st.session_state['analysis_description']}</div>",
                    unsafe_allow_html=True,
                )
        except Exception as e:
            self.logger.error(f"Error generating analysis description: {str(e)}")
            st.sidebar.error(f"Error generating analysis description: {str(e)}")

    def run(self):
        """Run the main Streamlit application."""
        st.title("Talk to Your Data")
        st.subheader("Interact with your data using natural language queries")

        # Display the database overview in the sidebar
        self.show_database_overview()

        # Input for natural language query
        prompt = st.text_input(
            "Enter Your Query:",
            placeholder="e.g., Show total sales by product category",
        )

        if st.button("Submit Query"):
            if prompt:
                try:
                    # Get the pure Python code from the LLM response
                    python_code = self.llm_service.process_data_analysis(prompt)

                    # Execute the generated Python code
                    exec(python_code)

                    # Show the generated Python code at the bottom of the page
                    with st.expander("View Generated Python Code", expanded=False):
                        st.write("## Generated Python Code")
                        st.code(python_code, language="python")

                except Exception as e:
                    # Show the generated Python code at the bottom of the page
                    with st.expander("View Generated Python Code", expanded=False):
                        st.write("## Generated Python Code")
                        st.code(python_code, language="python")

                    self.logger.error(
                        f"Error processing query: {str(e)}", exc_info=True
                    )
                    st.warning(f"Error processing query, please try again.")
            else:
                st.warning("Please enter a query.")
