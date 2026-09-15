"""Serve the precompiled Reflex UI and events on one port (pinned Reflex runtime)."""

from reflex.utils.exec import run_backend_prod

if __name__ == "__main__":
    run_backend_prod("0.0.0.0", 3000, mount_frontend_compiled_app=True)
