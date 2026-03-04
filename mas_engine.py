from knowledge import search_knowledge

def ask_ai(question):

    docs = search_knowledge(question)

    if docs:
        return docs
    else:
        return "No information found in knowledge base."
