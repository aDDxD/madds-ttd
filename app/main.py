import plotly.express as px
import streamlit as st
from app.services.prompt_service import process_query

# Set Streamlit page configuration
st.set_page_config(layout="wide")

st.title("Talk to Your Data")

# Input prompt from the user
prompt = st.text_input("Enter your query:")

if st.button("Submit Query"):
    if prompt:
        try:
            # Directly call the process_query function
            result_df, sql_query, visualization_suggestions = process_query(prompt)

            st.write("### SQL Query:")
            st.text(sql_query)

            st.write("### Data Result:")
            st.dataframe(result_df)

            st.write("### Visualizations:")
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

        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
    else:
        st.warning("Please enter a query.")
