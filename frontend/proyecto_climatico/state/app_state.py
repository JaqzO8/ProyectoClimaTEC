from typing import Any

import httpx
import reflex as rx

from proyecto_climatico.services.api_client import APIClient
from proyecto_climatico.state.events import event

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
    weather_data: dict[str, Any] = {}

    is_loading_weather: bool = False
    error_message: str = ""
    has_error: bool = False

    temperature_unit: str = rx.LocalStorage("celsius", name="climate_temperature_unit")
    wind_speed_unit: str = rx.LocalStorage("kmh", name="climate_wind_speed_unit")
    precipitation_unit: str = rx.LocalStorage("mm", name="climate_precipitation_unit")
    is_unit_modal_open: bool = False

    using_geolocation: bool = False
    geolocation_error: str = ""

    @rx.var
    def has_search_results(self) -> bool:
        return bool(self.search_results)

    @rx.var
    def temperature_symbol(self) -> str:
        return str(self.weather_data.get("units", {}).get("temperature", "°C"))

    @rx.var
    def wind_symbol(self) -> str:
        return str(self.weather_data.get("units", {}).get("wind_speed", "km/h"))

    @rx.var
    def precipitation_symbol(self) -> str:
        return str(self.weather_data.get("units", {}).get("precipitation", "mm"))

    @rx.var
    def has_weather_data(self) -> bool:
        return bool(self.weather_data and "current" in self.weather_data)

    @rx.var
    def current_temp_display(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "--°"
        curr = self.weather_data["current"]
        u = self.weather_data.get("units", {}).get("temperature", "°C")
        return f"{curr.get('temperature', 0):.0f}{u}"

    @rx.var
    def current_apparent_temp_display(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "--"
        curr = self.weather_data["current"]
        u = self.weather_data.get("units", {}).get("temperature", "°C")
        return f"Sensación térmica: {curr.get('apparent_temperature', 0):.0f}{u}"

    @rx.var
    def current_weather_label(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "Cargando..."
        return str(self.weather_data["current"].get("weather_label", ""))

    @rx.var
    def current_humidity(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "--"
        return f"{self.weather_data['current'].get('relative_humidity', 0)}%"

    @rx.var
    def current_wind_display(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "--"
        curr = self.weather_data["current"]
        u = self.weather_data.get("units", {}).get("wind_speed", "km/h")
        return f"{curr.get('wind_speed', 0):.1f} {u} ({curr.get('wind_direction', 0)}°)"

    @rx.var
    def current_gusts_display(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "--"
        curr = self.weather_data["current"]
        u = self.weather_data.get("units", {}).get("wind_speed", "km/h")
        return f"{curr.get('wind_gusts', 0):.1f} {u}"

    @rx.var
    def current_precip_display(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "--"
        curr = self.weather_data["current"]
        u = self.weather_data.get("units", {}).get("precipitation", "mm")
        return f"{curr.get('precipitation', 0):.1f} {u}"

    @rx.var
    def current_pressure_display(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "--"
        return f"{self.weather_data['current'].get('surface_pressure', 0):.0f} hPa"

    @rx.var
    def current_cloud_display(self) -> str:
        if not self.weather_data or "current" not in self.weather_data:
            return "--"
        return f"{self.weather_data['current'].get('cloud_cover', 0)}%"

    @rx.var
    def observed_at_display(self) -> str:
        if not self.weather_data:
            return "--"
        return str(self.weather_data.get("observed_at", ""))

    @rx.var
    def map_embed_url(self) -> str:
        lat = float(self.selected_location.get("latitude", -9.29388))
        lon = float(self.selected_location.get("longitude", -76.0064))
        return f"https://www.openstreetmap.org/export/embed.html?bbox={lon - 0.15:.4f}%2C{lat - 0.15:.4f}%2C{lon + 0.15:.4f}%2C{lat + 0.15:.4f}&layer=mapnik&marker={lat:.4f}%2C{lon:.4f}"

    @rx.var
    def coordinates_display(self) -> str:
        lat = float(self.selected_location.get("latitude", -9.29388))
        lon = float(self.selected_location.get("longitude", -76.0064))
        return f"Coordenadas: {lat:.4f}°, {lon:.4f}°"

    @rx.var
    def hourly_list(self) -> list[dict[str, Any]]:
        return list(self.weather_data.get("hourly", [])) if self.weather_data else []

    @rx.var
    def daily_list(self) -> list[dict[str, Any]]:
        return list(self.weather_data.get("daily", [])) if self.weather_data else []

    @event
    async def on_load(self) -> None:
        await self.load_weather()

    @event
    async def load_weather(self) -> None:
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
        except (httpx.HTTPError, ValueError, TypeError):
            self.has_error = True
            self.error_message = (
                "No fue posible obtener la información climática. Por favor, reintente."
            )
        finally:
            self.is_loading_weather = False

    @event
    async def handle_search_change(self, query: str) -> None:
        self.search_query = query
        self.active_result_index = -1
        if len(query.strip()) < 2:
            self.search_results = []
            return

        self.is_searching = True
        try:
            results = await api_client.search_locations(query.strip())
            self.search_results = results
        except (httpx.HTTPError, ValueError, TypeError):
            self.search_results = []
            self.geolocation_error = "No pudimos buscar ubicaciones. Inténtalo de nuevo."
        finally:
            self.is_searching = False

    @event
    async def select_location(self, location: dict[str, Any]) -> None:
        self.selected_location = location
        self.search_query = ""
        self.search_results = []
        self.using_geolocation = False
        await self.load_weather()

    @event
    async def handle_geolocation_success(self, coords: dict[str, float]) -> None:
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

    @event
    def handle_geolocation_error(self, err_msg: str) -> None:
        self.geolocation_error = "Permiso de geolocalización denegado o no disponible."

    @event
    async def handle_geolocation_result(self, result: dict[str, Any]) -> None:
        if result.get("error"):
            self.handle_geolocation_error(str(result["error"]))
        else:
            self.geolocation_error = ""
            await self.handle_geolocation_success(result)

    @event
    async def handle_search_key(self, key: str) -> None:
        count = len(self.search_results)
        if key == "Escape":
            self.search_results = []
            self.active_result_index = -1
        elif count and key in ("ArrowDown", "ArrowUp"):
            step = 1 if key == "ArrowDown" else -1
            self.active_result_index = (self.active_result_index + step) % count
        elif count and key == "Enter":
            await self.select_location(self.search_results[max(0, self.active_result_index)])

    @event
    def toggle_unit_modal(self) -> None:
        self.is_unit_modal_open = not self.is_unit_modal_open

    @event
    async def set_temperature_unit(self, unit: str) -> None:
        if unit not in ("celsius", "fahrenheit"):
            return
        self.temperature_unit = unit
        await self.load_weather()

    @event
    async def set_wind_speed_unit(self, unit: str) -> None:
        if unit not in ("kmh", "ms", "mph"):
            return
        self.wind_speed_unit = unit
        await self.load_weather()

    @event
    async def set_precipitation_unit(self, unit: str) -> None:
        if unit not in ("mm", "inch"):
            return
        self.precipitation_unit = unit
        await self.load_weather()
