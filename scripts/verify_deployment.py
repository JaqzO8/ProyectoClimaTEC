"""Fail if ECS rolled back automatically or the public application is unhealthy."""

import json
import os
import urllib.request

from deploy_ecs import SNAPSHOT, aws

snapshot = json.loads(SNAPSHOT.read_text())
for component, item in snapshot.items():
    services = aws(
        "ecs",
        "describe-services",
        "--cluster",
        os.environ["ECS_CLUSTER"],
        "--services",
        item["service"],
    )["services"]
    if services[0]["taskDefinition"] != item["new"]:
        raise RuntimeError(f"{component} is not running the requested revision")
base = os.environ["FRONTEND_PUBLIC_URL"].rstrip("/")
for path in (
    "/health",
    "/ready",
    "/",
    "/ping",
    "/api/v1/weather/overview?latitude=-12.04&longitude=-77.03",
):
    with urllib.request.urlopen(base + path, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"Smoke test failed: {path}")
        if path == "/health" and json.load(response)["status"] != "ok":
            raise RuntimeError("Backend health response is invalid")
print("Both ECS revisions and public application endpoints are healthy.")
