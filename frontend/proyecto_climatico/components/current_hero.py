import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def weather_metric_card(icon_tag: str, label: str, value: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon(tag=icon_tag, size=20, color=Theme.PRIMARY),
            rx.vstack(
                rx.text(
                    label,
                    font_size="12px",
                    color=Theme.TEXT_SECONDARY,
                    font_weight="500",
                ),
                rx.text(
                    value, font_size="15px", color=Theme.TEXT_PRIMARY, font_weight="700"
                ),
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
    curr = AppState.weather_data["current"]
    units = AppState.weather_data["units"]
    loc_display = AppState.selected_location["display_name"]
    observed_time = AppState.weather_data["observed_at"]

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.badge(
                        "Condiciones actuales", color_scheme="blue", variant="soft"
                    ),
                    rx.heading(
                        AppState.selected_location["name"],
                        size="8",
                        color=Theme.TEXT_PRIMARY,
                    ),
                    rx.text(loc_display, font_size="14px", color=Theme.TEXT_SECONDARY),
                    rx.text(
                        f"Actualizado: {observed_time}",
                        font_size="12px",
                        color=Theme.CLOUDY,
                    ),
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
                    f"{curr['temperature']:.0f}{units['temperature']}",
                    font_size="64px",
                    font_weight="800",
                    color=Theme.TEXT_PRIMARY,
                    line_height="1",
                ),
                rx.vstack(
                    rx.text(
                        curr["weather_label"],
                        font_size="20px",
                        font_weight="600",
                        color=Theme.PRIMARY,
                    ),
                    rx.text(
                        f"Sensación térmica: {curr['apparent_temperature']:.0f}{units['temperature']}",
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
                weather_metric_card(
                    "droplet", "Humedad", f"{curr['relative_humidity']}%"
                ),
                weather_metric_card(
                    "wind",
                    "Viento",
                    f"{curr['wind_speed']:.1f} {units['wind_speed']} ({curr['wind_direction']}°)",
                ),
                weather_metric_card(
                    "wind", "Ráfagas", f"{curr['wind_gusts']:.1f} {units['wind_speed']}"
                ),
                weather_metric_card(
                    "cloud_rain",
                    "Precipitación",
                    f"{curr['precipitation']:.1f} {units['precipitation']}",
                ),
                weather_metric_card(
                    "gauge", "Presión", f"{curr['surface_pressure']:.0f} hPa"
                ),
                weather_metric_card("cloud", "Nubosidad", f"{curr['cloud_cover']}%"),
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
