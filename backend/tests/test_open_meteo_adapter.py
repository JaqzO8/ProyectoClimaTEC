import httpx
import pytest

from app.domain.models import PrecipitationUnit, TemperatureUnit, WindSpeedUnit
from app.infrastructure.open_meteo import OpenMeteoError, OpenMeteoWeatherProvider


@pytest.mark.asyncio
async def test_search_locations_success(respx_mock):
    mock_response = {
        "results": [
            {
                "id": 3691348,
                "name": "Tingo María",
                "latitude": -9.29388,
                "longitude": -76.0064,
                "country": "Perú",
                "country_code": "PE",
                "admin1": "Huánuco",
                "admin2": "Leoncio Prado",
                "timezone": "America/Lima",
            }
        ]
    }
    respx_mock.get("https://geocoding-api.open-meteo.com/v1/search").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        provider = OpenMeteoWeatherProvider(client=client)
        result = await provider.search_locations("Tingo Maria")

    assert result.query == "Tingo Maria"
    assert len(result.items) == 1
    assert result.items[0].name == "Tingo María"
    assert result.items[0].country == "Perú"
    assert "Tingo María, Leoncio Prado, Huánuco, Perú" in result.items[0].display_name


@pytest.mark.asyncio
async def test_search_locations_empty(respx_mock):
    respx_mock.get("https://geocoding-api.open-meteo.com/v1/search").mock(
        return_value=httpx.Response(200, json={"results": []})
    )

    async with httpx.AsyncClient() as client:
        provider = OpenMeteoWeatherProvider(client=client)
        result = await provider.search_locations("NonExistentLocation")

    assert len(result.items) == 0


@pytest.mark.asyncio
async def test_forecast_current_success(respx_mock):
    mock_response = {
        "latitude": -9.29,
        "longitude": -76.0,
        "timezone": "America/Lima",
        "current": {
            "time": "2026-09-11T14:00",
            "temperature_2m": 28.5,
            "apparent_temperature": 31.0,
            "relative_humidity_2m": 75,
            "precipitation": 0.0,
            "rain": 0.0,
            "showers": 0.0,
            "snowfall": 0.0,
            "weather_code": 2,
            "cloud_cover": 40,
            "surface_pressure": 1012.5,
            "wind_speed_10m": 12.0,
            "wind_direction_10m": 180,
            "wind_gusts_10m": 18.0,
            "is_day": 1,
        },
    }
    respx_mock.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    async with httpx.AsyncClient() as client:
        provider = OpenMeteoWeatherProvider(client=client)
        res = await provider.get_current(
            -9.29, -76.0, TemperatureUnit.CELSIUS, WindSpeedUnit.KMH, PrecipitationUnit.MM
        )

    assert res.current.temperature == 28.5
    assert res.current.weather_label == "Parcialmente nublado"
    assert res.units.temperature == "°C"


@pytest.mark.asyncio
async def test_forecast_timeout_handling(respx_mock):
    respx_mock.get("https://api.open-meteo.com/v1/forecast").mock(
        side_effect=httpx.TimeoutException("Timeout reached")
    )

    async with httpx.AsyncClient() as client:
        provider = OpenMeteoWeatherProvider(client=client)
        with pytest.raises(OpenMeteoError) as exc_info:
            await provider.get_current(-9.29, -76.0)

    assert exc_info.value.code == "WEATHER_PROVIDER_TIMEOUT"
    assert exc_info.value.status_code == 504


@pytest.mark.asyncio
async def test_forecast_rate_limit(respx_mock):
    respx_mock.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(429, json={"error": True, "reason": "Rate limited"})
    )

    async with httpx.AsyncClient() as client:
        provider = OpenMeteoWeatherProvider(client=client)
        with pytest.raises(OpenMeteoError) as exc_info:
            await provider.get_current(-9.29, -76.0)

    assert exc_info.value.code == "RATE_LIMITED"
    assert exc_info.value.status_code == 429
