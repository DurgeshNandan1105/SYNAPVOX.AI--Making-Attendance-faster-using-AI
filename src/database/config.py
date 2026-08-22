import streamlit as st
from supabase import create_client, Client


def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"].strip().rstrip('/')
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)


supabase: Client = get_supabase_client()