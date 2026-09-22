import reflex as rx

from proyecto_climatico.styles.theme import Theme


def app_header(on_open_units) -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.badge("🚀 ENTORNO ACTIVO: PruebaRama", color_scheme="cyan", variant="solid", size="2"),
                rx.text(
                    "Despliegue y Validación en Vivo AWS EC2 • Quality Gate ≥ 80% Aprobado",
                    font_weight="bold",
                    font_size="13px",
                    color="white",
                ),
                rx.badge("AWS Live", color_scheme="green", variant="solid", size="1"),
                spacing="3",
                align_items="center",
                justify="center",
                flex_wrap="wrap",
            ),
            background="linear-gradient(90deg, #1e3a8a 0%, #0284c7 50%, #0d9488 100%)",
            padding="8px 16px",
            width="100%",
            box_shadow="0 2px 8px rgba(0, 0, 0, 0.12)",
        ),
        rx.hstack(
            rx.hstack(
                rx.icon(tag="cloud_sun", size=32, color=Theme.PRIMARY),
                rx.heading(
                    "ProyectoClimatico",
                    size=rx.breakpoints(initial="4", sm="6"),
                    color=Theme.TEXT_PRIMARY,
                    font_weight="bold",
                ),
                rx.badge("PruebaRama • AWS Live", color_scheme="blue", variant="surface", size="2"),
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
        ),
        spacing="0",
        width="100%",
    )
