
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace, create_branch_from_session, commit_merged_session_to_workspace
from session_merge import merge_sessions_three_way
from session_conflict_resolution import resolve_merge_result_conflicts
from project_branching import build_named_merge_lineage_graph, branch_summary


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
    total = 3
    passed = 0

    base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Base")
    left = create_session_from_text("gen(template -> instance_a)", profile="human", decompose=True, initial_state=empty_state(), session_name="Left")
    right = create_session_from_text("gen(template -> instance_b)", profile="human", decompose=True, initial_state=empty_state(), session_name="Right")

    project = create_workspace(project_name="Branch Project")
    project = add_session_to_workspace(project, base, session_id="base_s")
    project = create_branch_from_session(project, "base_s", "feature_a")
    ok1 = any(item["branch_name"] == "feature_a" for item in branch_summary(project))
    if ok1:
        passed += 1
    else:
        print("FAILED: branch creation", project)

    project = add_session_to_workspace(project, left, session_id="left_s", branch_name="feature_a")
    project = add_session_to_workspace(project, right, session_id="right_s", branch_name="main")
    merge_result = merge_sessions_three_way(project, "base_s", "left_s", "right_s")
    resolved = resolve_merge_result_conflicts(merge_result, {"source_text": {"choice": "left"}})
    project = commit_merged_session_to_workspace(project, resolved, session_id="merge_s", session_name="Merge", activate=True, branch_name="main")

    lineage = build_named_merge_lineage_graph(project)
    ok2 = lineage["summary"]["branch_count"] >= 2 and any(edge["to_session_id"] == "merge_s" for edge in lineage["edges"])
    if ok2:
        passed += 1
    else:
        print("FAILED: lineage graph", lineage)

    merge_entry = next(item for item in project["sessions"] if item["session_id"] == "merge_s")
    ok3 = merge_entry["entry_metadata"]["branching"]["branch_name"] == "main" and len(merge_entry["entry_metadata"]["branching"]["parent_session_ids"]) >= 2
    if ok3:
        passed += 1
    else:
        print("FAILED: merge branch metadata", merge_entry)

    print(f"branching_named_merge_lineage_graph: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
