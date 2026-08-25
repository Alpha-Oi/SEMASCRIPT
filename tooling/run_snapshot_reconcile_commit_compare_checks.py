
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    compare_snapshot_reconcile_commit_sets,
)


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

    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Base")
    source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Compare Source")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "compare_release", "feature_s", point_kind="release", note="anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "compare_release", snapshot_name="compare_snapshot")

    current = create_workspace(project_name="Compare Current")
    current = add_session_to_workspace(current, current_head, session_id="current_s")
    resolved, resolution = create_snapshot_reconcile_resolution_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        decisions={"feature_s": {"choice": "use_snapshot"}},
        resolution_name="resolution_v1",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    committed1, _ = create_snapshot_reconcile_commit_in_project(
        project_index=resolved,
        snapshot_reconcile_resolution_result=resolution,
        commit_name="commit_a",
        promote_point_name="release_a",
        promote_point_kind="release",
        note="first",
    )
    committed2, _ = create_snapshot_reconcile_commit_in_project(
        project_index=committed1,
        snapshot_reconcile_resolution_result=resolution,
        commit_name="commit_b",
        promote_point_name="tag_b",
        promote_point_kind="tag",
        note="second",
    )
    compare = compare_snapshot_reconcile_commit_sets(committed2, "commit_a", "commit_b")

    ok1 = compare["left_commit_name"] == "commit_a" and compare["right_commit_name"] == "commit_b"
    if ok1:
        passed += 1
    else:
        print("FAILED: compare identity", compare)

    ok2 = compare["metadata"]["promoted_point_kind"]["changed"] is True and compare["summary"]["metadata_diff_count"] >= 1
    if ok2:
        passed += 1
    else:
        print("FAILED: compare metadata", compare)

    ok3 = "resolution_pairs" in compare and "resolved_sessions" in compare and "summary" in compare
    if ok3:
        passed += 1
    else:
        print("FAILED: compare structure", compare)

    print(f"resolution_set_diff_compare_promoted_reconcile_outcomes: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
