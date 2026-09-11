# SPEC-08 — Criterios de aceptación en Gherkin

**ID:** SPEC-08  
**Prioridad:** P0

```gherkin
Feature: Consulta de clima global

  Scenario: Buscar una ciudad válida
    Given que el usuario está en la página principal
    When escribe "Tingo María" en el buscador
    Then el sistema debe mostrar resultados geográficos coincidentes
    And cada resultado debe incluir país y niveles administrativos disponibles

  Scenario: Seleccionar una ubicación
    Given que existen resultados de búsqueda
    When el usuario selecciona una ubicación
    Then el frontend debe solicitar el resumen climático al backend
    And debe mostrar las condiciones actuales
    And debe mostrar el pronóstico horario
    And debe mostrar el pronóstico diario

  Scenario: Buscar ubicación de otro país
    Given que el usuario está en la página principal
    When busca "Tokyo"
    Then deben aparecer resultados de Japón
    And el sistema no debe depender de términos administrativos exclusivos de Perú

  Scenario: Utilizar geolocalización
    Given que el navegador soporta geolocalización
    When el usuario presiona "Usar mi ubicación"
    And autoriza el permiso
    Then el sistema debe consultar clima para esas coordenadas
    And debe mostrar la hora correspondiente a la zona de la ubicación

  Scenario: Rechazar geolocalización
    Given que el usuario presiona "Usar mi ubicación"
    When rechaza el permiso
    Then la aplicación debe continuar operativa
    And debe invitar a utilizar el buscador

  Scenario: Cambiar a Fahrenheit
    Given que el usuario visualiza una ubicación
    When cambia la unidad de temperatura a Fahrenheit
    Then las temperaturas deben mostrarse en Fahrenheit
    And la preferencia debe conservarse localmente

  Scenario: Proveedor climático no disponible
    Given que el proveedor meteorológico devuelve un error temporal
    When el backend intenta obtener condiciones actuales
    Then debe devolver un error normalizado
    And el frontend debe mostrar un mensaje comprensible
    And debe ofrecer reintentar

  Scenario: Timeout del proveedor
    Given que el proveedor no responde dentro del timeout configurado
    When el backend realiza la solicitud
    Then debe terminar la operación sin bloquear indefinidamente
    And debe devolver WEATHER_PROVIDER_TIMEOUT

Feature: Interfaz responsive

  Scenario: Visualizar en teléfono
    Given un viewport de 320 pixeles de ancho
    When la página principal carga
    Then no debe existir overflow horizontal global
    And las acciones principales deben seguir siendo accesibles
    And la temperatura actual debe permanecer claramente visible

Feature: Accesibilidad

  Scenario: Usar el buscador con teclado
    Given que el foco está en el buscador
    When el usuario escribe una ubicación
    And usa flecha abajo
    And presiona Enter
    Then debe poder seleccionar un resultado sin utilizar mouse

Feature: Docker

  Scenario: Arranque local
    Given un checkout limpio del repositorio
    And Docker está instalado
    And existe configuración basada en .env.example
    When se ejecuta "docker compose up --build"
    Then backend debe alcanzar estado healthy
    And frontend debe alcanzar estado healthy
    And el frontend debe poder consultar el backend

Feature: AWS

  Scenario: Desplegar commit de main
    Given que CI pasó
    And GitHub dispone de autorización OIDC para AWS
    When se ejecuta el workflow de despliegue
    Then se deben publicar imágenes etiquetadas por SHA en ECR
    And ECS debe ejecutar la revisión nueva
    And el deployment debe esperar a que el servicio quede estable
```
