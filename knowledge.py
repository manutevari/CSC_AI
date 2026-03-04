knowledge_base = {
    "csc": "Common Service Center is a digital service delivery system.",
    "aadhaar": "CSC centers provide Aadhaar update and enrollment services.",
    "pmegp": "PMEGP loan scheme supports micro enterprises."
}


def search_knowledge(query):

    query = query.lower()

    for key in knowledge_base:
        if key in query:
            return knowledge_base[key]

    return None
