import uuid

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse

from app.application.use_cases import WeatherUseCases
from app.domain.models import (
    CurrentWeatherResponse,
    DailyForecastResponse,
    ErrorDetail,
    ErrorResponse,
    HourlyForecastResponse,
    LocationSearchResult,
    PrecipitationUnit,
    TemperatureUnit,
    WeatherOverview,
    WindSpeedUnit,
)
from app.infrastructure.open_meteo import OpenMeteoError, OpenMeteoWeatherProvider

router = APIRouter()
_provider = OpenMeteoWeatherProvider()
_use_cases = WeatherUseCases(provider=_provider)


def build_error_response(code: str, message: str, req_id: str | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST
        if code == "VALIDATION_ERROR"
        else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ErrorDetail(code=code, message=message, request_id=req_id)
        ).model_dump(),
    )


@router.get(
    "/locations/search",
    response_model=LocationSearchResult,
    responses={
        400: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
async def search_locations(
    request: Request,
    q: str = Query(
        ..., min_length=2, max_length=120, description="Término de búsqueda de ubicación"
    ),
    country_code: str | None = Query(
        None, min_length=2, max_length=2, description="Código ISO alpha-2"
    ),
    language: str = Query("es", description="Idioma de los resultados"),
    limit: int = Query(10, ge=1, le=20, description="Límite de resultados"),
) -> LocationSearchResult | JSONResponse:
    try:
        return await _use_cases.search_locations(
            q=q, country_code=country_code, language=language, limit=limit
        )
    except OpenMeteoError as exc:
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(code=exc.code, message=exc.message, request_id=req_id)
            ).model_dump(),
        )


@router.get(
    "/weather/current",
    response_model=CurrentWeatherResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
async def get_current_weather(
    request: Request,
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitud (-90 a 90)"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitud (-180 a 180)"),
    temperature_unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS),
    wind_speed_unit: WindSpeedUnit = Query(WindSpeedUnit.KMH),
    precipitation_unit: PrecipitationUnit = Query(PrecipitationUnit.MM),
    timezone: str = Query("auto"),
) -> CurrentWeatherResponse | JSONResponse:
    try:
        return await _use_cases.get_current_weather(
            latitude=latitude,
            longitude=longitude,
            temp_unit=temperature_unit,
            wind_unit=wind_speed_unit,
            precip_unit=precipitation_unit,
            timezone=timezone,
        )
    except OpenMeteoError as exc:
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(code=exc.code, message=exc.message, request_id=req_id)
            ).model_dump(),
        )


@router.get(
    "/weather/hourly",
    response_model=HourlyForecastResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
async def get_hourly_forecast(
    request: Request,
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    hours: int = Query(24, ge=1, le=72),
    temperature_unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS),
    wind_speed_unit: WindSpeedUnit = Query(WindSpeedUnit.KMH),
    precipitation_unit: PrecipitationUnit = Query(PrecipitationUnit.MM),
    timezone: str = Query("auto"),
) -> HourlyForecastResponse | JSONResponse:
    try:
        return await _use_cases.get_hourly_forecast(
            latitude=latitude,
            longitude=longitude,
            hours=hours,
            temp_unit=temperature_unit,
            wind_unit=wind_speed_unit,
            precip_unit=precipitation_unit,
            timezone=timezone,
        )
    except OpenMeteoError as exc:
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(code=exc.code, message=exc.message, request_id=req_id)
            ).model_dump(),
        )


@router.get(
    "/weather/daily",
    response_model=DailyForecastResponse,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
async def get_daily_forecast(
    request: Request,
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    days: int = Query(7, ge=1, le=16),
    temperature_unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS),
    wind_speed_unit: WindSpeedUnit = Query(WindSpeedUnit.KMH),
    precipitation_unit: PrecipitationUnit = Query(PrecipitationUnit.MM),
    timezone: str = Query("auto"),
) -> DailyForecastResponse | JSONResponse:
    try:
        return await _use_cases.get_daily_forecast(
            latitude=latitude,
            longitude=longitude,
            days=days,
            temp_unit=temperature_unit,
            wind_unit=wind_speed_unit,
            precip_unit=precipitation_unit,
            timezone=timezone,
        )
    except OpenMeteoError as exc:
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(code=exc.code, message=exc.message, request_id=req_id)
            ).model_dump(),
        )


@router.get(
    "/weather/overview",
    response_model=WeatherOverview,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
async def get_weather_overview(
    request: Request,
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    temperature_unit: TemperatureUnit = Query(TemperatureUnit.CELSIUS),
    wind_speed_unit: WindSpeedUnit = Query(WindSpeedUnit.KMH),
    precipitation_unit: PrecipitationUnit = Query(PrecipitationUnit.MM),
    timezone: str = Query("auto"),
) -> WeatherOverview | JSONResponse:
    try:
        return await _use_cases.get_weather_overview(
            latitude=latitude,
            longitude=longitude,
            temp_unit=temperature_unit,
            wind_unit=wind_speed_unit,
            precip_unit=precipitation_unit,
            timezone=timezone,
        )
    except OpenMeteoError as exc:
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(code=exc.code, message=exc.message, request_id=req_id)
            ).model_dump(),
        )
