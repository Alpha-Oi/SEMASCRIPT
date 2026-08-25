
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

    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Base")
    source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Source Local Package Commit")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "package_commit_release", "feature_s", point_kind="release", note="anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "package_commit_release", snapshot_name="pkg_commit_snapshot")

    current = create_workspace(project_name="Current Local Package Commit")
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
    committed_local_pkg, local_pkg_commit_result = create_local_outcome_set_package_import_commit_in_project(
        project_index=resolved_local_pkg,
        local_outcome_set_package_resolution_result=local_pkg_resolution_result,
        commit_name="local_portable_pkg_commit",
        promote_point_name="local_portable_pkg_release",
        promote_point_kind="release",
        note="portable local package commit",
    )

    ok1 = local_pkg_commit_result["commit_name"] == "local_portable_pkg_commit" and local_pkg_commit_result["summary"]["promoted"] is True
    if ok1:
        passed += 1
    else:
        print("FAILED: local package commit result", local_pkg_commit_result)

    ok2 = "local_portable_pkg_commit" in committed_local_pkg["snapshot_reconcile_commit_package_commits"] and "local_portable_pkg_commit" in committed_local_pkg["local_outcome_set_package_commits"]
    if ok2:
        passed += 1
    else:
        print("FAILED: local package commit registries", committed_local_pkg)

    ok3 = any(ev["event_type"] == "local_outcome_set_package_committed" for ev in committed_local_pkg["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: local package commit history", committed_local_pkg["history"])

    print(f"portable_local_outcome_package_commit_promote_imported_resolution: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
