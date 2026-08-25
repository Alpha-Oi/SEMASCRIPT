
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace, create_branch_from_session
from project_cherrypick import cherry_pick_sessions_onto_branch
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

    base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Base")
    feature1 = create_session_from_text("spr(seed -> feature_form_1)", profile="human", decompose=True, initial_state=empty_state(), session_name="Feature 1")
    feature2 = create_session_from_text("spr(seed -> feature_form_2)", profile="human", decompose=True, initial_state=empty_state(), session_name="Feature 2")
    main2 = create_session_from_text("gen(template -> instance_main)", profile="human", decompose=True, initial_state=empty_state(), session_name="Main 2")

    project = create_workspace(project_name="Cherry Pick Project")
    project = add_session_to_workspace(project, base, session_id="base_s", branch_name="main")
    project = create_branch_from_session(project, "base_s", "feature_cp")
    project = add_session_to_workspace(project, feature1, session_id="feature_1", branch_name="feature_cp")
    project = add_session_to_workspace(project, feature2, session_id="feature_2", branch_name="feature_cp")
    project = add_session_to_workspace(project, main2, session_id="main_2", branch_name="main")

    picked, result = cherry_pick_sessions_onto_branch(project, ["feature_1", "feature_2"], "main", activate_head=True)

    ok1 = result["summary"]["picked_count"] == 2 and picked["active_branch_name"] == "main"
    if ok1:
        passed += 1
    else:
        print("FAILED: pick count/active branch", result, picked)

    replayed_ids = [item["replayed_session_id"] for item in result["replayed_sessions"]]
    entries = [item for item in picked["sessions"] if item["session_id"] in replayed_ids]
    ok2 = (
        len(entries) == 2
        and entries[0]["entry_metadata"]["cherry_pick"]["source_session_id"] == "feature_1"
        and entries[0]["entry_metadata"]["branching"]["branch_name"] == "main"
        and entries[0]["entry_metadata"]["branching"]["parent_session_ids"] == ["main_2"]
    )
    if ok2:
        passed += 1
    else:
        print("FAILED: cherry-pick metadata", entries)

    lineage = build_named_merge_lineage_graph(picked)
    ok3 = any(edge["from_session_id"] == "main_2" and edge["to_session_id"] == replayed_ids[0] for edge in lineage["edges"])
    if ok3:
        passed += 1
    else:
        print("FAILED: lineage edge", lineage)

    print(f"cherry_pick_selective_session_replay_across_branches: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
