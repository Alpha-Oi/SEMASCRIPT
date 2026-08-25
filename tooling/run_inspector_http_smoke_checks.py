from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from inspector_server import InspectorHandler
from project_model import (
    add_session_to_workspace,
    compare_baseline_or_three_way_portable_local_outcomes_in_project,
    create_local_outcome_set_package_export_in_project,
    create_local_outcome_set_package_import_commit_in_project,
    create_local_outcome_set_package_import_resolution_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_commit_in_project,
    create_snapshot_reconcile_commit_package_import_resolution_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_tag_release_in_project,
    create_workspace,
)
from session_model import create_session_from_text


def fetch(base_url: str, path: str) -> tuple[int, str]:
    with urlopen(f"{base_url}{path}") as response:
        body = response.read().decode("utf-8")
        return response.status, body


def post_json(base_url: str, path: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def empty_state() -> dict:
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


def build_simple_project_index() -> dict:
    session = create_session_from_text(
        "gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="HTTP Smoke Session",
    )
    project = create_workspace(project_name="HTTP Smoke Project")
    project = add_session_to_workspace(project, session, session_id="http_smoke_s")
    return project


def build_portable_merge_http_payloads() -> tuple[dict, dict]:
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

    resolved, source_resolution_result = create_snapshot_reconcile_resolution_in_project(
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
        snapshot_reconcile_resolution_result=source_resolution_result,
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
    resolved_pkg, intermediate_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=committed,
        package=intermediate_pkg,
        decisions={"feature_s_reconcile_resolved": {"choice": "use_package"}},
        resolution_name="pkg_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    local_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
        resolved_pkg,
        intermediate_resolution_result,
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
    base_project, base_resolution_result = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=local_committed,
        package_data=portable_pkg,
        decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "use_package"}},
        resolution_name="base_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    base_project, _ = create_local_outcome_set_package_import_commit_in_project(
        project_index=base_project,
        local_outcome_set_package_resolution_result=base_resolution_result,
        commit_name="base_commit",
        promote_point_name="base_release",
        promote_point_kind="release",
        note="base",
    )
    left_project, left_resolution_result = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=base_project,
        package_data=portable_pkg,
        decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> left_form)"}},
        resolution_name="left_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    left_project, _ = create_local_outcome_set_package_import_commit_in_project(
        project_index=left_project,
        local_outcome_set_package_resolution_result=left_resolution_result,
        commit_name="left_commit",
        promote_point_name="left_release",
        promote_point_kind="release",
        note="left",
    )
    right_project, right_resolution_result = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=left_project,
        package_data=portable_pkg,
        decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> right_form)"}},
        resolution_name="right_resolution",
        target_branch_name="main",
        activate_last_imported=True,
    )
    right_project, _ = create_local_outcome_set_package_import_commit_in_project(
        project_index=right_project,
        local_outcome_set_package_resolution_result=right_resolution_result,
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
    return right_project, merge_result


def main() -> None:
    total = 15
    passed = 0

    server = ThreadingHTTPServer(("127.0.0.1", 0), InspectorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        status_root, body_root = fetch(base_url, "/")
        ok1 = status_root == 200 and "SEMASCRIPT Inspector" in body_root and "inspector-action-workflow.js" in body_root
        if ok1:
            passed += 1
        else:
            print("FAILED: inspector index route")

        status_action, body_action = fetch(base_url, "/inspector-action-workflow.js")
        ok2 = status_action == 200 and "createInspectorActionController" in body_action
        if ok2:
            passed += 1
        else:
            print("FAILED: inspector action workflow static route")

        status_merge, body_merge = fetch(base_url, "/portable-merge-workstation.js")
        ok3 = status_merge == 200 and "createPortableLocalOutcomeMergeController" in body_merge
        if ok3:
            passed += 1
        else:
            print("FAILED: portable merge workstation static route")

        status_styles, body_styles = fetch(base_url, "/styles.css")
        ok4 = status_styles == 200 and ".merge-workstation-card" in body_styles
        if ok4:
            passed += 1
        else:
            print("FAILED: inspector styles route")

        status_samples, body_samples = fetch(base_url, "/api/samples")
        samples_payload = json.loads(body_samples)
        ok5 = status_samples == 200 and len(samples_payload.get("samples", [])) >= 3
        if ok5:
            passed += 1
        else:
            print("FAILED: inspector api samples route")

        analyze_status, analyze_payload = post_json(base_url, "/api/analyze", {
            "text": "gen(template -> instance)",
            "profile": "human",
            "decompose": True,
            "initial_state": empty_state(),
        })
        ok6 = analyze_status == 200 and analyze_payload["validation"]["valid"] is True and "graph_document" in analyze_payload
        if ok6:
            passed += 1
        else:
            print("FAILED: inspector analyze route")

        import_project_status, import_project_payload = post_json(base_url, "/api/import-project-index", {
            "project_index": build_simple_project_index(),
        })
        ok7 = (
            import_project_status == 200
            and import_project_payload["project_index"]["active_session_id"] == "http_smoke_s"
            and len(import_project_payload["workspace_summary"]) == 1
        )
        if ok7:
            passed += 1
        else:
            print("FAILED: inspector import project route")

        branch_status, branch_payload = post_json(base_url, "/api/create-project-branch", {
            "project_index": import_project_payload["project_index"],
            "source_session_id": "http_smoke_s",
            "branch_name": "http_smoke_branch",
        })
        ok8 = branch_status == 200 and any(
            branch["branch_name"] == "http_smoke_branch"
            for branch in branch_payload.get("branch_summary", [])
        )
        if ok8:
            passed += 1
        else:
            print("FAILED: inspector create branch route")

        tag_status, tag_payload = post_json(base_url, "/api/create-project-tag-release-point", {
            "project_index": branch_payload["project_index"],
            "tag_name": "http_smoke_release",
            "target_session_id": "http_smoke_s",
            "point_kind": "release",
            "note": "http smoke release",
        })
        ok9 = tag_status == 200 and tag_payload["tag_release_result"]["tag_name"] == "http_smoke_release"
        if ok9:
            passed += 1
        else:
            print("FAILED: inspector tag/release route")

        snapshot_export_status, snapshot_export_payload = post_json(base_url, "/api/create-project-snapshot-export", {
            "project_index": tag_payload["project_index"],
            "source_point_name": "http_smoke_release",
            "snapshot_name": "http_smoke_snapshot",
            "note": "http smoke snapshot",
        })
        ok10 = (
            snapshot_export_status == 200
            and snapshot_export_payload["snapshot_export_result"]["snapshot_name"] == "http_smoke_snapshot"
            and "snapshot_export_package" in snapshot_export_payload
        )
        if ok10:
            passed += 1
        else:
            print("FAILED: inspector snapshot export route")

        snapshot_preview_status, snapshot_preview_payload = post_json(base_url, "/api/preview-project-snapshot-restore", {
            "current_project_index": tag_payload["project_index"],
            "snapshot_package": snapshot_export_payload["snapshot_export_package"],
            "restored_project_name": "HTTP Smoke Preview Restore",
            "activate_anchor": True,
        })
        ok11 = (
            snapshot_preview_status == 200
            and snapshot_preview_payload["snapshot_name"] == "http_smoke_snapshot"
            and snapshot_preview_payload["restore_target"]["would_activate_session_id"] == "http_smoke_s"
        )
        if ok11:
            passed += 1
        else:
            print("FAILED: inspector snapshot restore preview route")

        snapshot_restore_status, snapshot_restore_payload = post_json(base_url, "/api/restore-project-from-snapshot-export", {
            "snapshot_package": snapshot_export_payload["snapshot_export_package"],
            "restored_project_name": "HTTP Smoke Restored Project",
            "restore_name": "http_smoke_restore",
            "activate_anchor": True,
        })
        ok12 = (
            snapshot_restore_status == 200
            and snapshot_restore_payload["snapshot_restore_result"]["restore_name"] == "http_smoke_restore"
            and snapshot_restore_payload["project_index"]["active_session_id"] == "http_smoke_s"
        )
        if ok12:
            passed += 1
        else:
            print("FAILED: inspector snapshot restore route")

        portable_project, portable_merge_result = build_portable_merge_http_payloads()
        merge_compare_status, merge_compare_payload = post_json(
            base_url,
            "/api/compare-or-three-way-merge-committed-portable-local-outcomes",
            {
                "project_index": portable_project,
                "base_commit_name": "base_commit",
                "left_commit_name": "left_commit",
                "right_commit_name": "right_commit",
            },
        )
        ok13 = (
            merge_compare_status == 200
            and merge_compare_payload["base_commit_name"] == portable_merge_result["base_commit_name"]
            and len(merge_compare_payload.get("merge_items", [])) >= 1
        )
        if ok13:
            passed += 1
        else:
            print("FAILED: portable local outcome compare/merge route")

        merge_resolve_status, merge_resolve_payload = post_json(
            base_url,
            "/api/resolve-portable-local-outcome-package-three-way-merge-conflicts",
            {
                "project_index": portable_project,
                "merge_result": merge_compare_payload,
                "decisions": {
                    merge_compare_payload["merge_items"][0]["original_session_id"]: {"choice": "use_right"},
                },
                "resolution_name": "portable_local_merge_resolution_http",
                "target_branch_name": "main",
                "activate_last_resolved": True,
            },
        )
        ok14 = (
            merge_resolve_status == 200
            and merge_resolve_payload["portable_local_outcome_package_merge_resolution_result"]["resolution_name"] == "portable_local_merge_resolution_http"
        )
        if ok14:
            passed += 1
        else:
            print("FAILED: portable local outcome merge resolution route")

        merge_commit_status, merge_commit_payload = post_json(
            base_url,
            "/api/commit-portable-local-outcome-package-three-way-merge-resolution",
            {
                "project_index": merge_resolve_payload["project_index"],
                "merge_resolution_result": merge_resolve_payload["portable_local_outcome_package_merge_resolution_result"],
                "commit_name": "portable_local_merge_commit_http",
                "promote_point_name": "portable_local_merge_release_http",
                "promote_point_kind": "release",
                "note": "portable local merge http smoke",
            },
        )
        ok15 = (
            merge_commit_status == 200
            and merge_commit_payload["portable_local_outcome_package_merge_commit_result"]["commit_name"] == "portable_local_merge_commit_http"
            and merge_commit_payload["portable_local_outcome_package_merge_commit_result"]["summary"]["promoted"] is True
        )
        if ok15:
            passed += 1
        else:
            print("FAILED: portable local outcome merge commit route")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    print(f"inspector_http: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
