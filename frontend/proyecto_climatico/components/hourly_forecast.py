import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def hourly_item(item: rx.Var[dict]) -> rx.Component:
    units = AppState.weather_data["units"]
    return rx.box(
        rx.vstack(
            rx.text(
                item["time"],
                font_size="13px",
                color=Theme.TEXT_SECONDARY,
                font_weight="500",
            ),
            rx.icon(tag="cloud_sun", size=24, color=Theme.PRIMARY),
            rx.text(
                f"{item['temperature']:.0f}{units['temperature']}",
                font_size="16px",
                font_weight="700",
                color=Theme.TEXT_PRIMARY,
            ),
            rx.hstack(
                rx.icon(tag="droplet", size=12, color=Theme.ACCENT),
                rx.text(
                    f"{item['precipitation_probability']}%",
                    font_size="12px",
                    color=Theme.ACCENT,
                    font_weight="600",
                ),
                spacing="1",
                align_items="center",
            ),
            spacing="2",
            align_items="center",
        ),
        background=Theme.SURFACE,
        border=f"1px solid {Theme.BORDER}",
        border_radius=Theme.RADIUS_INPUT,
        padding="14px 18px",
        min_width="96px",
        text_align="center",
    )


def hourly_forecast() -> rx.Component:
    hourly_list = AppState.weather_data["hourly"]
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="clock", size=20, color=Theme.PRIMARY),
                rx.heading(
                    "Pronóstico por horas (próximas 24h)",
                    size="5",
                    color=Theme.TEXT_PRIMARY,
                ),
                spacing="2",
                align_items="center",
            ),
            rx.hstack(
                rx.foreach(hourly_list, hourly_item),
                overflow_x="auto",
                width="100%",
                padding_bottom="12px",
                spacing="3",
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
