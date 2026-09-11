import os
from typing import Any

import httpx

BACKEND_BASE_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000").rstrip("/")


class APIClient:
    def __init__(self, base_url: str = BACKEND_BASE_URL):
        self.base_url = base_url

    async def search_locations(
        self, query: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/api/v1/locations/search"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, params={"q": query, "limit": limit})
            resp.raise_for_status()
            data = resp.json()
            return data.get("items", [])

    async def get_weather_overview(
        self,
        latitude: float,
        longitude: float,
        temperature_unit: str = "celsius",
        wind_speed_unit: str = "kmh",
        precipitation_unit: str = "mm",
    ) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/weather/overview"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit,
        }
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
