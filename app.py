import streamlit as st
import psycopg2
import requests
from bs4 import BeautifulSoup
from datetime import datetime, UTC

from langchain_openai import ChatOpenAI
from tavily import TavilyClient

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(page_title="CSC AI Assistant", layout="wide")

st.title("CSC Enterprise AI Assistant")

# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------
# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------

try:

    conn = psycopg2.connect(st.secrets["DB_URL"])

    cursor = conn.cursor()

except Exception as e:

    st.error("Database connection failed")

    st.stop()

# -----------------------------------
# LLM
# -----------------------------------

llm = ChatOpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    model="gpt-4o-mini",
    temperature=0
)

# -----------------------------------
# ROUTER
# -----------------------------------

def supervisor(query):

    q = query.lower()

    if "loan" in q or "mudra" in q:
        return "loan"

    elif "gst" in q or "tax" in q:
        return "tax"

    elif "csc" in q or "aadhaar" in q:
        return "csc"

    elif "scheme" in q or "yojana" in q:
        return "scheme"

    else:
        return "general"

# -----------------------------------
# RETRIEVAL (simple)
# -----------------------------------

def retrieve_context(query):

    cursor.execute(
        """
        SELECT content
        FROM documents
        ORDER BY created_at DESC
        LIMIT 3
        """
    )

    rows = cursor.fetchall()

    return "\n".join([r[0] for r in rows])

# -----------------------------------
# KNOWLEDGE INGESTION
# -----------------------------------

def add_knowledge(text):

    cursor.execute(
        """
        INSERT INTO documents(content,source)
        VALUES(%s,%s)
        """,
        (text,"manual")
    )

    conn.commit()

# -----------------------------------
# WEBSITE CRAWLER
# -----------------------------------

def smart_crawl(url):

    try:

        r = requests.get(url, timeout=10)

        soup = BeautifulSoup(r.text,"lxml")

        for t in soup(["script","style","noscript"]):
            t.extract()

        text = soup.get_text(" ")

        cursor.execute(
            """
            INSERT INTO documents(content,source)
            VALUES(%s,%s)
            """,
            (text,url)
        )

        conn.commit()

    except:

        pass

# -----------------------------------
# MAIN MAS ANSWER FUNCTION
# -----------------------------------

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
        INSERT INTO audit_logs(query,source_used,confidence,created_at)
        VALUES(%s,%s,%s,%s)
        """,
        (query,route,0.9,datetime.now(UTC))
    )

    conn.commit()

    return answer

# -----------------------------------
# STREAMLIT UI
# -----------------------------------

tab1,tab2,tab3,tab4 = st.tabs(
["Ask AI","Knowledge","Crawler","Logs"]
)

# ASK AI

with tab1:

    query = st.text_input("Ask question")

    if st.button("Ask"):

        if query.strip()=="":
            st.warning("Enter question")

        else:

            with st.spinner("AI thinking..."):

                answer = ask(query)

            st.success(answer)

# ADD KNOWLEDGE

with tab2:

    text = st.text_area("Add knowledge")

    if st.button("Store"):

        if text.strip()=="":
            st.warning("Enter knowledge")

        else:

            add_knowledge(text)

            st.success("Knowledge stored")

# CRAWLER

with tab3:

    url = st.text_input("Website URL")

    if st.button("Crawl"):

        if url.startswith("http"):

            smart_crawl(url)

            st.success("Crawl completed")

        else:

            st.warning("Enter valid URL")

# LOGS

with tab4:

    cursor.execute(
        """
        SELECT query,source_used,confidence,created_at
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT 20
        """
    )

    rows = cursor.fetchall()

    for r in rows:

        st.write(r)

