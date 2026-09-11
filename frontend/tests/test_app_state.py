import os
import sys

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if frontend_path not in sys.path:
    sys.path.insert(0, frontend_path)

from proyecto_climatico.state.app_state import DEFAULT_LOCATION, AppState


def test_default_state_initialization():
    state = AppState()
    assert state.selected_location == DEFAULT_LOCATION
    assert state.temperature_unit == "celsius"
    assert state.wind_speed_unit == "kmh"
    assert state.precipitation_unit == "mm"
    assert state.is_unit_modal_open is False


def test_unit_modal_toggle():
    state = AppState()
    assert state.is_unit_modal_open is False
    state.toggle_unit_modal()
    assert state.is_unit_modal_open is True
    state.toggle_unit_modal()
    assert state.is_unit_modal_open is False


def test_geolocation_error_handling():
    state = AppState()
    state.handle_geolocation_error("User denied permission")
    assert "denegado" in state.geolocation_error
