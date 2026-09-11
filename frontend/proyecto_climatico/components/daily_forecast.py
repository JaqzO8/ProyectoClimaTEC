import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def daily_item(item: rx.Var[dict]) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(item["date"].to(str), font_size="15px", font_weight="700", color=Theme.TEXT_PRIMARY),
                rx.text(item["weather_label"].to(str), font_size="13px", color=Theme.TEXT_SECONDARY),
                spacing="0",
                align_items="start",
            ),
            rx.hstack(
                rx.icon(tag="sun", size=24, color=Theme.SUNNY),
                rx.hstack(
                    rx.text(item["temperature_max"].to(str) + "°", font_size="16px", font_weight="700", color=Theme.TEXT_PRIMARY),
                    rx.text("/ " + item["temperature_min"].to(str) + "°", font_size="14px", color=Theme.TEXT_SECONDARY),
                    spacing="1",
                    align_items="baseline",
                ),
                spacing="3",
                align_items="center",
            ),
            rx.hstack(
                rx.hstack(
                    rx.icon(tag="cloud_rain", size=14, color=Theme.ACCENT),
                    rx.text(item["precipitation_sum"].to(str) + " mm", font_size="13px", color=Theme.TEXT_SECONDARY),
                    spacing="1",
                    align_items="center",
                ),
                rx.hstack(
                    rx.icon(tag="wind", size=14, color=Theme.CLOUDY),
                    rx.text(item["wind_speed_max"].to(str) + " km/h", font_size="13px", color=Theme.TEXT_SECONDARY),
                    spacing="1",
                    align_items="center",
                ),
                spacing="4",
                align_items="center",
            ),
            width="100%",
            justify="between",
            align_items="center",
        ),
        background=Theme.SURFACE,
        border=f"1px solid {Theme.BORDER}",
        border_radius=Theme.RADIUS_INPUT,
        padding="14px 20px",
        width="100%",
    )


def daily_forecast() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="calendar", size=20, color=Theme.PRIMARY),
                rx.heading("Pronóstico diario (7 días)", size="5", color=Theme.TEXT_PRIMARY),
                spacing="2",
                align_items="center",
            ),
            rx.vstack(
                rx.foreach(AppState.daily_list, daily_item),
                spacing="2",
                width="100%",
            ),
            spacing="4",
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
