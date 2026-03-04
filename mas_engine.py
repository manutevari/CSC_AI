import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader


model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_FILE = "vector_store.index"
TEXT_FILE = "texts.pkl"


# -----------------------------
# PDF INGESTION
# -----------------------------

def ingest_pdf(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text


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


# -----------------------------
# RETRIEVE CONTEXT
# -----------------------------

def retrieve_context(question, k=4):

    try:

        index = faiss.read_index(VECTOR_FILE)

        with open(TEXT_FILE, "rb") as f:
            texts = pickle.load(f)

        q_embedding = model.encode([question])

        D, I = index.search(np.array(q_embedding), k)

        results = [texts[i] for i in I[0]]

        return " ".join(results)

    except:

        return "Knowledge base is empty. Please upload documents."


# -----------------------------
# CLASSIFY QUESTION
# -----------------------------

def classify_question(question):

    q = question.lower()

    if "fee" in q or "charge" in q or "price" in q:
        return "pricing"

    elif "document" in q or "required" in q:
        return "documents"

    elif "legal" in q or "allowed" in q:
        return "legal"

    elif "apply" in q or "registration" in q:
        return "process"

    elif "service" in q or "csc" in q:
        return "general"

    else:
        return "unknown"


# -----------------------------
# GUARDRAILS
# -----------------------------

def guardrail_filter(question):

    banned = ["hack", "fraud", "illegal bypass"]

    q = question.lower()

    for word in banned:

        if word in q:
            return False

    return True


# -----------------------------
# MAIN AI ENGINE
# -----------------------------

def ask_ai(question):

    if guardrail_filter(question) == False:

        return """
This system only answers questions related to CSC services
and government schemes.
"""


    category = classify_question(question)

    context = retrieve_context(question)


    if category == "pricing":

        answer = f"""
CSC pricing must follow official service charges.

Relevant information:
{context}

Conclusion:
VLEs must follow CSC or UIDAI approved service fees.
"""

    elif category == "documents":

        answer = f"""
Document requirements depend on the service.

Relevant information:
{context}

Conclusion:
Applicants must provide valid identity documents.
"""

    elif category == "legal":

        answer = f"""
Legal interpretation based on CSC guidelines.

Relevant information:
{context}

Conclusion:
CSC operators must follow Digital Seva policies.
"""

    elif category == "process":

        answer = f"""
Service application process explanation.

Relevant information:
{context}

Conclusion:
Applications are usually processed via Digital Seva portal.
"""

    else:

        answer = f"""
Relevant information found:

{context}
"""

    answer += """

⚠ Guardrail Notice:
Always verify final details from official CSC portals.
"""

    return answer
