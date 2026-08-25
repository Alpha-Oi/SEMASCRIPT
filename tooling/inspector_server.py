
from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from inspector_service import (
    analyze_input,
    analyze_graph,
    graph_from_input,
    load_sample_catalog,
    export_session_from_text,
    export_session_from_graph,
    import_session,
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
    commit_snapshot_reconcile_commit_package_resolution_in_project,
    export_local_outcome_set_as_portable_package,
    import_local_outcome_set_package_into_project,
    preview_portable_local_outcome_set_package_import,
    resolve_local_outcome_set_package_import_conflicts_in_project,
    commit_portable_local_outcome_package_resolution_in_project,
    compare_committed_portable_local_outcome_packages,
    compare_or_three_way_merge_committed_portable_local_outcomes,
    resolve_portable_local_outcome_package_three_way_merge_conflicts_in_project,
    commit_portable_local_outcome_package_three_way_merge_resolution_in_project,
)

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR.parent / "inspector"


class InspectorHandler(BaseHTTPRequestHandler):
    def _send_bytes(self, data: bytes, content_type: str = "application/octet-stream", status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        self._send_bytes(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"), "application/json; charset=utf-8", status)

    def _serve_static_file(self, parsed_path: str) -> bool:
        relative_path = unquote(parsed_path).lstrip("/") or "index.html"
        requested_file = (STATIC_DIR / relative_path).resolve()
        try:
            requested_file.relative_to(STATIC_DIR.resolve())
        except ValueError:
            self._send_json({"error": "Not found"}, status=404)
            return True

        if not requested_file.is_file():
            return False

        content_type, _ = mimetypes.guess_type(str(requested_file))
        if content_type is None:
            content_type = "application/octet-stream"
        elif content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
            "image/svg+xml",
        }:
            content_type = f"{content_type}; charset=utf-8"
        self._send_bytes(requested_file.read_bytes(), content_type)
        return True

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/samples":
            self._send_json({"samples": load_sample_catalog(BASE_DIR)})
            return
        if self._serve_static_file(parsed.path):
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw) if raw else {}
        except Exception as exc:
            self._send_json({"error": f"Invalid request: {exc}"}, status=400)
            return

        try:
            if parsed.path == "/api/analyze":
                result = analyze_input(
                    text=payload["text"],
                    profile=payload.get("profile", "core"),
                    decompose=payload.get("decompose", True),
                    initial_state=payload.get("initial_state"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/graph-from-input":
                result = graph_from_input(
                    text=payload["text"],
                    profile=payload.get("profile", "core"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/analyze-graph":
                result = analyze_graph(
                    graph_document=payload["graph_document"],
                    profile=payload.get("profile", "core"),
                    decompose=payload.get("decompose", True),
                    initial_state=payload.get("initial_state"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/export-session-text":
                result = export_session_from_text(
                    text=payload["text"],
                    profile=payload.get("profile", "core"),
                    decompose=payload.get("decompose", True),
                    initial_state=payload.get("initial_state"),
                    session_name=payload.get("session_name"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/export-session-graph":
                result = export_session_from_graph(
                    graph_document=payload["graph_document"],
                    profile=payload.get("profile", "core"),
                    decompose=payload.get("decompose", True),
                    initial_state=payload.get("initial_state"),
                    session_name=payload.get("session_name"),
                    ui_state=payload.get("ui_state"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/import-session":
                result = import_session(payload["session"])
                self._send_json(result)
                return

            if parsed.path == "/api/export-project-index":
                result = export_project_index_from_sessions(
                    sessions=payload.get("sessions", []),
                    project_name=payload.get("project_name", "Untitled SEMASCRIPT Project"),
                    active_session_id=payload.get("active_session_id"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/import-project-index":
                result = import_project_index(payload["project_index"])
                self._send_json(result)
                return

            if parsed.path == "/api/create-project-branch":
                result = create_project_branch(
                    project_index=payload["project_index"],
                    source_session_id=payload["source_session_id"],
                    branch_name=payload["branch_name"],
                )
                self._send_json(result)
                return

            if parsed.path == "/api/rebase-project-branch":
                result = rebase_project_branch_onto_target(
                    project_index=payload["project_index"],
                    source_branch_name=payload["source_branch_name"],
                    target_branch_name=payload["target_branch_name"],
                    activate_head=payload.get("activate_head", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/cherry-pick-project-sessions":
                result = cherry_pick_project_sessions(
                    project_index=payload["project_index"],
                    source_session_ids=payload["source_session_ids"],
                    target_branch_name=payload["target_branch_name"],
                    activate_head=payload.get("activate_head", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/squash-project-sessions":
                result = squash_project_sessions_into_commit(
                    project_index=payload["project_index"],
                    source_session_ids=payload["source_session_ids"],
                    target_branch_name=payload["target_branch_name"],
                    session_id=payload.get("session_id"),
                    session_name=payload.get("session_name"),
                    activate_head=payload.get("activate_head", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/reset-project-branch-head":
                result = reset_project_branch_head(
                    project_index=payload["project_index"],
                    branch_name=payload["branch_name"],
                    target_session_id=payload["target_session_id"],
                    activate_head=payload.get("activate_head", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/create-project-tag-release-point":
                result = create_project_tag_release_point(
                    project_index=payload["project_index"],
                    tag_name=payload["tag_name"],
                    target_session_id=payload["target_session_id"],
                    point_kind=payload.get("point_kind", "tag"),
                    note=payload.get("note"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/create-project-snapshot-export":
                result = create_project_snapshot_export(
                    project_index=payload["project_index"],
                    source_point_name=payload["source_point_name"],
                    snapshot_name=payload.get("snapshot_name"),
                    note=payload.get("note"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/preview-project-snapshot-restore":
                result = preview_project_snapshot_restore(
                    current_project_index=payload["current_project_index"],
                    snapshot_package=payload["snapshot_package"],
                    restored_project_name=payload.get("restored_project_name"),
                    activate_anchor=payload.get("activate_anchor", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/restore-project-from-snapshot-export":
                result = restore_project_from_snapshot_export(
                    snapshot_package=payload["snapshot_package"],
                    restored_project_name=payload.get("restored_project_name"),
                    restore_name=payload.get("restore_name"),
                    activate_anchor=payload.get("activate_anchor", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/partial-import-project-from-snapshot":
                result = partial_import_project_from_snapshot(
                    current_project_index=payload["current_project_index"],
                    snapshot_package=payload["snapshot_package"],
                    import_name=payload.get("import_name"),
                    selected_session_ids=payload.get("selected_session_ids"),
                    selected_tag_point_names=payload.get("selected_tag_point_names"),
                    selected_snapshot_export_names=payload.get("selected_snapshot_export_names"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_imported=payload.get("activate_last_imported", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/preview-snapshot-reconcile-in-project":
                result = preview_snapshot_reconcile_in_project_lineage(
                    current_project_index=payload["current_project_index"],
                    snapshot_package=payload["snapshot_package"],
                    selected_session_ids=payload.get("selected_session_ids"),
                    target_branch_name=payload.get("target_branch_name"),
                    reconcile_name=payload.get("reconcile_name"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/reconcile-snapshot-into-project":
                result = reconcile_snapshot_into_project_lineage(
                    current_project_index=payload["current_project_index"],
                    snapshot_package=payload["snapshot_package"],
                    reconcile_name=payload.get("reconcile_name"),
                    selected_session_ids=payload.get("selected_session_ids"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_reconciled=payload.get("activate_last_reconciled", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/switch-project-session":
                result = switch_project_session(
                    project_index=payload["project_index"],
                    session_id=payload["session_id"],
                )
                self._send_json(result)
                return

            if parsed.path == "/api/compare-project-sessions":
                result = compare_project_sessions(
                    project_index=payload["project_index"],
                    left_session_id=payload["left_session_id"],
                    right_session_id=payload["right_session_id"],
                )
                self._send_json(result)
                return

            if parsed.path == "/api/merge-project-sessions-three-way":
                result = merge_project_sessions_three_way(
                    project_index=payload["project_index"],
                    base_session_id=payload["base_session_id"],
                    left_session_id=payload["left_session_id"],
                    right_session_id=payload["right_session_id"],
                )
                self._send_json(result)
                return

            if parsed.path == "/api/resolve-project-merge-conflicts":
                result = resolve_project_merge_conflicts(
                    project_index=payload["project_index"],
                    base_session_id=payload["base_session_id"],
                    left_session_id=payload["left_session_id"],
                    right_session_id=payload["right_session_id"],
                    decisions=payload.get("decisions", {}),
                )
                self._send_json(result)
                return


            if parsed.path == "/api/commit-project-merge-result":
                result = commit_project_merge_result(
                    project_index=payload["project_index"],
                    merge_or_resolution_result=payload["merge_or_resolution_result"],
                    session_id=payload.get("session_id"),
                    session_name=payload.get("session_name"),
                    activate=payload.get("activate", True),
                    tags=payload.get("tags"),
                    branch_name=payload.get("branch_name"),
                )
                self._send_json(result)
                return


            if parsed.path == "/api/resolve-snapshot-reconcile-conflicts":
                result = resolve_snapshot_reconcile_conflicts_in_project_lineage(
                    current_project_index=payload["current_project_index"],
                    snapshot_package=payload["snapshot_package"],
                    decisions=payload.get("decisions", {}),
                    resolution_name=payload.get("resolution_name"),
                    selected_session_ids=payload.get("selected_session_ids"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_resolved=payload.get("activate_last_resolved", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/commit-snapshot-reconcile-resolution":
                result = commit_snapshot_reconcile_resolution_in_project_lineage(
                    project_index=payload["project_index"],
                    snapshot_reconcile_resolution_result=payload["snapshot_reconcile_resolution_result"],
                    commit_name=payload.get("commit_name"),
                    promote_point_name=payload.get("promote_point_name"),
                    promote_point_kind=payload.get("promote_point_kind", "release"),
                    note=payload.get("note"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/compare-snapshot-reconcile-commits":
                result = compare_snapshot_reconcile_commit_outcomes(
                    project_index=payload["project_index"],
                    left_commit_name=payload["left_commit_name"],
                    right_commit_name=payload["right_commit_name"],
                )
                self._send_json(result)
                return

            if parsed.path == "/api/export-snapshot-reconcile-commit-package":
                result = export_snapshot_reconcile_commit_as_package(
                    project_index=payload["project_index"],
                    commit_name=payload["commit_name"],
                    package_name=payload.get("package_name"),
                    note=payload.get("note"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/import-snapshot-reconcile-commit-package":
                result = import_snapshot_reconcile_commit_package_into_project(
                    current_project_index=payload["current_project_index"],
                    package=payload["package"],
                    import_name=payload.get("import_name"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_imported=payload.get("activate_last_imported", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/preview-snapshot-reconcile-commit-package-import":
                result = preview_snapshot_reconcile_commit_package_import_into_project(
                    current_project_index=payload["current_project_index"],
                    package=payload["package"],
                    import_name=payload.get("import_name"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_imported=payload.get("activate_last_imported", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/resolve-snapshot-reconcile-commit-package-import":
                result = resolve_snapshot_reconcile_commit_package_import_conflicts_in_project(
                    current_project_index=payload["current_project_index"],
                    package=payload["package"],
                    decisions=payload.get("decisions", {}),
                    resolution_name=payload.get("resolution_name"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_imported=payload.get("activate_last_imported", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/commit-snapshot-reconcile-commit-package-resolution":
                result = commit_snapshot_reconcile_commit_package_resolution_in_project(
                    project_index=payload["project_index"],
                    snapshot_reconcile_commit_package_resolution_result=payload["snapshot_reconcile_commit_package_resolution_result"],
                    commit_name=payload.get("commit_name"),
                    promote_point_name=payload.get("promote_point_name"),
                    promote_point_kind=payload.get("promote_point_kind", "release"),
                    note=payload.get("note"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/export-local-outcome-set-package":
                result = export_local_outcome_set_as_portable_package(
                    project_index=payload["project_index"],
                    commit_name=payload["commit_name"],
                    package_name=payload.get("package_name"),
                    note=payload.get("note"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/import-local-outcome-set-package":
                result = import_local_outcome_set_package_into_project(
                    current_project_index=payload["current_project_index"],
                    package=payload["package"],
                    import_name=payload.get("import_name"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_imported=payload.get("activate_last_imported", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/preview-local-outcome-set-package-import":
                result = preview_portable_local_outcome_set_package_import(
                    current_project_index=payload["current_project_index"],
                    package_data=payload["package_data"],
                    import_name=payload.get("import_name"),
                    target_branch_name=payload.get("target_branch_name"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/resolve-local-outcome-set-package-import-conflicts":
                result = resolve_local_outcome_set_package_import_conflicts_in_project(
                    current_project_index=payload["current_project_index"],
                    package_data=payload["package_data"],
                    decisions=payload.get("decisions", {}),
                    resolution_name=payload.get("resolution_name"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_imported=payload.get("activate_last_imported", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/commit-local-outcome-set-package-resolution":
                result = commit_portable_local_outcome_package_resolution_in_project(
                    project_index=payload["project_index"],
                    local_outcome_set_package_resolution_result=payload["local_outcome_set_package_resolution_result"],
                    commit_name=payload.get("commit_name"),
                    promote_point_name=payload.get("promote_point_name"),
                    promote_point_kind=payload.get("promote_point_kind", "release"),
                    note=payload.get("note"),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/compare-committed-portable-local-outcome-packages":
                result = compare_committed_portable_local_outcome_packages(
                    project_index=payload["project_index"],
                    left_commit_name=payload["left_commit_name"],
                    right_commit_name=payload["right_commit_name"],
                )
                self._send_json(result)
                return

            if parsed.path == "/api/compare-or-three-way-merge-committed-portable-local-outcomes":
                result = compare_or_three_way_merge_committed_portable_local_outcomes(
                    project_index=payload["project_index"],
                    base_commit_name=payload["base_commit_name"],
                    left_commit_name=payload["left_commit_name"],
                    right_commit_name=payload["right_commit_name"],
                )
                self._send_json(result)
                return

            if parsed.path == "/api/resolve-portable-local-outcome-package-three-way-merge-conflicts":
                result = resolve_portable_local_outcome_package_three_way_merge_conflicts_in_project(
                    project_index=payload["project_index"],
                    merge_result=payload["merge_result"],
                    decisions=payload.get("decisions", {}),
                    resolution_name=payload.get("resolution_name"),
                    target_branch_name=payload.get("target_branch_name"),
                    activate_last_resolved=payload.get("activate_last_resolved", True),
                )
                self._send_json(result)
                return

            if parsed.path == "/api/commit-portable-local-outcome-package-three-way-merge-resolution":
                result = commit_portable_local_outcome_package_three_way_merge_resolution_in_project(
                    project_index=payload["project_index"],
                    merge_resolution_result=payload["merge_resolution_result"],
                    commit_name=payload.get("commit_name"),
                    promote_point_name=payload.get("promote_point_name"),
                    promote_point_kind=payload.get("promote_point_kind", "release"),
                    note=payload.get("note"),
                )
                self._send_json(result)
                return

            self._send_json({"error": "Not found"}, status=404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)

    def log_message(self, format: str, *args) -> None:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="SEMASCRIPT editor / visual inspector server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), InspectorHandler)
    print(f"SEMASCRIPT Inspector running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
