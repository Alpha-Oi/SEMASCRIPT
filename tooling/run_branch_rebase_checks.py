
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace, create_branch_from_session
from project_rebase import replay_branch_onto_target_lineage
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
    feature1 = create_session_from_text("spr(seed -> form_a)", profile="human", decompose=True, initial_state=empty_state(), session_name="Feature 1")
    feature2 = create_session_from_text("spr(seed -> form_b)", profile="human", decompose=True, initial_state=empty_state(), session_name="Feature 2")
    main2 = create_session_from_text("gen(template -> instance_main)", profile="human", decompose=True, initial_state=empty_state(), session_name="Main 2")

    project = create_workspace(project_name="Rebase Project")
    project = add_session_to_workspace(project, base, session_id="base_s", branch_name="main")
    project = create_branch_from_session(project, "base_s", "feature_x")
    project = add_session_to_workspace(project, feature1, session_id="feature_1", branch_name="feature_x")
    project = add_session_to_workspace(project, feature2, session_id="feature_2", branch_name="feature_x")
    project = add_session_to_workspace(project, main2, session_id="main_2", branch_name="main")

    rebased, result = replay_branch_onto_target_lineage(project, "feature_x", "main", activate_head=True)
    ok1 = result["summary"]["replayed_count"] == 2 and rebased["active_branch_name"] == "feature_x"
    if ok1:
        passed += 1
    else:
        print("FAILED: replay count/active branch", result, rebased)

    replayed_ids = [item["replayed_session_id"] for item in result["replayed_sessions"]]
    replayed_entries = [item for item in rebased["sessions"] if item["session_id"] in replayed_ids]
    ok2 = (
        len(replayed_entries) == 2
        and replayed_entries[0]["entry_metadata"]["rebase_replay"]["target_branch_name"] == "main"
        and replayed_entries[0]["entry_metadata"]["branching"]["branch_name"] == "feature_x"
        and replayed_entries[0]["entry_metadata"]["branching"]["parent_session_ids"] == ["main_2"]
    )
    if ok2:
        passed += 1
    else:
        print("FAILED: replay metadata", replayed_entries)

    lineage = build_named_merge_lineage_graph(rebased)
    ok3 = any(edge["to_session_id"] == replayed_ids[0] and edge["from_session_id"] == "main_2" for edge in lineage["edges"])
    if ok3:
        passed += 1
    else:
        print("FAILED: lineage edge", lineage)

    print(f"branch_rebase_replay_target_lineage: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
