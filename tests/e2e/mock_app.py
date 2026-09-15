"""Deterministic upstream fixture. Mounted only by compose.test.yml, never in an image."""

from datetime import datetime, timedelta

import httpx
from app.api.v1.endpoints import _provider
from app.main import app as app


def upstream(request: httpx.Request) -> httpx.Response:
    params = request.url.params
    if request.url.path.endswith("/search"):
        query = params.get("name", "")
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "id": 1,
                        "name": query,
                        "country": "Perú",
                        "country_code": "PE",
                        "latitude": 66 if query == "ErrorTown" else -12.04,
                        "longitude": -77.03,
                        "timezone": "America/Lima",
                        "admin1": "Lima",
                    }
                ]
            },
        )
    if float(params["latitude"]) == 66:
        return httpx.Response(503)
    temp = 72 if params.get("temperature_unit") == "fahrenheit" else 22
    start = datetime(2026, 9, 15)
    payload = {
        "latitude": float(params["latitude"]),
        "longitude": -77.03,
        "timezone": "America/Lima",
    }
    for section in ("current", "hourly", "daily"):
        size = 168 if section == "hourly" else 7
        times = [
            (start + (timedelta(hours=i) if section == "hourly" else timedelta(days=i))).isoformat(
                timespec="minutes"
            )
            for i in range(size)
        ]
        values = {}
        for field in params[section].split(","):
            value = temp if "temperature" in field else 0
            if field in ("sunrise", "sunset"):
                values[field] = times
            else:
                values[field] = [value] * size if section != "current" else value
        values["time"] = "2026-09-15T14:00" if section == "current" else times
        payload[section] = values
    return httpx.Response(200, json=payload)


_provider._client = httpx.AsyncClient(transport=httpx.MockTransport(upstream))
