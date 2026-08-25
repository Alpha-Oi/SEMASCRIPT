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
    compare_baseline_or_three_way_portable_local_outcomes_in_project,
    create_portable_local_outcome_package_three_way_merge_resolution_in_project,
    create_portable_local_outcome_package_three_way_merge_commit_in_project,
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
    source_base = create_session_from_text(
        "gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Source Base",
    )
    source_feature = create_session_from_text(
        "spr(seed -> source_form)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Source Feature",
    )
    current_head = create_session_from_text(
        "spr(seed -> current_form)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Current Head",
    )
    source = create_workspace(project_name="Source Merge Commit")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "merge_release", "feature_s", point_kind="release", note="anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "merge_release", snapshot_name="merge_snapshot")

    current = create_workspace(project_name="Current Merge Commit")
    current = add_session_to_workspace(current, current_head, session_id="current_s")

    resolved, res_result = create_snapshot_reconcile_resolution_in_project(
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
        snapshot_reconcile_resolution_result=res_result,
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
    resolved_pkg, pkg_res = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=committed,
        package=intermediate_pkg,
        decisions={"feature_s_reconcile_resolved": {"choice": "use_package"}},
        resolution_name="pkg_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    local_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
        resolved_pkg,
        pkg_res,
        commit_name="local_outcome_commit_s",
        promote_point_name="local_release_s",
        promote_point_kind="release",
        note="local outcome",
    )
    local_committed, _, portable_pkg = create_local_outcome_set_package_export_in_project(
        local_committed,
        "local_outcome_commit_s",
        package_name="portable_local_pkg",
        note="portable local",
    )
    base_project, base_res = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=local_committed,
        package_data=portable_pkg,
        decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "use_package"}},
        resolution_name="base_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    base_project, _ = create_local_outcome_set_package_import_commit_in_project(
        project_index=base_project,
        local_outcome_set_package_resolution_result=base_res,
        commit_name="base_commit",
        promote_point_name="base_release",
        promote_point_kind="release",
        note="base",
    )
    left_project, left_res = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=base_project,
        package_data=portable_pkg,
        decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> left_form)"}},
        resolution_name="left_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    left_project, _ = create_local_outcome_set_package_import_commit_in_project(
        project_index=left_project,
        local_outcome_set_package_resolution_result=left_res,
        commit_name="left_commit",
        promote_point_name="left_release",
        promote_point_kind="release",
        note="left",
    )
    right_project, right_res = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=left_project,
        package_data=portable_pkg,
        decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> right_form)"}},
        resolution_name="right_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    right_project, _ = create_local_outcome_set_package_import_commit_in_project(
        project_index=right_project,
        local_outcome_set_package_resolution_result=right_res,
        commit_name="right_commit",
        promote_point_name="right_release",
        promote_point_kind="release",
        note="right",
    )
    merge_result = compare_baseline_or_three_way_portable_local_outcomes_in_project(
        right_project,
        "base_commit",
        "left_commit",
        "right_commit",
    )
    resolved_project, resolution_result = create_portable_local_outcome_package_three_way_merge_resolution_in_project(
        project_index=right_project,
        merge_result=merge_result,
        decisions={merge_result["merge_items"][0]["original_session_id"]: {"choice": "use_right"}},
        resolution_name="portable_local_merge_resolution",
        target_branch_name="main",
        activate_last_resolved=True,
    )
    return resolved_project, resolution_result


def main():
    total = 4
    passed = 0

    project, resolution_result = build_project()
    committed, commit_result = create_portable_local_outcome_package_three_way_merge_commit_in_project(
        project_index=project,
        merge_resolution_result=resolution_result,
        commit_name="portable_local_merge_commit",
        promote_point_name="portable_local_merge_release",
        promote_point_kind="release",
        note="promote resolved portable local merge",
    )

    ok1 = commit_result["commit_name"] == "portable_local_merge_commit" and commit_result["summary"]["promoted"]
    if ok1:
        passed += 1
    else:
        print("FAILED: commit identity", commit_result)

    ok2 = "portable_local_merge_commit" in committed.get("portable_local_outcome_set_package_merge_commits", {})
    if ok2:
        passed += 1
    else:
        print("FAILED: merge commit registry", committed.get("portable_local_outcome_set_package_merge_commits"))

    ok3 = "portable_local_merge_commit" in committed.get("local_outcome_set_package_commits", {})
    if ok3:
        passed += 1
    else:
        print("FAILED: local outcome commit registry", committed.get("local_outcome_set_package_commits"))

    ok4 = any(
        ev["event_type"] == "portable_local_outcome_package_three_way_merge_committed"
        for ev in committed["history"]["events"]
    )
    if ok4:
        passed += 1
    else:
        print("FAILED: merge commit history", committed["history"])

    print(
        f"portable_local_outcome_package_three_way_merge_commit_promote: passed={passed} failed={total-passed} total={total}"
    )


if __name__ == "__main__":
    main()
