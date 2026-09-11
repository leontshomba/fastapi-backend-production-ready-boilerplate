import os
import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.settings import settings
from src.config.global_handlers.error_reponse_handler import error_response_handler

# 1. Configure your Supabase Project URL instead of a static token secret
JWKS_URL = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# 2. Initialize the JWK Client. 
# This object manages the in-memory cache automatically across requests.
jwks_client = jwt.PyJWKClient(JWKS_URL)

# Supabase modern asymmetric tokens use "EdDSA" or sometimes "RS256" depending on setup.
# Passing both ensures compatibility regardless of your project's precise key configuration.
SUPPORTED_ALGORITHMS = ["ES256", "EdDSA", "RS256"]

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
        token_log = f"{str(token)[:10]}...[REDACTED]"

        try:
            # 3. Resolve the signing key from the local cache.
            # This extracts the 'kid' header from the token, checks the local RAM cache,
            # and returns the correct public key instantly without network overhead.
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # 4. Decode and verify using the public key math
            payload = jwt.decode(
                token,
                signing_key.key,  # The public key object
                algorithms=SUPPORTED_ALGORITHMS,
                audience="authenticated",
                leeway=60,  # Allows a 60-second time difference
            )

            if not payload.get("sub"):
                print("Auth Error: User ID not found")
                return error_response_handler("User ID not found")

            print(f"User authenticated successfully: {token_log}")
            
            # Optional: Attach the payload or user_id to request state for downstream routes
            request.state.user = {
                "id": payload['sub'],
                "email": payload['email'],
                "email_verified": payload['user_metadata']['email_verified']
            }

            print(f"AYE UYU: {request.state.user}")

        except jwt.PyJWKClientError as e:
            # Triggered if the Supabase JWKS endpoint is entirely unreachable
            print(f"Auth error: JWKS FETCH FAILED: {str(e)}")
            return error_response_handler("Authentication service unavailable")
        except jwt.ExpiredSignatureError:
            print("Auth error: TOKEN EXPIRED")
            return error_response_handler("Token expired")
        except jwt.InvalidTokenError as e:
            # Catches signature mismatches, invalid structures, or altered claims
            print(f"Auth error: INVALID TOKEN: {str(e)}")
            return error_response_handler("Invalid token")

        return await call_next(request)
