
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace
from session_merge import merge_sessions_three_way


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
        text="gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Right Session",
    )

    project = create_workspace(project_name="Merge Project")
    project = add_session_to_workspace(project, base, session_id="base_s")
    project = add_session_to_workspace(project, left, session_id="left_s")
    project = add_session_to_workspace(project, right, session_id="right_s")

    merged = merge_sessions_three_way(project, "base_s", "left_s", "right_s")
    ok1 = merged["summary"]["conflict_count"] == 0 and "merged_session" in merged and merged["merged_session"]["project"]["source_text"] == "gen(template -> instance_a)"
    if ok1:
        passed += 1
    else:
        print("FAILED: auto merge", merged)

    right_conflict = create_session_from_text(
        text="gen(template -> instance_b)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Right Conflict",
    )
    project2 = create_workspace(project_name="Merge Project Conflict")
    project2 = add_session_to_workspace(project2, base, session_id="base_s")
    project2 = add_session_to_workspace(project2, left, session_id="left_s")
    project2 = add_session_to_workspace(project2, right_conflict, session_id="right_s")
    merged2 = merge_sessions_three_way(project2, "base_s", "left_s", "right_s")
    ok2 = merged2["summary"]["conflict_count"] >= 1 and "merged_session" not in merged2
    if ok2:
        passed += 1
    else:
        print("FAILED: conflict detection", merged2)

    print(f"three_way_session_merge_conflict_detection: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
