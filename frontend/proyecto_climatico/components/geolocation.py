import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def geolocation_button() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon(tag="map_pin", size=18, color=Theme.PRIMARY),
            rx.text("Usar mi ubicación", font_size="14px", font_weight="medium"),
            variant="soft",
            color_scheme="blue",
            border_radius=Theme.RADIUS_INPUT,
            cursor="pointer",
            on_click=rx.call_script(
                """
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (pos) => {
                            const coords = { latitude: pos.coords.latitude, longitude: pos.coords.longitude };
                            // send event to Reflex backend state
                            rx.raise(new CustomEvent('geo_success', { detail: coords }));
                        },
                        (err) => {
                            rx.raise(new CustomEvent('geo_error', { detail: err.message }));
                        }
                    );
                }
                """
            ),
        ),
        rx.cond(
            AppState.using_geolocation,
            rx.badge(
                "Ubicación aproximada activa", color_scheme="blue", variant="solid"
            ),
        ),
        align_items="center",
        spacing="3",
    )
