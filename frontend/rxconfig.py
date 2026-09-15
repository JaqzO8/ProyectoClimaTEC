import os

import reflex as rx
from reflex.constants import StateManagerMode

config = rx.Config(
    app_name="proyecto_climatico",
    api_url=os.getenv("REFLEX_API_URL", "http://localhost:3000"),
    backend_port=3000,
    frontend_port=3000,
    cors_allowed_origins=[os.getenv("FRONTEND_PUBLIC_URL", "http://localhost:3000")],
    state_manager_mode=StateManagerMode.MEMORY,
    show_built_with_reflex=False,
    plugins=[],
)
