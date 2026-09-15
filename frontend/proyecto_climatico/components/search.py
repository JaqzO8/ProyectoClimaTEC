from typing import Any

import reflex as rx
from reflex.vars import ObjectVar

from proyecto_climatico.state.app_state import AppState
from proyecto_climatico.styles.theme import Theme


def location_search_item(item: ObjectVar[dict[str, Any]]) -> rx.Component:
    return rx.button(
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
        height="auto",
        white_space="normal",
        min_height="44px",
        variant="ghost",
        padding="12px 16px",
        width="100%",
        min_width="0",
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
                rx.input.slot(rx.icon(tag="search", size=18, color=Theme.TEXT_SECONDARY)),
                placeholder="Buscar ciudad, provincia, región...",
                value=AppState.search_query,
                on_change=AppState.handle_search_change,
                on_key_down=AppState.handle_search_key,
                aria_label="Buscar ubicación",
                max_length=120,
                width="100%",
                min_width="0",
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
            min_width="0",
            position="relative",
        ),
        rx.cond(
            AppState.has_search_results,
            rx.box(
                rx.foreach(
                    AppState.search_results,
                    location_search_item,
                ),
                position="absolute",
                top="100%",
                left="0",
                width="100%",
                min_width="0",
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
        min_width="0",
        position="relative",
        spacing="2",
    )
