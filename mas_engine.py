from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings()

def ask_ai(question):

    vector_db = FAISS.load_local("vector_store", embedding)

    docs = vector_db.similarity_search(question, k=3)

    context = " ".join([doc.page_content for doc in docs])

    return context

