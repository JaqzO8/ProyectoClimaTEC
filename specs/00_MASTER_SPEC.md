# SPEC-00 — Especificación maestra de ProyectoClimatico

**ID:** SPEC-00  
**Estado:** obligatorio  
**Prioridad:** P0  
**Repositorio:** `ProyectoClimatico`

## 1. Visión

ProyectoClimatico será una aplicación web global para consultar clima actual y pronósticos de ubicaciones de cualquier país, desde una localidad concreta hasta ciudades y divisiones administrativas regionales.

La experiencia debe ser rápida, limpia, visualmente atractiva, accesible y útil tanto en escritorio como en móvil.

## 2. Principios no negociables

1. Python será el lenguaje principal.
2. Backend y frontend tendrán especificaciones separadas.
3. La lógica meteorológica no estará acoplada directamente a Open-Meteo.
4. Todo acceso a proveedores externos deberá ocurrir mediante adaptadores.
5. Nunca se expondrán secretos en el frontend.
6. El proyecto deberá ejecutarse completamente con `docker compose up --build`.
7. El repositorio Git se llamará `ProyectoClimatico`.
8. El despliegue objetivo será AWS.
9. La infraestructura AWS deberá poder recrearse con Terraform.
10. Se aplicarán pruebas automatizadas, tipado, linting, seguridad y observabilidad.
11. No se aceptará código con credenciales hardcodeadas.
12. No se aceptará una UI que solo funcione en una resolución.
13. La interfaz tendrá fondo predominantemente blanco.
14. Todo endpoint público deberá validar entradas y manejar errores.
15. La aplicación deberá degradarse correctamente cuando el proveedor climático falle.

## 3. Objetivos funcionales

### FR-M-001 — Búsqueda global

El usuario podrá buscar lugares por nombre.

La respuesta deberá mostrar, cuando exista:

- nombre;
- país;
- código de país;
- latitud;
- longitud;
- zona horaria;
- `admin1`;
- `admin2`;
- `admin3`;
- `admin4`.

### FR-M-002 — Ubicación actual

El usuario podrá autorizar la geolocalización del navegador.

Si acepta:

- se tomarán latitud y longitud;
- se consultará el clima actual;
- la aplicación indicará que se está usando su ubicación aproximada.

Si rechaza:

- no debe producirse ningún error;
- se mostrará el buscador como vía principal.

### FR-M-003 — Condiciones actuales

Como mínimo:

- temperatura;
- sensación térmica;
- humedad;
- condición/WMO code traducida;
- precipitación;
- nubosidad;
- presión;
- velocidad del viento;
- dirección del viento;
- ráfagas;
- indicador día/noche;
- hora local de los datos.

### FR-M-004 — Pronóstico horario

Mostrar al menos las siguientes 24 horas y permitir ampliar hasta 48/72 según diseño.

Variables mínimas:

- temperatura;
- precipitación/probabilidad;
- humedad;
- viento;
- código meteorológico.

### FR-M-005 — Pronóstico diario

Mostrar 7 días por defecto.

Debe incluir:

- máxima;
- mínima;
- precipitación;
- probabilidad máxima de precipitación;
- amanecer;
- atardecer;
- viento máximo;
- condición principal.

La arquitectura permitirá ampliar el horizonte hasta el máximo disponible del proveedor.

### FR-M-006 — Vista geográfica

Mostrar un mapa interactivo con:

- posición seleccionada;
- nombre de la ubicación;
- coordenadas;
- información climática resumida.

No se deberá confundir un mapa puntual con un radar meteorológico. Si en una futura versión se añaden tiles meteorológicos, se implementarán mediante un proveedor específico y licencia compatible.

### FR-M-007 — Cambio de unidades

Permitir como mínimo:

- Celsius / Fahrenheit;
- km/h / m/s / mph;
- mm / pulgadas.

Preferencias persistidas localmente en el navegador.

### FR-M-008 — Idioma

MVP:

- español como idioma inicial;
- infraestructura de textos preparada para i18n;
- no hardcodear textos en componentes complejos si impide internacionalización futura.

### FR-M-009 — Estados meteorológicos

El diseño podrá modificar iconografía y acentos según:

- despejado;
- parcialmente nublado;
- nublado;
- niebla;
- lluvia;
- tormenta;
- nieve.

El fondo general seguirá siendo claro/blanco.

## 4. Requisitos no funcionales

### NFR-M-001 — Rendimiento

Objetivos iniciales:

- health check backend: p95 < 150 ms en condiciones normales;
- endpoints cacheados: p95 < 500 ms;
- llamada meteorológica sin caché: objetivo p95 < 2.5 s, sujeto al proveedor;
- UI debe mostrar skeleton/loading sin bloquear la pantalla;
- evitar payloads innecesarios.

### NFR-M-002 — Accesibilidad

Objetivo WCAG 2.2 AA:

- navegación por teclado;
- foco visible;
- texto con contraste suficiente;
- labels accesibles;
- `aria-*` donde corresponda;
- no depender solo del color para transmitir estado.

### NFR-M-003 — Compatibilidad

Últimas versiones estables de:

- Chrome/Chromium;
- Firefox;
- Edge;
- Safari.

Viewport mínimo de referencia: 320 px.

### NFR-M-004 — Resiliencia

Ante error del proveedor:

- devolver error normalizado;
- UI con mensaje claro;
- botón reintentar;
- conservar última selección del usuario;
- no mostrar stack traces.

### NFR-M-005 — Seguridad

- HTTPS en producción;
- headers de seguridad;
- CORS explícito;
- rate limiting configurable;
- secretos por variables de entorno / AWS;
- dependencias auditables;
- imágenes Docker no ejecutadas como root siempre que sea viable.

## 5. Arquitectura lógica

```text
Browser
   |
   v
Frontend Reflex
   |
   | HTTPS /api/v1/*
   v
FastAPI API
   |
   +--> Application Services / Use Cases
   |
   +--> WeatherProvider interface
           |
           +--> OpenMeteoWeatherProvider
```

## 6. Estructura de repositorio requerida

```text
ProyectoClimatico/
├─ README.md
├─ LICENSE
├─ .gitignore
├─ .editorconfig
├─ .env.example
├─ compose.yml
├─ Makefile
├─ backend/
│  ├─ pyproject.toml
│  ├─ Dockerfile
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ api/
│  │  │  └─ v1/
│  │  ├─ core/
│  │  ├─ domain/
│  │  ├─ application/
│  │  └─ infrastructure/
│  └─ tests/
├─ frontend/
│  ├─ pyproject.toml
│  ├─ Dockerfile
│  ├─ rxconfig.py
│  ├─ proyecto_climatico/
│  │  ├─ pages/
│  │  ├─ components/
│  │  ├─ state/
│  │  ├─ services/
│  │  ├─ styles/
│  │  └─ assets/
│  └─ tests/
├─ infra/
│  └─ terraform/
│     ├─ modules/
│     ├─ envs/
│     │  ├─ dev/
│     │  └─ prod/
│     └─ README.md
├─ specs/
├─ scripts/
├─ tests/
│  └─ e2e/
└─ .github/
   └─ workflows/
```

## 7. Clean Architecture pragmática

Dependencias permitidas:

```text
domain <- application <- infrastructure
             ^
             |
            api
```

- `domain`: modelos y reglas sin FastAPI ni HTTPX.
- `application`: casos de uso y puertos/interfaces.
- `infrastructure`: Open-Meteo, caché, logging, configuración.
- `api`: routers, DTOs HTTP, dependencias.

No crear abstracciones sin uso. Aplicar SOLID donde reduzca acoplamiento, no por ceremonia.

## 8. Definition of Done global

El proyecto no se considera terminado hasta que:

- [ ] `docker compose up --build` levante backend y frontend.
- [ ] `/health` responda correctamente.
- [ ] el usuario pueda buscar Tingo María, Lima, Cusco, Nueva York, Tokio u otra ubicación válida.
- [ ] pueda utilizar geolocalización si concede permiso.
- [ ] pueda ver clima actual.
- [ ] pueda ver pronóstico horario.
- [ ] pueda ver pronóstico diario.
- [ ] pueda cambiar unidades.
- [ ] exista vista móvil funcional.
- [ ] backend tenga OpenAPI/Swagger.
- [ ] linters y type checks pasen.
- [ ] tests unitarios/integración pasen.
- [ ] exista cobertura mínima establecida.
- [ ] Docker healthchecks pasen.
- [ ] Terraform tenga `fmt`, `validate` y documentación.
- [ ] CI pase en `main`.
- [ ] no existan secretos versionados.
- [ ] exista documentación de despliegue AWS.
