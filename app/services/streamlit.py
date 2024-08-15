import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(layout="wide")

# URL of the FastAPI backend
API_URL = "http://localhost:8000/process_query/"

st.title("Talk to Your Data")

# Input prompt from the user
prompt = st.text_input("Enter your query:")

if st.button("Submit Query"):
    if prompt:
        # Send the prompt to the FastAPI backend
        response = requests.post(API_URL, json={"query": prompt})

        if response.status_code == 200:
            data = response.json()
            result_df = pd.DataFrame(data["result"])
            visualization_suggestions = data["visualization_suggestions"]

            st.write("### SQL Query:")
            st.text(data["sql_query"])

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

        else:
            st.error("There was an error processing your query. Please try again.")
    else:
        st.warning("Please enter a query.")
