
from __future__ import annotations

import json
from pathlib import Path

from state_model import execute_text_with_state


def _get_resource(state: dict, entity: str, resource: str) -> int:
    return int(state["resources"].get(entity, {}).get(resource, 0))


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"
    positive = json.loads((fixture_dir / "hardening_state_positive.json").read_text(encoding="utf-8"))
    negative = json.loads((fixture_dir / "hardening_state_negative.json").read_text(encoding="utf-8"))

    total = 0
    passed = 0

    for case in positive:
        total += 1
        result = execute_text_with_state(case["input"], profile=case["profile"], initial_state=case.get("initial_state"))
        ok = result["accepted"] is True
        final_state = result.get("final_state", {})
        if "expect_resources" in case:
            for entity, resources in case["expect_resources"].items():
                for resource, qty in resources.items():
                    ok = ok and (_get_resource(final_state, entity, resource) == qty)
        if "expect_action_count" in case:
            ok = ok and len(final_state.get("actions", [])) == case["expect_action_count"]
        if "expect_observation_count" in case:
            ok = ok and len(final_state.get("observations", [])) == case["expect_observation_count"]
        if "expect_history_len" in case:
            ok = ok and len(final_state.get("history", [])) == case["expect_history_len"]
        if ok:
            passed += 1
        else:
            print(f"FAILED POSITIVE: {case['id']}")
            print(json.dumps(result, ensure_ascii=False))

    for case in negative:
        total += 1
        result = execute_text_with_state(case["input"], profile=case["profile"], initial_state=case.get("initial_state"))
        codes = [err["code"] for err in result.get("errors", [])]
        ok = result["accepted"] is False and case["required_error"] in codes
        if ok:
            passed += 1
        else:
            print(f"FAILED NEGATIVE: {case['id']}")
            print(json.dumps(result, ensure_ascii=False))

    print(f"hardening_state: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
