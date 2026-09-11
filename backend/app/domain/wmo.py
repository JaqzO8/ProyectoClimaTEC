from app.domain.models import WeatherCondition

_WMO_CATALOG: dict[int, dict[str, str]] = {
    0: {"key": "clear", "label": "Despejado", "icon_day": "sun", "icon_night": "moon"},
    1: {
        "key": "mainly_clear",
        "label": "Principalmente despejado",
        "icon_day": "sun_cloud",
        "icon_night": "moon_cloud",
    },
    2: {
        "key": "partly_cloudy",
        "label": "Parcialmente nublado",
        "icon_day": "partly_cloudy_day",
        "icon_night": "partly_cloudy_night",
    },
    3: {"key": "overcast", "label": "Nublado", "icon_day": "cloud", "icon_night": "cloud"},
    45: {"key": "fog", "label": "Niebla", "icon_day": "fog", "icon_night": "fog"},
    48: {
        "key": "depositing_rime_fog",
        "label": "Niebla helada",
        "icon_day": "fog",
        "icon_night": "fog",
    },
    51: {
        "key": "light_drizzle",
        "label": "Llovizna ligera",
        "icon_day": "drizzle",
        "icon_night": "drizzle",
    },
    53: {
        "key": "moderate_drizzle",
        "label": "Llovizna moderada",
        "icon_day": "drizzle",
        "icon_night": "drizzle",
    },
    55: {
        "key": "dense_drizzle",
        "label": "Llovizna intensa",
        "icon_day": "drizzle",
        "icon_night": "drizzle",
    },
    56: {
        "key": "light_freezing_drizzle",
        "label": "Llovizna helada ligera",
        "icon_day": "freezing_drizzle",
        "icon_night": "freezing_drizzle",
    },
    57: {
        "key": "dense_freezing_drizzle",
        "label": "Llovizna helada intensa",
        "icon_day": "freezing_drizzle",
        "icon_night": "freezing_drizzle",
    },
    61: {
        "key": "slight_rain",
        "label": "Lluvia ligera",
        "icon_day": "rain_light",
        "icon_night": "rain_light",
    },
    63: {
        "key": "moderate_rain",
        "label": "Lluvia moderada",
        "icon_day": "rain",
        "icon_night": "rain",
    },
    65: {
        "key": "heavy_rain",
        "label": "Lluvia fuerte",
        "icon_day": "rain_heavy",
        "icon_night": "rain_heavy",
    },
    66: {
        "key": "light_freezing_rain",
        "label": "Lluvia helada ligera",
        "icon_day": "freezing_rain",
        "icon_night": "freezing_rain",
    },
    67: {
        "key": "heavy_freezing_rain",
        "label": "Lluvia helada fuerte",
        "icon_day": "freezing_rain",
        "icon_night": "freezing_rain",
    },
    71: {"key": "slight_snow", "label": "Nieve ligera", "icon_day": "snow", "icon_night": "snow"},
    73: {
        "key": "moderate_snow",
        "label": "Nieve moderada",
        "icon_day": "snow",
        "icon_night": "snow",
    },
    75: {
        "key": "heavy_snow",
        "label": "Nieve fuerte",
        "icon_day": "snow_heavy",
        "icon_night": "snow_heavy",
    },
    77: {"key": "snow_grains", "label": "Granizo fino", "icon_day": "snow", "icon_night": "snow"},
    80: {
        "key": "slight_showers",
        "label": "Chubascos ligeros",
        "icon_day": "showers",
        "icon_night": "showers",
    },
    81: {
        "key": "moderate_showers",
        "label": "Chubascos moderados",
        "icon_day": "showers",
        "icon_night": "showers",
    },
    82: {
        "key": "violent_showers",
        "label": "Chubascos violentos",
        "icon_day": "showers_heavy",
        "icon_night": "showers_heavy",
    },
    85: {
        "key": "slight_snow_showers",
        "label": "Chubascos de nieve ligeros",
        "icon_day": "snow_showers",
        "icon_night": "snow_showers",
    },
    86: {
        "key": "heavy_snow_showers",
        "label": "Chubascos de nieve fuertes",
        "icon_day": "snow_showers",
        "icon_night": "snow_showers",
    },
    95: {
        "key": "thunderstorm",
        "label": "Tormenta eléctrica",
        "icon_day": "thunderstorm",
        "icon_night": "thunderstorm",
    },
    96: {
        "key": "thunderstorm_hail_slight",
        "label": "Tormenta con granizo ligero",
        "icon_day": "thunderstorm_hail",
        "icon_night": "thunderstorm_hail",
    },
    99: {
        "key": "thunderstorm_hail_heavy",
        "label": "Tormenta con granizo fuerte",
        "icon_day": "thunderstorm_hail",
        "icon_night": "thunderstorm_hail",
    },
}


def get_wmo_condition(code: int, is_day: bool = True) -> WeatherCondition:
    entry = _WMO_CATALOG.get(
        code,
        {
            "key": "unknown",
            "label": f"Condición climática ({code})",
            "icon_day": "cloud",
            "icon_night": "cloud",
        },
    )
    icon_key = entry["icon_day"] if is_day else entry["icon_night"]
    return WeatherCondition(
        code=code,
        key=entry["key"],
        label_es=entry["label"],
        icon_key=icon_key,
    )
