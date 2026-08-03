from src.llm_factory.gemini.gemini_client import GeminiClient
from src.llm_factory.specialized_agents.rag_agents import get_query_trasformer
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

# gemini = GeminiClient()

# print("Process started...")

# transformer = get_query_trasformer("narrow")
# content = "Can you help me buy a residential property in downtown Seattle connected to fiber internet?"


# response = gemini.generate_content(instruction=transformer, content=content)

# print(response)

# print("Process finished.")

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("Starting...")

supabase: Client = create_client(SUPABASE_PROJECT_URL, SUPABASE_SERVICE_ROLE_KEY)

params = [
    "title",
    "description",
]

res = supabase.table("tasks").select(", ".join(params)).execute()

print(res.data)

print("Finished.")
