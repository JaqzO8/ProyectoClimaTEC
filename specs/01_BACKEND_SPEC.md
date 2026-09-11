# SPEC-01 — Backend climático con FastAPI

**ID:** SPEC-01  
**Prioridad:** P0  
**Tecnología:** Python + FastAPI

## 1. Propósito

Crear una API REST independiente de la UI que normalice geocodificación, clima actual y pronóstico.

## 2. Stack

- Python 3.13+
- FastAPI
- Pydantic v2
- pydantic-settings
- HTTPX async
- Uvicorn/FastAPI CLI
- cachetools o implementación de caché TTL segura
- structlog o logging estructurado equivalente
- tenacity solo si se justifica retry controlado
- pytest
- pytest-asyncio
- respx para mocks HTTP

## 3. Configuración

Variables mínimas:

```env
APP_ENV=development
APP_NAME=ProyectoClimatico
API_V1_PREFIX=/api/v1
WEATHER_PROVIDER=open_meteo
WEATHER_TIMEOUT_SECONDS=5
WEATHER_CACHE_TTL_SECONDS=300
GEOCODING_CACHE_TTL_SECONDS=1800
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=false
```

Nunca committear `.env`.

## 4. Endpoints

### GET `/health`

Respuesta:

```json
{
  "status": "ok",
  "service": "backend",
  "version": "..."
}
```

No debe llamar a Open-Meteo.

### GET `/ready`

Puede validar configuración mínima. No debe convertir una caída temporal del proveedor externo en caída permanente del servicio.

### GET `/api/v1/locations/search`

Parámetros:

- `q`: string, 2..120;
- `country_code`: ISO alpha-2 opcional;
- `language`: default `es`;
- `limit`: default 10, máximo 20.

Respuesta:

```json
{
  "query": "Tingo Maria",
  "items": [
    {
      "provider_id": "...",
      "name": "Tingo María",
      "country": "Perú",
      "country_code": "PE",
      "latitude": -9.29,
      "longitude": -76.00,
      "timezone": "America/Lima",
      "population": null,
      "admin1": "Huánuco",
      "admin2": "Leoncio Prado",
      "admin3": null,
      "admin4": null,
      "display_name": "Tingo María, Leoncio Prado, Huánuco, Perú"
    }
  ]
}
```

### GET `/api/v1/weather/current`

Parámetros:

- `latitude`: -90..90;
- `longitude`: -180..180;
- `temperature_unit`;
- `wind_speed_unit`;
- `precipitation_unit`;
- `timezone=auto` por defecto.

Respuesta normalizada:

```json
{
  "location": {
    "latitude": 0,
    "longitude": 0,
    "timezone": "..."
  },
  "observed_at": "...",
  "current": {
    "temperature": 0,
    "apparent_temperature": 0,
    "relative_humidity": 0,
    "precipitation": 0,
    "rain": 0,
    "showers": 0,
    "snowfall": 0,
    "weather_code": 0,
    "weather_label": "...",
    "cloud_cover": 0,
    "surface_pressure": 0,
    "wind_speed": 0,
    "wind_direction": 0,
    "wind_gusts": 0,
    "is_day": true
  },
  "units": {}
}
```

### GET `/api/v1/weather/hourly`

Parámetros:

- lat/lon;
- `hours`: 24, 48 o 72;
- unidades.

### GET `/api/v1/weather/daily`

Parámetros:

- lat/lon;
- `days`: 1..16;
- default 7;
- unidades.

### GET `/api/v1/weather/overview`

Endpoint agregado recomendado para la pantalla principal:

- ubicación;
- current;
- siguientes 24 h;
- 7 días.

Debe reducir round trips del frontend.

## 5. Códigos de error

Formato único:

```json
{
  "error": {
    "code": "WEATHER_PROVIDER_UNAVAILABLE",
    "message": "No fue posible obtener información climática.",
    "request_id": "..."
  }
}
```

Códigos mínimos:

- `VALIDATION_ERROR`
- `LOCATION_NOT_FOUND`
- `WEATHER_PROVIDER_TIMEOUT`
- `WEATHER_PROVIDER_UNAVAILABLE`
- `WEATHER_PROVIDER_BAD_RESPONSE`
- `RATE_LIMITED`
- `INTERNAL_ERROR`

## 6. Capa de proveedor

Puerto:

```python
class WeatherProvider(Protocol):
    async def search_locations(...): ...
    async def get_current(...): ...
    async def get_hourly(...): ...
    async def get_daily(...): ...
```

El código de aplicación no puede importar clases concretas de Open-Meteo.

## 7. Validación

- rechazar NaN/Infinity;
- normalizar espacios en `q`;
- no permitir límites arbitrariamente grandes;
- validar enums de unidades;
- sanitizar información que llegue a logs;
- nunca devolver respuesta cruda del proveedor como contrato público.

## 8. Caché

TTL inicial:

- geocoding: 30 min;
- current: 2–5 min;
- forecast: 10–15 min.

Clave de caché debe incorporar:

- endpoint;
- coordenadas normalizadas;
- unidades;
- timezone;
- horizonte solicitado.

La caché del MVP puede ser in-memory. Diseñar interfaz para Redis futura.

## 9. Timeouts y retries

- timeout total inicial: 5 s;
- retry máximo: 1 para fallos transitorios idempotentes;
- no reintentar errores 4xx de validación;
- añadir jitter/backoff si se implementa retry.

## 10. Seguridad HTTP

- CORS por allowlist;
- `X-Content-Type-Options: nosniff`;
- `Referrer-Policy`;
- `X-Frame-Options` o CSP `frame-ancestors`;
- CSP preferentemente aplicada en reverse proxy/frontend;
- request ID;
- límite de tamaño de entrada razonable.

## 11. Documentación

FastAPI deberá exponer:

- `/docs`
- `/redoc`
- `/openapi.json`

En producción podrá restringirse `/docs` mediante variable si se requiere.

## 12. Tests backend obligatorios

### Unitarios

- conversión WMO code -> label/icon key;
- normalización de unidades;
- construcción `display_name`;
- validación de coordenadas;
- TTL/cache key;
- mapeo de errores.

### Integración

Mockear Open-Meteo:

- éxito búsqueda;
- cero resultados;
- timeout;
- 400 proveedor;
- 429;
- 500;
- JSON malformado;
- campos opcionales ausentes.

### Contract tests

Validar shape de DTOs públicos.

## 13. Criterios de aceptación

- [ ] API completamente async donde exista I/O.
- [ ] Sin llamadas externas bloqueantes.
- [ ] `WeatherProvider` reemplazable.
- [ ] OpenAPI válido.
- [ ] errores homogéneos.
- [ ] caché funcional.
- [ ] tests pasan sin internet.
- [ ] ningún test depende de clima real para ser determinista.
