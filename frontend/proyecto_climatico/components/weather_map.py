import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def weather_map() -> rx.Component:
    lat = AppState.selected_location["latitude"]
    lon = AppState.selected_location["longitude"]
    loc_name = AppState.selected_location["name"]

    # OpenStreetMap iframe embed link for responsive interactive map
    map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={lon - 0.15}%2C{lat - 0.15}%2C{lon + 0.15}%2C{lat + 0.15}&layer=mapnik&marker={lat}%2C{lon}"

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="map", size=20, color=Theme.PRIMARY),
                rx.heading(
                    f"Mapa de ubicación: {loc_name}", size="5", color=Theme.TEXT_PRIMARY
                ),
                spacing="2",
                align_items="center",
            ),
            rx.text(
                f"Coordenadas: {lat:.4f}°, {lon:.4f}°",
                font_size="13px",
                color=Theme.TEXT_SECONDARY,
            ),
            rx.box(
                rx.html(
                    f'<iframe width="100%" height="280" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{map_url}" style="border-radius: 12px; border: 1px solid #E2E8F0;"></iframe>'
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
