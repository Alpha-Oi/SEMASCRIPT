
from __future__ import annotations

import json
from pathlib import Path

from human_normalizer import normalize, HumanNormalizationError
from semascript_validator import validate_core_text


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"

    pos_cases = json.loads((fixture_dir / "human_normalization_positive.json").read_text(encoding="utf-8"))
    neg_cases = json.loads((fixture_dir / "human_normalization_negative.json").read_text(encoding="utf-8"))

    total = 0
    passed = 0

    for case in pos_cases:
        total += 1
        try:
            normalized = normalize(case["human"])
            valid = validate_core_text(normalized).valid
            ok = (normalized == case["expected_core"]) and valid
        except HumanNormalizationError:
            ok = False
            normalized = "<ERROR>"

        if ok:
            passed += 1
        else:
            print(f"FAILED POSITIVE: {case['id']}")
            print(f" human={case['human']}")
            print(f" expected={case['expected_core']}")
            print(f" got={normalized}")

    for case in neg_cases:
        total += 1
        try:
            normalized = normalize(case["human"])
            ok = False
            print(f"FAILED NEGATIVE: {case['id']}")
            print(f" human={case['human']}")
            print(f" expected error, got={normalized}")
        except HumanNormalizationError:
            ok = True

        if ok:
            passed += 1

    print(f"human_normalization: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
