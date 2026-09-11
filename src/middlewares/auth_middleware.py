from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from dotenv import load_dotenv
import os

from src.config.global_handlers.error_reponse_handler import error_response_handler

load_dotenv()

SUPABASE_JWT_TOKEN = os.getenv("SUPABASE_JWT_TOKEN")
SUPABASE_JWT_ALGORITHM = "HS256"

public_routes = ("/public", "webhooks")


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Whitelist Public Routes
        if request.url.path in [
            "/docs",
            "/openapi.json",
            "/redoc",
        ] or request.url.path.startswith(public_routes):
            return await call_next(request)

        # Get Authorization Header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            print("Auth Error: MISSING TOKEN")
            return error_response_handler("Missing Token")

        # Get the token
        token = auth_header.split(" ")[1]
        # token_log = f"{str(token)[:10]}...[REDACTED]"

        try:
            # print(f"The token from FastAPI: {token}")
            payload = jwt.decode(
                token,
                SUPABASE_JWT_TOKEN,
                algorithms=[SUPABASE_JWT_ALGORITHM],
                audience="authenticated",
                leeway=60,  # (Allows a 60-second time difference)
            )

            if not payload.get("sub"):
                print("Auth Error: User ID not found")
                return error_response_handler("User ID not found")

        except jwt.ExpiredSignatureError:
            print("Auth eror: TOKEN EXPIRED")
            return error_response_handler("Token expired")
        except jwt.InvalidTokenError:
            print("Auth error: INVALID TOKEN")
            return error_response_handler("Invalid token")

        return await call_next(request)
