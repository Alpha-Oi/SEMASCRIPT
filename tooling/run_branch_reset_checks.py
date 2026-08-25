
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace, create_branch_from_session
from project_reset import reset_branch_head_to_historical_session
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
    c1 = create_session_from_text("spr(seed -> form_1)", profile="human", decompose=True, initial_state=empty_state(), session_name="Commit 1")
    c2 = create_session_from_text("spr(seed -> form_2)", profile="human", decompose=True, initial_state=empty_state(), session_name="Commit 2")

    project = create_workspace(project_name="Reset Project")
    project = add_session_to_workspace(project, base, session_id="base_s", branch_name="main")
    project = create_branch_from_session(project, "base_s", "feature_reset")
    project = add_session_to_workspace(project, c1, session_id="c1", branch_name="feature_reset")
    project = add_session_to_workspace(project, c2, session_id="c2", branch_name="feature_reset")

    updated, result = reset_branch_head_to_historical_session(project, "feature_reset", "c1", activate_head=True)
    bs = branch_summary(updated)
    feature = next(item for item in bs if item["branch_name"] == "feature_reset")
    ok1 = result["target_session_id"] == "c1" and feature["head_session_id"] == "c1" and feature["manual_head_session_id"] == "c1"
    if ok1:
        passed += 1
    else:
        print("FAILED: reset summary", result, bs)

    ok2 = updated["active_session_id"] == "c1" and any(ev["event_type"] == "branch_reset" and ev["session_id"] == "c1" for ev in updated["history"]["events"])
    if ok2:
        passed += 1
    else:
        print("FAILED: reset history/active", updated)

    lineage = build_named_merge_lineage_graph(updated)
    node = next(item for item in lineage["nodes"] if item["session_id"] == "c1")
    ok3 = node["is_branch_head"] is True
    if ok3:
        passed += 1
    else:
        print("FAILED: lineage head highlight", lineage)

    print(f"reset_restore_branch_head_historical_session: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
