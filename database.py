import psycopg2
import streamlit as st

# Connect using Streamlit secrets
conn = psycopg2.connect(st.secrets["DB_URL"])

cursor = conn.cursor()
