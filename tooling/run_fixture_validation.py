
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict, List

from semascript_validator import validate_core_text, validate_exec_text


def run_fixture(path: Path) -> Dict[str, object]:
    cases: List[dict] = json.loads(path.read_text(encoding="utf-8"))
    passed = 0
    total = len(cases)

    for case in cases:
        mode = case["mode"]
        validator: Callable[[str], object] = validate_core_text if mode == "core" else validate_exec_text
        result = validator(case["text"])
        expected_valid = case["expected_valid"]
        if result.valid == expected_valid:
            passed += 1
        else:
            print(f"FAILED: {case['id']}")
            print(f" expected_valid={expected_valid} got={result.valid}")
            print(f" text={case['text']}")
            print(f" errors={result.errors}")

    return {"total": total, "passed": passed, "failed": total - passed}


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"
    all_results = {}
    allowed = {
        "core_positive.json",
        "core_negative.json",
        "exec_positive.json",
        "exec_negative.json",
    }

    for fixture in sorted(fixture_dir.glob("*.json")):
        if fixture.name not in allowed:
            continue
        result = run_fixture(fixture)
        all_results[fixture.name] = result

    for name, stats in all_results.items():
        print(f"{name}: passed={stats['passed']} failed={stats['failed']} total={stats['total']}")


if __name__ == "__main__":
    main()
