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
    @staticmethod
    @st.cache_resource
    def init_connection():
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]

        return create_client(url, key)

    #function to run query in supabase
    def run_query(self, conn):
        self.conn = conn
        return self.conn.table("actas").select("*").execute()

    #function to save dataframe in supabase table
    def save_supabase(self, conn, dataframe):

        self.dataframe = dataframe

        conn.table("actas").insert(self.dataframe).execute()
        return "Data saved in Supabase"

    