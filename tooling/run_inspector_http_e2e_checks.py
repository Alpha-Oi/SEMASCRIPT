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


def main() -> None:
    total = 7
    passed = 0

    server = ThreadingHTTPServer(("127.0.0.1", 0), InspectorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        source_base = export_text_session(base_url, "gen(template -> instance)", "Source Base")
        source_feature = export_text_session(base_url, "spr(seed -> source_form)", "Source Feature")
        current_head = export_text_session(base_url, "spr(seed -> current_form)", "Current Head")
        target_current = export_text_session(base_url, "spr(seed -> portable_current)", "Portable Current")

        source_project = export_project_index(
            base_url,
            [
                {"session_id": "base_s", "session": source_base, "tags": ["source"]},
                {"session_id": "feature_s", "session": source_feature, "tags": ["feature"]},
            ],
            project_name="HTTP E2E Source",
            active_session_id="feature_s",
        )
        _, tagged_source = post_json(base_url, "/api/create-project-tag-release-point", {
            "project_index": source_project,
            "tag_name": "http_e2e_release",
            "target_session_id": "feature_s",
            "point_kind": "release",
            "note": "http e2e anchor",
        })
        _, snapshot_export = post_json(base_url, "/api/create-project-snapshot-export", {
            "project_index": tagged_source["project_index"],
            "source_point_name": "http_e2e_release",
            "snapshot_name": "http_e2e_snapshot",
            "note": "http e2e snapshot",
        })

        current_project = export_project_index(
            base_url,
            [
                {"session_id": "current_s", "session": current_head, "tags": ["current"]},
            ],
            project_name="HTTP E2E Current",
            active_session_id="current_s",
        )

        _, reconcile_preview = post_json(base_url, "/api/preview-snapshot-reconcile-in-project", {
            "current_project_index": current_project,
            "snapshot_package": snapshot_export["snapshot_export_package"],
            "selected_session_ids": ["feature_s"],
            "target_branch_name": "main",
            "reconcile_name": "http_e2e_reconcile_preview",
        })
        ok1 = (
            reconcile_preview["summary"]["selected_session_count"] == 1
            and len(reconcile_preview.get("preview_items", [])) == 1
            and reconcile_preview["preview_items"][0]["original_session_id"] == "feature_s"
        )
        if ok1:
            passed += 1
        else:
            print("FAILED: snapshot reconcile preview scenario", reconcile_preview)

        _, reconcile_resolution = post_json(base_url, "/api/resolve-snapshot-reconcile-conflicts", {
            "current_project_index": current_project,
            "snapshot_package": snapshot_export["snapshot_export_package"],
            "decisions": {"feature_s": {"choice": "use_snapshot"}},
            "resolution_name": "http_e2e_reconcile_resolution",
            "selected_session_ids": ["feature_s"],
            "target_branch_name": "main",
            "activate_last_resolved": True,
        })
        _, reconcile_commit = post_json(base_url, "/api/commit-snapshot-reconcile-resolution", {
            "project_index": reconcile_resolution["project_index"],
            "snapshot_reconcile_resolution_result": reconcile_resolution["snapshot_reconcile_resolution_result"],
            "commit_name": "http_e2e_reconcile_commit",
            "promote_point_name": "http_e2e_reconcile_release",
            "promote_point_kind": "release",
            "note": "http e2e reconcile commit",
        })
        ok2 = (
            reconcile_commit["snapshot_reconcile_commit_result"]["commit_name"] == "http_e2e_reconcile_commit"
            and reconcile_commit["snapshot_reconcile_commit_result"]["summary"]["promoted"] is True
        )
        if ok2:
            passed += 1
        else:
            print("FAILED: snapshot reconcile resolution/commit scenario", reconcile_commit)

        _, standalone_package_export = post_json(base_url, "/api/export-snapshot-reconcile-commit-package", {
            "project_index": reconcile_commit["project_index"],
            "commit_name": "http_e2e_reconcile_commit",
            "package_name": "http_e2e_standalone_pkg",
            "note": "http e2e standalone package",
        })

        target_project = export_project_index(
            base_url,
            [
                {"session_id": "portable_current", "session": target_current, "tags": ["portable"]},
            ],
            project_name="HTTP E2E Target",
            active_session_id="portable_current",
        )
        _, standalone_preview = post_json(base_url, "/api/preview-snapshot-reconcile-commit-package-import", {
            "current_project_index": target_project,
            "package": standalone_package_export["snapshot_reconcile_commit_package"],
            "import_name": "http_e2e_standalone_import_preview",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        _, standalone_resolution = post_json(base_url, "/api/resolve-snapshot-reconcile-commit-package-import", {
            "current_project_index": target_project,
            "package": standalone_package_export["snapshot_reconcile_commit_package"],
            "decisions": {
                standalone_preview["preview_items"][0]["original_session_id"]: {"choice": "use_package"},
            },
            "resolution_name": "http_e2e_standalone_resolution",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        _, standalone_commit = post_json(base_url, "/api/commit-snapshot-reconcile-commit-package-resolution", {
            "project_index": standalone_resolution["project_index"],
            "snapshot_reconcile_commit_package_resolution_result": standalone_resolution["snapshot_reconcile_commit_package_resolution_result"],
            "commit_name": "http_e2e_local_outcome_commit",
            "promote_point_name": "http_e2e_local_outcome_release",
            "promote_point_kind": "release",
            "note": "http e2e standalone commit",
        })
        ok3 = (
            standalone_preview["compatibility"]["version_supported"] is True
            and standalone_commit["snapshot_reconcile_commit_package_commit_result"]["commit_name"] == "http_e2e_local_outcome_commit"
            and standalone_commit["snapshot_reconcile_commit_package_commit_result"]["summary"]["promoted"] is True
        )
        if ok3:
            passed += 1
        else:
            print("FAILED: standalone package scenario", standalone_preview, standalone_commit)

        _, local_package_export = post_json(base_url, "/api/export-local-outcome-set-package", {
            "project_index": standalone_commit["project_index"],
            "commit_name": "http_e2e_local_outcome_commit",
            "package_name": "http_e2e_local_pkg",
            "note": "http e2e local package",
        })
        _, local_package_preview = post_json(base_url, "/api/preview-local-outcome-set-package-import", {
            "current_project_index": standalone_commit["project_index"],
            "package_data": local_package_export["local_outcome_set_package"],
            "import_name": "http_e2e_local_preview",
            "target_branch_name": "main",
        })
        ok4 = (
            local_package_export["local_outcome_set_package_result"]["package_name"] == "http_e2e_local_pkg"
            and local_package_preview["compatibility"]["version_ok"] is True
        )
        if ok4:
            passed += 1
        else:
            print("FAILED: local outcome package export/preview scenario", local_package_export, local_package_preview)

        package_session_id = local_package_export["local_outcome_set_package"]["resolved_sessions"][0]["session_id"]
        _, base_resolution = post_json(base_url, "/api/resolve-local-outcome-set-package-import-conflicts", {
            "current_project_index": standalone_commit["project_index"],
            "package_data": local_package_export["local_outcome_set_package"],
            "decisions": {package_session_id: {"choice": "use_package"}},
            "resolution_name": "http_e2e_base_resolution",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        _, base_commit = post_json(base_url, "/api/commit-local-outcome-set-package-resolution", {
            "project_index": base_resolution["project_index"],
            "local_outcome_set_package_resolution_result": base_resolution["local_outcome_set_package_resolution_result"],
            "commit_name": "http_e2e_base_commit",
            "promote_point_name": "http_e2e_base_release",
            "promote_point_kind": "release",
            "note": "http e2e base",
        })

        _, left_resolution = post_json(base_url, "/api/resolve-local-outcome-set-package-import-conflicts", {
            "current_project_index": base_commit["project_index"],
            "package_data": local_package_export["local_outcome_set_package"],
            "decisions": {package_session_id: {"choice": "custom_text", "custom_text": "spr(seed -> left_http_form)"}},
            "resolution_name": "http_e2e_left_resolution",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        _, left_commit = post_json(base_url, "/api/commit-local-outcome-set-package-resolution", {
            "project_index": left_resolution["project_index"],
            "local_outcome_set_package_resolution_result": left_resolution["local_outcome_set_package_resolution_result"],
            "commit_name": "http_e2e_left_commit",
            "promote_point_name": "http_e2e_left_release",
            "promote_point_kind": "release",
            "note": "http e2e left",
        })

        _, right_resolution = post_json(base_url, "/api/resolve-local-outcome-set-package-import-conflicts", {
            "current_project_index": left_commit["project_index"],
            "package_data": local_package_export["local_outcome_set_package"],
            "decisions": {package_session_id: {"choice": "custom_text", "custom_text": "spr(seed -> right_http_form)"}},
            "resolution_name": "http_e2e_right_resolution",
            "target_branch_name": "main",
            "activate_last_imported": True,
        })
        _, right_commit = post_json(base_url, "/api/commit-local-outcome-set-package-resolution", {
            "project_index": right_resolution["project_index"],
            "local_outcome_set_package_resolution_result": right_resolution["local_outcome_set_package_resolution_result"],
            "commit_name": "http_e2e_right_commit",
            "promote_point_name": "http_e2e_right_release",
            "promote_point_kind": "release",
            "note": "http e2e right",
        })
        ok5 = (
            base_commit["local_outcome_set_package_commit_result"]["commit_name"] == "http_e2e_base_commit"
            and left_commit["local_outcome_set_package_commit_result"]["commit_name"] == "http_e2e_left_commit"
            and right_commit["local_outcome_set_package_commit_result"]["commit_name"] == "http_e2e_right_commit"
        )
        if ok5:
            passed += 1
        else:
            print("FAILED: local outcome base/left/right commit scenario", base_commit, left_commit, right_commit)

        _, merge_compare = post_json(base_url, "/api/compare-or-three-way-merge-committed-portable-local-outcomes", {
            "project_index": right_commit["project_index"],
            "base_commit_name": "http_e2e_base_commit",
            "left_commit_name": "http_e2e_left_commit",
            "right_commit_name": "http_e2e_right_commit",
        })
        _, merge_resolution = post_json(base_url, "/api/resolve-portable-local-outcome-package-three-way-merge-conflicts", {
            "project_index": right_commit["project_index"],
            "merge_result": merge_compare,
            "decisions": {
                merge_compare["merge_items"][0]["original_session_id"]: {"choice": "use_right"},
            },
            "resolution_name": "http_e2e_portable_merge_resolution",
            "target_branch_name": "main",
            "activate_last_resolved": True,
        })
        ok6 = (
            merge_compare["base_commit_name"] == "http_e2e_base_commit"
            and merge_resolution["portable_local_outcome_package_merge_resolution_result"]["resolution_name"] == "http_e2e_portable_merge_resolution"
        )
        if ok6:
            passed += 1
        else:
            print("FAILED: portable merge compare/resolve scenario", merge_compare, merge_resolution)

        _, merge_commit = post_json(base_url, "/api/commit-portable-local-outcome-package-three-way-merge-resolution", {
            "project_index": merge_resolution["project_index"],
            "merge_resolution_result": merge_resolution["portable_local_outcome_package_merge_resolution_result"],
            "commit_name": "http_e2e_portable_merge_commit",
            "promote_point_name": "http_e2e_portable_merge_release",
            "promote_point_kind": "release",
            "note": "http e2e portable merge commit",
        })
        ok7 = (
            merge_commit["portable_local_outcome_package_merge_commit_result"]["commit_name"] == "http_e2e_portable_merge_commit"
            and merge_commit["portable_local_outcome_package_merge_commit_result"]["summary"]["promoted"] is True
        )
        if ok7:
            passed += 1
        else:
            print("FAILED: portable merge commit scenario", merge_commit)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    print(f"inspector_http_e2e: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
