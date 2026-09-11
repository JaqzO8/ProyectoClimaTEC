# SPEC-02 — Frontend climático con Reflex

**ID:** SPEC-02  
**Prioridad:** P0  
**Tecnología:** Python + Reflex

## 1. Propósito

Construir una interfaz climática clara, moderna y responsive usando Python como lenguaje principal.

## 2. Principios visuales

### Estilo general

- fondo principal blanco;
- sensación ligera, limpia y tecnológica;
- tarjetas con profundidad sutil;
- acentos azules/celestes;
- iconografía meteorológica consistente;
- gradientes extremadamente suaves, no saturados;
- evitar fondos oscuros dominantes.

### Tokens de diseño

```text
color.background      #FFFFFF
color.surface         #F8FAFC
color.surface_alt     #F1F5F9
color.primary         #2563EB
color.primary_hover   #1D4ED8
color.accent          #0EA5E9
color.text_primary    #0F172A
color.text_secondary  #475569
color.border          #E2E8F0
color.success         #15803D
color.warning         #B45309
color.danger          #B91C1C
```

Colores meteorológicos secundarios:

```text
sunny      #F59E0B
cloudy     #64748B
rain       #0284C7
storm      #4F46E5
snow       #7DD3FC
```

No usar los colores secundarios para texto crítico si no cumplen contraste.

### Tipografía

Preferir fuente de sistema para reducir dependencias:

```css
system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

Escala sugerida:

- H1: 36/44 desktop, 28/36 mobile;
- H2: 28/36;
- H3: 20/28;
- body: 16/24;
- caption: 14/20.

### Espaciado

Sistema base 8 px:

- 4;
- 8;
- 12;
- 16;
- 24;
- 32;
- 48;
- 64.

### Bordes

- cards: 16 px;
- inputs: 12 px;
- chips: 999 px;
- borde: 1 px `#E2E8F0`.

## 3. Leyes y principios UX obligatorios

Aplicar:

- jerarquía visual;
- proximidad de Gestalt;
- similitud;
- región común;
- Ley de Hick: evitar exceso de acciones simultáneas;
- Ley de Fitts: targets táctiles suficientes;
- consistencia de Nielsen;
- visibilidad del estado del sistema;
- prevención de errores;
- reconocimiento antes que recuerdo;
- progressive disclosure;
- mobile-first;
- accesibilidad WCAG 2.2 AA.

## 4. Estructura de pantalla principal

```text
┌────────────────────────────────────────────┐
│ Logo / ProyectoClimatico      Unidades ⚙  │
├────────────────────────────────────────────┤
│ "¿Qué tiempo hace?"                       │
│ [ Buscar ciudad, provincia, región... ] 🔎│
│ [ Usar mi ubicación ]                     │
├────────────────────────────────────────────┤
│ Tingo María, Huánuco, Perú                │
│ 28°    Parcialmente nublado               │
│ Sensación 30°                             │
│ humedad | viento | lluvia | presión       │
├────────────────────────────────────────────┤
│ Próximas horas → carrusel/gráfico          │
├────────────────────────────────────────────┤
│ Pronóstico 7 días                         │
├────────────────────────────────────────────┤
│ Mapa de ubicación                         │
└────────────────────────────────────────────┘
```

## 5. Componentes

Crear componentes reutilizables:

- `AppHeader`
- `LocationSearch`
- `LocationSearchResult`
- `CurrentWeatherHero`
- `WeatherMetric`
- `HourlyForecast`
- `DailyForecast`
- `WeatherMap`
- `UnitSelector`
- `GeolocationButton`
- `WeatherIcon`
- `LoadingSkeleton`
- `InlineError`
- `EmptyState`
- `Footer`

No crear componentes monolíticos >250 líneas salvo justificación.

## 6. Buscador

Comportamiento:

1. No consultar por menos de 2 caracteres.
2. Debounce 300–450 ms.
3. Estado loading visible.
4. Flechas ↑↓ para navegar resultados.
5. Enter selecciona.
6. Escape cierra.
7. Mouse/touch soportados.
8. Mostrar jerarquía administrativa para desambiguar.
9. Mostrar país/código.
10. Evitar solicitar clima para todos los resultados; solo al seleccionar.

## 7. Clima actual

Hero principal:

- ubicación;
- fecha/hora local;
- temperatura grande;
- descripción;
- sensación térmica;
- icono;
- 4–6 métricas secundarias.

La UI debe diferenciar claramente dato actual de pronóstico.

## 8. Pronóstico horario

Desktop:

- gráfico o fila desplazable;
- al menos 12–24 puntos visibles según ancho.

Mobile:

- scroll horizontal accesible;
- no comprimir texto hasta hacerlo ilegible.

## 9. Pronóstico diario

Cards/filas con:

- día;
- icono;
- estado;
- máxima;
- mínima;
- precipitación;
- viento.

## 10. Vista mapa

La ubicación debe representarse con un mapa interactivo.

Requisitos:

- marker seleccionable;
- zoom inicial coherente;
- responsive;
- fallback textual con coordenadas si el mapa falla;
- no bloquear el resto de la página si la librería cartográfica falla.

La implementación puede usar MapLibre/Leaflet mediante componente compatible. Si se requiere una pequeña capa JS para integrar el mapa, aislarla y documentarla; no mover lógica de negocio meteorológica a JavaScript.

## 11. Responsive

Breakpoints orientativos:

- mobile: <640;
- tablet: 640–1023;
- desktop: >=1024.

No codificar el layout para un dispositivo específico.

## 12. Estados de interfaz

Todo módulo remoto debe tener:

- idle;
- loading;
- success;
- empty;
- error.

Ejemplo error:

> No pudimos actualizar el clima en este momento. Reintentar.

No mostrar mensajes técnicos de HTTP al usuario final.

## 13. Accesibilidad

- contraste AA;
- botones >=44x44 CSS px cuando sea razonable;
- focus ring visible;
- inputs con label;
- resultados de autocomplete accesibles;
- `aria-live` para mensajes de actualización pertinentes;
- respetar `prefers-reduced-motion`;
- animaciones <=250 ms por defecto;
- no usar autoplay decorativo.

## 14. Geolocalización y privacidad

- solicitar permiso solo como consecuencia de una acción del usuario;
- explicar brevemente el motivo;
- no almacenar coordenadas en servidor;
- no enviar ubicación a servicios distintos del backend;
- rechazo de permiso = flujo normal, no error fatal.

## 15. Estado de aplicación

Estado mínimo:

- ubicación seleccionada;
- resultados de búsqueda;
- clima;
- unidades;
- loading/error;
- preferencia de unidades.

Persistir solo preferencias no sensibles en local storage.

## 16. Criterios de aceptación

- [ ] 320 px sin overflow horizontal global.
- [ ] funciona con teclado.
- [ ] fondo principal blanco.
- [ ] buscador global legible.
- [ ] ubicación administrativa clara.
- [ ] clima actual domina la jerarquía visual.
- [ ] hourly y daily diferenciados.
- [ ] mapa responsive.
- [ ] estados loading/error completos.
- [ ] selector de unidades funcional.
- [ ] Lighthouse/axe sin errores críticos de accesibilidad.
