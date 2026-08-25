
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    base = Path(__file__).parent
    scripts = [
        "run_environment_bootstrap_checks.py",
        "run_fixture_validation.py",
        "run_human_normalization_checks.py",
        "run_pattern_decomposition_checks.py",
        "run_exec_runtime_checks.py",
        "run_state_model_checks.py",
        "run_batch_runtime_state_corpus_checks.py",
        "run_svg_renderer_checks.py",
        "run_hardening_human_checks.py",
        "run_hardening_runtime_checks.py",
        "run_hardening_state_checks.py",
        "run_inspector_smoke_checks.py",
        "run_inspector_http_smoke_checks.py",
        "run_inspector_http_e2e_checks.py",
        "run_inspector_http_project_ops_e2e_checks.py",
        "run_inspector_http_lifecycle_import_e2e_checks.py",
        "run_inspector_http_graph_session_e2e_checks.py",
    ]
    expected_markers = {
        "run_environment_bootstrap_checks.py": "env_bootstrap_self_check: passed=",
    }

    ok = True
    for script in scripts:
        proc = subprocess.run([sys.executable, str(base / script)], cwd=str(base), capture_output=True, text=True, check=False)
        print(proc.stdout.strip())
        if proc.returncode != 0:
            ok = False
        expected_marker = expected_markers.get(script)
        if expected_marker and expected_marker not in proc.stdout:
            ok = False
        if "failed=0" not in proc.stdout and "passed=1 failed=0" not in proc.stdout:
            ok = False

    if ok:
        print("v0_2_hardening_suite: passed=1 failed=0 total=1")
    else:
        print("v0_2_hardening_suite: passed=0 failed=1 total=1")


if __name__ == "__main__":
    main()
