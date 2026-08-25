
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace, create_tag_release_in_project, workspace_to_inspector_payload
from project_branching import build_named_merge_lineage_graph


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

    s1 = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="S1")
    s2 = create_session_from_text("spr(seed -> form)", profile="human", decompose=True, initial_state=empty_state(), session_name="S2")

    project = create_workspace(project_name="Tag Project")
    project = add_session_to_workspace(project, s1, session_id="s1", branch_name="main")
    project = add_session_to_workspace(project, s2, session_id="s2", branch_name="main")

    updated, result = create_tag_release_in_project(project, "v0.1-beta", "s2", point_kind="release", note="First release point")
    ok1 = result["tag_name"] == "v0.1-beta" and updated["tag_points"]["v0.1-beta"]["point_kind"] == "release"
    if ok1:
        passed += 1
    else:
        print("FAILED: create tag/release", result, updated)

    payload = workspace_to_inspector_payload(updated)
    ok2 = "tag_point_summary" in payload and any(item["tag_name"] == "v0.1-beta" for item in payload["tag_point_summary"])
    if ok2:
        passed += 1
    else:
        print("FAILED: tag summary payload", payload)

    lineage = build_named_merge_lineage_graph(updated)
    node = next(item for item in lineage["nodes"] if item["session_id"] == "s2")
    ok3 = any(point["tag_name"] == "v0.1-beta" for point in node["attached_points"])
    if ok3:
        passed += 1
    else:
        print("FAILED: lineage tag annotation", lineage)

    print(f"tag_release_points_lineage_states: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
