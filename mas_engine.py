import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_FILE = "vector_store.index"
TEXT_FILE = "texts.pkl"


# -----------------------------
# CSC BUILT-IN KNOWLEDGE
# -----------------------------

CSC_SERVICES = {

"aadhaar update":
"Aadhaar update services include demographic and biometric updates through authorized CSC operators.",

"pmegp":
"PMEGP is a government scheme supporting micro enterprises with credit linked subsidy.",

"fssai":
"FSSAI registration and licensing can be applied through CSC portals.",

"pan card":
"PAN card applications can be submitted through CSC using NSDL or UTI portals."

}


# -----------------------------
# PDF ingestion
# -----------------------------

def ingest_pdf(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text += page_text


    chunks = [text[i:i+500] for i in range(0,len(text),500)]

    embeddings = model.encode(chunks)

    dim = embeddings.shape[1]


    try:

        index = faiss.read_index(VECTOR_FILE)

        with open(TEXT_FILE,"rb") as f:

            texts = pickle.load(f)

    except:

        index = faiss.IndexFlatL2(dim)

        texts = []


    index.add(np.array(embeddings))

    texts.extend(chunks)


    faiss.write_index(index,VECTOR_FILE)

    with open(TEXT_FILE,"wb") as f:

        pickle.dump(texts,f)


# -----------------------------
# retrieve context
# -----------------------------

def retrieve_context(question,k=3):

    try:

        index = faiss.read_index(VECTOR_FILE)

        with open(TEXT_FILE,"rb") as f:

            texts = pickle.load(f)

        q_embedding = model.encode([question])

        D,I = index.search(np.array(q_embedding),k)

        results = [texts[i] for i in I[0]]

        return " ".join(results)

    except:

        return ""


# -----------------------------
# guardrails
# -----------------------------

def guardrail(question):

    banned = ["hack","fraud","illegal bypass"]

    q = question.lower()

    for word in banned:

        if word in q:

            return False

    return True


# -----------------------------
# classification
# -----------------------------

def classify(question):

    q = question.lower()

    if "fee" in q or "charge" in q:

        return "pricing"

    elif "document" in q:

        return "documents"

    elif "legal" in q or "allowed" in q:

        return "legal"

    elif "apply" in q or "process" in q:

        return "process"

    else:

        return "general"


# -----------------------------
# main AI logic
# -----------------------------

def ask_ai(question):

    if guardrail(question) == False:

        return "This system only answers legal CSC service questions."


    category = classify(question)

    context = retrieve_context(question)


    # check built-in CSC knowledge

    for key in CSC_SERVICES:

        if key in question.lower():

            return CSC_SERVICES[key]


    if category == "pricing":

        return f"""
CSC pricing must follow official service charges.

Context:
{context}

Always follow CSC SPV or UIDAI pricing guidelines.
"""


    elif category == "legal":

        return f"""
CSC operators must follow Digital Seva policies.

Context:
{context}

Operating outside approved services may not be legally permitted.
"""


    elif category == "documents":

        return f"""
Document requirements depend on the service.

Context:
{context}
"""


    elif category == "process":

        return f"""
Service application process explanation.

Context:
{context}
"""


    else:

        return f"""
Relevant information found:

{context}

⚠ Always verify with official CSC portals.
"""
