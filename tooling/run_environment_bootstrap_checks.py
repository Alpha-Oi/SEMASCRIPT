from __future__ import annotations

import importlib.util
import platform
import sys
from pathlib import Path


REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "docs/SEMASCRIPT_ENV_BOOTSTRAP_AND_VERIFICATION_v0.2.md",
    "tooling/run_v0_2_hardening_suite.py",
    "tooling/run_inspector_browser_ui_checks.py",
    "tooling/inspector_server.py",
]

MANIFEST_FILES = [
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "Pipfile",
    "poetry.lock",
    "Dockerfile",
]


def print_line(level: str, message: str) -> None:
    print(f"[{level}] {message}")


def main() -> int:
    passed = 0
    warnings = 0
    failed = 0

    try:
        project_root = Path(__file__).resolve().parents[1]
        print("SEMASCRIPT environment bootstrap self-check")
        print(f"project_root={project_root}")
        print(f"python_executable={sys.executable}")
        print(f"python_version={platform.python_version()}")

        for relative_path in REQUIRED_FILES:
            path = project_root / relative_path
            if path.is_file():
                passed += 1
                print_line("PASS", f"required file exists: {relative_path}")
            else:
                failed += 1
                print_line("FAIL", f"required file missing: {relative_path}")

        present_manifests = []
        for relative_path in MANIFEST_FILES:
            path = project_root / relative_path
            if path.exists():
                present_manifests.append(relative_path)

        if present_manifests:
            warnings += len(present_manifests)
            for relative_path in present_manifests:
                print_line("WARN", f"dependency manifest present; review bootstrap contract: {relative_path}")
        else:
            print_line("INFO", "standard dependency manifests absent; this matches the current bootstrap contract")

        if importlib.util.find_spec("playwright") is not None:
            passed += 1
            print_line("OK", "optional playwright: available")
        else:
            warnings += 1
            print_line("WARN", "optional playwright: optional-missing")

    except Exception as exc:
        failed += 1
        print_line("FAIL", f"internal error: {exc}")

    print(f"env_bootstrap_self_check: passed={passed} warnings={warnings} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
