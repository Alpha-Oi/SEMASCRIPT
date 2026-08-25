
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
    create_snapshot_reconcile_commit_package_import_resolution_in_project,
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

    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Package Source Base")
    source_feature = create_session_from_text("spr(seed -> package_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Package Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Package Resolution Source")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "pkg_release", "feature_s", point_kind="release", note="pkg anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "pkg_release", snapshot_name="pkg_snapshot")
    current = create_workspace(project_name="Package Resolution Current")
    current = add_session_to_workspace(current, current_head, session_id="current_s")
    resolved, reconcile_resolution_result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        decisions={"feature_s": {"choice": "use_snapshot"}},
        resolution_name="reconcile_resolution_v1",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    committed, _ = create_snapshot_reconcile_commit_in_project(
        project_index=resolved,
        snapshot_reconcile_resolution_result=reconcile_resolution_result,
        commit_name="reconcile_commit_v1",
        promote_point_name="reconcile_release_v1",
        promote_point_kind="release",
        note="commit",
    )
    packaged, package_export_result, pkg = create_snapshot_reconcile_commit_package_export_in_project(
        committed,
        commit_name="reconcile_commit_v1",
        package_name="portable_pkg_v1",
        note="portable",
    )

    preview = create_snapshot_reconcile_commit_package_import_preview_in_project(
        current_project_index=current,
        package=pkg,
        import_name="portable_pkg_preview",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok1 = preview["compatibility"]["version_supported"] is True and preview["summary"]["conflict_like_count"] >= 0
    if ok1:
        passed += 1
    else:
        print("FAILED: package preview", preview)

    resolved_import, result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=current,
        package=pkg,
        decisions={preview["preview_items"][0]["original_session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> imported_resolved_form)"}},
        resolution_name="pkg_resolution_v1",
        target_branch_name="main",
        activate_last_imported=True,
    )
    rid = result["resolved_session_ids"][0]
    entry = next(item for item in resolved_import["sessions"] if item["session_id"] == rid)
    ok2 = result["summary"]["resolved_session_count"] == 1 and entry["session"]["project"]["source_text"] == "spr(seed -> imported_resolved_form)"
    if ok2:
        passed += 1
    else:
        print("FAILED: package resolution custom text", result, entry)

    ok3 = (
        entry["entry_metadata"]["commit_kind"] == "snapshot_reconcile_commit_package_import_resolution"
        and entry["entry_metadata"]["snapshot_reconcile_commit_package_import_resolution"]["decision_choice"] == "custom_text"
        and "pkg_resolution_v1" in resolved_import["snapshot_reconcile_commit_package_resolutions"]
        and any(ev["event_type"] == "snapshot_reconcile_commit_package_import_resolved" for ev in resolved_import["history"]["events"])
    )
    if ok3:
        passed += 1
    else:
        print("FAILED: package resolution provenance/history", entry, resolved_import["history"])

    print(f"standalone_outcome_package_conflict_resolution_manual_import_decisions: passed={passed} failed={total-passed} total={total}")


if __name__ == "__main__":
    main()
