from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print("RequestContextMiddleware invoked")

        if request.url.path in ["public", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Get or Generate Request/Correlation IDs
        request_id = str(uuid.uuid4())
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())

        # Attach IDs to request context
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        response = await call_next(request)

        # Attach IDs to the api response
        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response


