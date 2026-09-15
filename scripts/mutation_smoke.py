"""Portable baseline mutation suite; each mutation runs in an isolated temporary copy.

This score covers these declared mutations only, not the whole application. The
broader mutmut configuration can be run on Linux/WSL for exploratory analysis.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("app/domain/wmo.py", "if is_day else", "if not is_day else"),
    ("app/application/use_cases.py", "clean_query = q.strip()", "clean_query = q"),
    ("app/application/use_cases.py", "len(clean_query) < 2", "len(clean_query) < 0"),
    ("app/application/use_cases.py", "hours >= 72", "hours > 72"),
    ("app/application/use_cases.py", "hours >= 48", "hours > 48"),
    ("app/application/use_cases.py", "max(1, min(days, 16))", "max(1, min(days, 15))"),
    ("app/infrastructure/cache.py", "monotonic() >= expires", "monotonic() < expires"),
    (
        "app/infrastructure/cache.py",
        "ttl if ttl is not None else self._default_ttl",
        "self._default_ttl",
    ),
]


def run_suite(directory: Path) -> int:
    env = {**os.environ, "PYTHONPATH": str(directory), "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-x",
            "-q",
            "--override-ini=addopts=--asyncio-mode=auto",
        ],
        cwd=directory,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=90,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Mutation test infrastructure failed with exit code {result.returncode}"
        )
    return result.returncode


def main() -> None:
    killed = 0
    with tempfile.TemporaryDirectory(prefix="climate-mutation-") as temporary:
        copy = Path(temporary) / "backend"
        shutil.copytree(ROOT / "backend" / "app", copy / "app")
        shutil.copytree(ROOT / "backend" / "tests", copy / "tests")
        shutil.copy2(ROOT / "backend" / "pyproject.toml", copy / "pyproject.toml")
        if run_suite(copy):
            raise RuntimeError("Baseline tests must pass before mutation testing")
        for filename, before, after in CASES:
            path = copy / filename
            original = path.read_text(encoding="utf-8")
            if original.count(before) != 1:
                raise RuntimeError(f"Mutation anchor is not unique: {filename}: {before}")
            path.write_text(original.replace(before, after), encoding="utf-8")
            try:
                detected = run_suite(copy) == 1
                killed += detected
                print(f"{'KILLED' if detected else 'SURVIVED'}: {filename}: {before}", flush=True)
            finally:
                path.write_text(original, encoding="utf-8")
    score = killed / len(CASES) * 100
    print(f"Baseline mutation score: {killed}/{len(CASES)} ({score:.1f}%)")
    if score < 70:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
