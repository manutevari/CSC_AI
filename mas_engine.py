import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_FILE = "vector_store.index"
TEXT_FILE = "texts.pkl"


def retrieve_context(question, k=5):

    index = faiss.read_index(VECTOR_FILE)

    with open(TEXT_FILE, "rb") as f:
        texts = pickle.load(f)

    q_embedding = model.encode([question])

    D, I = index.search(np.array(q_embedding), k)

    results = [texts[i] for i in I[0]]

    return " ".join(results)


def ask_ai(question):

    context = retrieve_context(question)

    answer = f"""
Based on CSC guidelines and available knowledge:

Question:
{question}

Relevant Information:
{context}

Conclusion:
The answer should follow CSC policies and legal service guidelines.
"""

    return answer
