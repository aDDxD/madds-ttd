import streamlit as st

from app.core.llm.llm_service import LLMService
from app.core.utils.config import Config


class StreamlitApp:
    def __init__(self):
        # Set Streamlit page configuration
        st.set_page_config(layout="wide")

        # Initialize the LLMService with your database URL
        self.database_url = (
            Config.DW_DATABASE_URL
        )  # You can replace this with other databases as needed
        self.llm_service = LLMService(database_url=self.database_url)

        # Initialize session state for database overview
        if "analysis_description" not in st.session_state:
            st.session_state["analysis_description"] = None

    def show_database_overview(self):
        """Displays the database overview when the app starts."""
        st.write("### Database Overview")
        try:
            if st.session_state["analysis_description"] is None:
                analysis_description = self.llm_service.generate_analysis_description()
                st.session_state["analysis_description"] = analysis_description

            st.markdown(
                f"<div style='width: auto; word-wrap: break-word;'>{st.session_state['analysis_description']}</div>",
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Error generating analysis description: {str(e)}")

    def run(self):
        """Runs the main Streamlit application."""
        st.title("Talk to Your Data")

        # Display the database overview once when the app starts
        self.show_database_overview()

        # Input prompt from the user
        prompt = st.text_input("Enter your query:")

        if st.button("Submit Query"):
            if prompt:
                try:
                    # Get the structured response from LLM
                    structured_response = self.llm_service.process_data_analysis(prompt)

                    # Display the raw response for debugging
                    st.write("### Raw LLM Response:")
                    st.text_area("LLM Response", structured_response, height=400)

                    # Display the structured data for debugging
                    st.write("### Extracted Data:")
                    for i, item in enumerate(structured_response.visualizations):
                        st.write(f"**Visualization {i + 1}:**")
                        st.write(f"- **Description:** {item.description}")
                        st.write(f"- **SQL Query:** {item.sql_query}")
                        st.write(f"- **Visualization Type:** {item.visualization}")

                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
            else:
                st.warning("Please enter a query.")
