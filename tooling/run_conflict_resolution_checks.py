
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace
from session_merge import merge_sessions_three_way
from session_conflict_resolution import resolve_merge_result_conflicts


def empty_state():
    return {
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    }


def main() -> None:
    total = 2
    passed = 0

    base = create_session_from_text(
        text="gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Base Session",
    )
    left = create_session_from_text(
        text="gen(template -> instance_a)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Left Session",
    )
    right = create_session_from_text(
        text="gen(template -> instance_b)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Right Session",
    )

    project = create_workspace(project_name="Resolve Project")
    project = add_session_to_workspace(project, base, session_id="base_s")
    project = add_session_to_workspace(project, left, session_id="left_s")
    project = add_session_to_workspace(project, right, session_id="right_s")

    merge_result = merge_sessions_three_way(project, "base_s", "left_s", "right_s")
    ok1 = merge_result["summary"]["conflict_count"] >= 1 and "merged_session" not in merge_result
    if ok1:
        passed += 1
    else:
        print("FAILED: expected merge conflict", merge_result)

    decisions = {"source_text": {"choice": "left"}}
    resolved = resolve_merge_result_conflicts(merge_result, decisions)
    ok2 = (
        resolved["summary"]["finalized"] is True
        and "merged_session" in resolved
        and resolved["merged_session"]["project"]["source_text"] == "gen(template -> instance_a)"
    )
    if ok2:
        passed += 1
    else:
        print("FAILED: manual resolution", resolved)

    print(f"interactive_conflict_resolution_manual_merge_decisions: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
