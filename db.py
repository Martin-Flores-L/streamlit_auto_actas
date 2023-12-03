import streamlit as st
from supabase import create_client, Client

# streamlit_app.py

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def run_query():
    return supabase.table("actas").select("*").execute()

rows = run_query()

# Print results.

def show_data():
    for row in rows:
        st.write("Got lookup: ", row["id"], row["OC"], row['Proyecto'])

    
