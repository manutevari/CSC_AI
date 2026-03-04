import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle

model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_FILE = "vector_store.index"
TEXT_FILE = "texts.pkl"


def ingest_pdf(file):

    from pypdf import PdfReader

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text()

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


def ask_ai(question):

    index = faiss.read_index(VECTOR_FILE)

    with open(TEXT_FILE, "rb") as f:
        texts = pickle.load(f)

    q_embedding = model.encode([question])

    D, I = index.search(np.array(q_embedding), k=3)

    results = [texts[i] for i in I[0]]

    return " ".join(results)
