
from __future__ import annotations

import re
from pathlib import Path

from inspector_service import (
    analyze_input,
    analyze_graph,
    graph_from_input,
    load_sample_catalog,
    export_session_from_text,
    export_session_from_graph,
    export_project_index_from_sessions,
    import_project_index,
    switch_project_session,
    compare_project_sessions,
    merge_project_sessions_three_way,
    resolve_project_merge_conflicts,
    commit_project_merge_result,
    create_project_branch,
    rebase_project_branch_onto_target,
    cherry_pick_project_sessions,
    squash_project_sessions_into_commit,
    reset_project_branch_head,
    create_project_tag_release_point,
    create_project_snapshot_export,
    restore_project_from_snapshot_export,
    preview_project_snapshot_restore,
    partial_import_project_from_snapshot,
    reconcile_snapshot_into_project_lineage,
    preview_snapshot_reconcile_in_project_lineage,
    resolve_snapshot_reconcile_conflicts_in_project_lineage,
    commit_snapshot_reconcile_resolution_in_project_lineage,
    compare_snapshot_reconcile_commit_outcomes,
    export_snapshot_reconcile_commit_as_package,
    import_snapshot_reconcile_commit_package_into_project,
    preview_snapshot_reconcile_commit_package_import_into_project,
    resolve_snapshot_reconcile_commit_package_import_conflicts_in_project,
    commit_imported_resolution_into_local_outcome_set_in_project,
    compare_local_imported_promoted_outcomes,
    export_local_outcome_set_as_portable_package,
    import_local_outcome_set_package_into_project,
    preview_portable_local_outcome_set_package_import,
    resolve_local_outcome_set_package_import_conflicts_in_project,
    commit_portable_local_outcome_package_resolution_in_project,
    compare_committed_portable_local_outcome_packages,
    compare_or_three_way_merge_committed_portable_local_outcomes,
    resolve_portable_local_outcome_package_three_way_merge_conflicts_in_project,
    commit_portable_local_outcome_package_three_way_merge_resolution_in_project,
    commit_snapshot_reconcile_commit_package_resolution_in_project,
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
    total = 64
    passed = 0

    samples = load_sample_catalog(Path(__file__).parent)
    if len(samples) >= 3:
        passed += 1
    else:
        print("FAILED: sample catalog too small")

    result = analyze_input("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state())
    ok = (
        "graph_document" in result
        and "ast_document" in result
        and "svg_raw" in result
        and result["validation"]["valid"] is True
    )
    if ok:
        passed += 1
    else:
        print("FAILED: analyze_input expected fields")

    graph_result = graph_from_input("[EXEC:TRANSFER <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]", profile="exec")
    graph_doc = graph_result["graph_document"]
    ok2 = graph_doc["root_entity_id"] and len(graph_doc["entities"]) >= 4 and len(graph_doc["edges"]) >= 3
    if ok2:
        passed += 1
    else:
        print("FAILED: graph_from_input")

    analyzed_graph = analyze_graph(graph_doc, profile="exec", decompose=True, initial_state={
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {"A": {"RES": 2}, "B": {"RES": 0}},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    })
    ok3 = analyzed_graph["runtime_report"]["accepted"] is True and analyzed_graph["state_report"]["accepted"] is True
    if ok3:
        passed += 1
    else:
        print("FAILED: analyze_graph")

    s1 = export_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="S1")
    s2 = export_session_from_graph(graph_doc, profile="exec", decompose=True, initial_state={
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {"A": {"RES": 2}, "B": {"RES": 0}},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    }, session_name="S2", ui_state={"selected_entity_id": graph_doc["root_entity_id"], "preview_mode": "raw", "decompose": True, "viewport": {"scroll_x": 0, "scroll_y": 0, "zoom": 1.0}, "panels": {}})
    project = export_project_index_from_sessions(
        sessions=[
            {"session_id": "s1", "session": s1, "tags": ["text"]},
            {"session_id": "s2", "session": s2, "tags": ["graph"]},
        ],
        project_name="Inspector Project",
        active_session_id="s2",
    )
    imported = import_project_index(project)
    ok4 = imported["project_index"]["active_session_id"] == "s2" and len(imported["workspace_summary"]) == 2 and "workspace_dependency_map" in imported and "workspace_timeline" in imported
    if ok4:
        passed += 1
    else:
        print("FAILED: project import")

    switched = switch_project_session(project, "s1")
    ok5 = switched["project_index"]["active_session_id"] == "s1" and switched["session_name"] == "S1" and switched["workspace_timeline"]["summary"]["event_count"] >= imported["workspace_timeline"]["summary"]["event_count"]
    if ok5:
        passed += 1
    else:
        print("FAILED: project switch")

    diff = compare_project_sessions(project, "s1", "s2")
    ok6 = diff["left_session_id"] == "s1" and diff["right_session_id"] == "s2" and "structure" in diff and "execution" in diff
    if ok6:
        passed += 1
    else:
        print("FAILED: project compare", diff)

    merged = merge_project_sessions_three_way(project, "s1", "s1", "s2")
    ok7 = merged["base_session_id"] == "s1" and merged["left_session_id"] == "s1" and merged["right_session_id"] == "s2" and "summary" in merged
    if ok7:
        passed += 1
    else:
        print("FAILED: project merge", merged)

    conflict_project = export_project_index_from_sessions(
        sessions=[
            {"session_id": "base_c", "session": export_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Base")},
            {"session_id": "left_c", "session": export_session_from_text("gen(template -> instance_a)", profile="human", decompose=True, initial_state=empty_state(), session_name="Left")},
            {"session_id": "right_c", "session": export_session_from_text("gen(template -> instance_b)", profile="human", decompose=True, initial_state=empty_state(), session_name="Right")},
        ],
        project_name="Conflict Project",
        active_session_id="right_c",
    )
    resolved = resolve_project_merge_conflicts(
        conflict_project,
        "base_c",
        "left_c",
        "right_c",
        {"source_text": {"choice": "left"}},
    )
    ok8 = resolved["summary"]["finalized"] is True and resolved["merged_session"]["project"]["source_text"] == "gen(template -> instance_a)"
    if ok8:
        passed += 1
    else:
        print("FAILED: manual resolve", resolved)

    committed = commit_project_merge_result(
        conflict_project,
        resolved,
        session_id="merge_commit_s",
        session_name="Merge Commit Session",
        activate=True,
        tags=["commit"],
        branch_name="main",
    )
    ok9 = committed["project_index"]["active_session_id"] == "merge_commit_s" and any(item["session_id"] == "merge_commit_s" for item in committed["project_index"]["sessions"])
    if ok9:
        passed += 1
    else:
        print("FAILED: merge commit project insertion", committed)

    branched = create_project_branch(committed["project_index"], "merge_commit_s", "feature_ui")
    ok10 = "branch_summary" in branched and any(item["branch_name"] == "feature_ui" for item in branched["branch_summary"]) and "workspace_lineage_graph" in branched
    if ok10:
        passed += 1
    else:
        print("FAILED: branch creation/lineage", branched)

    rebased = rebase_project_branch_onto_target(branched["project_index"], "feature_ui", "main", activate_head=True)
    ok11 = "branch_rebase_result" in rebased and rebased["branch_rebase_result"]["source_branch_name"] == "feature_ui" and "workspace_lineage_graph" in rebased
    if ok11:
        passed += 1
    else:
        print("FAILED: branch rebase", rebased)

    picked = cherry_pick_project_sessions(rebased["project_index"], ["merge_commit_s"], "main", activate_head=True)
    ok12 = "branch_cherry_pick_result" in picked and picked["branch_cherry_pick_result"]["summary"]["picked_count"] == 1 and "workspace_lineage_graph" in picked
    if ok12:
        passed += 1
    else:
        print("FAILED: cherry pick", picked)

    squashed = squash_project_sessions_into_commit(
        picked["project_index"],
        ["merge_commit_s", picked["branch_cherry_pick_result"]["replayed_sessions"][-1]["replayed_session_id"]],
        "main",
        session_id="squash_smoke_s",
        session_name="Squash Smoke Session",
        activate_head=True,
    )
    ok13 = "branch_squash_result" in squashed and squashed["branch_squash_result"]["summary"]["folded_count"] == 2 and "workspace_lineage_graph" in squashed
    if ok13:
        passed += 1
    else:
        print("FAILED: squash", squashed)

    reset = reset_project_branch_head(
        squashed["project_index"],
        "main",
        "merge_commit_s",
        activate_head=True,
    )
    ok14 = "branch_reset_result" in reset and reset["branch_reset_result"]["target_session_id"] == "merge_commit_s" and reset["project_index"]["active_session_id"] == "merge_commit_s"
    if ok14:
        passed += 1
    else:
        print("FAILED: branch reset", reset)

    tagged = create_project_tag_release_point(
        reset["project_index"],
        "release_smoke",
        "merge_commit_s",
        point_kind="release",
        note="Smoke release point",
    )
    ok15 = "tag_release_result" in tagged and tagged["tag_release_result"]["tag_name"] == "release_smoke" and any(item["tag_name"] == "release_smoke" for item in tagged["tag_point_summary"])
    if ok15:
        passed += 1
    else:
        print("FAILED: tag/release point", tagged)

    snapped = create_project_snapshot_export(
        tagged["project_index"],
        "release_smoke",
        snapshot_name="snapshot_smoke",
        note="frozen smoke export",
    )
    ok16 = "snapshot_export_result" in snapped and snapped["snapshot_export_result"]["snapshot_name"] == "snapshot_smoke" and "snapshot_export_package" in snapped
    if ok16:
        passed += 1
    else:
        print("FAILED: snapshot export", snapped)

    preview = preview_project_snapshot_restore(
        tagged["project_index"],
        snapped["snapshot_export_package"],
        restored_project_name="Preview Smoke Project",
        activate_anchor=True,
    )
    ok17 = preview["snapshot_name"] == "snapshot_smoke" and preview["restore_target"]["would_activate_session_id"] == "merge_commit_s"
    if ok17:
        passed += 1
    else:
        print("FAILED: snapshot restore preview", preview)

    restored = restore_project_from_snapshot_export(
        snapped["snapshot_export_package"],
        restored_project_name="Restored Smoke Project",
        restore_name="restore_smoke",
        activate_anchor=True,
    )
    ok18 = "snapshot_restore_result" in restored and restored["snapshot_restore_result"]["restore_name"] == "restore_smoke" and restored["project_index"]["active_session_id"] == "merge_commit_s"
    if ok18:
        passed += 1
    else:
        print("FAILED: snapshot restore", restored)

    partial = partial_import_project_from_snapshot(
        current_project_index=tagged["project_index"],
        snapshot_package=snapped["snapshot_export_package"],
        import_name="partial_smoke",
        selected_session_ids=["merge_commit_s"],
        selected_tag_point_names=["release_smoke"],
        selected_snapshot_export_names=[],
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok19 = "partial_snapshot_import_result" in partial and partial["partial_snapshot_import_result"]["summary"]["imported_session_count"] == 1 and "partial_snapshot_import_summary" in partial
    if ok19:
        passed += 1
    else:
        print("FAILED: partial snapshot import", partial)

    reconcile_preview = preview_snapshot_reconcile_in_project_lineage(
        current_project_index=partial["project_index"],
        snapshot_package=snapped["snapshot_export_package"],
        selected_session_ids=["merge_commit_s"],
        target_branch_name="main",
        reconcile_name="reconcile_preview_smoke",
    )
    ok20 = reconcile_preview["summary"]["selected_session_count"] == 1 and "preview_items" in reconcile_preview
    if ok20:
        passed += 1
    else:
        print("FAILED: snapshot reconcile preview", reconcile_preview)

    reconciled = reconcile_snapshot_into_project_lineage(
        current_project_index=partial["project_index"],
        snapshot_package=snapped["snapshot_export_package"],
        reconcile_name="reconcile_smoke",
        selected_session_ids=["merge_commit_s"],
        target_branch_name="main",
        activate_last_reconciled=True,
    )
    ok21 = "snapshot_reconcile_result" in reconciled and reconciled["snapshot_reconcile_result"]["summary"]["reconciled_session_count"] == 1 and "snapshot_reconcile_summary" in reconciled
    if ok21:
        passed += 1
    else:
        print("FAILED: snapshot reconcile", reconciled)

    reconcile_resolved = resolve_snapshot_reconcile_conflicts_in_project_lineage(
        current_project_index=partial["project_index"],
        snapshot_package=snapped["snapshot_export_package"],
        decisions={"merge_commit_s": {"choice": "use_snapshot"}},
        resolution_name="reconcile_resolution_smoke",
        selected_session_ids=["merge_commit_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    ok22 = "snapshot_reconcile_resolution_result" in reconcile_resolved and reconcile_resolved["snapshot_reconcile_resolution_result"]["summary"]["resolved_session_count"] == 1
    if ok22:
        passed += 1
    else:
        print("FAILED: snapshot reconcile resolution", reconcile_resolved)

    reconcile_committed = commit_snapshot_reconcile_resolution_in_project_lineage(
        project_index=reconcile_resolved["project_index"],
        snapshot_reconcile_resolution_result=reconcile_resolved["snapshot_reconcile_resolution_result"],
        commit_name="reconcile_commit_smoke",
        promote_point_name="reconcile_release_smoke",
        promote_point_kind="release",
        note="promote smoke",
    )
    ok23 = "snapshot_reconcile_commit_result" in reconcile_committed and reconcile_committed["snapshot_reconcile_commit_result"]["summary"]["promoted"] is True
    if ok23:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit", reconcile_committed)

    reconcile_committed_2 = commit_snapshot_reconcile_resolution_in_project_lineage(
        project_index=reconcile_committed["project_index"],
        snapshot_reconcile_resolution_result=reconcile_resolved["snapshot_reconcile_resolution_result"],
        commit_name="reconcile_commit_smoke_2",
        promote_point_name="reconcile_tag_smoke",
        promote_point_kind="tag",
        note="promote smoke 2",
    )
    compare_reconcile_commit = compare_snapshot_reconcile_commit_outcomes(
        project_index=reconcile_committed_2["project_index"],
        left_commit_name="reconcile_commit_smoke",
        right_commit_name="reconcile_commit_smoke_2",
    )
    ok24 = compare_reconcile_commit["summary"]["metadata_diff_count"] >= 1 and compare_reconcile_commit["metadata"]["promoted_point_kind"]["changed"] is True
    if ok24:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit compare", compare_reconcile_commit)

    exported_pkg = export_snapshot_reconcile_commit_as_package(
        project_index=reconcile_committed_2["project_index"],
        commit_name="reconcile_commit_smoke",
        package_name="reconcile_commit_pkg_smoke",
        note="portable smoke",
    )
    import_target = export_project_index_from_sessions(
        sessions=[{"session_id": "portable_current", "session": export_session_from_text("spr(seed -> portable_current)", profile="human", decompose=True, initial_state=empty_state(), session_name="Portable Current")}],
        project_name="Portable Import Smoke",
        active_session_id="portable_current",
    )
    imported_pkg = import_snapshot_reconcile_commit_package_into_project(
        current_project_index=import_target,
        package=exported_pkg["snapshot_reconcile_commit_package"],
        import_name="reconcile_commit_pkg_smoke_import",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok25 = "snapshot_reconcile_commit_package_result" in exported_pkg and "snapshot_reconcile_commit_package_import_result" in imported_pkg and imported_pkg["snapshot_reconcile_commit_package_import_result"]["summary"]["imported_session_count"] >= 1
    if ok25:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit package export/import", exported_pkg, imported_pkg)

    previewed_pkg = preview_snapshot_reconcile_commit_package_import_into_project(
        current_project_index=import_target,
        package=exported_pkg["snapshot_reconcile_commit_package"],
        import_name="reconcile_commit_pkg_smoke_preview",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok26 = previewed_pkg["compatibility"]["version_supported"] is True and previewed_pkg["summary"]["resolved_session_count"] >= 1
    if ok26:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit package preview", previewed_pkg)

    resolved_pkg = resolve_snapshot_reconcile_commit_package_import_conflicts_in_project(
        current_project_index=import_target,
        package=exported_pkg["snapshot_reconcile_commit_package"],
        decisions={previewed_pkg["preview_items"][0]["original_session_id"]: {"choice": "use_package"}},
        resolution_name="reconcile_commit_pkg_smoke_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok27 = "snapshot_reconcile_commit_package_resolution_result" in resolved_pkg and resolved_pkg["snapshot_reconcile_commit_package_resolution_result"]["summary"]["resolved_session_count"] >= 1
    if ok27:
        passed += 1
    else:
        print("FAILED: snapshot reconcile commit package resolution", resolved_pkg)

    committed_local = commit_imported_resolution_into_local_outcome_set_in_project(
        resolved_pkg["project_index"],
        package_resolution_result=resolved_pkg["snapshot_reconcile_commit_package_resolution_result"],
        commit_name="local_outcome_smoke",
        promote_point_name="local_release_smoke",
        promote_point_kind="release",
        note="local promote smoke",
    )
    ok28 = "local_outcome_commit_result" in committed_local and committed_local["local_outcome_commit_result"]["commit_name"] == "local_outcome_smoke"
    if ok28:
        passed += 1
    else:
        print("FAILED: local outcome commit/promote", committed_local)

    resolved_pkg_2 = resolve_snapshot_reconcile_commit_package_import_conflicts_in_project(
        current_project_index=committed_local["project_index"],
        package=exported_pkg["snapshot_reconcile_commit_package"],
        decisions={previewed_pkg["preview_items"][0]["original_session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> alt_form)"}},
        resolution_name="reconcile_commit_pkg_smoke_resolution_2",
        target_branch_name="main",
        activate_last_imported=True,
    )
    committed_local_2 = commit_imported_resolution_into_local_outcome_set_in_project(
        resolved_pkg_2["project_index"],
        package_resolution_result=resolved_pkg_2["snapshot_reconcile_commit_package_resolution_result"],
        commit_name="local_outcome_smoke_2",
        promote_point_name="local_release_smoke_2",
        promote_point_kind="release",
        note="local promote smoke 2",
    )
    compare_local = compare_local_imported_promoted_outcomes(
        committed_local_2["project_index"],
        "local_outcome_smoke",
        "local_outcome_smoke_2",
    )
    ok29 = compare_local["left_commit_name"] == "local_outcome_smoke" and compare_local["right_commit_name"] == "local_outcome_smoke_2"
    if ok29:
        passed += 1
    else:
        print("FAILED: local outcome compare", compare_local)

    exported_local_outcome_pkg = export_local_outcome_set_as_portable_package(
        committed_local_2["project_index"],
        "local_outcome_smoke",
        package_name="local_outcome_smoke_pkg",
        note="portable local outcome smoke",
    )
    imported_local_outcome_pkg = import_local_outcome_set_package_into_project(
        import_target,
        exported_local_outcome_pkg["local_outcome_set_package"],
        import_name="local_outcome_smoke_pkg_import",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok30 = "local_outcome_set_package_result" in exported_local_outcome_pkg and "local_outcome_set_package_import_result" in imported_local_outcome_pkg and imported_local_outcome_pkg["local_outcome_set_package_import_result"]["summary"]["imported_session_count"] >= 1
    if ok30:
        passed += 1
    else:
        print("FAILED: local outcome set portable package export/import", exported_local_outcome_pkg, imported_local_outcome_pkg)

    preview_local_outcome_pkg = preview_portable_local_outcome_set_package_import(
        imported_local_outcome_pkg["project_index"],
        exported_local_outcome_pkg["local_outcome_set_package"],
        import_name="local_outcome_smoke_pkg_import_preview",
        target_branch_name="main",
    )
    ok31 = preview_local_outcome_pkg["package_name"] == "local_outcome_smoke_pkg" and preview_local_outcome_pkg["compatibility"]["version_ok"] is True
    if ok31:
        passed += 1
    else:
        print("FAILED: local outcome package preview", preview_local_outcome_pkg)

    resolved_local_outcome_pkg = resolve_local_outcome_set_package_import_conflicts_in_project(
        imported_local_outcome_pkg["project_index"],
        exported_local_outcome_pkg["local_outcome_set_package"],
        decisions={exported_local_outcome_pkg["local_outcome_set_package"]["resolved_sessions"][0]["session_id"]: {"choice": "use_package"}},
        resolution_name="local_outcome_smoke_pkg_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    ok32 = "local_outcome_set_package_resolution_result" in resolved_local_outcome_pkg and resolved_local_outcome_pkg["local_outcome_set_package_resolution_result"]["summary"]["resolved_session_count"] >= 1
    if ok32:
        passed += 1
    else:
        print("FAILED: local outcome package resolution", resolved_local_outcome_pkg)

    committed_local_outcome_pkg = commit_portable_local_outcome_package_resolution_in_project(
        resolved_local_outcome_pkg["project_index"],
        resolved_local_outcome_pkg["local_outcome_set_package_resolution_result"],
        commit_name="local_outcome_pkg_commit_smoke",
        promote_point_name="local_outcome_pkg_release_smoke",
        promote_point_kind="release",
        note="local outcome package smoke commit",
    )
    ok33 = "local_outcome_set_package_commit_result" in committed_local_outcome_pkg and committed_local_outcome_pkg["local_outcome_set_package_commit_result"]["commit_name"] == "local_outcome_pkg_commit_smoke"
    if ok33:
        passed += 1
    else:
        print("FAILED: local outcome package commit", committed_local_outcome_pkg)

    committed_local_outcome_pkg_2 = commit_portable_local_outcome_package_resolution_in_project(
        committed_local_outcome_pkg["project_index"],
        resolved_local_outcome_pkg["local_outcome_set_package_resolution_result"],
        commit_name="local_outcome_pkg_commit_smoke_2",
        promote_point_name="local_outcome_pkg_release_smoke_2",
        promote_point_kind="release",
        note="local outcome package smoke commit 2",
    )
    compare_local_outcome_pkg = compare_committed_portable_local_outcome_packages(
        committed_local_outcome_pkg_2["project_index"],
        "local_outcome_pkg_commit_smoke",
        "local_outcome_pkg_commit_smoke_2",
    )
    ok34 = compare_local_outcome_pkg["left_commit_name"] == "local_outcome_pkg_commit_smoke" and compare_local_outcome_pkg["right_commit_name"] == "local_outcome_pkg_commit_smoke_2"
    if ok34:
        passed += 1
    else:
        print("FAILED: portable local outcome package compare", compare_local_outcome_pkg)

    committed_local_outcome_pkg_3 = commit_portable_local_outcome_package_resolution_in_project(
        committed_local_outcome_pkg_2["project_index"],
        resolved_local_outcome_pkg["local_outcome_set_package_resolution_result"],
        commit_name="local_outcome_pkg_commit_smoke_3",
        promote_point_name="local_outcome_pkg_release_smoke_3",
        promote_point_kind="release",
        note="local outcome package smoke commit 3",
    )
    compare_three_way_local_outcome_pkg = compare_or_three_way_merge_committed_portable_local_outcomes(
        committed_local_outcome_pkg_3["project_index"],
        "local_outcome_pkg_commit_smoke",
        "local_outcome_pkg_commit_smoke_2",
        "local_outcome_pkg_commit_smoke_3",
    )
    ok35 = compare_three_way_local_outcome_pkg["base_commit_name"] == "local_outcome_pkg_commit_smoke" and compare_three_way_local_outcome_pkg["summary"]["original_session_count"] >= 1
    if ok35:
        passed += 1
    else:
        print("FAILED: portable local outcome package three-way merge", compare_three_way_local_outcome_pkg)

    resolved_three_way_local_outcome_pkg = resolve_portable_local_outcome_package_three_way_merge_conflicts_in_project(
        committed_local_outcome_pkg_3["project_index"],
        compare_three_way_local_outcome_pkg,
        decisions={compare_three_way_local_outcome_pkg["merge_items"][0]["original_session_id"]: {"choice": "use_left"}},
        resolution_name="local_outcome_pkg_merge_resolution_smoke",
        target_branch_name="main",
        activate_last_resolved=True,
    )
    ok36 = "portable_local_outcome_package_merge_resolution_result" in resolved_three_way_local_outcome_pkg and resolved_three_way_local_outcome_pkg["portable_local_outcome_package_merge_resolution_result"]["resolution_name"] == "local_outcome_pkg_merge_resolution_smoke"
    if ok36:
        passed += 1
    else:
        print("FAILED: portable local outcome package three-way merge resolution", resolved_three_way_local_outcome_pkg)

    committed_three_way_local_outcome_pkg = commit_portable_local_outcome_package_three_way_merge_resolution_in_project(
        resolved_three_way_local_outcome_pkg["project_index"],
        resolved_three_way_local_outcome_pkg["portable_local_outcome_package_merge_resolution_result"],
        commit_name="local_outcome_pkg_merge_commit_smoke",
        promote_point_name="local_outcome_pkg_merge_release_smoke",
        promote_point_kind="release",
        note="portable local merge commit smoke",
    )
    ok37 = (
        "portable_local_outcome_package_merge_commit_result" in committed_three_way_local_outcome_pkg
        and committed_three_way_local_outcome_pkg["portable_local_outcome_package_merge_commit_result"]["commit_name"] == "local_outcome_pkg_merge_commit_smoke"
    )
    if ok37:
        passed += 1
    else:
        print("FAILED: portable local outcome package three-way merge commit", committed_three_way_local_outcome_pkg)

    inspector_dir = Path(__file__).resolve().parent.parent / "inspector"
    frontend_sources = list(inspector_dir.glob("*.js"))
    ok38 = any("function updatePartialImportSelectors" in source.read_text(encoding="utf-8") for source in frontend_sources)
    if ok38:
        passed += 1
    else:
        print("FAILED: inspector frontend missing updatePartialImportSelectors helper")

    index_html = (inspector_dir / "index.html").read_text(encoding="utf-8")
    ok39 = "/snapshot-reconcile-workflow.js" in index_html and any(
        "createSnapshotReconcileController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok39:
        passed += 1
    else:
        print("FAILED: inspector frontend missing snapshot reconcile workflow module wiring")

    ok40 = "/reconcile-commit-package-workflow.js" in index_html and any(
        "createReconcileCommitPackageController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok40:
        passed += 1
    else:
        print("FAILED: inspector frontend missing reconcile commit package workflow module wiring")

    ok41 = "/local-outcome-set-package-workflow.js" in index_html and any(
        "createLocalOutcomeSetPackageController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok41:
        passed += 1
    else:
        print("FAILED: inspector frontend missing local outcome set package workflow module wiring")

    ok42 = "/project-operations-workflow.js" in index_html and any(
        "createProjectOperationsController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok42:
        passed += 1
    else:
        print("FAILED: inspector frontend missing project operations workflow module wiring")

    ok43 = "/project-workspace-workflow.js" in index_html and any(
        "createProjectWorkspaceController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok43:
        passed += 1
    else:
        print("FAILED: inspector frontend missing project workspace workflow module wiring")

    ok44 = "/project-lifecycle-workflow.js" in index_html and any(
        "createProjectLifecycleController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok44:
        passed += 1
    else:
        print("FAILED: inspector frontend missing project lifecycle workflow module wiring")

    ok45 = "/graph-session-workspace.js" in index_html and any(
        "createGraphSessionWorkspaceController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok45:
        passed += 1
    else:
        print("FAILED: inspector frontend missing graph session workspace module wiring")

    ok46 = "/inspector-bootstrap-workflow.js" in index_html and any(
        "createInspectorBootstrapController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok46:
        passed += 1
    else:
        print("FAILED: inspector frontend missing inspector bootstrap workflow module wiring")

    ok47 = "/inspector-core-workflow.js" in index_html and any(
        "createInspectorCoreController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok47:
        passed += 1
    else:
        print("FAILED: inspector frontend missing inspector core workflow module wiring")

    ok48 = "/inspector-panel-workflow.js" in index_html and any(
        "createInspectorPanelController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok48:
        passed += 1
    else:
        print("FAILED: inspector frontend missing inspector panel workflow module wiring")

    ok49 = "/inspector-action-workflow.js" in index_html and any(
        "createInspectorActionController" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok49:
        passed += 1
    else:
        print("FAILED: inspector frontend missing inspector action workflow module wiring")

    bootstrap_source = (inspector_dir / "inspector-bootstrap-workflow.js").read_text(encoding="utf-8")
    critical_bindings = [
        'bind(els.compareReconcileCommitsBtn, "click", actions.comparePromotedReconcileOutcomes);',
        'bind(els.exportReconcileCommitPackageBtn, "click", actions.exportReconcileCommitPackage);',
        'bind(els.commitReconcileCommitPackageBtn, "click", actions.commitReconcileCommitPackageResolution);',
        'bind(els.previewLocalOutcomeSetPackageBtn, "click", actions.previewLocalOutcomeSetPackageImport);',
        'bind(els.applyLocalOutcomePackageDecisionsBtn, "click", actions.applyLocalOutcomeSetPackageDecisions);',
        'bind(els.commitLocalOutcomeSetPackageBtn, "click", actions.commitLocalOutcomeSetPackageResolution);',
    ]
    ok50 = all(binding in bootstrap_source for binding in critical_bindings)
    if ok50:
        passed += 1
    else:
        print("FAILED: inspector bootstrap missing critical reconcile/local-outcome event bindings")

    frontend_post_routes = set()
    route_pattern = re.compile(r'postJson\("(/api/[^"]+)"')
    for source in frontend_sources:
        frontend_post_routes.update(route_pattern.findall(source.read_text(encoding="utf-8")))
    server_routes = set(re.compile(r'if parsed.path == "(/api/[^"]+)"').findall((Path(__file__).resolve().parent / "inspector_server.py").read_text(encoding="utf-8")))
    missing_frontend_routes = sorted(frontend_post_routes - server_routes)
    ok51 = not missing_frontend_routes
    if ok51:
        passed += 1
    else:
        print(f"FAILED: inspector server missing frontend API routes {missing_frontend_routes}")

    http_test_routes = set()
    tooling_dir = Path(__file__).resolve().parent
    for source in tooling_dir.glob("run_inspector_http*_checks.py"):
        http_test_routes.update(re.compile(r'"(/api/[^"]+)"').findall(source.read_text(encoding="utf-8")))
    uncovered_frontend_routes = sorted(frontend_post_routes - http_test_routes)
    ok52 = not uncovered_frontend_routes
    if ok52:
        passed += 1
    else:
        print(f"FAILED: inspector frontend API routes missing HTTP test coverage {uncovered_frontend_routes}")

    app_dom_ids = set(re.findall(r'document\.getElementById\("([^"]+)"\)', (inspector_dir / "app.js").read_text(encoding="utf-8")))
    html_dom_ids = set(re.findall(r'id="([^"]+)"', index_html))
    missing_dom_ids = sorted(app_dom_ids - html_dom_ids)
    ok53 = not missing_dom_ids
    if ok53:
        passed += 1
    else:
        print(f"FAILED: inspector index.html missing app.js DOM ids {missing_dom_ids}")

    ok54 = 'option value="human" selected' in index_html and 'id="profileHint"' in index_html and any(
        "applyProfileGuidance" in source.read_text(encoding="utf-8")
        for source in frontend_sources
    )
    if ok54:
        passed += 1
    else:
        print("FAILED: inspector profile guidance/default wiring missing")

    ok55 = (
        'src="/inspector-package-guidance.js"' in index_html
        and 'id="snapshotPackageHint"' in index_html
        and 'id="partialImportSelectionHint"' in index_html
        and 'id="snapshotReconcileSessionHint"' in index_html
        and 'id="reconcileCommitPackageHint"' in index_html
        and 'id="localOutcomeSetPackageHint"' in index_html
        and any("InspectorPackageGuidance" in source.read_text(encoding="utf-8") for source in frontend_sources)
    )
    if ok55:
        passed += 1
    else:
        print("FAILED: inspector package guidance wiring missing")

    autofill_sources = [
        inspector_dir / "project-lifecycle-workflow.js",
        inspector_dir / "reconcile-commit-package-workflow.js",
        inspector_dir / "local-outcome-set-package-workflow.js",
    ]
    ok56 = all("dataset.autofillValue" in source.read_text(encoding="utf-8") for source in autofill_sources)
    if ok56:
        passed += 1
    else:
        print("FAILED: inspector package/snapshot autofill wiring missing")

    local_outcome_commit_sources = [
        inspector_dir / "local-outcome-set-package-workflow.js",
        inspector_dir / "inspector-action-workflow.js",
    ]
    ok57 = (
        'id="localOutcomeSetPackageCommitName"' in index_html
        and 'id="localOutcomeSetPackagePromotePointName"' in index_html
        and 'id="commitLocalOutcomeSetPackageBtn"' in index_html
        and any('postJson("/api/commit-local-outcome-set-package-resolution"' in source.read_text(encoding="utf-8") for source in local_outcome_commit_sources)
        and any("commitLocalOutcomeSetPackageResolution" in source.read_text(encoding="utf-8") for source in local_outcome_commit_sources)
    )
    if ok57:
        passed += 1
    else:
        print("FAILED: inspector local outcome package commit/promote wiring missing")

    fallback_sources = [
        inspector_dir / "local-outcome-set-package-workflow.js",
        inspector_dir / "reconcile-commit-package-workflow.js",
    ]
    ok58 = all("snapshot_reconcile_commit_package_commits" in source.read_text(encoding="utf-8") for source in fallback_sources)
    if ok58:
        passed += 1
    else:
        print("FAILED: inspector standalone commit -> local outcome selector fallback wiring missing")

    browser_runner_source = (tooling_dir / "run_inspector_browser_ui_checks.py").read_text(encoding="utf-8")
    ok59 = all(
        marker in browser_runner_source
        for marker in [
            "def run_snapshot_to_portable_pipeline_check(",
            'sample_snapshot_reconcile_project_index.json',
            'sample_snapshot_reconcile_package.json',
            'sample_snapshot_reconcile_commit_package_project_index.json',
            "check_8 = run_snapshot_to_portable_pipeline_check",
            "CHECK snapshot_to_portable_pipeline OK",
        ]
    )
    if ok59:
        passed += 1
    else:
        print("FAILED: inspector browser runner missing snapshot-reconcile -> portable-merge pipeline coverage")

    downstream_autofill_sources = {
        "snapshot": (inspector_dir / "snapshot-reconcile-workflow.js").read_text(encoding="utf-8"),
        "reconcile_package": (inspector_dir / "reconcile-commit-package-workflow.js").read_text(encoding="utf-8"),
        "local_outcome": (inspector_dir / "local-outcome-set-package-workflow.js").read_text(encoding="utf-8"),
        "portable_merge": (inspector_dir / "portable-merge-workstation.js").read_text(encoding="utf-8"),
        "bootstrap": bootstrap_source,
    }
    ok60 = (
        "syncCommitAutofill" in downstream_autofill_sources["snapshot"]
        and "snapshotReconcileCommitName" in downstream_autofill_sources["snapshot"]
        and "syncExportAutofill" in downstream_autofill_sources["reconcile_package"]
        and "reconcileCommitPackageCommitName" in downstream_autofill_sources["reconcile_package"]
        and "syncExportAutofill" in downstream_autofill_sources["local_outcome"]
        and "localOutcomeSetPackageName" in downstream_autofill_sources["local_outcome"]
        and "syncCommitAutofill" in downstream_autofill_sources["portable_merge"]
        and "portableLocalOutcomeMergeCommitName" in downstream_autofill_sources["portable_merge"]
        and 'bind(els.exportReconcileCommitName, "change", actions.syncReconcileCommitPackageExportAutofill);' in downstream_autofill_sources["bootstrap"]
        and 'bind(els.exportLocalOutcomeSetCommit, "change", actions.syncLocalOutcomeSetPackageExportAutofill);' in downstream_autofill_sources["bootstrap"]
    )
    if ok60:
        passed += 1
    else:
        print("FAILED: inspector downstream autofill/export wiring missing")

    guidance_source = (inspector_dir / "inspector-package-guidance.js").read_text(encoding="utf-8")
    reconcile_source = (inspector_dir / "reconcile-commit-package-workflow.js").read_text(encoding="utf-8")
    local_source = (inspector_dir / "local-outcome-set-package-workflow.js").read_text(encoding="utf-8")
    styles_source = (inspector_dir / "styles.css").read_text(encoding="utf-8")
    ok61 = (
        'id="reconcileCommitPackageCurrentSummary"' in index_html
        and 'id="localOutcomeSetPackageCurrentSummary"' in index_html
        and "renderPayloadSummary" in guidance_source
        and "reconcileCommitPackageCurrentSummary" in reconcile_source
        and "localOutcomeSetPackageCurrentSummary" in local_source
    )
    if ok61:
        passed += 1
    else:
        print("FAILED: inspector package summary cards/wiring missing")

    ok62 = (
        "packageGuidanceNextAction" in guidance_source
        and "package-guidance-next-action" in guidance_source
        and "Next action:" in guidance_source
        and ".package-guidance-next-action" in styles_source
        and "snapshot_next_action" in browser_runner_source
        and "standalone_next_action" in browser_runner_source
        and "local_next_action" in browser_runner_source
    )
    if ok62:
        passed += 1
    else:
        print("FAILED: inspector package guidance next-action contract missing")

    portable_merge_source = downstream_autofill_sources["portable_merge"]
    ok63 = (
        "merge-next-action" in portable_merge_source
        and "Manual decisions" in portable_merge_source
        and "Skipped" in portable_merge_source
        and "Review decisions, then apply merge decisions." in portable_merge_source
        and "Ready to commit resolved portable merge." in portable_merge_source
        and ".merge-next-action" in styles_source
        and ".merge-session-card.needs-input" in styles_source
        and "portable_merge_guidance" in browser_runner_source
        and "portable_merge_resolution_guidance" in browser_runner_source
    )
    if ok63:
        passed += 1
    else:
        print("FAILED: inspector portable merge workstation decision guidance contract missing")

    print(f"editor_visual_inspector: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
