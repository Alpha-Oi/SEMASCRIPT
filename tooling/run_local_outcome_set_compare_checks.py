
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
    compare_local_outcome_sets_in_project,
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

    source = create_workspace(project_name="Source Compare Project")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "compare_release", "feature_s", point_kind="release", note="compare anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "compare_release", snapshot_name="compare_snapshot")

    current = create_workspace(project_name="Current Compare Project")
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
    committed, _, package = create_snapshot_reconcile_commit_package_export_in_project(
        committed,
        "source_commit",
        package_name="compare_package",
        note="portable compare package",
    )

    left_imported, left_resolution = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=committed,
        package=package,
        decisions={"feature_s_reconcile_resolved": {"choice": "use_package"}},
        resolution_name="left_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    left_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
        left_imported,
        left_resolution,
        commit_name="left_commit",
        promote_point_name="left_release",
        promote_point_kind="release",
        note="left",
    )

    right_imported, right_resolution = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=left_committed,
        package=package,
        decisions={"feature_s_reconcile_resolved": {"choice": "custom_text", "custom_text": "spr(seed -> alt_form)"}},
        resolution_name="right_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    right_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
        right_imported,
        right_resolution,
        commit_name="right_commit",
        promote_point_name="right_release",
        promote_point_kind="release",
        note="right",
    )
    return right_committed


def main() -> None:
    total = 3
    passed = 0
    project = build_project()

    result = compare_local_outcome_sets_in_project(project, "left_commit", "right_commit")
    ok1 = result["left_commit_name"] == "left_commit" and result["right_commit_name"] == "right_commit"
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
        print("FAILED: text diff", result)

    print(f"local_outcome_set_diff_compare_imported_promoted_resolutions: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
