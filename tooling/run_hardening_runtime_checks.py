
from __future__ import annotations

import json
from pathlib import Path

from exec_runtime import execute_text


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"
    positive = json.loads((fixture_dir / "hardening_runtime_positive.json").read_text(encoding="utf-8"))
    negative = json.loads((fixture_dir / "hardening_runtime_negative.json").read_text(encoding="utf-8"))

    total = 0
    passed = 0

    for case in positive:
        total += 1
        result = execute_text(case["input"], profile=case["profile"])
        ok = result["accepted"] is True
        if "required_schedule" in case:
            ok = ok and result.get("context", {}).get("schedule") == case["required_schedule"]
        if "required_note" in case:
            ok = ok and case["required_note"] in result.get("notes", [])
        if "required_ops" in case:
            ops = [step["op_name"] for step in result.get("plan", [])]
            ok = ok and all(op in ops for op in case["required_ops"])
        if ok:
            passed += 1
        else:
            print(f"FAILED POSITIVE: {case['id']}")
            print(json.dumps(result, ensure_ascii=False))

    for case in negative:
        total += 1
        result = execute_text(case["input"], profile=case["profile"])
        codes = [err["code"] for err in result.get("errors", [])]
        ok = result["accepted"] is False and case["required_error"] in codes
        if ok:
            passed += 1
        else:
            print(f"FAILED NEGATIVE: {case['id']}")
            print(json.dumps(result, ensure_ascii=False))

    print(f"hardening_runtime: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
