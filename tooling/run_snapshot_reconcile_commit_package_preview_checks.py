
from __future__ import annotations

from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_preview_in_project,
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


def main() -> None:
    total = 3
    passed = 0

    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Pkg Base")
    source_feature = create_session_from_text("spr(seed -> feature_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Pkg Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Package Preview Source")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "pkg_release", "feature_s", point_kind="release", note="pkg anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "pkg_release", snapshot_name="pkg_snapshot")
    source, resolution_result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=create_workspace(project_name="tmp"),
        snapshot_package=snapshot_package,
        decisions={"feature_s": {"choice": "use_snapshot"}},
        resolution_name="pkg_resolution",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    source, _, outcome_package = create_snapshot_reconcile_commit_package_export_in_project(
        create_snapshot_reconcile_commit_in_project(
            source,
            resolution_result,
            commit_name="pkg_commit",
            promote_point_name="pkg_promoted",
            promote_point_kind="release",
            note="promoted",
        )[0],
        commit_name="pkg_commit",
        package_name="pkg_outcome",
        note="portable",
    )

    current = create_workspace(project_name="Package Preview Current")
    current = add_session_to_workspace(current, current_head, session_id="current_s")

    preview = create_snapshot_reconcile_commit_package_import_preview_in_project(
        current_project_index=current,
        package=outcome_package,
        import_name="pkg_import_preview",
        target_branch_name="main",
        activate_last_imported=True,
    )

    ok1 = preview["package_name"] == "pkg_outcome" and preview["compatibility"]["version_supported"] is True
    if ok1:
        passed += 1
    else:
        print("FAILED: package identity", preview)

    ok2 = preview["summary"]["conflict_like_count"] == 1 and preview["preview_items"][0]["status"] == "conflict_like"
    if ok2:
        passed += 1
    else:
        print("FAILED: package conflict preview", preview)

    ok3 = preview["compatibility"]["import_name_available"] is True and preview["import_target"]["target_branch_name"] == "main"
    if ok3:
        passed += 1
    else:
        print("FAILED: package compatibility", preview)

    print(f"standalone_outcome_package_diff_compatibility_check: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
