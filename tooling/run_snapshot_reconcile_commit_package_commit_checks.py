
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_resolution_in_project,
    create_snapshot_reconcile_commit_package_import_commit_in_project,
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

    source = create_workspace(project_name="Source Package Commit Project")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "package_commit_release", "feature_s", point_kind="release", note="anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "package_commit_release", snapshot_name="package_commit_snapshot")

    # create a promoted reconcile commit to export as standalone package
    current = create_workspace(project_name="Current Commit Project")
    current = add_session_to_workspace(current, current_head, session_id="current_s")
    # Build minimal resolution result object manually via package resolution path
    commit_project = create_workspace(project_name="Promoted Commit Source")
    commit_project = add_session_to_workspace(commit_project, current_head, session_id="current_s")
    # import resolution target
    package_source = create_workspace(project_name="Portable Resolution Source")
    package_source = add_session_to_workspace(package_source, current_head, session_id="portable_current")
    # build reconcile commit package from synthetic commit
    synthetic_resolution_result = {
        "resolution_name": "reconcile_resolution_src",
        "snapshot_name": "package_commit_snapshot",
        "source_point_name": "package_commit_release",
        "target_branch_name": "main",
        "resolved_session_ids": ["current_s"],
        "skipped_session_ids": [],
        "resolution_pairs": [],
    }
    commit_project, commit_result = create_snapshot_reconcile_commit_in_project(
        project_index=commit_project,
        snapshot_reconcile_resolution_result=synthetic_resolution_result,
        commit_name="portable_commit_src",
        promote_point_name="portable_release_src",
        promote_point_kind="release",
        note="portable",
    )
    commit_project, package_export_result, standalone_package = create_snapshot_reconcile_commit_package_export_in_project(
        commit_project,
        commit_name="portable_commit_src",
        package_name="portable_commit_pkg",
        note="package",
    )
    target = create_workspace(project_name="Portable Resolution Target")
    target = add_session_to_workspace(target, current_head, session_id="target_current")
    resolved_import, resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=target,
        package=standalone_package,
        decisions={standalone_package["resolved_sessions"][0]["session_id"]: {"choice": "use_package"}},
        resolution_name="portable_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok1 = resolution_result["summary"]["resolved_session_count"] >= 1 and "portable_resolution" in resolved_import["snapshot_reconcile_commit_package_resolutions"]
    if ok1:
        passed += 1
    else:
        print("FAILED: package resolution prep", resolution_result)

    committed, commit_pkg_result = create_snapshot_reconcile_commit_package_import_commit_in_project(
        project_index=resolved_import,
        snapshot_reconcile_commit_package_resolution_result=resolution_result,
        commit_name="portable_resolution_commit",
        promote_point_name="portable_resolution_release",
        promote_point_kind="release",
        note="promote imported resolution",
    )
    ok2 = commit_pkg_result["summary"]["promoted"] is True and "portable_resolution_commit" in committed["snapshot_reconcile_commit_package_commits"]
    if ok2:
        passed += 1
    else:
        print("FAILED: package resolution commit", commit_pkg_result)

    ok3 = "portable_resolution_release" in committed["tag_points"] and any(ev["event_type"] == "snapshot_reconcile_commit_package_committed" for ev in committed["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: package resolution promotion/history", committed["tag_points"], committed["history"])

    print(f"standalone_outcome_package_commit_promote_imported_resolution: passed={passed} failed={total-passed} total={total}")

if __name__ == "__main__":
    main()
