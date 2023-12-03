import streamlit as st
from supabase import create_client, Client

# Initialize connection.

class Supabase_db():
    
    def __init__(self, url, key):
        self.url = url
        self.key = key

    def __str__(self):
        return 'Usuario {}'.format(self.nombre)
    
    #function to connect to supabase
    @st.cache_resource
    def init_connection(self):
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)

    #function to run query in supabase
    def run_query(self):
        return supabase.table("actas").select("*").execute()

    #function to save dataframe in supabase table
    def save_supabase(self, dataframe):
        self.dataframe = dataframe
        supabase.table("mytable").insert(self.dataframe).execute()

    