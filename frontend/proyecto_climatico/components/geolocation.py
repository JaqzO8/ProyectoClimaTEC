import reflex as rx

from proyecto_climatico.state.app_state import AppState


def geolocation_button() -> rx.Component:
    return rx.vstack(
        rx.button(
            rx.icon(tag="map_pin", size=18),
            "Usar mi ubicación",
            min_height="44px",
            variant="soft",
            on_click=rx.call_script(
                """new Promise((resolve) => {
                    if (!navigator.geolocation) {
                        resolve({error: 'unavailable'});
                        return;
                    }
                    navigator.geolocation.getCurrentPosition(
                        (pos) => resolve({latitude: pos.coords.latitude, longitude: pos.coords.longitude}),
                        () => resolve({error: 'denied'}),
                        {timeout: 10000, maximumAge: 300000, enableHighAccuracy: false}
                    );
                })""",
                callback=AppState.handle_geolocation_result,
            ),
        ),
        rx.cond(AppState.using_geolocation, rx.badge("Ubicación aproximada activa")),
        rx.cond(
            AppState.geolocation_error != "",
            rx.text(AppState.geolocation_error, role="status", size="2"),
        ),
        align_items="start",
    )
