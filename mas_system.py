from datetime import datetime, UTC
from database import cursor, conn
from retrieval import retrieve_context
from router import supervisor
from llm import llm


def ask(query):

    route = supervisor(query)

    context = retrieve_context(query)

    prompt = f"""
Answer the question using the context.

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    answer = response.content

    cursor.execute(
        """
        INSERT INTO audit_logs(query, source_used, confidence, created_at)
        VALUES (%s,%s,%s,%s)
        """,
        (query, route, 0.9, datetime.now(UTC))
    )

    conn.commit()

    return answer
