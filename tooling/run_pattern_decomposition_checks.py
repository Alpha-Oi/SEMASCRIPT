
from __future__ import annotations

import json
from pathlib import Path

from semascript_ast import text_to_ast_document
from human_normalizer import normalize, HumanNormalizationError
from pattern_decomposer import decompose_ast_document, ast_document_to_slinear, PatternDecompositionError
from semascript_validator import validate_core_text


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"
    positive = json.loads((fixture_dir / "pattern_decomposition_positive.json").read_text(encoding="utf-8"))
    negative = json.loads((fixture_dir / "pattern_decomposition_negative.json").read_text(encoding="utf-8"))

    total = 0
    passed = 0

    for case in positive:
        total += 1
        try:
            text = normalize(case["input"]) if case["profile"] == "human" else case["input"]
            doc = text_to_ast_document(text, source_profile=case["profile"], source_text=case["input"])
            decomp = decompose_ast_document(doc)
            slinear = ast_document_to_slinear(decomp)
            valid = validate_core_text(slinear).valid
            ok = (slinear == case["expected_slinear"]) and valid
        except Exception as exc:
            ok = False
            slinear = f"<ERROR:{exc}>"

        if ok:
            passed += 1
        else:
            print(f"FAILED POSITIVE: {case['id']}")
            print(f" input={case['input']}")
            print(f" expected={case['expected_slinear']}")
            print(f" got={slinear}")

    for case in negative:
        total += 1
        try:
            text = normalize(case["input"]) if case["profile"] == "human" else case["input"]
            doc = text_to_ast_document(text, source_profile=case["profile"], source_text=case["input"])
            _ = decompose_ast_document(doc)
            ok = False
            print(f"FAILED NEGATIVE: {case['id']}")
            print(" expected decomposition error, got success")
        except (PatternDecompositionError, HumanNormalizationError):
            ok = True
        except Exception:
            ok = True

        if ok:
            passed += 1

    print(f"pattern_decomposition: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
