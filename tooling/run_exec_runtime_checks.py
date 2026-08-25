
from __future__ import annotations

import json
from pathlib import Path

from exec_runtime import execute_text


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"
    positive = json.loads((fixture_dir / "exec_runtime_positive.json").read_text(encoding="utf-8"))
    negative = json.loads((fixture_dir / "exec_runtime_negative.json").read_text(encoding="utf-8"))

    total = 0
    passed = 0

    for case in positive:
        total += 1
        result = execute_text(case["input"], profile=case["profile"])
        ops = [step["op_name"] for step in result.get("plan", [])]
        ok = result["accepted"] == True
        if "required_ops" in case:
            ok = ok and all(op in ops for op in case["required_ops"])
        if "required_schedule" in case:
            ok = ok and result.get("context", {}).get("schedule") == case["required_schedule"]
        if "required_invariant" in case:
            ok = ok and result.get("context", {}).get("invariant_law") == case["required_invariant"]

        if ok:
            passed += 1
        else:
            print(f"FAILED POSITIVE: {case['id']}")
            print(f" input={case['input']}")
            print(f" result={json.dumps(result, ensure_ascii=False)}")

    for case in negative:
        total += 1
        result = execute_text(case["input"], profile=case["profile"])
        codes = [err["code"] for err in result.get("errors", [])]
        ok = result["accepted"] == False and case["required_error"] in codes

        if ok:
            passed += 1
        else:
            print(f"FAILED NEGATIVE: {case['id']}")
            print(f" input={case['input']}")
            print(f" result={json.dumps(result, ensure_ascii=False)}")

    print(f"exec_runtime: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
