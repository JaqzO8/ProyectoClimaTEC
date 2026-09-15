import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def weather_map() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="map", size=20, color=Theme.PRIMARY),
                rx.heading(
                    "Mapa de ubicación: " + AppState.selected_location["name"].to(str),
                    size="5",
                    color=Theme.TEXT_PRIMARY,
                ),
                spacing="2",
                align_items="center",
            ),
            rx.text(
                AppState.coordinates_display,
                font_size="13px",
                color=Theme.TEXT_SECONDARY,
            ),
            rx.box(
                rx.cond(
                    AppState.using_geolocation,
                    rx.text(
                        "Tu ubicación aproximada se muestra arriba. El mapa externo está desactivado para proteger tu ubicación."
                    ),
                    rx.el.iframe(
                        src=AppState.map_embed_url,
                        title="Mapa de la ubicación seleccionada",
                        width="100%",
                        height="280",
                        loading="lazy",
                        style={"border": "0"},
                    ),
                ),
                width="100%",
                height="280px",
                border_radius=Theme.RADIUS_INPUT,
                overflow="hidden",
                margin_top="12px",
            ),
            spacing="3",
            align_items="start",
            width="100%",
        ),
        background=Theme.BACKGROUND,
        border=f"1px solid {Theme.BORDER}",
        border_radius=Theme.RADIUS_CARD,
        padding="24px",
        width="100%",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)",
    )
