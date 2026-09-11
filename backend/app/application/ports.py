from typing import Protocol

from app.domain.models import (
    CurrentWeatherResponse,
    DailyForecastResponse,
    HourlyForecastResponse,
    LocationSearchResult,
    PrecipitationUnit,
    TemperatureUnit,
    WeatherOverview,
    WindSpeedUnit,
)


class WeatherProvider(Protocol):
    async def search_locations(
        self,
        q: str,
        country_code: str | None = None,
        language: str = "es",
        limit: int = 10,
    ) -> LocationSearchResult: ...

    async def get_current(
        self,
        latitude: float,
        longitude: float,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> CurrentWeatherResponse: ...

    async def get_hourly(
        self,
        latitude: float,
        longitude: float,
        hours: int = 24,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> HourlyForecastResponse: ...

    async def get_daily(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> DailyForecastResponse: ...

    async def get_overview(
        self,
        latitude: float,
        longitude: float,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> WeatherOverview: ...
