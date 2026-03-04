from mas_engine import ingest_pdf, ask_ai
import streamlit as st
from mas_engine import ask_ai
from crawler import crawl_url
from pypdf import PdfReader
import docx
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


st.set_page_config(page_title="CSC AI Assistant", layout="wide")

st.title("CSC AI Legal & Service Assistant")

st.write(
"""
This assistant answers questions related to:
• CSC services  
• government schemes  
• document requirements  
• service legality  
"""
)

model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_FILE = "vector_store.index"
TEXT_FILE = "texts.pkl"


# -----------------------
# Knowledge ingestion
# -----------------------

def add_to_vector_store(text):

    chunks = [text[i:i+500] for i in range(0, len(text), 500)]

    embeddings = model.encode(chunks)

    dim = embeddings.shape[1]

    try:

        index = faiss.read_index(VECTOR_FILE)

        with open(TEXT_FILE, "rb") as f:
            texts = pickle.load(f)

    except:

        index = faiss.IndexFlatL2(dim)

        texts = []

    index.add(np.array(embeddings))

    texts.extend(chunks)

    faiss.write_index(index, VECTOR_FILE)

    with open(TEXT_FILE, "wb") as f:

        pickle.dump(texts, f)


# -----------------------
# Upload PDF
# -----------------------

uploaded_pdf = st.file_uploader(
    "Upload Knowledge PDF",
    type=["pdf"]
)

if uploaded_pdf:

    reader = PdfReader(uploaded_pdf)

    text = ""

    for page in reader.pages:

        text += page.extract_text()

    add_to_vector_store(text)

    st.success("PDF knowledge added successfully")


# -----------------------
# Upload DOCX
# -----------------------

uploaded_docx = st.file_uploader(
    "Upload DOCX file",
    type=["docx"]
)

if uploaded_docx:

    doc = docx.Document(uploaded_docx)

    text = ""

    for para in doc.paragraphs:

        text += para.text

    add_to_vector_store(text)

    st.success("DOCX knowledge added successfully")


# -----------------------
# Website ingestion
# -----------------------

url = st.text_input("Enter website URL to ingest")

if st.button("Ingest Website"):

    if url:

        text = crawl_url(url)

        add_to_vector_store(text)

        st.success("Website knowledge added")


# -----------------------
# Ask Question
# -----------------------

st.subheader("Ask CSC AI")

query = st.text_input("Enter your question")

if st.button("Ask"):

    if query:

        answer = ask_ai(query)

        st.write(answer)

