import reflex as rx

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def location_search_item(item: rx.Var[dict]) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                item["name"],
                font_weight="600",
                color=Theme.TEXT_PRIMARY,
                font_size="15px",
            ),
            rx.text(item["display_name"], font_size="13px", color=Theme.TEXT_SECONDARY),
            spacing="1",
            align_items="start",
        ),
        padding="12px 16px",
        width="100%",
        cursor="pointer",
        _hover={"background": Theme.SURFACE_ALT},
        on_click=AppState.select_location(item),
        border_bottom=f"1px solid {Theme.BORDER}",
    )


def location_search() -> rx.Component:
    return rx.vstack(
        rx.text(
            "¿Qué tiempo hace?",
            font_size="22px",
            font_weight="700",
            color=Theme.TEXT_PRIMARY,
        ),
        rx.box(
            rx.input(
                rx.input.slot(
                    rx.icon(tag="search", size=18, color=Theme.TEXT_SECONDARY)
                ),
                placeholder="Buscar ciudad, provincia, región...",
                value=AppState.search_query,
                on_change=AppState.handle_search_change,
                width="100%",
                size="3",
                border_radius=Theme.RADIUS_INPUT,
                border_color=Theme.BORDER,
                background=Theme.BACKGROUND,
                color=Theme.TEXT_PRIMARY,
            ),
            rx.cond(
                AppState.is_searching,
                rx.box(
                    rx.spinner(size="2", color=Theme.PRIMARY),
                    position="absolute",
                    right="12px",
                    top="12px",
                    z_index="10",
                ),
            ),
            width="100%",
            position="relative",
        ),
        rx.cond(
            AppState.search_results.length() > 0,
            rx.box(
                rx.foreach(
                    AppState.search_results,
                    location_search_item,
                ),
                position="absolute",
                top="100%",
                left="0",
                width="100%",
                background=Theme.BACKGROUND,
                border=f"1px solid {Theme.BORDER}",
                border_radius=Theme.RADIUS_INPUT,
                box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                z_index="50",
                max_height="320px",
                overflow_y="auto",
                margin_top="6px",
            ),
        ),
        width="100%",
        position="relative",
        spacing="2",
    )
