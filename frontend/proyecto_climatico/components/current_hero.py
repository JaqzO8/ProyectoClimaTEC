import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def weather_metric_card(icon_tag: str, label: str, value: rx.Var[str]) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon(tag=icon_tag, size=20, color=Theme.PRIMARY),
            rx.vstack(
                rx.text(label, font_size="12px", color=Theme.TEXT_SECONDARY, font_weight="500"),
                rx.text(value, font_size="15px", color=Theme.TEXT_PRIMARY, font_weight="700"),
                spacing="0",
                align_items="start",
            ),
            spacing="3",
            align_items="center",
        ),
        background=Theme.SURFACE,
        border=f"1px solid {Theme.BORDER}",
        border_radius=Theme.RADIUS_INPUT,
        padding="12px 16px",
        width="100%",
    )


def current_weather_hero() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.badge("Condiciones actuales", color_scheme="blue", variant="soft"),
                    rx.heading(AppState.selected_location["name"], size="8", color=Theme.TEXT_PRIMARY),
                    rx.text(AppState.selected_location["display_name"], font_size="14px", color=Theme.TEXT_SECONDARY),
                    rx.text(f"Actualizado: {AppState.observed_at_display}", font_size="12px", color=Theme.CLOUDY),
                    align_items="start",
                    spacing="1",
                ),
                rx.icon(tag="sun", size=64, color=Theme.SUNNY),
                width="100%",
                justify="between",
                align_items="start",
            ),
            rx.hstack(
                rx.text(
                    AppState.current_temp_display,
                    font_size="64px",
                    font_weight="800",
                    color=Theme.TEXT_PRIMARY,
                    line_height="1",
                ),
                rx.vstack(
                    rx.text(AppState.current_weather_label, font_size="20px", font_weight="600", color=Theme.PRIMARY),
                    rx.text(
                        AppState.current_apparent_temp_display,
                        font_size="14px",
                        color=Theme.TEXT_SECONDARY,
                    ),
                    align_items="start",
                    spacing="0",
                ),
                spacing="5",
                align_items="center",
                margin_top="16px",
                margin_bottom="24px",
            ),
            rx.grid(
                weather_metric_card("droplet", "Humedad", AppState.current_humidity),
                weather_metric_card("wind", "Viento", AppState.current_wind_display),
                weather_metric_card("wind", "Ráfagas", AppState.current_gusts_display),
                weather_metric_card("cloud_rain", "Precipitación", AppState.current_precip_display),
                weather_metric_card("gauge", "Presión", AppState.current_pressure_display),
                weather_metric_card("cloud", "Nubosidad", AppState.current_cloud_display),
                columns="3",
                spacing="3",
                width="100%",
            ),
            width="100%",
            align_items="start",
        ),
        background=Theme.BACKGROUND,
        border=f"1px solid {Theme.BORDER}",
        border_radius=Theme.RADIUS_CARD,
        padding="28px",
        width="100%",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)",
    )
