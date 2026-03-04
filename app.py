import streamlit as st
import psycopg2
import pandas as pd

from mas_system import ask
from crawler import smart_crawl
from knowledge import add_knowledge

st.set_page_config(page_title="CSC Enterprise AI Assistant", layout="wide")

st.title("CSC Enterprise AI Assistant")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Ask AI", "Knowledge", "Crawler", "Logs"]
)

# -------------------------------
# TAB 1 — ASK AI
# -------------------------------
with tab1:

    query = st.text_input("Ask question")

    if st.button("Ask"):

        if query.strip() == "":
            st.warning("Please enter a question")

        else:
            with st.spinner("AI thinking..."):

                answer = ask(query)

            st.success(answer)


# -------------------------------
# TAB 2 — ADD KNOWLEDGE
# -------------------------------
with tab2:

    text = st.text_area("Add knowledge")

    if st.button("Store Knowledge"):

        if text.strip() == "":
            st.warning("Please enter knowledge")

        else:

            add_knowledge(text)

            st.success("Knowledge added")


# -------------------------------
# TAB 3 — WEBSITE CRAWLER
# -------------------------------
with tab3:

    url = st.text_input("Website URL")

    if st.button("Crawl Website"):

        if url.startswith("http"):

            with st.spinner("Crawling website..."):

                smart_crawl(url, 20)

            st.success("Crawl completed")

        else:

            st.warning("Enter valid URL")


# -------------------------------
# TAB 4 — LOGS
# -------------------------------
with tab4:

    try:

        conn = psycopg2.connect(st.secrets["DB_URL"])

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT query, source_used, confidence, created_at
            FROM audit_logs
            ORDER BY created_at DESC
            LIMIT 20
            """
        )

        rows = cursor.fetchall()

        df = pd.DataFrame(
            rows,
            columns=["Query", "Agent Used", "Confidence", "Time"]
        )

        st.dataframe(df)

    except Exception as e:

        st.error("Could not load logs")
