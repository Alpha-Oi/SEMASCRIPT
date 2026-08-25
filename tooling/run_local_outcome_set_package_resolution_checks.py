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


def build_local_package():
    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Base")
    source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Source Local Package Resolution")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "release_s", "feature_s", point_kind="release", note="anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "release_s", snapshot_name="snapshot_s")

    current = create_workspace(project_name="Current Local Package Resolution")
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
    local_committed, _, package = create_local_outcome_set_package_export_in_project(
        local_committed,
        "local_outcome_s",
        package_name="local_outcome_s_pkg",
        note="portable local outcome",
    )
    return package, current_head


def main() -> None:
    total = 3
    passed = 0

    package, current_head = build_local_package()
    target = create_workspace(project_name="Resolution Target")
    target = add_session_to_workspace(target, current_head, session_id="target_current")

    resolved, result = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=target,
        package_data=package,
        decisions={package["resolved_sessions"][0]["session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> resolved_form)"}},
        resolution_name="local_pkg_resolution_s",
        target_branch_name="main",
        activate_last_imported=True,
    )

    ok1 = result["resolution_name"] == "local_pkg_resolution_s" and result["summary"]["resolved_session_count"] == 1
    if ok1:
        passed += 1
    else:
        print("FAILED: package resolution result", result)

    resolved_id = result["resolved_session_ids"][0]
    resolved_entry = next(item for item in resolved["sessions"] if item["session_id"] == resolved_id)
    ok2 = resolved_entry["entry_metadata"]["commit_kind"] == "local_outcome_set_package_import_resolution" and resolved_entry["session"]["project"]["source_text"] == "spr(seed -> resolved_form)"
    if ok2:
        passed += 1
    else:
        print("FAILED: package resolution entry", resolved_entry)

    ok3 = any(ev["event_type"] == "local_outcome_set_package_import_resolved" for ev in resolved["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: package resolution history", resolved["history"])

    print(f"portable_local_outcome_package_conflict_resolution_manual_import_decisions: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
