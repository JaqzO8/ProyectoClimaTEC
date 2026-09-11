from app.application.ports import WeatherProvider
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


class WeatherUseCases:
    def __init__(self, provider: WeatherProvider):
        self.provider = provider

    async def search_locations(
        self,
        q: str,
        country_code: str | None = None,
        language: str = "es",
        limit: int = 10,
    ) -> LocationSearchResult:
        clean_query = q.strip()
        if len(clean_query) < 2:
            return LocationSearchResult(query=clean_query, items=[])
        return await self.provider.search_locations(
            q=clean_query,
            country_code=country_code,
            language=language,
            limit=min(max(limit, 1), 20),
        )

    async def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> CurrentWeatherResponse:
        return await self.provider.get_current(
            latitude=latitude,
            longitude=longitude,
            temp_unit=temp_unit,
            wind_unit=wind_unit,
            precip_unit=precip_unit,
            timezone=timezone,
        )

    async def get_hourly_forecast(
        self,
        latitude: float,
        longitude: float,
        hours: int = 24,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> HourlyForecastResponse:
        valid_hours = 24
        if hours >= 72:
            valid_hours = 72
        elif hours >= 48:
            valid_hours = 48
        return await self.provider.get_hourly(
            latitude=latitude,
            longitude=longitude,
            hours=valid_hours,
            temp_unit=temp_unit,
            wind_unit=wind_unit,
            precip_unit=precip_unit,
            timezone=timezone,
        )

    async def get_daily_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> DailyForecastResponse:
        valid_days = max(1, min(days, 16))
        return await self.provider.get_daily(
            latitude=latitude,
            longitude=longitude,
            days=valid_days,
            temp_unit=temp_unit,
            wind_unit=wind_unit,
            precip_unit=precip_unit,
            timezone=timezone,
        )

    async def get_weather_overview(
        self,
        latitude: float,
        longitude: float,
        temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        wind_unit: WindSpeedUnit = WindSpeedUnit.KMH,
        precip_unit: PrecipitationUnit = PrecipitationUnit.MM,
        timezone: str = "auto",
    ) -> WeatherOverview:
        return await self.provider.get_overview(
            latitude=latitude,
            longitude=longitude,
            temp_unit=temp_unit,
            wind_unit=wind_unit,
            precip_unit=precip_unit,
            timezone=timezone,
        )
