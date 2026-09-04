from fastapi import FastAPI
from dotenv import load_dotenv

from src.routes import docs_routes

load_dotenv()

app = FastAPI(
    title= "FastAPI Production Ready Boilerplate",
    version= "0.1.0"
)

app.include_router(
    docs_routes.router,
    prefix="/documents",
    tags=["Documents"]
)