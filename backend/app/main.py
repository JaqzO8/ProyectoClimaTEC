import uuid
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from ipaddress import ip_address
from time import monotonic
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from app.api.v1.endpoints import _provider
from app.api.v1.endpoints import router as v1_router
from app.core.config import settings
from app.domain.models import ErrorDetail, ErrorResponse
from app.infrastructure.logging import logger, setup_logging
from app.infrastructure.open_meteo import OpenMeteoError
from app.infrastructure.rate_limit import RateLimiter

rate_limiter = RateLimiter()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    setup_logging(settings.LOG_LEVEL)
    logger.info("backend_starting", version=settings.APP_VERSION, env=settings.APP_ENV)
    try:
        yield
    finally:
        await _provider.aclose()
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
    allow_methods=["GET"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


# Security & Request-ID Middleware
@app.middleware("http")
async def security_and_request_id_middleware(
    request: Request, call_next: Callable[[Request], Any]
) -> Response:
    req_id = str(uuid.uuid4())
    request.state.request_id = req_id
    started = monotonic()
    address = request.client.host if request.client else "unknown"
    if settings.TRUST_ALB_HEADERS and request.headers.get("x-forwarded-for"):
        # AWS ALB append mode: the rightmost address is added by our load balancer.
        # Enable only where security groups restrict ingress to that ALB.
        try:
            address = str(ip_address(request.headers["x-forwarded-for"].split(",")[-1].strip()))
        except ValueError:
            pass  # Keep the actual peer address when a header is malformed.
    if (
        settings.RATE_LIMIT_ENABLED
        and request.url.path.startswith(settings.API_V1_PREFIX)
        and not rate_limiter.allow(
            address,
            settings.RATE_LIMIT_REQUESTS,
            settings.RATE_LIMIT_WINDOW_SECONDS,
        )
    ):
        response: Response = JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "Demasiadas solicitudes. Inténtalo de nuevo más tarde.",
                    "request_id": req_id,
                }
            },
            headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)},
        )
    else:
        response = await call_next(request)

    response.headers["X-Request-ID"] = req_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    logger.info(
        "request_completed",
        request_id=req_id,
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration_ms=round((monotonic() - started) * 1000, 2),
    )
    return response


# Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.warning("validation_error", path=request.url.path, request_id=req_id)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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
    logger.error(
        "internal_error", path=request.url.path, error_type=type(exc).__name__, request_id=req_id
    )
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
@app.exception_handler(OpenMeteoError)
async def provider_exception_handler(request: Request, exc: OpenMeteoError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                code=exc.code, message=exc.message, request_id=request.state.request_id
            )
        ).model_dump(),
    )


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "backend",
        "version": settings.APP_VERSION,
        "branch": "PruebaRama",
    }


@app.get("/ready", tags=["System"])
async def readiness_check() -> dict[str, str]:
    return {
        "status": "ready",
        "service": "backend",
    }


# Include V1 Router
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
