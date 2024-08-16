import plotly.express as px
import streamlit as st

from app.core.config import Config
from app.core.llm_service import LLMService

# Set Streamlit page configuration
st.set_page_config(layout="wide")

st.title("Talk to Your Data")

# Initialize the LLMService with your database URL
database_url = (
    Config.DW_DATABASE_URL
)  # You can replace this with other databases as needed
llm_service = LLMService(database_url=database_url)

# Display the database analysis description with auto width and line breaks
st.write("### Database Overview")
try:
    analysis_description = llm_service.generate_analysis_description()
    st.markdown(
        f"<div style='width: auto; word-wrap: break-word;'>{analysis_description}</div>",
        unsafe_allow_html=True,
    )
except Exception as e:
    st.error(f"Error generating analysis description: {str(e)}")

# Input prompt from the user
prompt = st.text_input("Enter your query:")

if st.button("Submit Query"):
    if prompt:
        try:
            result_df, sql_query, visualization_suggestions, layout_suggestions = (
                llm_service.process_data_analysis(prompt)
            )

            st.write("### SQL Query:")
            st.text(sql_query)

            st.write("### Data Result:")
            st.dataframe(result_df)

            st.write("### Visualizations and Layout Suggestions:")
            for suggestion in visualization_suggestions:
                st.write(f"#### {suggestion.capitalize()} Visualization")
                if "bar" in suggestion.lower():
                    fig = px.bar(
                        result_df, x=result_df.columns[0], y=result_df.columns[1]
                    )
                elif "line" in suggestion.lower():
                    fig = px.line(
                        result_df, x=result_df.columns[0], y=result_df.columns[1]
                    )
                elif "scatter" in suggestion.lower():
                    fig = px.scatter(
                        result_df, x=result_df.columns[0], y=result_df.columns[1]
                    )
                elif "pie" in suggestion.lower():
                    fig = px.pie(
                        result_df,
                        names=result_df.columns[0],
                        values=result_df.columns[1],
                    )
                st.plotly_chart(fig)

            st.write("### Layout Suggestions:")
            for suggestion in layout_suggestions:
                st.write(f"- {suggestion}")

        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
    else:
        st.warning("Please enter a query.")
