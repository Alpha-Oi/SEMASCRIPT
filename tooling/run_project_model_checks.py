
from __future__ import annotations

from pathlib import Path

from session_model import create_session_from_text, create_session_from_graph
from inspector_service import graph_from_input
from project_model import (
    create_workspace,
    add_session_to_workspace,
    set_active_session,
    workspace_to_inspector_payload,
    commit_merged_session_to_workspace,
    create_branch_from_session,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_restore_in_project,
    create_snapshot_restore_preview,
    create_partial_snapshot_import_in_project,
    create_snapshot_reconcile_in_project,
    create_snapshot_reconcile_preview,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    compare_snapshot_reconcile_commit_sets,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_in_project,
    create_snapshot_reconcile_commit_package_import_preview_in_project,
    create_snapshot_reconcile_commit_package_import_resolution_in_project,
    create_snapshot_reconcile_commit_package_import_commit_in_project,
    create_local_outcome_set_package_export_in_project,
    create_local_outcome_set_package_import_in_project,
    preview_local_outcome_set_package_before_import_in_project,
    create_local_outcome_set_package_import_resolution_in_project,
    create_local_outcome_set_package_import_commit_in_project,
    compare_portable_local_outcome_package_commits_in_project,
    compare_baseline_or_three_way_portable_local_outcomes_in_project,
    create_portable_local_outcome_package_three_way_merge_resolution_in_project,
    compare_local_outcome_sets_in_project,
    save_project_index,
    load_project_index,
)
from project_rebase import replay_branch_onto_target_lineage
from project_reset import reset_branch_head_to_historical_session
from project_squash import squash_sessions_into_lineage_commit
from project_cherrypick import cherry_pick_sessions_onto_branch


def empty_state():
    return {
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {"A": {"RES": 2}, "B": {"RES": 0}},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    }


def main() -> None:
    total = 30
    passed = 0

    text_session = create_session_from_text(
        text="gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Text Session",
    )
    graph_doc = graph_from_input("[EXEC:TRANSFER <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]", profile="exec")["graph_document"]
    graph_session = create_session_from_graph(
        graph_document=graph_doc,
        profile="exec",
        decompose=True,
        initial_state=empty_state(),
        session_name="Graph Session",
        ui_state={"selected_entity_id": graph_doc["root_entity_id"], "preview_mode": "raw", "decompose": True, "viewport": {"scroll_x": 0, "scroll_y": 0, "zoom": 1.0}, "panels": {}},
    )

    project = create_workspace(project_name="Workspace Project")
    project = add_session_to_workspace(project, text_session, session_id="text_s", tags=["text"])
    project = add_session_to_workspace(project, graph_session, session_id="graph_s", tags=["graph"])
    ok1 = len(project["sessions"]) == 2 and project["active_session_id"] == "text_s" and len(project["history"]["events"]) >= 3
    if ok1:
        passed += 1
    else:
        print("FAILED: workspace add")

    project = set_active_session(project, "graph_s")
    payload = workspace_to_inspector_payload(project)
    ok2 = payload["project_index"]["active_session_id"] == "graph_s" and payload["session_name"] == "Graph Session" and "workspace_dependency_map" in payload and "workspace_timeline" in payload
    if ok2:
        passed += 1
    else:
        print("FAILED: workspace payload")

    target = Path("corpus") / "project_roundtrip_test.json"
    save_project_index(project, target)
    loaded = load_project_index(target)
    ok3 = loaded["project_name"] == "Workspace Project" and len(loaded["sessions"]) == 2 and len(loaded["history"]["events"]) >= 4
    if ok3:
        passed += 1
    else:
        print("FAILED: project roundtrip")

    committed = commit_merged_session_to_workspace(
        project,
        {"merged_session": text_session, "base_session_id": "text_s", "left_session_id": "text_s", "right_session_id": "graph_s", "summary": {"conflict_count": 0}},
        session_id="committed_s",
        session_name="Committed Session",
        activate=False,
        tags=["commit"],
    )
    ok4 = any(item["session_id"] == "committed_s" for item in committed["sessions"]) and any(ev["event_type"] == "merge_committed" for ev in committed["history"]["events"])
    if ok4:
        passed += 1
    else:
        print("FAILED: merge commit insert")

    branched = create_branch_from_session(committed, "graph_s", "feature_branch")
    ok5 = any(b["branch_name"] == "feature_branch" for b in branched["branches"].values()) or "feature_branch" in branched.get("branches", {})
    if ok5:
        passed += 1
    else:
        print("FAILED: branch create")

    branched_feature = add_session_to_workspace(branched, text_session, session_id="feature_commit_s", branch_name="feature_branch", tags=["feature"])
    branched_feature2 = add_session_to_workspace(branched_feature, graph_session, session_id="feature_commit_s2", branch_name="feature_branch", tags=["feature"])
    rebased, rebase_result = replay_branch_onto_target_lineage(branched_feature2, "feature_branch", "main", activate_head=False)
    ok6 = "rebase_version" in rebase_result and rebased["branches"]["feature_branch"]["head_session_id"] != branched_feature2["branches"]["feature_branch"]["head_session_id"]
    if ok6:
        passed += 1
    else:
        print("FAILED: branch rebase")

    picked, cp_result = cherry_pick_sessions_onto_branch(branched_feature2, ["feature_commit_s"], "main", activate_head=False)
    ok7 = "cherry_pick_version" in cp_result and any(item["session_id"] == cp_result["replayed_sessions"][0]["replayed_session_id"] for item in picked["sessions"])
    if ok7:
        passed += 1
    else:
        print("FAILED: cherry pick")

    reset, reset_result = reset_branch_head_to_historical_session(branched_feature2, "feature_branch", "feature_commit_s", activate_head=False)
    ok8 = reset_result["target_session_id"] == "feature_commit_s" and reset["branches"]["feature_branch"]["head_session_id"] == "feature_commit_s"
    if ok8:
        passed += 1
    else:
        print("FAILED: branch reset")

    tagged, tag_result = create_tag_release_in_project(reset, "release_candidate", "feature_commit_s", point_kind="tag", note="Tagged historical point")
    ok9 = tag_result["tag_name"] == "release_candidate" and tagged["tag_points"]["release_candidate"]["target_session_id"] == "feature_commit_s"
    if ok9:
        passed += 1
    else:
        print("FAILED: tag/release create")

    snapped, snapshot_result, snapshot_package = create_snapshot_export_in_project(tagged, "release_candidate", snapshot_name="snapshot_candidate", note="frozen")
    ok10 = snapshot_result["snapshot_name"] == "snapshot_candidate" and "snapshot_candidate" in snapped["snapshot_exports"] and snapshot_package["anchor"]["target_session_id"] == "feature_commit_s"
    if ok10:
        passed += 1
    else:
        print("FAILED: snapshot export")

    restored, snapshot_restore_result = create_snapshot_restore_in_project(snapshot_package, restored_project_name="Restored Candidate", restore_name="restore_candidate", activate_anchor=True)
    ok11 = snapshot_restore_result["restore_name"] == "restore_candidate" and restored["active_session_id"] == "feature_commit_s" and "restore_candidate" in restored["snapshot_restores"]
    if ok11:
        passed += 1
    else:
        print("FAILED: snapshot restore")

    preview = create_snapshot_restore_preview(snapped, snapshot_package, restored_project_name="Preview Candidate", activate_anchor=True)
    ok12 = preview["snapshot_name"] == "snapshot_candidate" and preview["restore_target"]["would_activate_session_id"] == "feature_commit_s"
    if ok12:
        passed += 1
    else:
        print("FAILED: snapshot restore preview")

    imported, partial_result = create_partial_snapshot_import_in_project(
        current_project_index=snapped,
        snapshot_package=snapshot_package,
        import_name="partial_candidate",
        selected_session_ids=["feature_commit_s"],
        selected_tag_point_names=["release_candidate"],
        selected_snapshot_export_names=[],
        target_branch_name="main",
        activate_last_imported=False,
    )
    ok13 = partial_result["summary"]["imported_session_count"] == 1 and "partial_candidate" in imported["partial_snapshot_imports"]
    if ok13:
        passed += 1
    else:
        print("FAILED: partial snapshot import")

    preview_reconcile = create_snapshot_reconcile_preview(
        current_project_index=imported,
        snapshot_package=snapshot_package,
        selected_session_ids=["feature_commit_s"],
        target_branch_name="main",
        reconcile_name="reconcile_preview_candidate",
    )
    ok14 = preview_reconcile["summary"]["selected_session_count"] == 1 and preview_reconcile["summary"]["conflict_like_count"] >= 0
    if ok14:
        passed += 1
    else:
        print("FAILED: snapshot reconcile preview")

    reconciled, reconcile_result = create_snapshot_reconcile_in_project(
        current_project_index=imported,
        snapshot_package=snapshot_package,
        reconcile_name="reconcile_candidate",
        selected_session_ids=["feature_commit_s"],
        target_branch_name="main",
        activate_last_reconciled=True,
    )
    ok15 = reconcile_result["summary"]["reconciled_session_count"] == 1 and "reconcile_candidate" in reconciled["snapshot_reconciles"]
    if ok15:
        passed += 1
    else:
        print("FAILED: snapshot reconcile")

    resolved_reconcile, reconcile_resolution_result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=imported,
        snapshot_package=snapshot_package,
        decisions={"feature_commit_s": {"choice": "use_snapshot"}},
        resolution_name="reconcile_resolution_candidate",
        selected_session_ids=["feature_commit_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    ok16 = reconcile_resolution_result["summary"]["resolved_session_count"] == 1 and "reconcile_resolution_candidate" in resolved_reconcile["snapshot_reconcile_resolutions"]
    if ok16:
        passed += 1
    else:
        print("FAILED: snapshot reconcile resolution")

    committed_reconcile, reconcile_commit_result = create_snapshot_reconcile_commit_in_project(
        project_index=resolved_reconcile,
        snapshot_reconcile_resolution_result=reconcile_resolution_result,
        commit_name="reconcile_commit_candidate",
        promote_point_name="reconcile_release_candidate",
        promote_point_kind="release",
        note="promote reconcile",
    )
    ok17 = reconcile_commit_result["summary"]["promoted"] is True and "reconcile_commit_candidate" in committed_reconcile["snapshot_reconcile_commits"] and "reconcile_release_candidate" in committed_reconcile["tag_points"]
    if ok17:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit")

    committed_reconcile_2, reconcile_commit_result_2 = create_snapshot_reconcile_commit_in_project(
        project_index=committed_reconcile,
        snapshot_reconcile_resolution_result=reconcile_resolution_result,
        commit_name="reconcile_commit_candidate_2",
        promote_point_name="reconcile_tag_candidate",
        promote_point_kind="tag",
        note="promote reconcile 2",
    )
    reconcile_commit_compare_result = compare_snapshot_reconcile_commit_sets(
        project_index=committed_reconcile_2,
        left_commit_name="reconcile_commit_candidate",
        right_commit_name="reconcile_commit_candidate_2",
    )
    ok18 = reconcile_commit_compare_result["summary"]["metadata_diff_count"] >= 1 and reconcile_commit_compare_result["metadata"]["promoted_point_kind"]["changed"] is True
    if ok18:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit compare")

    packaged, package_export_result, standalone_package = create_snapshot_reconcile_commit_package_export_in_project(
        committed_reconcile_2,
        commit_name="reconcile_commit_candidate",
        package_name="reconcile_commit_candidate_pkg",
        note="portable",
    )
    imported_package_target = create_workspace(project_name="Portable Import Project")
    imported_package_target = add_session_to_workspace(imported_package_target, text_session, session_id="portable_current")
    imported_package, package_import_result = create_snapshot_reconcile_commit_package_import_in_project(
        current_project_index=imported_package_target,
        package=standalone_package,
        import_name="reconcile_commit_candidate_pkg_import",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok19 = package_export_result["package_name"] == "reconcile_commit_candidate_pkg" and package_import_result["summary"]["imported_session_count"] >= 1 and "reconcile_commit_candidate_pkg_import" in imported_package["snapshot_reconcile_commit_package_imports"]
    if ok19:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit package export/import")

    package_preview = create_snapshot_reconcile_commit_package_import_preview_in_project(
        current_project_index=imported_package_target,
        package=standalone_package,
        import_name="reconcile_commit_candidate_pkg_preview",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok20 = package_preview["compatibility"]["version_supported"] is True and package_preview["summary"]["resolved_session_count"] >= 1
    if ok20:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit package preview")

    package_resolution_target = create_workspace(project_name="Portable Resolution Project")
    package_resolution_target = add_session_to_workspace(package_resolution_target, text_session, session_id="portable_current")
    resolved_package_import, package_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=package_resolution_target,
        package=standalone_package,
        decisions={package_preview["preview_items"][0]["original_session_id"]: {"choice": "use_package"}},
        resolution_name="reconcile_commit_candidate_pkg_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok21 = package_resolution_result["summary"]["resolved_session_count"] >= 1 and "reconcile_commit_candidate_pkg_resolution" in resolved_package_import["snapshot_reconcile_commit_package_resolutions"]
    if ok21:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit package resolution")

    committed_pkg_resolution, package_commit_result = create_snapshot_reconcile_commit_package_import_commit_in_project(
    project_index=resolved_package_import,
    snapshot_reconcile_commit_package_resolution_result=package_resolution_result,
    commit_name="reconcile_commit_pkg_resolution_commit",
    promote_point_name="reconcile_commit_pkg_resolution_release",
    promote_point_kind="release",
    note="commit imported resolution",
)
    ok22 = package_commit_result["summary"]["promoted"] is True and "reconcile_commit_pkg_resolution_commit" in committed_pkg_resolution["snapshot_reconcile_commit_package_commits"] and "reconcile_commit_pkg_resolution_release" in committed_pkg_resolution["tag_points"]
    if ok22:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit package commit")

    resolved_package_import_2, package_resolution_result_2 = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=committed_pkg_resolution,
        package=standalone_package,
        decisions={package_preview["preview_items"][0]["original_session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> alt_form)"}},
        resolution_name="reconcile_commit_candidate_pkg_resolution_2",
        target_branch_name="main",
        activate_last_imported=True,
    )
    committed_pkg_resolution_2, package_commit_result_2 = create_snapshot_reconcile_commit_package_import_commit_in_project(
        project_index=resolved_package_import_2,
        snapshot_reconcile_commit_package_resolution_result=package_resolution_result_2,
        commit_name="reconcile_commit_pkg_resolution_commit_2",
        promote_point_name="reconcile_commit_pkg_resolution_release_2",
        promote_point_kind="release",
        note="commit imported resolution 2",
    )
    local_outcome_compare_result = compare_local_outcome_sets_in_project(
        committed_pkg_resolution_2,
        "reconcile_commit_pkg_resolution_commit",
        "reconcile_commit_pkg_resolution_commit_2",
    )
    ok23 = local_outcome_compare_result["left_commit_name"] == "reconcile_commit_pkg_resolution_commit" and local_outcome_compare_result["right_commit_name"] == "reconcile_commit_pkg_resolution_commit_2"
    if ok23:
        passed += 1
    else:
        print("FAILED: local outcome compare")

    local_packaged, local_package_result, local_package = create_local_outcome_set_package_export_in_project(
        committed_pkg_resolution_2,
        "reconcile_commit_pkg_resolution_commit",
        package_name="local_outcome_pkg_candidate",
        note="portable local outcome",
    )
    local_import_target = create_workspace(project_name="Local Portable Import")
    local_import_target = add_session_to_workspace(local_import_target, text_session, session_id="local_import_current")
    imported_local_package, local_package_import_result = create_local_outcome_set_package_import_in_project(
        current_project_index=local_import_target,
        package=local_package,
        import_name="local_outcome_pkg_candidate_import",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok24 = local_package_result["package_name"] == "local_outcome_pkg_candidate" and local_package_import_result["import_name"] == "local_outcome_pkg_candidate_import" and "local_outcome_pkg_candidate_import" in imported_local_package["local_outcome_set_package_imports"]
    if ok24:
        passed += 1
    else:
        print("FAILED: local outcome set portable package export/import")

    local_package_preview = preview_local_outcome_set_package_before_import_in_project(
        current_project_index=imported_local_package,
        package_data=local_package,
        import_name="local_outcome_pkg_candidate_import_preview",
        target_branch_name="main",
    )
    ok25 = local_package_preview["package_name"] == "local_outcome_pkg_candidate" and local_package_preview["compatibility"]["version_ok"] is True
    if ok25:
        passed += 1
    else:
        print("FAILED: local outcome set package preview")

    local_package_resolution_project, local_package_resolution_result = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=imported_local_package,
        package_data=local_package,
        decisions={local_package["resolved_sessions"][0]["session_id"]: {"choice": "use_package"}},
        resolution_name="local_outcome_pkg_candidate_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok26 = local_package_resolution_result["summary"]["resolved_session_count"] >= 1 and "local_outcome_pkg_candidate_resolution" in local_package_resolution_project["local_outcome_set_package_resolutions"]
    if ok26:
        passed += 1
    else:
        print("FAILED: local outcome set package resolution")

    committed_local_package, local_package_commit_result = create_local_outcome_set_package_import_commit_in_project(
        project_index=local_package_resolution_project,
        local_outcome_set_package_resolution_result=local_package_resolution_result,
        commit_name="local_outcome_pkg_candidate_commit",
        promote_point_name="local_outcome_pkg_candidate_release",
        promote_point_kind="release",
        note="portable local outcome commit",
    )
    ok27 = local_package_commit_result["commit_name"] == "local_outcome_pkg_candidate_commit" and "local_outcome_pkg_candidate_commit" in committed_local_package["local_outcome_set_package_commits"]
    if ok27:
        passed += 1
    else:
        print("FAILED: local outcome set package commit")

    committed_local_package_2, local_package_commit_result_2 = create_local_outcome_set_package_import_commit_in_project(
        project_index=committed_local_package,
        local_outcome_set_package_resolution_result=local_package_resolution_result,
        commit_name="local_outcome_pkg_candidate_commit_2",
        promote_point_name="local_outcome_pkg_candidate_release_2",
        promote_point_kind="release",
        note="portable local outcome commit 2",
    )
    portable_local_outcome_compare = compare_portable_local_outcome_package_commits_in_project(
        committed_local_package_2,
        "local_outcome_pkg_candidate_commit",
        "local_outcome_pkg_candidate_commit_2",
    )
    ok28 = portable_local_outcome_compare["left_commit_name"] == "local_outcome_pkg_candidate_commit" and portable_local_outcome_compare["right_commit_name"] == "local_outcome_pkg_candidate_commit_2"
    if ok28:
        passed += 1
    else:
        print("FAILED: portable local outcome package commit compare", portable_local_outcome_compare)

    committed_local_package_3, local_package_commit_result_3 = create_local_outcome_set_package_import_commit_in_project(
        project_index=committed_local_package_2,
        local_outcome_set_package_resolution_result=local_package_resolution_result,
        commit_name="local_outcome_pkg_candidate_commit_3",
        promote_point_name="local_outcome_pkg_candidate_release_3",
        promote_point_kind="release",
        note="portable local outcome commit 3",
    )
    portable_local_three_way_merge = compare_baseline_or_three_way_portable_local_outcomes_in_project(
        committed_local_package_3,
        "local_outcome_pkg_candidate_commit",
        "local_outcome_pkg_candidate_commit_2",
        "local_outcome_pkg_candidate_commit_3",
    )
    ok29 = portable_local_three_way_merge["base_commit_name"] == "local_outcome_pkg_candidate_commit" and portable_local_three_way_merge["summary"]["original_session_count"] >= 1
    if ok29:
        passed += 1
    else:
        print("FAILED: portable local outcome package three-way merge", portable_local_three_way_merge)

    portable_local_merge_resolution_project, portable_local_merge_resolution_result = create_portable_local_outcome_package_three_way_merge_resolution_in_project(
        project_index=committed_local_package_3,
        merge_result=portable_local_three_way_merge,
        decisions={portable_local_three_way_merge["merge_items"][0]["original_session_id"]: {"choice": "use_left"}},
        resolution_name="portable_local_pkg_merge_resolution",
        target_branch_name="main",
        activate_last_resolved=True,
    )
    ok30 = portable_local_merge_resolution_result["resolution_name"] == "portable_local_pkg_merge_resolution" and "portable_local_pkg_merge_resolution" in portable_local_merge_resolution_project["portable_local_outcome_set_package_merge_resolutions"]
    if ok30:
        passed += 1
    else:
        print("FAILED: portable local outcome package three-way merge resolution", portable_local_merge_resolution_result)

    print(f"multi_session_project_workspace: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
