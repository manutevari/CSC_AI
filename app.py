import streamlit as st
from database import get_connection
from mas_engine import ask_ai

st.set_page_config(page_title="CSC Enterprise AI Assistant")

st.title("CSC Enterprise AI Assistant")

# database test
try:
    conn = get_connection()
    st.success("Database connected successfully")
except Exception as e:
    st.error("Database connection failed")
    st.write(e)

query = st.text_input("Ask your question")

if query:
    response = ask_ai(query)
    st.write(response)
