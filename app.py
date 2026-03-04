import streamlit as st
from mas_engine import ingest_pdf, ask_ai
from crawler import crawl_url


st.set_page_config(page_title="CSC AI Assistant", layout="wide")

st.title("CSC AI Legal & Service Assistant")

st.write(
"""
This assistant answers questions related to:

• CSC services  
• government schemes  
• document requirements  
• CSC legality  
"""
)


# -----------------------
# Upload PDF
# -----------------------

uploaded_pdf = st.file_uploader(
    "Upload CSC Knowledge PDF",
    type=["pdf"]
)

if uploaded_pdf:

    ingest_pdf(uploaded_pdf)

    st.success("PDF knowledge added to system")


# -----------------------
# Website ingestion
# -----------------------

url = st.text_input("Enter government website URL")

if st.button("Ingest Website"):

    if url:

        text = crawl_url(url)

        ingest_pdf(text)

        st.success("Website knowledge added")


# -----------------------
# Ask Question
# -----------------------

st.subheader("Ask CSC AI")

query = st.text_input("Enter your question")

if st.button("Ask AI"):

    if query:

        answer = ask_ai(query)

        st.write(answer)
