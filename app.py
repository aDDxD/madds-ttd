import streamlit as st

# Set a title for the app
st.title("Simple Streamlit App")

# Create an input box
name = st.text_input("Enter your name:")

# Create a button
if st.button("Greet"):
    st.write(f"Hello, {name}!")
