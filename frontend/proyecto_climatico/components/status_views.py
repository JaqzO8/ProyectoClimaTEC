import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def loading_skeleton() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.spinner(size="3", color=Theme.PRIMARY),
                rx.text(
                    "Cargando información meteorológica...",
                    font_size="16px",
                    color=Theme.TEXT_SECONDARY,
                    font_weight="500",
                ),
                spacing="3",
                align_items="center",
            ),
            padding="48px",
            align_items="center",
            justify="center",
            width="100%",
        ),
        background=Theme.SURFACE,
        border=f"1px solid {Theme.BORDER}",
        border_radius=Theme.RADIUS_CARD,
        width="100%",
    )


def inline_error() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="circle_alert", size=24, color=Theme.DANGER),
                rx.vstack(
                    rx.text(
                        "Error de conexión",
                        font_weight="700",
                        color=Theme.DANGER,
                        font_size="16px",
                    ),
                    rx.text(
                        AppState.error_message,
                        color=Theme.TEXT_SECONDARY,
                        font_size="14px",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                spacing="3",
                align_items="start",
            ),
            rx.button(
                rx.icon(tag="refresh_cw", size=16),
                rx.text("Reintentar"),
                on_click=AppState.load_weather,
                color_scheme="red",
                variant="solid",
                size="2",
                margin_top="12px",
                cursor="pointer",
            ),
            spacing="3",
            align_items="start",
        ),
        background="#FEF2F2",
        border="1px solid #FCA5A5",
        border_radius=Theme.RADIUS_CARD,
        padding="20px 24px",
        width="100%",
    )


def empty_state() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.icon(tag="cloud_off", size=48, color=Theme.CLOUDY),
            rx.text(
                "No se encontró información meteorológica",
                font_weight="600",
                color=Theme.TEXT_PRIMARY,
            ),
            rx.text(
                "Prueba a buscar otra ciudad o región en el buscador superior.",
                color=Theme.TEXT_SECONDARY,
                font_size="14px",
            ),
            spacing="3",
            align_items="center",
            padding="48px",
        ),
        background=Theme.SURFACE,
        border=f"1px solid {Theme.BORDER}",
        border_radius=Theme.RADIUS_CARD,
        width="100%",
    )


def app_footer() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.divider(color=Theme.BORDER),
            rx.hstack(
                rx.text(
                    "© 2026 ProyectoClimatico — Aplicación Meteorológica Global",
                    font_size="13px",
                    color=Theme.TEXT_SECONDARY,
                ),
                rx.badge("Entorno: AWS PruebaRama (CI/CD Validated)", color_scheme="blue", variant="surface", size="1"),
                rx.text(
                    "Datos provistos por Open-Meteo API",
                    font_size="13px",
                    color=Theme.PRIMARY,
                ),
                width="100%",
                justify="between",
                align_items="center",
            ),
            spacing="3",
            width="100%",
        ),
        padding="24px 0",
        margin_top="32px",
        width="100%",
    )
