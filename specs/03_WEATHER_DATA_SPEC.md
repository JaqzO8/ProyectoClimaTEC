# SPEC-03 — Datos meteorológicos y geográficos

**ID:** SPEC-03  
**Prioridad:** P0

## 1. Proveedor inicial

Implementar `OpenMeteoWeatherProvider`.

Open-Meteo será una implementación, no el dominio.

## 2. Geocodificación

Utilizar el endpoint de geocoding del proveedor para búsqueda mundial.

Normalizar:

```text
provider_id
name
latitude
longitude
elevation
timezone
country
country_code
population
admin1
admin2
admin3
admin4
```

## 3. Niveles administrativos

Regla:

- no asumir que `admin1 = departamento`;
- no asumir que `admin2 = provincia`;
- conservar los nombres reales;
- mostrar de general a específico o específico a general según componente;
- eliminar niveles repetidos o vacíos.

Ejemplo:

```text
Tingo María · Leoncio Prado · Huánuco · Perú
```

## 4. Weather code

Crear catálogo interno basado en WMO codes que produzca:

```python
WeatherCondition(
    code=2,
    key="partly_cloudy",
    label_es="Parcialmente nublado",
    icon_key="partly_cloudy_day"
)
```

Día/noche podrá alterar icono, no el significado base.

No colocar strings de códigos meteorológicos dispersos por la UI.

## 5. Variables actuales

Solicitar solo variables utilizadas.

Set recomendado:

- temperature_2m;
- relative_humidity_2m;
- apparent_temperature;
- is_day;
- precipitation;
- rain;
- showers;
- snowfall;
- weather_code;
- cloud_cover;
- surface_pressure;
- wind_speed_10m;
- wind_direction_10m;
- wind_gusts_10m.

## 6. Variables horarias

Mínimo:

- temperature_2m;
- relative_humidity_2m;
- precipitation_probability;
- precipitation;
- weather_code;
- cloud_cover;
- wind_speed_10m;
- wind_direction_10m.

## 7. Variables diarias

Mínimo:

- weather_code;
- temperature_2m_max;
- temperature_2m_min;
- sunrise;
- sunset;
- precipitation_sum;
- precipitation_probability_max;
- wind_speed_10m_max;
- wind_gusts_10m_max.

## 8. Timezone

Usar zona horaria de la ubicación.

Nunca renderizar todas las fechas como si fueran hora del servidor AWS.

La API deberá devolver timezone explícita.

## 9. Unidades

Dominio normalizado mediante enums.

Temperatura:

- `celsius`
- `fahrenheit`

Viento:

- `kmh`
- `ms`
- `mph`

Precipitación:

- `mm`
- `inch`

## 10. Precisión

No presentar más decimales de los útiles.

UI:

- temperatura: 0–1 decimal;
- humedad: entero;
- viento: 0–1 decimal;
- precipitación: 0–1 decimal;
- coordenadas en panel técnico: 4–5 decimales.

## 11. Condición “tiempo real”

En UI preferir la etiqueta **“Condiciones actuales”**.

No afirmar que cada dato es una medición física instantánea de una estación concreta si el proveedor usa modelos/nowcast.

Mostrar:

- “Actualizado HH:mm”;
- zona horaria local.

## 12. Política de proveedor

Crear configuración:

```env
WEATHER_PROVIDER=open_meteo
```

La fábrica podrá soportar:

```text
open_meteo
provider_x
provider_y
```

sin cambiar casos de uso.

## 13. Rate limits

El backend deberá:

- cachear;
- evitar duplicate requests;
- limitar búsquedas abusivas;
- responder 429 propio cuando aplique;
- respetar términos/licencia del proveedor configurado.

Antes de un despliegue comercial, revisar la licencia/plan vigente del proveedor.

## 14. Fallback futuro

No implementar en MVP salvo tiempo disponible, pero diseñar extensión:

1. primary provider;
2. fallback provider;
3. circuit breaker opcional.

## 15. Tests

Fixtures locales representativas:

- Perú;
- EE. UU.;
- Japón;
- Alemania;
- ubicación sin admin4;
- ubicación sin población;
- clima con lluvia;
- nieve;
- tormenta;
- horario nocturno.

Nunca depender exclusivamente de snapshots enormes de terceros.
