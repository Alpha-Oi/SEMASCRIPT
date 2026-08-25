from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from inspector_server import InspectorHandler


def post_json(base_url: str, path: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


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


def export_text_session(base_url: str, text: str, session_name: str) -> dict:
    _, payload = post_json(base_url, "/api/export-session-text", {
        "text": text,
        "profile": "human",
        "decompose": True,
        "initial_state": empty_state(),
        "session_name": session_name,
    })
    return payload


def export_project_index(base_url: str, sessions: list[dict], project_name: str, active_session_id: str) -> dict:
    _, payload = post_json(base_url, "/api/export-project-index", {
        "sessions": sessions,
        "project_name": project_name,
        "active_session_id": active_session_id,
    })
    return payload


def find_session(project_index: dict, session_id: str) -> dict:
    return next(item for item in project_index.get("sessions", []) if item["session_id"] == session_id)


def main() -> None:
    total = 7
    passed = 0

    server = ThreadingHTTPServer(("127.0.0.1", 0), InspectorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        source_base = export_text_session(base_url, "gen(template -> instance)", "Lifecycle Source Base")
        source_feature = export_text_session(base_url, "spr(seed -> source_form)", "Lifecycle Source Feature")
        current_head = export_text_session(base_url, "spr(seed -> current_form)", "Lifecycle Current Head")
        alternate_head = export_text_session(base_url, "spr(seed -> alternate_form)", "Lifecycle Alternate Head")

        source_project = export_project_index(
            base_url,
            [
                {"session_id": "base_s", "session": source_base, "tags": ["source"]},
                {"session_id": "feature_s", "session": source_feature, "tags": ["feature"]},
            ],
            project_name="HTTP Lifecycle Source",
            active_session_id="feature_s",
        )
        _, tagged_source = post_json(base_url, "/api/create-project-tag-release-point", {
            "project_index": source_project,
            "tag_name": "http_lifecycle_release",
            "target_session_id": "feature_s",
            "point_kind": "release",
            "note": "lifecycle anchor",
        })
        _, snapshot_export = post_json(base_url, "/api/create-project-snapshot-export", {
            "project_index": tagged_source["project_index"],
            "source_point_name": "http_lifecycle_release",
            "snapshot_name": "http_lifecycle_snapshot",
            "note": "lifecycle snapshot",
        })

        current_project = export_project_index(
            base_url,
            [
                {"session_id": "current_s", "session": current_head, "tags": ["current"]},
                {"session_id": "alternate_s", "session": alternate_head, "tags": ["alternate"]},
            ],
            project_name="HTTP Lifecycle Current",
            active_session_id="current_s",
        )

        _, switched_project = post_json(base_url, "/api/switch-project-session", {
            "project_index": current_project,
            "session_id": "alternate_s",
        })
        ok1 = (
            switched_project["project_index"]["active_session_id"] == "alternate_s"
            and switched_project["session_name"] == "Lifecycle Alternate Head"
            and switched_project["project_index"]["active_branch_name"] == "main"
        )
        if ok1:
            passed += 1
        else:
            print("FAILED: switch project session route", switched_project)

        _, partial_import = post_json(base_url, "/api/partial-import-project-from-snapshot", {
            "current_project_index": switched_project["project_index"],
            "snapshot_package": snapshot_export["snapshot_export_package"],
            "import_name": "http_lifecycle_partial_import",
            "selected_session_ids": ["feature_s"],
            "selected_tag_point_names": ["http_lifecycle_release"],
            "selected_snapshot_export_names": [],
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        imported_id = partial_import["partial_snapshot_import_result"]["imported_session_ids"][0]
        ok2 = (
            partial_import["partial_snapshot_import_result"]["summary"]["imported_session_count"] == 1
            and imported_id != "feature_s"
            and partial_import["project_index"]["active_session_id"] == imported_id
            and "http_lifecycle_partial_import" in partial_import["project_index"]["partial_snapshot_imports"]
        )
        if ok2:
            passed += 1
        else:
            print("FAILED: partial snapshot import route", partial_import)

        _, direct_reconcile = post_json(base_url, "/api/reconcile-snapshot-into-project", {
            "current_project_index": switched_project["project_index"],
            "snapshot_package": snapshot_export["snapshot_export_package"],
            "reconcile_name": "http_lifecycle_reconcile",
            "selected_session_ids": ["feature_s"],
            "target_branch_name": "main",
            "activate_last_reconciled": True,
        })
        reconciled_id = direct_reconcile["snapshot_reconcile_result"]["reconciled_session_ids"][0]
        reconciled_entry = find_session(direct_reconcile["project_index"], reconciled_id)
        ok3 = (
            direct_reconcile["snapshot_reconcile_result"]["summary"]["reconciled_session_count"] == 1
            and reconciled_entry["entry_metadata"]["commit_kind"] == "snapshot_reconcile"
            and reconciled_entry["entry_metadata"]["snapshot_reconcile"]["reconciled_with_head_session_id"] == "alternate_s"
        )
        if ok3:
            passed += 1
        else:
            print("FAILED: direct snapshot reconcile route", direct_reconcile)

        _, reconcile_resolution = post_json(base_url, "/api/resolve-snapshot-reconcile-conflicts", {
            "current_project_index": switched_project["project_index"],
            "snapshot_package": snapshot_export["snapshot_export_package"],
            "decisions": {"feature_s": {"choice": "use_snapshot"}},
            "resolution_name": "http_lifecycle_resolution",
            "selected_session_ids": ["feature_s"],
            "target_branch_name": "main",
            "activate_last_resolved": True,
        })
        _, reconcile_commit_a = post_json(base_url, "/api/commit-snapshot-reconcile-resolution", {
            "project_index": reconcile_resolution["project_index"],
            "snapshot_reconcile_resolution_result": reconcile_resolution["snapshot_reconcile_resolution_result"],
            "commit_name": "http_lifecycle_commit_a",
            "promote_point_name": "http_lifecycle_release_a",
            "promote_point_kind": "release",
            "note": "lifecycle commit a",
        })
        _, reconcile_commit_b = post_json(base_url, "/api/commit-snapshot-reconcile-resolution", {
            "project_index": reconcile_commit_a["project_index"],
            "snapshot_reconcile_resolution_result": reconcile_resolution["snapshot_reconcile_resolution_result"],
            "commit_name": "http_lifecycle_commit_b",
            "promote_point_name": "http_lifecycle_tag_b",
            "promote_point_kind": "tag",
            "note": "lifecycle commit b",
        })
        _, reconcile_compare = post_json(base_url, "/api/compare-snapshot-reconcile-commits", {
            "project_index": reconcile_commit_b["project_index"],
            "left_commit_name": "http_lifecycle_commit_a",
            "right_commit_name": "http_lifecycle_commit_b",
        })
        ok4 = (
            reconcile_compare["left_commit_name"] == "http_lifecycle_commit_a"
            and reconcile_compare["right_commit_name"] == "http_lifecycle_commit_b"
            and reconcile_compare["metadata"]["promoted_point_kind"]["changed"] is True
            and reconcile_compare["summary"]["metadata_diff_count"] >= 1
        )
        if ok4:
            passed += 1
        else:
            print("FAILED: compare snapshot reconcile commits route", reconcile_compare)

        _, standalone_package_export = post_json(base_url, "/api/export-snapshot-reconcile-commit-package", {
            "project_index": reconcile_commit_b["project_index"],
            "commit_name": "http_lifecycle_commit_a",
            "package_name": "http_lifecycle_standalone_pkg",
            "note": "lifecycle standalone package",
        })
        standalone_target = export_project_index(
            base_url,
            [{"session_id": "target_current", "session": current_head, "tags": ["target"]}],
            project_name="HTTP Lifecycle Standalone Import",
            active_session_id="target_current",
        )
        _, standalone_import = post_json(base_url, "/api/import-snapshot-reconcile-commit-package", {
            "current_project_index": standalone_target,
            "package": standalone_package_export["snapshot_reconcile_commit_package"],
            "import_name": "http_lifecycle_standalone_import",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        imported_commit_name = standalone_import["snapshot_reconcile_commit_package_import_result"]["imported_commit_name"]
        ok5 = (
            standalone_import["snapshot_reconcile_commit_package_import_result"]["summary"]["imported_session_count"] == 1
            and "http_lifecycle_standalone_import" in standalone_import["project_index"]["snapshot_reconcile_commit_package_imports"]
            and imported_commit_name in standalone_import["project_index"]["snapshot_reconcile_commits"]
        )
        if ok5:
            passed += 1
        else:
            print("FAILED: direct standalone package import route", standalone_import)

        local_outcome_target = export_project_index(
            base_url,
            [{"session_id": "local_current", "session": current_head, "tags": ["local-current"]}],
            project_name="HTTP Lifecycle Local Outcome Build",
            active_session_id="local_current",
        )
        _, local_outcome_resolution = post_json(base_url, "/api/resolve-snapshot-reconcile-commit-package-import", {
            "current_project_index": local_outcome_target,
            "package": standalone_package_export["snapshot_reconcile_commit_package"],
            "decisions": {"feature_s_reconcile_resolved": {"choice": "use_package"}},
            "resolution_name": "http_lifecycle_local_resolution",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        _, local_outcome_commit = post_json(base_url, "/api/commit-snapshot-reconcile-commit-package-resolution", {
            "project_index": local_outcome_resolution["project_index"],
            "snapshot_reconcile_commit_package_resolution_result": local_outcome_resolution["snapshot_reconcile_commit_package_resolution_result"],
            "commit_name": "http_lifecycle_local_outcome_commit",
            "promote_point_name": "http_lifecycle_local_release",
            "promote_point_kind": "release",
            "note": "lifecycle local outcome commit",
        })
        _, local_package_export = post_json(base_url, "/api/export-local-outcome-set-package", {
            "project_index": local_outcome_commit["project_index"],
            "commit_name": "http_lifecycle_local_outcome_commit",
            "package_name": "http_lifecycle_local_pkg",
            "note": "lifecycle local package",
        })
        local_import_target = export_project_index(
            base_url,
            [{"session_id": "portable_current", "session": alternate_head, "tags": ["portable"]}],
            project_name="HTTP Lifecycle Local Import",
            active_session_id="portable_current",
        )
        _, local_direct_import = post_json(base_url, "/api/import-local-outcome-set-package", {
            "current_project_index": local_import_target,
            "package": local_package_export["local_outcome_set_package"],
            "import_name": "http_lifecycle_local_import",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        ok6 = (
            "http_lifecycle_local_import" in local_direct_import["project_index"]["local_outcome_set_package_imports"]
            and any(event["event_type"] == "local_outcome_set_package_imported" for event in local_direct_import["project_index"]["history"]["events"])
            and local_direct_import["local_outcome_set_package_import_result"]["imported_commit_name"] in local_direct_import["project_index"]["snapshot_reconcile_commit_package_commits"]
        )
        if ok6:
            passed += 1
        else:
            print("FAILED: direct local outcome package import route", local_direct_import)

        _, local_commit_a_resolution = post_json(base_url, "/api/resolve-local-outcome-set-package-import-conflicts", {
            "current_project_index": local_outcome_commit["project_index"],
            "package_data": local_package_export["local_outcome_set_package"],
            "decisions": {
                local_package_export["local_outcome_set_package"]["resolved_sessions"][0]["session_id"]: {"choice": "use_package"},
            },
            "resolution_name": "http_lifecycle_compare_local_resolution",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        _, local_commit_a = post_json(base_url, "/api/commit-local-outcome-set-package-resolution", {
            "project_index": local_commit_a_resolution["project_index"],
            "local_outcome_set_package_resolution_result": local_commit_a_resolution["local_outcome_set_package_resolution_result"],
            "commit_name": "http_lifecycle_local_compare_a",
            "promote_point_name": "http_lifecycle_local_compare_release_a",
            "promote_point_kind": "release",
            "note": "local compare a",
        })
        _, local_commit_b = post_json(base_url, "/api/commit-local-outcome-set-package-resolution", {
            "project_index": local_commit_a["project_index"],
            "local_outcome_set_package_resolution_result": local_commit_a_resolution["local_outcome_set_package_resolution_result"],
            "commit_name": "http_lifecycle_local_compare_b",
            "promote_point_name": "http_lifecycle_local_compare_release_b",
            "promote_point_kind": "release",
            "note": "local compare b",
        })
        _, local_compare = post_json(base_url, "/api/compare-committed-portable-local-outcome-packages", {
            "project_index": local_commit_b["project_index"],
            "left_commit_name": "http_lifecycle_local_compare_a",
            "right_commit_name": "http_lifecycle_local_compare_b",
        })
        ok7 = (
            local_compare["left_commit_name"] == "http_lifecycle_local_compare_a"
            and local_compare["right_commit_name"] == "http_lifecycle_local_compare_b"
            and local_compare["metadata"]["promoted_point_name"]["same"] is False
            and local_compare["summary"]["promoted_point_differs"] is True
            and local_compare["summary"]["has_any_diff"] is True
        )
        if ok7:
            passed += 1
        else:
            print("FAILED: compare committed portable local outcomes route", local_compare)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    print(f"inspector_http_lifecycle_import_e2e: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
