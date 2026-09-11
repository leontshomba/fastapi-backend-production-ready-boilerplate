from fastapi import FastAPI
from dotenv import load_dotenv

from src.config.settings import settings

from src.middlewares.auth_middleware import AuthenticationMiddleware

from src.routes import docs_routes
from src.lib.swagger_auth import custom_openapi

load_dotenv()

app = FastAPI(
    title= "FastAPI Production Ready Boilerplate",
    version= "0.1.0"
)

# FOR DEVELOPMENT COMMODITY
if settings.ENVIRONMENT == "development":
    app.openapi = lambda: custom_openapi(app)

app.add_middleware(AuthenticationMiddleware)

@app.get("/api/health_check")
def health_check():
    return {
        "success": True,
        "Message": "FROM HEALTH CHECK: Server is runningn successfully"
    }

app.include_router(
    docs_routes.router,
    prefix="/api/documents",
    tags=["Documents"]
)