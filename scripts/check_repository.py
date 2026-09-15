"""Reject tracked environment files, private keys and Terraform state before upload."""

import subprocess
import sys
from pathlib import PurePosixPath


def forbidden(name: str) -> bool:
    path = PurePosixPath(name)
    basename = path.name.lower()
    if basename.endswith(".example"):
        return False
    return (
        basename == ".env"
        or basename.startswith(".env.")
        or basename in {"credentials", "credentials.json", "secrets.json"}
        or ".tfstate" in basename
        or basename.endswith((".pem", ".key", ".p12", ".pfx", ".tfvars", ".tfvars.json", ".tfplan"))
        or any(part in {".aws", ".venv", ".terraform"} for part in path.parts)
    )


def main() -> int:
    files = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    bad = [name for name in files if name and forbidden(name)]
    for name in bad:
        print(f"Forbidden tracked file: {name}")
    if bad:
        return 1
    print("Repository file policy passed. Secret content is scanned separately with Gitleaks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
