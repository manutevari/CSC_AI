from knowledge import search_knowledge

from mas_engine import ask_ai
def ask_ai(question):

    docs = search_knowledge(question)

    if docs:
        return docs
    else:
        return "No information found in knowledge base."

