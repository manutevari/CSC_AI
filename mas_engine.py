import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

VECTOR_FILE = "vector_store.index"
TEXT_FILE = "texts.pkl"


# -------------------------
# Retrieve context
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
# Question classification
# -------------------------

def classify_question(question):

    q = question.lower()

    if "fee" in q or "charge" in q or "price" in q:
        return "pricing"

    elif "document" in q or "required" in q:
        return "documents"

    elif "legal" in q or "allowed" in q or "law" in q:
        return "legal"

    elif "apply" in q or "registration" in q:
        return "process"

    elif "service" in q or "csc" in q:
        return "general"

    else:
        return "unknown"


# -------------------------
# Guardrail system
# -------------------------

def guardrail_filter(question):

    q = question.lower()

    banned = [
        "hack",
        "illegal activity",
        "fraud",
        "bypass government"
    ]

    for word in banned:

        if word in q:
            return False

    return True


# -------------------------
# Main AI Engine
# -------------------------

def ask_ai(question):

    # guardrail check
    allowed = guardrail_filter(question)

    if allowed == False:

        return """
This query violates system safety rules.

The CSC AI assistant only answers questions related to:
• CSC services
• government schemes
• service guidelines
• documentation requirements
"""

    # classify question
    category = classify_question(question)

    context = retrieve_context(question)

    # reasoning logic

    if category == "pricing":

        answer = f"""
CSC pricing rules depend on official guidelines.

Relevant information:
{context}

Conclusion:
CSC VLEs should follow the official service charges defined by CSC SPV or UIDAI.
Charging beyond approved service fees may violate service rules unless extra optional assistance is provided.
"""

    elif category == "documents":

        answer = f"""
Document requirements depend on the specific CSC service.

Relevant information:
{context}

Conclusion:
Applicants must provide valid identity and supporting documents as defined by the scheme guidelines.
Always verify requirements on the official CSC or government portal.
"""

    elif category == "legal":

        answer = f"""
Legal interpretation based on CSC operational guidelines.

Relevant information:
{context}

Conclusion:
CSC operators must comply with Digital Seva and government policies.
Activities outside approved service guidelines may not be legally permitted.
"""

    elif category == "process":

        answer = f"""
Service application process explanation.

Relevant information:
{context}

Conclusion:
Most CSC services are applied through the Digital Seva portal using VLE credentials.
Follow official workflow defined by CSC SPV.
"""

    elif category == "general":

        answer = f"""
CSC service explanation.

Relevant information:
{context}

Conclusion:
Common Service Centers provide digital public services including Aadhaar updates,
government scheme applications, financial services, and utility services.
"""

    else:

        answer = f"""
The system could not classify the question precisely.

Relevant information:
{context}

Please refine your question related to CSC services or government schemes.
"""

    # final guardrail message
    answer += """

⚠ Guardrail Notice:
This answer is generated from the CSC knowledge base.
Always verify official guidelines from CSC or the relevant government portal.
"""

    return answer
