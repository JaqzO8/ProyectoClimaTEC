import uuid
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api.v1.endpoints import router as v1_router
from app.core.config import settings
from app.domain.models import ErrorDetail, ErrorResponse
from app.infrastructure.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging(settings.LOG_LEVEL)
    logger.info("backend_starting", version=settings.APP_VERSION, env=settings.APP_ENV)
    yield
    logger.info("backend_stopping")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security & Request-ID Middleware
@app.middleware("http")
async def security_and_request_id_middleware(
    request: Request, call_next: Callable[[Request], Any]
) -> Response:
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = req_id

    response: Response = await call_next(request)

    response.headers["X-Request-ID"] = req_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.warning("validation_error", path=request.url.path, errors=exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Parámetros de solicitud no válidos.",
                request_id=req_id,
            )
        ).model_dump(),
    )


# Generic Exception Handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error("internal_error", path=request.url.path, error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="Ocurrió un error interno en el servidor.",
                request_id=req_id,
            )
        ).model_dump(),
    )


# Health & Ready endpoints
@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "backend",
        "version": settings.APP_VERSION,
    }


@app.get("/ready", tags=["System"])
async def readiness_check() -> dict[str, str]:
    return {
        "status": "ready",
        "service": "backend",
    }


# Include V1 Router
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
