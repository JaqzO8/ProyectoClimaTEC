import reflex as rx

from proyecto_climatico.components.current_hero import current_weather_hero
from proyecto_climatico.components.daily_forecast import daily_forecast
from proyecto_climatico.components.geolocation import geolocation_button
from proyecto_climatico.components.header import app_header
from proyecto_climatico.components.hourly_forecast import hourly_forecast
from proyecto_climatico.components.search import location_search
from proyecto_climatico.components.status_views import (
    app_footer,
    empty_state,
    inline_error,
    loading_skeleton,
)
from proyecto_climatico.components.unit_selector import unit_selector_dialog
from proyecto_climatico.components.weather_map import weather_map
from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def index() -> rx.Component:
    return rx.box(
        app_header(on_open_units=AppState.toggle_unit_modal),
        rx.container(
            rx.vstack(
                # Search bar & geolocation section
                rx.box(
                    rx.vstack(
                        location_search(),
                        geolocation_button(),
                        spacing="3",
                        width="100%",
                    ),
                    background=Theme.BACKGROUND,
                    border=f"1px solid {Theme.BORDER}",
                    border_radius=Theme.RADIUS_CARD,
                    padding="24px",
                    width="100%",
                    box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)",
                    margin_top="24px",
                    margin_bottom="24px",
                ),
                # Main content state handling
                rx.cond(
                    AppState.is_loading_weather,
                    loading_skeleton(),
                    rx.cond(
                        AppState.has_error,
                        inline_error(),
                        rx.cond(
                            AppState.has_weather_data,
                            rx.vstack(
                                current_weather_hero(),
                                hourly_forecast(),
                                daily_forecast(),
                                weather_map(),
                                spacing="5",
                                width="100%",
                            ),
                            empty_state(),
                        ),
                    ),
                ),
                unit_selector_dialog(),
                app_footer(),
                spacing="4",
                width="100%",
            ),
            size="4",
            padding_x="16px",
        ),
        background=Theme.BACKGROUND,
        min_height="100vh",
        color=Theme.TEXT_PRIMARY,
        font_family=Theme.FONT_FAMILY,
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        panel_background="solid",
    )
)
app.add_page(index, title="ProyectoClimatico — Aplicación Meteorológica Global", on_load=AppState.on_load)
