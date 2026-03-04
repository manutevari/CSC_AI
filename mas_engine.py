import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_FILE = "vector_store.index"
TEXT_FILE = "texts.pkl"


# -------------------------
# PDF ingestion
# -------------------------

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


# -------------------------
# retrieve context
# -------------------------

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

        return "Knowledge base empty. Please upload documents."


# -------------------------
# question classification
# -------------------------

def classify_question(question):

    q = question.lower()

    if "fee" in q or "charge" in q:
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


# -------------------------
# guardrails
# -------------------------

def guardrail_filter(question):

    banned = [
        "hack",
        "fraud",
        "illegal bypass"
    ]

    q = question.lower()

    for word in banned:

        if word in q:
            return False

    return True


# -------------------------
# main AI logic
# -------------------------

def ask_ai(question):

    if guardrail_filter(question) == False:

        return """
This query violates safety rules.

The system only answers questions about:
• CSC services
• government schemes
• service legality
"""

    category = classify_question(question)

    context = retrieve_context(question)

    if category == "pricing":

        answer = f"""
CSC pricing must follow official service charges.

Relevant context:
{context}

Conclusion:
VLEs should follow CSC SPV or UIDAI approved pricing.
Extra charges beyond permitted service fees may violate rules.
"""

    elif category == "documents":

        answer = f"""
Document requirements depend on the service.

Relevant context:
{context}

Conclusion:
Applicants must provide valid identity and supporting documents.
"""

    elif category == "legal":

        answer = f"""
Legal interpretation based on CSC policies.

Relevant context:
{context}

Conclusion:
CSC operators must follow Digital Seva and government guidelines.
"""

    elif category == "process":

        answer = f"""
Service application process explanation.

Relevant context:
{context}

Conclusion:
Most services are applied through the Digital Seva portal.
"""

    else:

        answer = f"""
Relevant information found:

{context}

Please verify with official CSC guidelines.
"""

    answer += """

⚠ Guardrail Notice:
Always verify final information from official CSC portals.
"""

    return answer
