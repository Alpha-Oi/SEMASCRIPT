
from __future__ import annotations

from project_model import create_workspace, add_session_to_workspace, commit_merged_session_to_workspace
from session_model import create_session_from_text
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

    base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Base")
    left = create_session_from_text("gen(template -> instance_a)", profile="human", decompose=True, initial_state=empty_state(), session_name="Left")
    right = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Right")

    project = create_workspace(project_name="Commit Project")
    project = add_session_to_workspace(project, base, session_id="base_s")
    project = add_session_to_workspace(project, left, session_id="left_s")
    project = add_session_to_workspace(project, right, session_id="right_s")

    merge_result = merge_sessions_three_way(project, "base_s", "left_s", "right_s")
    committed = commit_merged_session_to_workspace(
        project,
        merge_result,
        session_id="merged_s",
        session_name="Merged Session",
        activate=True,
        tags=["committed"],
    )
    ok1 = (
        committed["active_session_id"] == "merged_s"
        and any(item["session_id"] == "merged_s" for item in committed["sessions"])
        and any(ev["event_type"] == "merge_committed" and ev["session_id"] == "merged_s" for ev in committed["history"]["events"])
    )
    if ok1:
        passed += 1
    else:
        print("FAILED: direct merge commit", committed)

    right_conflict = create_session_from_text("gen(template -> instance_b)", profile="human", decompose=True, initial_state=empty_state(), session_name="Right Conflict")
    project2 = create_workspace(project_name="Resolved Commit Project")
    project2 = add_session_to_workspace(project2, base, session_id="base_s")
    project2 = add_session_to_workspace(project2, left, session_id="left_s")
    project2 = add_session_to_workspace(project2, right_conflict, session_id="right_s")
    merge_result2 = merge_sessions_three_way(project2, "base_s", "left_s", "right_s")
    resolved = resolve_merge_result_conflicts(merge_result2, {"source_text": {"choice": "left"}})
    committed2 = commit_merged_session_to_workspace(
        project2,
        resolved,
        session_id="resolved_merge_s",
        session_name="Resolved Merge Session",
        activate=False,
        tags=["resolved"],
    )
    merged_entry = next(item for item in committed2["sessions"] if item["session_id"] == "resolved_merge_s")
    ok2 = (
        committed2["active_session_id"] == "base_s"
        and merged_entry["entry_metadata"]["commit_kind"] == "merge_commit"
        and merged_entry["entry_metadata"]["merge_commit"]["base_session_id"] == "base_s"
    )
    if ok2:
        passed += 1
    else:
        print("FAILED: resolved merge commit", committed2)

    print(f"merge_commit_workspace_insertion: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
