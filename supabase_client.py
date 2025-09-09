from supabase import create_client, Client

SUPABASE_URL = "https://zxtqfcmsiaguupigzdey.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4dHFmY21zaWFndXVwaWd6ZGV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcyMzIwOTUsImV4cCI6MjA2MjgwODA5NX0.tyZPbbe5cnROQ8IyrsTCCgFT05f5WFrrjDAeNmpQES0"

def get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
