from enum import StrEnum

from pydantic import BaseModel, Field


class TemperatureUnit(StrEnum):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class WindSpeedUnit(StrEnum):
    KMH = "kmh"
    MS = "ms"
    MPH = "mph"


class PrecipitationUnit(StrEnum):
    MM = "mm"
    INCH = "inch"


class WeatherCondition(BaseModel):
    code: int
    key: str
    label_es: str
    icon_key: str


class LocationItem(BaseModel):
    provider_id: str
    name: str
    country: str
    country_code: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    elevation: float | None = None
    timezone: str
    population: int | None = None
    admin1: str | None = None
    admin2: str | None = None
    admin3: str | None = None
    admin4: str | None = None
    display_name: str


class LocationSearchResult(BaseModel):
    query: str
    items: list[LocationItem]


class TargetLocation(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    name: str | None = None
    display_name: str | None = None


class UnitsSpec(BaseModel):
    temperature: str = "°C"
    wind_speed: str = "km/h"
    precipitation: str = "mm"


class CurrentWeatherData(BaseModel):
    temperature: float
    apparent_temperature: float
    relative_humidity: int
    precipitation: float
    rain: float
    showers: float
    snowfall: float
    weather_code: int
    weather_label: str
    cloud_cover: int
    surface_pressure: float
    wind_speed: float
    wind_direction: int
    wind_gusts: float
    is_day: bool


class CurrentWeatherResponse(BaseModel):
    location: TargetLocation
    observed_at: str
    current: CurrentWeatherData
    units: UnitsSpec


class HourlyForecastItem(BaseModel):
    time: str
    temperature: float
    precipitation_probability: int
    precipitation: float
    weather_code: int
    weather_label: str
    cloud_cover: int
    wind_speed: float
    wind_direction: int


class HourlyForecastResponse(BaseModel):
    location: TargetLocation
    hourly: list[HourlyForecastItem]
    units: UnitsSpec


class DailyForecastItem(BaseModel):
    date: str
    weather_code: int
    weather_label: str
    temperature_max: float
    temperature_min: float
    sunrise: str
    sunset: str
    precipitation_sum: float
    precipitation_probability_max: int
    wind_speed_max: float
    wind_gusts_max: float


class DailyForecastResponse(BaseModel):
    location: TargetLocation
    daily: list[DailyForecastItem]
    units: UnitsSpec


class WeatherOverview(BaseModel):
    location: TargetLocation
    observed_at: str
    current: CurrentWeatherData
    hourly: list[HourlyForecastItem]
    daily: list[DailyForecastItem]
    units: UnitsSpec


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
