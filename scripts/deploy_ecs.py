"""Update both ECS services using exact image SHAs and preserve rollback revisions."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SNAPSHOT = Path(tempfile.gettempdir()) / "climate-deployment.json"


def aws(*args: str) -> dict[str, Any]:
    result = subprocess.run(["aws", *args, "--output", "json"], capture_output=True, text=True)
    if result.returncode:
        # Do not print complete task definitions or AWS responses containing environment values.
        raise RuntimeError(f"AWS command failed: {args[0]} {args[1]}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def render_task(task: dict[str, Any], component: str, image: str) -> dict[str, Any]:
    allowed = {
        "family",
        "taskRoleArn",
        "executionRoleArn",
        "networkMode",
        "containerDefinitions",
        "volumes",
        "placementConstraints",
        "requiresCompatibilities",
        "cpu",
        "memory",
        "pidMode",
        "ipcMode",
        "proxyConfiguration",
        "inferenceAccelerators",
        "ephemeralStorage",
        "runtimePlatform",
    }
    task = {key: value for key, value in task.items() if key in allowed}
    container = next(item for item in task["containerDefinitions"] if item["name"] == component)
    container["image"] = image
    env = {item["name"]: item["value"] for item in container.get("environment", [])}
    public_url = os.environ["FRONTEND_PUBLIC_URL"].rstrip("/")
    if component == "backend":
        env.pop("OPEN_METEO_API_KEY", None)
        env.update(
            OPEN_METEO_API_MODE=os.environ["OPEN_METEO_API_MODE"],
            CORS_ORIGINS=public_url,
        )
        container["secrets"] = [
            item for item in container.get("secrets", []) if item["name"] != "OPEN_METEO_API_KEY"
        ]
        if os.environ["OPEN_METEO_API_MODE"] == "commercial":
            secret_arn = os.environ["OPEN_METEO_SECRET_ARN"]
            if not secret_arn.startswith("arn:"):
                raise ValueError("A real Secrets Manager ARN is required")
            container["secrets"].append({"name": "OPEN_METEO_API_KEY", "valueFrom": secret_arn})
    else:
        env.update(
            FRONTEND_PUBLIC_URL=public_url,
            REFLEX_API_URL=public_url,
            BACKEND_INTERNAL_URL=public_url,
        )
    container["environment"] = [{"name": name, "value": value} for name, value in env.items()]
    return task


def main(rollback: bool = False) -> None:
    cluster = os.environ["ECS_CLUSTER"]
    if rollback:
        snapshot = json.loads(SNAPSHOT.read_text())
        for item in snapshot.values():
            aws(
                "ecs",
                "update-service",
                "--cluster",
                cluster,
                "--service",
                item["service"],
                "--task-definition",
                item["old"],
            )
        aws(
            "ecs",
            "wait",
            "services-stable",
            "--cluster",
            cluster,
            "--services",
            *[item["service"] for item in snapshot.values()],
        )
        print("Previous service revisions restored. The deployment remains failed.")
        return
    snapshot = {}
    for component in ("backend", "frontend"):
        service = os.environ[f"ECS_{component.upper()}_SERVICE"]
        response = aws("ecs", "describe-services", "--cluster", cluster, "--services", service)
        if response.get("failures") or len(response.get("services", [])) != 1:
            raise RuntimeError(f"ECS service not found: {component}")
        old = response["services"][0]["taskDefinition"]
        if response["services"][0]["desiredCount"] < 1:
            raise RuntimeError(
                "Set ECS desired count to at least one after provisioning ECR images"
            )
        task = aws("ecs", "describe-task-definition", "--task-definition", old)["taskDefinition"]
        image = f"{os.environ['ECR_REGISTRY']}/{os.environ[f'ECR_{component.upper()}_REPOSITORY']}:{os.environ['IMAGE_TAG']}"
        rendered = render_task(task, component, image)
        task_file = Path(tempfile.gettempdir()) / f"climate-{component}-task.json"
        task_file.write_text(json.dumps(rendered))
        new = aws("ecs", "register-task-definition", "--cli-input-json", f"file://{task_file}")[
            "taskDefinition"
        ]["taskDefinitionArn"]
        snapshot[component] = {"service": service, "old": old, "new": new}
    SNAPSHOT.write_text(json.dumps(snapshot))
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
        output.write("started=true\n")
    for item in snapshot.values():
        aws(
            "ecs",
            "update-service",
            "--cluster",
            cluster,
            "--service",
            item["service"],
            "--task-definition",
            item["new"],
        )


if __name__ == "__main__":
    main("--rollback" in sys.argv)
