import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def unit_selector_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Configuración de unidades", color=Theme.TEXT_PRIMARY),
            rx.dialog.description(
                "Selecciona tus preferencias de unidades meteorológicas.",
                color=Theme.TEXT_SECONDARY,
                margin_bottom="16px",
            ),
            rx.vstack(
                # Temperature
                rx.vstack(
                    rx.text("Temperatura", font_weight="600", font_size="14px", color=Theme.TEXT_PRIMARY),
                    rx.hstack(
                        rx.button(
                            "Celsius (°C)",
                            variant=rx.cond(AppState.temperature_unit == "celsius", "solid", "outline"),
                            on_click=AppState.set_temperature_unit("celsius"),
                        ),
                        rx.button(
                            "Fahrenheit (°F)",
                            variant=rx.cond(AppState.temperature_unit == "fahrenheit", "solid", "outline"),
                            on_click=AppState.set_temperature_unit("fahrenheit"),
                        ),
                        spacing="2",
                    ),
                    align_items="start",
                    spacing="2",
                ),
                # Wind speed
                rx.vstack(
                    rx.text("Velocidad del viento", font_weight="600", font_size="14px", color=Theme.TEXT_PRIMARY),
                    rx.hstack(
                        rx.button(
                            "km/h",
                            variant=rx.cond(AppState.wind_speed_unit == "kmh", "solid", "outline"),
                            on_click=AppState.set_wind_speed_unit("kmh"),
                        ),
                        rx.button(
                            "m/s",
                            variant=rx.cond(AppState.wind_speed_unit == "ms", "solid", "outline"),
                            on_click=AppState.set_wind_speed_unit("ms"),
                        ),
                        rx.button(
                            "mph",
                            variant=rx.cond(AppState.wind_speed_unit == "mph", "solid", "outline"),
                            on_click=AppState.set_wind_speed_unit("mph"),
                        ),
                        spacing="2",
                    ),
                    align_items="start",
                    spacing="2",
                ),
                # Precipitation
                rx.vstack(
                    rx.text("Precipitación", font_weight="600", font_size="14px", color=Theme.TEXT_PRIMARY),
                    rx.hstack(
                        rx.button(
                            "Milímetros (mm)",
                            variant=rx.cond(AppState.precipitation_unit == "mm", "solid", "outline"),
                            on_click=AppState.set_precipitation_unit("mm"),
                        ),
                        rx.button(
                            "Pulgadas (inch)",
                            variant=rx.cond(AppState.precipitation_unit == "inch", "solid", "outline"),
                            on_click=AppState.set_precipitation_unit("inch"),
                        ),
                        spacing="2",
                    ),
                    align_items="start",
                    spacing="2",
                ),
                spacing="5",
                width="100%",
            ),
            rx.hstack(
                rx.dialog.close(
                    rx.button("Cerrar", variant="soft", color_scheme="gray", on_click=AppState.toggle_unit_modal),
                ),
                justify="end",
                margin_top="24px",
            ),
            background=Theme.BACKGROUND,
            border_radius=Theme.RADIUS_CARD,
            padding="24px",
            max_width="450px",
        ),
        open=AppState.is_unit_modal_open,
        on_open_change=AppState.toggle_unit_modal,
    )
