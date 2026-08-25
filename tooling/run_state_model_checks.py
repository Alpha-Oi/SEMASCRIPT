
from __future__ import annotations

import json
from pathlib import Path

from state_model import execute_text_with_state


def _get_resource(state: dict, entity: str, resource: str) -> int:
    return int(state["resources"].get(entity, {}).get(resource, 0))


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"
    positive = json.loads((fixture_dir / "state_model_positive.json").read_text(encoding="utf-8"))
    negative = json.loads((fixture_dir / "state_model_negative.json").read_text(encoding="utf-8"))

    total = 0
    passed = 0

    for case in positive:
        total += 1
        result = execute_text_with_state(case["input"], profile=case["profile"], initial_state=case.get("initial_state"))
        ok = result["accepted"] == True

        if ok and "expect_resources" in case:
            for entity, resources in case["expect_resources"].items():
                for resource, qty in resources.items():
                    ok = ok and (_get_resource(result["final_state"], entity, resource) == qty)

        if ok and "expect_history_len" in case:
            ok = ok and (len(result["final_state"]["history"]) == case["expect_history_len"])

        if ok and "expect_dependency_count" in case:
            ok = ok and (len(result["final_state"]["dependencies"]) == case["expect_dependency_count"])

        if ok and "expect_expansion_count" in case:
            ok = ok and (len(result["final_state"]["expansions"]) == case["expect_expansion_count"])

        if ok:
            passed += 1
        else:
            print(f"FAILED POSITIVE: {case['id']}")
            print(json.dumps(result, ensure_ascii=False))

    for case in negative:
        total += 1
        result = execute_text_with_state(case["input"], profile=case["profile"], initial_state=case.get("initial_state"))
        codes = [err["code"] for err in result.get("errors", [])]
        ok = result["accepted"] == False and case["required_error"] in codes

        if ok:
            passed += 1
        else:
            print(f"FAILED NEGATIVE: {case['id']}")
            print(json.dumps(result, ensure_ascii=False))

    print(f"state_model: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
