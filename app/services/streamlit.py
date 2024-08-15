import streamlit as st

st.title("Welcome to My Streamlit App")

prompt = st.text_input("Enter your prompt:")

if st.button("Submit"):
    st.write(f"Your prompt was: {prompt}")
