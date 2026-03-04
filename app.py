import streamlit as st
from mas_engine import ingest_pdf, ask_ai
from crawler import crawl_url

st.set_page_config(page_title="CSC AI Assistant")

st.title("CSC AI Knowledge Assistant")


uploaded_file = st.file_uploader("Upload CSC knowledge PDF", type=["pdf"])

if uploaded_file:

    ingest_pdf(uploaded_file)

    st.success("Knowledge added")


url = st.text_input("Enter website URL")

if st.button("Ingest Website"):

    if url:

        text = crawl_url(url)

        ingest_pdf(text)

        st.success("Website knowledge added")


query = st.text_input("Ask your CSC question")

if st.button("Ask"):

    if query:

        answer = ask_ai(query)

        st.write(answer)
