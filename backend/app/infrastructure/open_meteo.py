import asyncio
from typing import Any, cast

import httpx

from app.application.ports import WeatherProvider
from app.core.config import settings
from app.domain.models import (
    CurrentWeatherData,
    CurrentWeatherResponse,
    DailyForecastItem,
    DailyForecastResponse,
    HourlyForecastItem,
    HourlyForecastResponse,
    LocationItem,
    LocationSearchResult,
    PrecipitationUnit,
    TargetLocation,
    TemperatureUnit,
    UnitsSpec,
    WeatherOverview,
    WindSpeedUnit,
)
from app.domain.wmo import get_wmo_condition
from app.infrastructure.cache import TTLMemoryCache
from app.infrastructure.logging import logger


class OpenMeteoError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class OpenMeteoWeatherProvider(WeatherProvider):
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        cache: TTLMemoryCache | None = None,
    ):
        self.client = client or httpx.AsyncClient(timeout=settings.WEATHER_TIMEOUT_SECONDS)
        self.cache = cache or TTLMemoryCache(default_ttl=settings.WEATHER_CACHE_TTL_SECONDS)

    def _build_display_name(
        self,
        name: str,
        admin1: str | None,
        admin2: str | None,
        admin3: str | None,
        admin4: str | None,
        country: str,
    ) -> str:
        parts: list[str] = []
        seen = set()

        for item in [name, admin4, admin3, admin2, admin1, country]:
            if item and item.strip() and item.strip() not in seen:
                parts.append(item.strip())
                seen.add(item.strip())

        return ", ".join(parts)

    def _map_temperature_unit(self, unit: TemperatureUnit) -> str:
        return "fahrenheit" if unit == TemperatureUnit.FAHRENHEIT else "celsius"

    def _map_wind_unit(self, unit: WindSpeedUnit) -> str:
        if unit == WindSpeedUnit.MS:
            return "ms"
        elif unit == WindSpeedUnit.MPH:
            return "mph"
        return "kmh"

    def _map_precip_unit(self, unit: PrecipitationUnit) -> str:
        return "inch" if unit == PrecipitationUnit.INCH else "mm"

    def _get_units_spec(
        self,
        temp_unit: TemperatureUnit,
        wind_unit: WindSpeedUnit,
        precip_unit: PrecipitationUnit,
    ) -> UnitsSpec:
        temp_str = "°F" if temp_unit == TemperatureUnit.FAHRENHEIT else "°C"
        wind_str = (
            "m/s"
            if wind_unit == WindSpeedUnit.MS
            else ("mph" if wind_unit == WindSpeedUnit.MPH else "km/h")
        )
        precip_str = "in" if precip_unit == PrecipitationUnit.INCH else "mm"
        return UnitsSpec(temperature=temp_str, wind_speed=wind_str, precipitation=precip_str)

    async def search_locations(
        self,
        q: str,
        country_code: str | None = None,
        language: str = "es",
        limit: int = 10,
    ) -> LocationSearchResult:
        cache_key = self.cache.build_key(
            "geocoding", q=q, country_code=country_code, language=language, limit=limit
        )
        cached = await self.cache.get(cache_key)
        if cached is not None:
            logger.info("cache_hit", type="geocoding", query=q)
            return LocationSearchResult.model_validate(cached)

        params: dict[str, str | int | float | bool | None] = {
            "name": q,
            "count": limit,
            "language": language,
            "format": "json",
        }

        try:
            resp = await self.client.get(self.GEOCODING_URL, params=params)
            resp.raise_for_status()
            data: dict[str, Any] = cast(dict[str, Any], resp.json())
        except httpx.TimeoutException as exc:
            logger.error("geocoding_timeout", query=q, error=str(exc))
            raise OpenMeteoError(
                "WEATHER_PROVIDER_TIMEOUT",
                "El servicio de geocodificación no respondió a tiempo.",
                status_code=504,
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error("geocoding_http_error", query=q, status=exc.response.status_code)
            if exc.response.status_code == 429:
                raise OpenMeteoError(
                    "RATE_LIMITED",
                    "Se ha alcanzado el límite de solicitudes de geocodificación.",
                    status_code=429,
                ) from exc
            raise OpenMeteoError(
                "WEATHER_PROVIDER_UNAVAILABLE",
                "El proveedor de geocodificación devolvió un error.",
                status_code=502,
            ) from exc
        except Exception as exc:
            logger.error("geocoding_bad_response", query=q, error=str(exc))
            raise OpenMeteoError(
                "WEATHER_PROVIDER_BAD_RESPONSE",
                "Respuesta no válida del proveedor de geocodificación.",
                status_code=502,
            ) from exc

        raw_results = data.get("results") or []
        items: list[LocationItem] = []

        for loc in raw_results:
            c_code = (loc.get("country_code") or "").upper()
            if country_code and c_code != country_code.upper():
                continue

            name = loc.get("name", "")
            country = loc.get("country", "")
            admin1 = loc.get("admin1")
            admin2 = loc.get("admin2")
            admin3 = loc.get("admin3")
            admin4 = loc.get("admin4")
            disp_name = self._build_display_name(name, admin1, admin2, admin3, admin4, country)

            item = LocationItem(
                provider_id=str(loc.get("id", "")),
                name=name,
                country=country,
                country_code=c_code,
                latitude=float(loc.get("latitude", 0.0)),
                longitude=float(loc.get("longitude", 0.0)),
                elevation=loc.get("elevation"),
                timezone=loc.get("timezone") or "UTC",
                population=loc.get("population"),
                admin1=admin1,
                admin2=admin2,
                admin3=admin3,
                admin4=admin4,
                display_name=disp_name,
            )
            items.append(item)

        result = LocationSearchResult(query=q, items=items)
        await self.cache.set(
            cache_key, result.model_dump(), ttl=settings.GEOCODING_CACHE_TTL_SECONDS
        )
        return result

    async def _fetch_forecast_raw(
        self,
        latitude: float,
        longitude: float,
        temp_unit: TemperatureUnit,
        wind_unit: WindSpeedUnit,
        precip_unit: PrecipitationUnit,
        timezone: str,
        forecast_days: int = 7,
    ) -> dict[str, Any]:
        params: dict[str, str | int | float | bool | None] = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max",
            "temperature_unit": self._map_temperature_unit(temp_unit),
            "wind_speed_unit": self._map_wind_unit(wind_unit),
            "precipitation_unit": self._map_precip_unit(precip_unit),
            "timezone": timezone,
            "forecast_days": forecast_days,
        }

        cache_key = self.cache.build_key("forecast", **params)
        cached = await self.cache.get(cache_key)
        if cached is not None:
            logger.info("cache_hit", type="forecast", lat=latitude, lon=longitude)
            return cast(dict[str, Any], cached)

        try:
            resp = await self.client.get(self.FORECAST_URL, params=params)
            resp.raise_for_status()
            data: dict[str, Any] = cast(dict[str, Any], resp.json())
        except httpx.TimeoutException as exc:
            logger.error("forecast_timeout", lat=latitude, lon=longitude, error=str(exc))
            raise OpenMeteoError(
                "WEATHER_PROVIDER_TIMEOUT",
                "El proveedor meteorológico no respondió dentro del tiempo límite.",
                status_code=504,
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error(
                "forecast_http_error", lat=latitude, lon=longitude, status=exc.response.status_code
            )
            if exc.response.status_code == 429:
                raise OpenMeteoError(
                    "RATE_LIMITED",
                    "Se ha superado el límite de peticiones al servicio de clima.",
                    status_code=429,
                ) from exc
            raise OpenMeteoError(
                "WEATHER_PROVIDER_UNAVAILABLE",
                "El proveedor de datos meteorológicos no está disponible temporalmente.",
                status_code=502,
            ) from exc
        except Exception as exc:
            logger.error("forecast_bad_response", lat=latitude, lon=longitude, error=str(exc))
            raise OpenMeteoError(
                "WEATHER_PROVIDER_BAD_RESPONSE",
                "Respuesta no válida del proveedor de datos meteorológicos.",
                status_code=502,
            ) from exc

        await self.cache.set(cache_key, data, ttl=settings.WEATHER_CACHE_TTL_SECONDS)
        return data

    async def get_current(
        self,
        latitude: float,
        longitude: float,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> CurrentWeatherResponse:
        data = await self._fetch_forecast_raw(
            latitude, longitude, temp_unit, wind_unit, precip_unit, timezone, forecast_days=1
        )
        curr = data.get("current", {})
        w_code = int(curr.get("weather_code", 0))
        is_day = bool(curr.get("is_day", 1))
        w_cond = get_wmo_condition(w_code, is_day)

        target_loc = TargetLocation(
            latitude=float(data.get("latitude", latitude)),
            longitude=float(data.get("longitude", longitude)),
            timezone=data.get("timezone", "UTC"),
        )
        units_spec = self._get_units_spec(temp_unit, wind_unit, precip_unit)

        current_data = CurrentWeatherData(
            temperature=float(curr.get("temperature_2m", 0.0)),
            apparent_temperature=float(curr.get("apparent_temperature", 0.0)),
            relative_humidity=int(curr.get("relative_humidity_2m", 0)),
            precipitation=float(curr.get("precipitation", 0.0)),
            rain=float(curr.get("rain", 0.0)),
            showers=float(curr.get("showers", 0.0)),
            snowfall=float(curr.get("snowfall", 0.0)),
            weather_code=w_code,
            weather_label=w_cond.label_es,
            cloud_cover=int(curr.get("cloud_cover", 0)),
            surface_pressure=float(curr.get("surface_pressure", 0.0)),
            wind_speed=float(curr.get("wind_speed_10m", 0.0)),
            wind_direction=int(curr.get("wind_direction_10m", 0)),
            wind_gusts=float(curr.get("wind_gusts_10m", 0.0)),
            is_day=is_day,
        )

        return CurrentWeatherResponse(
            location=target_loc,
            observed_at=str(curr.get("time", "")),
            current=current_data,
            units=units_spec,
        )

    async def get_hourly(
        self,
        latitude: float,
        longitude: float,
        hours: int = 24,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> HourlyForecastResponse:
        forecast_days = 3 if hours > 48 else (2 if hours > 24 else 1)
        data = await self._fetch_forecast_raw(
            latitude,
            longitude,
            temp_unit,
            wind_unit,
            precip_unit,
            timezone,
            forecast_days=forecast_days,
        )
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        p_probs = hourly.get("precipitation_probability", [])
        precips = hourly.get("precipitation", [])
        w_codes = hourly.get("weather_code", [])
        clouds = hourly.get("cloud_cover", [])
        w_speeds = hourly.get("wind_speed_10m", [])
        w_dirs = hourly.get("wind_direction_10m", [])

        items: list[HourlyForecastItem] = []
        limit = min(hours, len(times))

        for i in range(limit):
            code = int(w_codes[i]) if i < len(w_codes) else 0
            w_cond = get_wmo_condition(code, is_day=True)
            items.append(
                HourlyForecastItem(
                    time=str(times[i]),
                    temperature=float(temps[i]) if i < len(temps) else 0.0,
                    precipitation_probability=int(p_probs[i]) if i < len(p_probs) else 0,
                    precipitation=float(precips[i]) if i < len(precips) else 0.0,
                    weather_code=code,
                    weather_label=w_cond.label_es,
                    cloud_cover=int(clouds[i]) if i < len(clouds) else 0,
                    wind_speed=float(w_speeds[i]) if i < len(w_speeds) else 0.0,
                    wind_direction=int(w_dirs[i]) if i < len(w_dirs) else 0,
                )
            )

        target_loc = TargetLocation(
            latitude=float(data.get("latitude", latitude)),
            longitude=float(data.get("longitude", longitude)),
            timezone=data.get("timezone", "UTC"),
        )
        return HourlyForecastResponse(
            location=target_loc,
            hourly=items,
            units=self._get_units_spec(temp_unit, wind_unit, precip_unit),
        )

    async def get_daily(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> DailyForecastResponse:
        data = await self._fetch_forecast_raw(
            latitude, longitude, temp_unit, wind_unit, precip_unit, timezone, forecast_days=days
        )
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        w_codes = daily.get("weather_code", [])
        t_maxs = daily.get("temperature_2m_max", [])
        t_mins = daily.get("temperature_2m_min", [])
        sunrises = daily.get("sunrise", [])
        sunsets = daily.get("sunset", [])
        p_sums = daily.get("precipitation_sum", [])
        p_maxs = daily.get("precipitation_probability_max", [])
        w_maxs = daily.get("wind_speed_10m_max", [])
        g_maxs = daily.get("wind_gusts_10m_max", [])

        items: list[DailyForecastItem] = []
        limit = min(days, len(dates))

        for i in range(limit):
            code = int(w_codes[i]) if i < len(w_codes) else 0
            w_cond = get_wmo_condition(code, is_day=True)
            items.append(
                DailyForecastItem(
                    date=str(dates[i]),
                    weather_code=code,
                    weather_label=w_cond.label_es,
                    temperature_max=float(t_maxs[i]) if i < len(t_maxs) else 0.0,
                    temperature_min=float(t_mins[i]) if i < len(t_mins) else 0.0,
                    sunrise=str(sunrises[i]) if i < len(sunrises) else "",
                    sunset=str(sunsets[i]) if i < len(sunsets) else "",
                    precipitation_sum=float(p_sums[i]) if i < len(p_sums) else 0.0,
                    precipitation_probability_max=int(p_maxs[i])
                    if i < len(p_maxs) and p_maxs[i] is not None
                    else 0,
                    wind_speed_max=float(w_maxs[i]) if i < len(w_maxs) else 0.0,
                    wind_gusts_max=float(g_maxs[i]) if i < len(g_maxs) else 0.0,
                )
            )

        target_loc = TargetLocation(
            latitude=float(data.get("latitude", latitude)),
            longitude=float(data.get("longitude", longitude)),
            timezone=data.get("timezone", "UTC"),
        )
        return DailyForecastResponse(
            location=target_loc,
            daily=items,
            units=self._get_units_spec(temp_unit, wind_unit, precip_unit),
        )

    async def get_overview(
        self,
        latitude: float,
        longitude: float,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> WeatherOverview:
        curr_task = self.get_current(
            latitude, longitude, temp_unit, wind_unit, precip_unit, timezone
        )
        hourly_task = self.get_hourly(
            latitude, longitude, 24, temp_unit, wind_unit, precip_unit, timezone
        )
        daily_task = self.get_daily(
            latitude, longitude, 7, temp_unit, wind_unit, precip_unit, timezone
        )

        curr_res, hourly_res, daily_res = await asyncio.gather(curr_task, hourly_task, daily_task)

        return WeatherOverview(
            location=curr_res.location,
            observed_at=curr_res.observed_at,
            current=curr_res.current,
            hourly=hourly_res.hourly,
            daily=daily_res.daily,
            units=curr_res.units,
        )
