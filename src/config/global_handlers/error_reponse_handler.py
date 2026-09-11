from fastapi.responses import JSONResponse

def error_response_handler(message: str) -> JSONResponse:

    return JSONResponse(
        status_code=500,
        content={
            # "error": exc.error_code,
            "message": message,
        },
    )
