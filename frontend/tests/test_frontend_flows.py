from copy import deepcopy
from unittest.mock import AsyncMock

import httpx
import pytest

from proyecto_climatico.services.api_client import APIClient
from proyecto_climatico.state.app_state import DEFAULT_LOCATION, AppState, api_client


@pytest.fixture
def weather():
    return {
        "current": {
            "temperature": 22,
            "apparent_temperature": 24,
            "relative_humidity": 80,
            "weather_label": "Despejado",
            "wind_speed": 10,
            "wind_direction": 90,
            "wind_gusts": 15,
            "precipitation": 1,
            "surface_pressure": 1012,
            "cloud_cover": 20,
        },
        "units": {"temperature": "°F", "wind_speed": "mph", "precipitation": "in"},
        "hourly": [{"time": "2026-09-15T14:00"}],
        "daily": [{"date": "2026-09-15"}],
        "observed_at": "2026-09-15T14:00",
    }


@pytest.mark.parametrize(
    "name",
    [
        "current_temp_display",
        "current_apparent_temp_display",
        "current_humidity",
        "current_wind_display",
        "current_gusts_display",
        "current_precip_display",
        "current_pressure_display",
        "current_cloud_display",
        "observed_at_display",
        "current_weather_label",
        "map_embed_url",
        "coordinates_display",
        "temperature_symbol",
        "wind_symbol",
        "precipitation_symbol",
    ],
)
def test_display_fields_empty_and_loaded(weather, name):
    state = AppState()
    assert isinstance(getattr(state, name), str)
    assert not state.has_weather_data
    assert state.hourly_list == []
    assert state.daily_list == []
    state.weather_data = weather
    assert state.has_weather_data
    assert isinstance(getattr(state, name), str)
    assert state.hourly_list == weather["hourly"]
    assert state.daily_list == weather["daily"]
    assert state.current_temp_display == "22°F"
    assert state.current_wind_display == "10.0 mph (90°)"
    assert state.current_precip_display == "1.0 in"


async def test_search_keyboard_and_selection(monkeypatch, weather):
    monkeypatch.setattr(
        api_client, "search_locations", AsyncMock(return_value=[deepcopy(DEFAULT_LOCATION)])
    )
    monkeypatch.setattr(api_client, "get_weather_overview", AsyncMock(return_value=weather))
    state = AppState()
    await state.handle_search_change("L")
    assert state.search_results == []
    await state.handle_search_change(" Lima ")
    assert state.has_search_results
    api_client.search_locations.assert_awaited_once_with("Lima")
    await state.handle_search_key("ArrowDown")
    assert state.active_result_index == 0
    await state.handle_search_key("ArrowUp")
    await state.handle_search_key("Enter")
    assert state.weather_data == weather
    assert state.search_results == []
    await state.handle_search_change("Lima")
    await state.handle_search_key("Escape")
    assert state.search_results == []


async def test_weather_error_retry_and_search_error(monkeypatch, weather):
    monkeypatch.setattr(
        api_client, "get_weather_overview", AsyncMock(side_effect=httpx.ReadTimeout("timeout"))
    )
    monkeypatch.setattr(
        api_client, "search_locations", AsyncMock(side_effect=httpx.ConnectError("offline"))
    )
    state = AppState()
    await state.on_load()
    assert state.has_error and not state.is_loading_weather
    assert state.selected_location == DEFAULT_LOCATION
    await state.handle_search_change("Lima")
    assert not state.is_searching
    assert "buscar" in state.geolocation_error
    monkeypatch.setattr(api_client, "get_weather_overview", AsyncMock(return_value=weather))
    await state.load_weather()
    assert not state.has_error


async def test_geolocation_consent_and_denial(monkeypatch, weather):
    monkeypatch.setattr(api_client, "get_weather_overview", AsyncMock(return_value=weather))
    state = AppState()
    await state.handle_geolocation_result({"error": "denied"})
    assert "denegado" in state.geolocation_error
    assert state.selected_location == DEFAULT_LOCATION
    await state.handle_geolocation_success({})
    assert not state.using_geolocation
    await state.handle_geolocation_result({"latitude": -12.04, "longitude": -77.03})
    assert state.using_geolocation
    assert state.geolocation_error == ""
    assert state.selected_location["latitude"] == -12.04


@pytest.mark.parametrize(
    "method,field,value",
    [
        ("set_temperature_unit", "temperature_unit", "fahrenheit"),
        ("set_wind_speed_unit", "wind_speed_unit", "mph"),
        ("set_precipitation_unit", "precipitation_unit", "inch"),
    ],
)
async def test_unit_changes_and_invalid_values(monkeypatch, weather, method, field, value):
    monkeypatch.setattr(api_client, "get_weather_overview", AsyncMock(return_value=weather))
    state = AppState()
    await getattr(state, method)(value)
    assert getattr(state, field) == value
    api_client.get_weather_overview.assert_awaited_once()
    await getattr(state, method)("invalid")
    assert getattr(state, field) == value
    api_client.get_weather_overview.assert_awaited_once()


async def test_api_client_calls_only_configured_backend(respx_mock, weather):
    search = respx_mock.get("http://backend:8000/api/v1/locations/search").respond(
        200, json={"items": [DEFAULT_LOCATION]}
    )
    overview = respx_mock.get("http://backend:8000/api/v1/weather/overview").respond(
        200, json=weather
    )
    client = APIClient(base_url="http://backend:8000")
    assert len(await client.search_locations("Lima")) == 1
    assert await client.get_weather_overview(-12, -77, temperature_unit="fahrenheit") == weather
    assert search.calls[0].request.url.params["q"] == "Lima"
    assert overview.calls[0].request.url.params["temperature_unit"] == "fahrenheit"


async def test_api_client_propagates_http_failure(respx_mock):
    respx_mock.get("http://backend:8000/api/v1/locations/search").respond(503)
    with pytest.raises(httpx.HTTPStatusError):
        await APIClient("http://backend:8000").search_locations("Lima")
