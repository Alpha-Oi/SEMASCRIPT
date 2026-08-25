
from __future__ import annotations

from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_in_project,
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

    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Pkg Source Base")
    source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Pkg Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Pkg Current Head")

    source = create_workspace(project_name="Package Source Project")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "pkg_release", "feature_s", point_kind="release", note="package anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "pkg_release", snapshot_name="pkg_snapshot")

    current = create_workspace(project_name="Package Current Project")
    current = add_session_to_workspace(current, current_head, session_id="current_s")
    resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        decisions={"feature_s": {"choice": "use_snapshot"}},
        resolution_name="resolution_pkg",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    committed, commit_result = create_snapshot_reconcile_commit_in_project(
        project_index=resolved,
        snapshot_reconcile_resolution_result=resolution_result,
        commit_name="reconcile_commit_pkg",
        promote_point_name="pkg_promoted_release",
        promote_point_kind="release",
        note="package commit",
    )

    exported, export_result, standalone = create_snapshot_reconcile_commit_package_export_in_project(
        committed,
        commit_name="reconcile_commit_pkg",
        package_name="outcome_pkg",
        note="standalone package",
    )
    ok1 = export_result["package_name"] == "outcome_pkg" and standalone["commit_name"] == "reconcile_commit_pkg"
    if ok1:
        passed += 1
    else:
        print("FAILED: package export", export_result, standalone)

    imported_base = create_workspace(project_name="Package Import Target")
    imported_base = add_session_to_workspace(imported_base, current_head, session_id="target_current")
    imported, import_result = create_snapshot_reconcile_commit_package_import_in_project(
        current_project_index=imported_base,
        package=standalone,
        import_name="outcome_pkg_import",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok2 = import_result["summary"]["imported_session_count"] == 1 and "outcome_pkg_import" in imported["snapshot_reconcile_commit_package_imports"]
    if ok2:
        passed += 1
    else:
        print("FAILED: package import", import_result, imported)

    imported_commit_name = import_result["imported_commit_name"]
    ok3 = imported_commit_name in imported["snapshot_reconcile_commits"] and any(ev["event_type"] == "snapshot_reconcile_commit_package_imported" for ev in imported["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: package import commit/history", imported)

    print(f"resolution_set_export_import_standalone_package: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
