import asyncio
import logging
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient
from hypothesis import given
from hypothesis import strategies as st
from pydantic import SecretStr, ValidationError

from app.application.use_cases import WeatherUseCases
from app.core.config import Settings, settings
from app.domain.models import PrecipitationUnit, TemperatureUnit, WindSpeedUnit
from app.infrastructure.cache import TTLMemoryCache
from app.infrastructure.logging import setup_logging
from app.infrastructure.open_meteo import OpenMeteoError, OpenMeteoWeatherProvider
from app.infrastructure.rate_limit import RateLimiter
from app.main import app


def provider_with_key(client):
    return OpenMeteoWeatherProvider(
        client=client,
        config=Settings(
            OPEN_METEO_API_MODE="commercial",
            OPEN_METEO_API_KEY=SecretStr("test-value-not-a-real-key"),
        ),
    )


async def test_commercial_geocoding_key_and_cache(respx_mock, caplog):
    route = respx_mock.get("https://customer-geocoding-api.open-meteo.com/v1/search").respond(
        200, json={"results": []}
    )
    async with httpx.AsyncClient() as client:
        provider = provider_with_key(client)
        setup_logging()
        with caplog.at_level(logging.INFO):
            await provider.search_locations("Lima", country_code="pe")
            await provider.search_locations("Lima", country_code="pe")
        assert route.call_count == 1
        assert route.calls[0].request.url.params["apikey"] == "test-value-not-a-real-key"
        assert route.calls[0].request.url.params["countryCode"] == "PE"
        assert "test-value-not-a-real-key" not in caplog.text
        assert "test-value-not-a-real-key" not in repr(provider.config)
        assert all("apikey" not in key for key in provider.cache._cache)


async def test_commercial_forecast_key(respx_mock):
    route = respx_mock.get("https://customer-api.open-meteo.com/v1/forecast").respond(401)
    async with httpx.AsyncClient() as client:
        with pytest.raises(OpenMeteoError, match="no está disponible"):
            await provider_with_key(client).get_current(0, 0)
    assert route.call_count == 1
    assert route.calls[0].request.url.params["apikey"] == "test-value-not-a-real-key"


@pytest.mark.parametrize(
    "url,method,args",
    [
        (OpenMeteoWeatherProvider.GEOCODING_URL, "search_locations", ("Lima",)),
        (OpenMeteoWeatherProvider.FORECAST_URL, "get_current", (0, 0)),
    ],
)
@pytest.mark.parametrize(
    "status,code,calls",
    [
        (400, "WEATHER_PROVIDER_UNAVAILABLE", 1),
        (401, "WEATHER_PROVIDER_UNAVAILABLE", 1),
        (429, "RATE_LIMITED", 1),
        (500, "WEATHER_PROVIDER_UNAVAILABLE", 2),
    ],
)
async def test_provider_http_errors(respx_mock, url, method, args, status, code, calls):
    route = respx_mock.get(url).respond(status)
    async with httpx.AsyncClient() as client:
        with pytest.raises(OpenMeteoError) as error:
            await getattr(OpenMeteoWeatherProvider(client=client), method)(*args)
    assert error.value.code == code
    assert route.call_count == calls


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"error": True},
        {"timezone": "UTC", "current": {}},
        {"timezone": "UTC", "current": {"time": "2026-01-01T12:00", "temperature_2m": None}},
    ],
)
async def test_bad_forecast_is_not_fabricated_weather(respx_mock, payload):
    respx_mock.get(OpenMeteoWeatherProvider.FORECAST_URL).respond(200, json=payload)
    async with httpx.AsyncClient() as client:
        with pytest.raises(OpenMeteoError) as error:
            await OpenMeteoWeatherProvider(client=client).get_current(0, 0)
    assert error.value.code == "WEATHER_PROVIDER_BAD_RESPONSE"


async def test_malformed_json_and_connection_errors(respx_mock):
    route = respx_mock.get(OpenMeteoWeatherProvider.GEOCODING_URL)
    async with httpx.AsyncClient() as client:
        provider = OpenMeteoWeatherProvider(client=client)
        route.respond(200, text="not JSON")
        with pytest.raises(OpenMeteoError) as error:
            await provider.search_locations("Lima")
        assert error.value.code == "WEATHER_PROVIDER_BAD_RESPONSE"
        route.mock(side_effect=httpx.ConnectError("connection failed"))
        with pytest.raises(OpenMeteoError) as error:
            await provider.search_locations("Lima")
        assert error.value.code == "WEATHER_PROVIDER_UNAVAILABLE"


async def test_total_timeout(respx_mock):
    async def delayed(request):
        await asyncio.sleep(0.1)
        return httpx.Response(200, json={})

    respx_mock.get(OpenMeteoWeatherProvider.GEOCODING_URL).mock(side_effect=delayed)
    async with httpx.AsyncClient() as client:
        provider = OpenMeteoWeatherProvider(
            client=client, config=Settings(WEATHER_TIMEOUT_SECONDS=0.01)
        )
        with pytest.raises(OpenMeteoError) as error:
            await provider.search_locations("Lima")
        assert error.value.code == "WEATHER_PROVIDER_TIMEOUT"


async def test_ttl_is_respected(monkeypatch):
    now = [100.0]
    monkeypatch.setattr("app.infrastructure.cache.monotonic", lambda: now[0])
    cache = TTLMemoryCache(default_ttl=5)
    await cache.set("forecast", 1)
    await cache.set("geocoding", 2, ttl=30)
    now[0] = 106
    assert await cache.get("forecast") is None
    assert await cache.get("geocoding") == 2
    now[0] = 131
    assert await cache.get("geocoding") is None


def test_config_rejects_missing_key_invalid_limits_and_wildcard():
    for values in (
        {"OPEN_METEO_API_MODE": "commercial"},
        {"WEATHER_TIMEOUT_SECONDS": 0},
        {"CORS_ORIGINS": "*"},
    ):
        with pytest.raises(ValidationError):
            Settings(_env_file=None, **values)


@pytest.mark.parametrize(
    "query",
    [
        "latitude=nan&longitude=0",
        "latitude=inf&longitude=0",
        "latitude=0&longitude=-181",
        "latitude=0&longitude=0&temperature_unit=kelvin",
    ],
)
async def test_invalid_coordinates_units(async_client, query):
    response = await async_client.get(f"/api/v1/weather/current?{query}")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_api_provider_errors_and_headers(async_client, respx_mock):
    respx_mock.get(OpenMeteoWeatherProvider.FORECAST_URL).respond(500)
    response = await async_client.get(
        "/api/v1/weather/current?latitude=0&longitude=0", headers={"X-Request-ID": "untrusted"}
    )
    assert response.status_code == 502
    assert response.headers["X-Request-ID"] != "untrusted"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]


async def test_rate_limit_keeps_health_available(async_client, monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_REQUESTS", 1)
    monkeypatch.setattr("app.main.rate_limiter", RateLimiter())
    await async_client.get("/api/v1/weather/current")
    limited = await async_client.get("/api/v1/weather/current")
    assert limited.status_code == 429
    assert limited.headers["Retry-After"] == "60"
    assert (await async_client.get("/health")).status_code == 200


def test_limiter_resets_window(monkeypatch):
    now = [10]
    monkeypatch.setattr("app.infrastructure.rate_limit.monotonic", lambda: now[0])
    limiter = RateLimiter()
    assert limiter.allow("one", 1, 60)
    assert not limiter.allow("one", 1, 60)
    assert limiter.allow("two", 1, 60)
    now[0] = 70
    assert limiter.allow("one", 1, 60)


def test_lifespan():
    with TestClient(app) as client:
        assert client.get("/ready").status_code == 200


@given(
    st.floats(min_value=-90, max_value=90, allow_nan=False),
    st.floats(min_value=-180, max_value=180, allow_nan=False),
)
def test_cache_units_never_collide(latitude, longitude):
    cache = TTLMemoryCache()
    assert cache.build_key(
        "forecast", latitude=latitude, longitude=longitude, unit="celsius"
    ) != cache.build_key("forecast", latitude=latitude, longitude=longitude, unit="fahrenheit")


@pytest.mark.parametrize("hours,expected", [(24, 24), (48, 48), (72, 72)])
async def test_use_case_forecast_horizon(hours, expected):
    provider = AsyncMock()
    await WeatherUseCases(provider).get_hourly_forecast(1, 2, hours=hours)
    assert provider.get_hourly.call_args.kwargs["hours"] == expected


async def test_blank_search_and_units():
    assert (await WeatherUseCases(AsyncMock()).search_locations(" ")).items == []
    provider = OpenMeteoWeatherProvider()
    units = provider._get_units_spec(
        TemperatureUnit.FAHRENHEIT, WindSpeedUnit.MPH, PrecipitationUnit.INCH
    )
    assert (units.temperature, units.wind_speed, units.precipitation) == ("°F", "mph", "in")
    assert provider._map_wind_unit(WindSpeedUnit.MS) == "ms"
    assert provider._map_wind_unit(WindSpeedUnit.MPH) == "mph"
    assert provider._map_temperature_unit(TemperatureUnit.FAHRENHEIT) == "fahrenheit"
    assert provider._map_precip_unit(PrecipitationUnit.INCH) == "inch"


async def test_use_case_normalizes_search_and_daily_limits():
    provider = AsyncMock()
    use_cases = WeatherUseCases(provider)
    await use_cases.search_locations(" Lima ")
    assert provider.search_locations.call_args.kwargs["q"] == "Lima"
    for days, expected in ((0, 1), (16, 16), (100, 16)):
        await use_cases.get_daily_forecast(0, 0, days=days)
        assert provider.get_daily.call_args.kwargs["days"] == expected
