from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # --- Default variables ---
    # App's settings
    PROJECT_NAME = "FastAPI Production Boilerplate"
    ENVIRONMENT = "production"  # Must be 'development' in local .env
    DEBUG: bool = False         # Must be True in local .env

    # --- Required variables (Must match keys in your .env) ---
    DATABASE_URL: str
    SUPABASE_PROJECT_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Pydantic Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra=True    # Ignores extra variables in .env without throwing errors
    )

# Global settings singleton
settings = Settings()