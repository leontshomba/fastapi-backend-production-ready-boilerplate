from dotenv import load_dotenv
import os
from supabase import create_client, Client

from src.config.settings import settings

supabase: Client = create_client(settings.SUPABASE_PROJECT_URL, settings.SUPABASE_SERVICE_ROLE_KEY)