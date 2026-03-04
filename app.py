import streamlit as st
from mas_engine import ingest_pdf, ask_ai
from crawler import crawl_url

st.title("CSC AI Knowledge Assistant")

# Upload PDF
uploaded_file = st.file_uploader(
    "Upload Knowledge PDF",
    type=["pdf"]
)

if uploaded_file:
    ingest_pdf(uploaded_file)
    st.success("PDF added to knowledge base")

# URL ingestion
url = st.text_input("Enter website URL")

if st.button("Ingest URL"):
    if url:
        text = crawl_url(url)
        ingest_pdf(text)
        st.success("Website content added")

# Ask question
query = st.text_input("Ask your question")

if query:
    answer = ask_ai(query)
    st.write(answer)
