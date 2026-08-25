
from __future__ import annotations

from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_resolution_in_project,
    create_snapshot_reconcile_commit_package_import_commit_in_project,
    create_local_outcome_set_package_export_in_project,
    create_local_outcome_set_package_import_resolution_in_project,
    create_local_outcome_set_package_import_commit_in_project,
    compare_portable_local_outcome_package_commits_in_project,
)
from session_model import create_session_from_text


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


def build_project():
    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Base")
    source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Source Portable Local Compare")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "compare_release", "feature_s", point_kind="release", note="compare anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "compare_release", snapshot_name="compare_snapshot")

    current = create_workspace(project_name="Current Portable Local Compare")
    current = add_session_to_workspace(current, current_head, session_id="current_s")

    resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        decisions={"feature_s": {"choice": "use_snapshot"}},
        resolution_name="source_resolution",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    committed, _ = create_snapshot_reconcile_commit_in_project(
        project_index=resolved,
        snapshot_reconcile_resolution_result=resolution_result,
        commit_name="source_commit",
        promote_point_name="source_release",
        promote_point_kind="release",
        note="source commit",
    )
    committed, _, intermediate_pkg = create_snapshot_reconcile_commit_package_export_in_project(
        committed,
        "source_commit",
        package_name="intermediate_pkg",
        note="intermediate",
    )
    resolved_pkg, pkg_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=committed,
        package=intermediate_pkg,
        decisions={"feature_s_reconcile_resolved": {"choice": "use_package"}},
        resolution_name="pkg_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    local_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
        resolved_pkg,
        pkg_resolution_result,
        commit_name="local_outcome_commit_s",
        promote_point_name="local_release_s",
        promote_point_kind="release",
        note="local outcome",
    )
    local_committed, _, portable_pkg = create_local_outcome_set_package_export_in_project(
        local_committed,
        "local_outcome_commit_s",
        package_name="local_outcome_portable_pkg",
        note="portable local outcome",
    )
    resolved_local_pkg, local_pkg_resolution_result = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=local_committed,
        package_data=portable_pkg,
        decisions={"feature_s_reconcile_resolved_pkg_import": {"choice": "use_package"}},
        resolution_name="local_portable_pkg_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    committed_local_pkg, _ = create_local_outcome_set_package_import_commit_in_project(
        project_index=resolved_local_pkg,
        local_outcome_set_package_resolution_result=local_pkg_resolution_result,
        commit_name="local_portable_pkg_commit",
        promote_point_name="local_portable_pkg_release",
        promote_point_kind="release",
        note="portable local package commit",
    )
    committed_local_pkg_2, _ = create_local_outcome_set_package_import_commit_in_project(
        project_index=committed_local_pkg,
        local_outcome_set_package_resolution_result=local_pkg_resolution_result,
        commit_name="local_portable_pkg_commit_2",
        promote_point_name="local_portable_pkg_release_2",
        promote_point_kind="release",
        note="portable local package commit 2",
    )
    return committed_local_pkg_2


def main() -> None:
    total = 3
    passed = 0
    project = build_project()

    result = compare_portable_local_outcome_package_commits_in_project(
        project,
        "local_portable_pkg_commit",
        "local_portable_pkg_commit_2",
    )
    ok1 = result["left_commit_name"] == "local_portable_pkg_commit" and result["right_commit_name"] == "local_portable_pkg_commit_2"
    if ok1:
        passed += 1
    else:
        print("FAILED: compare identity", result)

    ok2 = result["metadata"]["promoted_point_name"]["same"] is False and result["summary"]["promoted_point_differs"] is True
    if ok2:
        passed += 1
    else:
        print("FAILED: promoted point diff", result)

    ok3 = "resolved_session_texts" in result and result["summary"]["has_any_diff"] is True
    if ok3:
        passed += 1
    else:
        print("FAILED: compare result", result)

    print(f"portable_local_outcome_package_diff_compare_committed_imported_outcomes: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
