from typing import Any

import reflex as rx

from proyecto_climatico.services.api_client import APIClient

api_client = APIClient()

DEFAULT_LOCATION = {
    "provider_id": "3691348",
    "name": "Tingo María",
    "country": "Perú",
    "country_code": "PE",
    "latitude": -9.29388,
    "longitude": -76.0064,
    "timezone": "America/Lima",
    "display_name": "Tingo María, Leoncio Prado, Huánuco, Perú",
}


class AppState(rx.State):
    search_query: str = ""
    search_results: list[dict[str, Any]] = []
    is_searching: bool = False
    active_result_index: int = -1

    selected_location: dict[str, Any] = DEFAULT_LOCATION
    weather_data: dict[str, Any] | None = None

    is_loading_weather: bool = False
    error_message: str = ""
    has_error: bool = False

    temperature_unit: str = "celsius"
    wind_speed_unit: str = "kmh"
    precipitation_unit: str = "mm"
    is_unit_modal_open: bool = False

    using_geolocation: bool = False
    geolocation_error: str = ""

    async def on_load(self):
        await self.load_weather()

    async def load_weather(self):
        self.is_loading_weather = True
        self.has_error = False
        self.error_message = ""
        try:
            lat = float(self.selected_location.get("latitude", -9.29388))
            lon = float(self.selected_location.get("longitude", -76.0064))

            data = await api_client.get_weather_overview(
                latitude=lat,
                longitude=lon,
                temperature_unit=self.temperature_unit,
                wind_speed_unit=self.wind_speed_unit,
                precipitation_unit=self.precipitation_unit,
            )
            self.weather_data = data
        except Exception:
            self.has_error = True
            self.error_message = (
                "No fue posible obtener la información climática. Por favor, reintente."
            )
        finally:
            self.is_loading_weather = False

    async def handle_search_change(self, query: str):
        self.search_query = query
        self.active_result_index = -1
        if len(query.strip()) < 2:
            self.search_results = []
            return

        self.is_searching = True
        try:
            results = await api_client.search_locations(query.strip())
            self.search_results = results
        except Exception:
            self.search_results = []
        finally:
            self.is_searching = False

    async def select_location(self, location: dict[str, Any]):
        self.selected_location = location
        self.search_query = ""
        self.search_results = []
        self.using_geolocation = False
        await self.load_weather()

    async def handle_geolocation_success(self, coords: dict[str, float]):
        lat = coords.get("latitude")
        lon = coords.get("longitude")
        if lat is not None and lon is not None:
            self.selected_location = {
                "provider_id": "geo",
                "name": "Ubicación aproximada",
                "country": "",
                "country_code": "",
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "timezone": "auto",
                "display_name": f"Ubicación aproximada ({round(lat, 2)}°, {round(lon, 2)}°)",
            }
            self.using_geolocation = True
            await self.load_weather()

    def handle_geolocation_error(self, err_msg: str):
        self.geolocation_error = "Permiso de geolocalización denegado o no disponible."

    def toggle_unit_modal(self):
        self.is_unit_modal_open = not self.is_unit_modal_open

    async def set_temperature_unit(self, unit: str):
        self.temperature_unit = unit
        await self.load_weather()

    async def set_wind_speed_unit(self, unit: str):
        self.wind_speed_unit = unit
        await self.load_weather()

    async def set_precipitation_unit(self, unit: str):
        self.precipitation_unit = unit
        await self.load_weather()
