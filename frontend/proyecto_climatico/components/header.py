import reflex as rx

from proyecto_climatico.styles.theme import Theme


def app_header(on_open_units) -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.icon(tag="cloud_sun", size=32, color=Theme.PRIMARY),
            rx.heading(
                "ProyectoClimatico",
                size=rx.breakpoints(initial="4", sm="6"),
                color=Theme.TEXT_PRIMARY,
                font_weight="bold",
            ),
            spacing="3",
            align_items="center",
        ),
        rx.button(
            rx.icon(tag="settings", size=18),
            rx.text("Unidades ⚙", font_size="14px", font_weight="medium"),
            on_click=on_open_units,
            variant="outline",
            border_color=Theme.BORDER,
            color=Theme.TEXT_PRIMARY,
            background=Theme.BACKGROUND,
            _hover={"background": Theme.SURFACE_ALT},
            border_radius=Theme.RADIUS_INPUT,
            padding="8px 16px",
            cursor="pointer",
        ),
        width="100%",
        justify="between",
        flex_wrap="wrap",
        gap="12px",
        align_items="center",
        padding="16px 24px",
        background=Theme.BACKGROUND,
        border_bottom=f"1px solid {Theme.BORDER}",
    )
