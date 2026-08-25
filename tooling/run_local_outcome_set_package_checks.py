from __future__ import annotations

from session_model import create_session_from_text
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
    create_local_outcome_set_package_import_in_project,
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


def build_local_outcome_project():
    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Base")
    source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Source Local Package Project")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "release_s", "feature_s", point_kind="release", note="anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "release_s", snapshot_name="snapshot_s")

    current = create_workspace(project_name="Current Local Package Project")
    current = add_session_to_workspace(current, current_head, session_id="current_s")

    resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        decisions={"feature_s": {"choice": "use_snapshot"}},
        resolution_name="resolution_s",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    committed, _ = create_snapshot_reconcile_commit_in_project(
        project_index=resolved,
        snapshot_reconcile_resolution_result=resolution_result,
        commit_name="source_commit_s",
        promote_point_name="source_release_s",
        promote_point_kind="release",
        note="source",
    )
    committed, _, intermediate_pkg = create_snapshot_reconcile_commit_package_export_in_project(
        committed,
        "source_commit_s",
        package_name="intermediate_pkg_s",
        note="intermediate",
    )
    resolved_pkg, pkg_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=committed,
        package=intermediate_pkg,
        decisions={"feature_s_reconcile_resolved": {"choice": "use_package"}},
        resolution_name="pkg_resolution_s",
        target_branch_name="main",
        activate_last_imported=True,
    )
    local_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
        resolved_pkg,
        pkg_resolution_result,
        commit_name="local_outcome_s",
        promote_point_name="local_release_s",
        promote_point_kind="release",
        note="local outcome",
    )
    return local_committed


def main() -> None:
    total = 3
    passed = 0

    project = build_local_outcome_project()
    exported, export_result, package = create_local_outcome_set_package_export_in_project(
        project,
        "local_outcome_s",
        package_name="local_outcome_s_pkg",
        note="portable local outcome",
    )
    ok1 = export_result["package_name"] == "local_outcome_s_pkg" and package["local_outcome_set_package_version"] == "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1"
    if ok1:
        passed += 1
    else:
        print("FAILED: local outcome export", export_result, package)

    import_target = create_workspace(project_name="Portable Local Import")
    import_target = add_session_to_workspace(import_target, create_session_from_text("spr(seed -> import_current)", profile="human", decompose=True, initial_state=empty_state(), session_name="Import Current"), session_id="import_current")
    imported, import_result = create_local_outcome_set_package_import_in_project(
        current_project_index=import_target,
        package=package,
        import_name="local_outcome_s_pkg_import",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok2 = import_result["imported_commit_name"] in imported["snapshot_reconcile_commit_package_commits"] and "local_outcome_s_pkg_import" in imported["local_outcome_set_package_imports"]
    if ok2:
        passed += 1
    else:
        print("FAILED: local outcome import", import_result, imported)

    ok3 = any(ev["event_type"] == "local_outcome_set_package_imported" for ev in imported["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: local outcome import history", imported["history"])

    print(f"local_outcome_set_export_import_portable_package: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
