
from __future__ import annotations

import json
from pathlib import Path

from human_normalizer import normalize, HumanNormalizationError
from semascript_validator import validate_core_text


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"
    positive = json.loads((fixture_dir / "hardening_human_positive.json").read_text(encoding="utf-8"))
    negative = json.loads((fixture_dir / "hardening_human_negative.json").read_text(encoding="utf-8"))

    total = 0
    passed = 0

    for case in positive:
        total += 1
        try:
            normalized = normalize(case["input"])
            ok = normalized == case["expected_core"] and validate_core_text(normalized).valid
        except Exception as exc:
            ok = False
            normalized = f"<ERROR:{exc}>"
        if ok:
            passed += 1
        else:
            print(f"FAILED POSITIVE: {case['id']}")
            print(case["input"])
            print(normalized)

    for case in negative:
        total += 1
        try:
            normalized = normalize(case["input"])
            ok = False
            print(f"FAILED NEGATIVE: {case['id']}")
            print(normalized)
        except HumanNormalizationError:
            ok = True
        except Exception:
            ok = True
        if ok:
            passed += 1

    print(f"hardening_human: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
