
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace, create_branch_from_session
from project_squash import squash_sessions_into_lineage_commit
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
    feat1 = create_session_from_text("spr(seed -> form_a)", profile="human", decompose=True, initial_state=empty_state(), session_name="Feat 1")
    feat2 = create_session_from_text("spr(seed -> form_b)", profile="human", decompose=True, initial_state=empty_state(), session_name="Feat 2")
    main2 = create_session_from_text("gen(template -> instance_main)", profile="human", decompose=True, initial_state=empty_state(), session_name="Main 2")

    project = create_workspace(project_name="Squash Project")
    project = add_session_to_workspace(project, base, session_id="base_s", branch_name="main")
    project = create_branch_from_session(project, "base_s", "feature_x")
    project = add_session_to_workspace(project, feat1, session_id="feat_1", branch_name="feature_x")
    project = add_session_to_workspace(project, feat2, session_id="feat_2", branch_name="feature_x")
    project = add_session_to_workspace(project, main2, session_id="main_2", branch_name="main")

    squashed, result = squash_sessions_into_lineage_commit(
        project,
        source_session_ids=["feat_1", "feat_2"],
        target_branch_name="main",
        session_id="squash_s",
        session_name="Squashed Feature",
        activate_head=True,
    )
    ok1 = result["summary"]["folded_count"] == 2 and result["squashed_session_id"] == "squash_s"
    if ok1:
        passed += 1
    else:
        print("FAILED: squash summary", result)

    entry = next(item for item in squashed["sessions"] if item["session_id"] == "squash_s")
    ok2 = (
        entry["entry_metadata"]["commit_kind"] == "squash_fold"
        and entry["entry_metadata"]["branching"]["branch_name"] == "main"
        and entry["entry_metadata"]["squash_fold"]["materialized_from_session_id"] == "feat_2"
    )
    if ok2:
        passed += 1
    else:
        print("FAILED: squash entry metadata", entry)

    lineage = build_named_merge_lineage_graph(squashed)
    ok3 = any(edge["relation"] == "squash_origin" and edge["to_session_id"] == "squash_s" and edge["from_session_id"] == "feat_1" for edge in lineage["edges"])
    if ok3:
        passed += 1
    else:
        print("FAILED: squash lineage edge", lineage)

    print(f"squash_fold_multiple_sessions_lineage_commit: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
