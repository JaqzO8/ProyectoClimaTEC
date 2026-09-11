import httpx
import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    resp = await async_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "backend"


@pytest.mark.asyncio
async def test_ready_endpoint(async_client):
    resp = await async_client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_locations_search_endpoint(async_client, respx_mock):
    mock_response = {
        "results": [
            {
                "id": 1,
                "name": "Lima",
                "latitude": -12.04,
                "longitude": -77.03,
                "country": "Perú",
                "country_code": "PE",
                "admin1": "Lima",
                "timezone": "America/Lima",
            }
        ]
    }
    respx_mock.get("https://geocoding-api.open-meteo.com/v1/search").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    resp = await async_client.get("/api/v1/locations/search?q=Lima")
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "Lima"
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Lima"


@pytest.mark.asyncio
async def test_current_weather_endpoint(async_client, respx_mock):
    mock_response = {
        "latitude": -12.04,
        "longitude": -77.03,
        "timezone": "America/Lima",
        "current": {
            "time": "2026-09-11T14:00",
            "temperature_2m": 22.0,
            "apparent_temperature": 22.5,
            "relative_humidity_2m": 80,
            "precipitation": 0.0,
            "rain": 0.0,
            "showers": 0.0,
            "snowfall": 0.0,
            "weather_code": 1,
            "cloud_cover": 20,
            "surface_pressure": 1015.0,
            "wind_speed_10m": 15.0,
            "wind_direction_10m": 160,
            "wind_gusts_10m": 20.0,
            "is_day": 1,
        },
    }
    respx_mock.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    resp = await async_client.get("/api/v1/weather/current?latitude=-12.04&longitude=-77.03")
    assert resp.status_code == 200
    data = resp.json()
    assert data["current"]["temperature"] == 22.0
    assert data["units"]["temperature"] == "°C"


@pytest.mark.asyncio
async def test_hourly_weather_endpoint(async_client, respx_mock):
    mock_response = {
        "latitude": -12.04,
        "longitude": -77.03,
        "timezone": "America/Lima",
        "hourly": {
            "time": ["2026-09-11T14:00"],
            "temperature_2m": [22.0],
            "precipitation_probability": [10],
            "precipitation": [0.0],
            "weather_code": [1],
            "cloud_cover": [20],
            "wind_speed_10m": [15.0],
            "wind_direction_10m": [160],
        },
    }
    respx_mock.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    resp = await async_client.get(
        "/api/v1/weather/hourly?latitude=-12.04&longitude=-77.03&hours=24"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["hourly"]) == 1


@pytest.mark.asyncio
async def test_daily_weather_endpoint(async_client, respx_mock):
    mock_response = {
        "latitude": -12.04,
        "longitude": -77.03,
        "timezone": "America/Lima",
        "daily": {
            "time": ["2026-09-11"],
            "weather_code": [1],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [18.0],
            "sunrise": ["2026-09-11T06:00"],
            "sunset": ["2026-09-11T18:00"],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [10],
            "wind_speed_10m_max": [20.0],
            "wind_gusts_10m_max": [25.0],
        },
    }
    respx_mock.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    resp = await async_client.get("/api/v1/weather/daily?latitude=-12.04&longitude=-77.03&days=7")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["daily"]) == 1


@pytest.mark.asyncio
async def test_overview_weather_endpoint(async_client, respx_mock):
    mock_response = {
        "latitude": -12.04,
        "longitude": -77.03,
        "timezone": "America/Lima",
        "current": {
            "time": "2026-09-11T14:00",
            "temperature_2m": 22.0,
            "apparent_temperature": 22.5,
            "relative_humidity_2m": 80,
            "precipitation": 0.0,
            "rain": 0.0,
            "showers": 0.0,
            "snowfall": 0.0,
            "weather_code": 1,
            "cloud_cover": 20,
            "surface_pressure": 1015.0,
            "wind_speed_10m": 15.0,
            "wind_direction_10m": 160,
            "wind_gusts_10m": 20.0,
            "is_day": 1,
        },
        "hourly": {
            "time": ["2026-09-11T14:00"],
            "temperature_2m": [22.0],
            "precipitation_probability": [10],
            "precipitation": [0.0],
            "weather_code": [1],
            "cloud_cover": [20],
            "wind_speed_10m": [15.0],
            "wind_direction_10m": [160],
        },
        "daily": {
            "time": ["2026-09-11"],
            "weather_code": [1],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [18.0],
            "sunrise": ["2026-09-11T06:00"],
            "sunset": ["2026-09-11T18:00"],
            "precipitation_sum": [0.0],
            "precipitation_probability_max": [10],
            "wind_speed_10m_max": [20.0],
            "wind_gusts_10m_max": [25.0],
        },
    }
    respx_mock.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    resp = await async_client.get("/api/v1/weather/overview?latitude=-12.04&longitude=-77.03")
    assert resp.status_code == 200
    data = resp.json()
    assert "current" in data
    assert "hourly" in data
    assert "daily" in data


@pytest.mark.asyncio
async def test_validation_error_invalid_coordinates(async_client):
    resp = await async_client.get("/api/v1/weather/current?latitude=150.0&longitude=0.0")
    assert resp.status_code == 422
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
