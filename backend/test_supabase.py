from supabase_client import supabase

response = supabase.table("transactions").select("*").execute()

print(response)