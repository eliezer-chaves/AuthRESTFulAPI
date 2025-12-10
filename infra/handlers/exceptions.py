from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Handler para HTTPException (401, 404, 409, 500 etc.)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "error"),
            "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "An error occurred.")
        }
    )

# Handler para erros de validação (422)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status_code": 422,
            "error": "validation_error",
            "message": "Invalid request data.",
            "details": exc.errors()
        }
    )
