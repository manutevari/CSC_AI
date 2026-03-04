import streamlit as st
from mas_engine import ask_ai

st.title("CSC Enterprise AI Assistant")

query = st.text_input("Ask your question")

if query:
    response = ask_ai(query)
    st.write(response)
