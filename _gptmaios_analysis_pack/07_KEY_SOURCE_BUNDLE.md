# Key Source Bundle

Selected source files for architecture analysis. Selection is capped at 40 files and prioritizes entry points, parser/runtime/state/project modules, UI/API workflow modules, and verification entrypoints.

## Selection Summary

- Included files: 40
- Full-file limit: files larger than 80 KB are truncated to first 250 and last 100 lines.

## FILE: tooling/inspector_server.py

Size: 27126 bytes

```file

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
```


## FILE: tooling/inspector_service.py

Size: 31328 bytes

```file

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List

from human_normalizer import normalize
from semascript_ast import text_to_ast_document, ast_to_slinear, ast_to_node
from semascript_validator import validate_core_node, validate_exec_node
from pattern_decomposer import decompose_ast_document
from exec_runtime import execute_text
from state_model import execute_text_with_state
from svg_renderer import render_svg_from_ast_document
from graph_model import ast_document_to_graph_document, graph_document_to_ast_document
from session_model import create_session_from_text, create_session_from_graph, session_to_inspector_payload
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
    compare_local_outcome_sets_in_project,
    compare_portable_local_outcome_package_commits_in_project,
    compare_baseline_or_three_way_portable_local_outcomes_in_project,
    create_portable_local_outcome_package_three_way_merge_resolution_in_project,
    create_portable_local_outcome_package_three_way_merge_commit_in_project,
)
from session_diff import compare_sessions
from session_merge import merge_sessions_three_way
from session_conflict_resolution import resolve_merge_result_conflicts
from project_rebase import replay_branch_onto_target_lineage
from project_cherrypick import cherry_pick_sessions_onto_branch
from project_squash import squash_sessions_into_lineage_commit
from project_reset import reset_branch_head_to_historical_session


def _mode_from_ast(doc: dict, profile: str) -> str:
    if doc["ast"]["class_name"] == "EXEC" or profile == "exec":
        return "exec"
    return "core"


def _validation_report(doc: dict, profile: str) -> dict:
    node = ast_to_node(doc["ast"])
    mode = _mode_from_ast(doc, profile)
    result = validate_exec_node(node) if mode == "exec" else validate_core_node(node)
    return {
        "mode": mode,
        "valid": result.valid,
        "errors": [{"code": code, "message": message} for code, message in result.errors],
    }


def analyze_ast_document(
    ast_doc: dict,
    profile: str,
    decompose: bool = True,
    initial_state: Optional[dict] = None,
) -> dict:
    source_text = ast_doc.get("source_text") or ast_to_slinear(ast_doc["ast"])
    validation = _validation_report(ast_doc, profile)
    decomposed_doc = decompose_ast_document(ast_doc) if decompose else None
    decomposed_slinear = ast_to_slinear(decomposed_doc["ast"]) if decomposed_doc else None

    runtime_report = execute_text(source_text, profile=profile)
    state_report = execute_text_with_state(source_text, profile=profile, initial_state=initial_state)

    svg_raw = render_svg_from_ast_document(ast_doc)
    svg_decomposed = render_svg_from_ast_document(decomposed_doc) if decomposed_doc else None
    graph_doc = ast_document_to_graph_document(ast_doc)
    graph_decomposed_doc = ast_document_to_graph_document(decomposed_doc) if decomposed_doc else None

    result = {
        "source_text": source_text,
        "profile": profile,
        "normalized_text": ast_doc.get("metadata", {}).get("normalized_text") or source_text,
        "ast_document": ast_doc,
        "graph_document": graph_doc,
        "slinear": ast_to_slinear(ast_doc["ast"]),
        "validation": validation,
        "runtime_report": runtime_report,
        "state_report": state_report,
        "svg_raw": svg_raw,
        "svg_decomposed": svg_decomposed,
    }
    if decomposed_doc:
        result["decomposed_ast_document"] = decomposed_doc
        result["decomposed_graph_document"] = graph_decomposed_doc
        result["decomposed_slinear"] = decomposed_slinear
    return result


def analyze_input(
    text: str,
    profile: str = "core",
    decompose: bool = True,
    initial_state: Optional[dict] = None,
) -> dict:
    source_text = text.strip()
    if not source_text:
        raise ValueError("Empty input")

    normalized_text = normalize(source_text) if profile == "human" else source_text
    source_profile = "normalized" if profile == "human" else profile

    ast_doc = text_to_ast_document(
        normalized_text,
        source_profile=source_profile,
        source_text=source_text,
    )
    if profile == "human":
        ast_doc["metadata"]["normalized_text"] = normalized_text

    return analyze_ast_document(ast_doc, profile=profile, decompose=decompose, initial_state=initial_state)


def graph_from_input(text: str, profile: str = "core") -> dict:
    result = analyze_input(text=text, profile=profile, decompose=False, initial_state=None)
    return {
        "graph_document": result["graph_document"],
        "slinear": result["slinear"],
        "normalized_text": result["normalized_text"],
        "ast_document": result["ast_document"],
    }


def analyze_graph(
    graph_document: dict,
    profile: str = "core",
    decompose: bool = True,
    initial_state: Optional[dict] = None,
) -> dict:
    ast_doc = graph_document_to_ast_document(graph_document)
    ast_doc["source_profile"] = profile
    if not ast_doc.get("source_text"):
        ast_doc["source_text"] = ast_to_slinear(ast_doc["ast"])
    return analyze_ast_document(ast_doc, profile=profile, decompose=decompose, initial_state=initial_state)


def export_session_from_text(
    text: str,
    profile: str = "core",
    decompose: bool = True,
    initial_state: Optional[dict] = None,
    session_name: Optional[str] = None,
) -> dict:
    return create_session_from_text(
        text=text,
        profile=profile,
        decompose=decompose,
        initial_state=initial_state,
        session_name=session_name,
    )


def export_session_from_graph(
    graph_document: dict,
    profile: str = "core",
    decompose: bool = True,
    initial_state: Optional[dict] = None,
    session_name: Optional[str] = None,
    ui_state: Optional[dict] = None,
) -> dict:
    return create_session_from_graph(
        graph_document=graph_document,
        profile=profile,
        decompose=decompose,
        initial_state=initial_state,
        session_name=session_name,
        ui_state=ui_state,
    )


def import_session(session: dict) -> dict:
    return session_to_inspector_payload(session)


def export_project_index_from_sessions(
    sessions: list[dict],
    project_name: str = "Untitled SEMASCRIPT Project",
    active_session_id: Optional[str] = None,
) -> dict:
    project = create_workspace(project_name=project_name)
    for item in sessions:
        entry_metadata = item.get("entry_metadata")
        branch_name = item.get("branch_name")
        if branch_name is None and isinstance(entry_metadata, dict):
            branch_name = entry_metadata.get("branching", {}).get("branch_name")
        project = add_session_to_workspace(
            project_index=project,
            session=item["session"],
            session_id=item.get("session_id"),
            file_name=item.get("file_name"),
            tags=item.get("tags"),
            entry_metadata=entry_metadata,
            branch_name=branch_name,
        )
    if active_session_id:
        project = set_active_session(project, active_session_id)
    return project


def import_project_index(project_index: dict) -> dict:
    return workspace_to_inspector_payload(project_index)


def switch_project_session(project_index: dict, session_id: str) -> dict:
    updated = set_active_session(project_index, session_id)
    return workspace_to_inspector_payload(updated)

def compare_project_sessions(project_index: dict, left_session_id: str, right_session_id: str) -> dict:
    return compare_sessions(project_index, left_session_id, right_session_id)

def merge_project_sessions_three_way(project_index: dict, base_session_id: str, left_session_id: str, right_session_id: str) -> dict:
    return merge_sessions_three_way(project_index, base_session_id, left_session_id, right_session_id)


def resolve_project_merge_conflicts(project_index: dict, base_session_id: str, left_session_id: str, right_session_id: str, decisions: dict[str, dict]) -> dict:
    merge_result = merge_sessions_three_way(project_index, base_session_id, left_session_id, right_session_id)
    return resolve_merge_result_conflicts(merge_result, decisions)



def commit_project_merge_result(
    project_index: dict,
    merge_or_resolution_result: dict,
    session_id: Optional[str] = None,
    session_name: Optional[str] = None,
    activate: bool = True,
    tags: Optional[list[str]] = None,
    branch_name: Optional[str] = None,
) -> dict:
    updated = commit_merged_session_to_workspace(
        project_index=project_index,
        merge_or_resolution_result=merge_or_resolution_result,
        session_id=session_id,
        session_name=session_name,
        activate=activate,
        tags=tags,
        branch_name=branch_name,
    )
    return workspace_to_inspector_payload(updated)



def create_project_branch(project_index: dict, source_session_id: str, branch_name: str) -> dict:
    updated = create_branch_from_session(project_index, source_session_id, branch_name)
    return workspace_to_inspector_payload(updated)



def rebase_project_branch_onto_target(
    project_index: dict,
    source_branch_name: str,
    target_branch_name: str,
    activate_head: bool = True,
) -> dict:
    updated, rebase_result = replay_branch_onto_target_lineage(
        project_index=project_index,
        source_branch_name=source_branch_name,
        target_branch_name=target_branch_name,
        activate_head=activate_head,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["branch_rebase_result"] = rebase_result
    return payload



def cherry_pick_project_sessions(
    project_index: dict,
    source_session_ids: list[str],
    target_branch_name: str,
    activate_head: bool = True,
) -> dict:
    updated, cherry_pick_result = cherry_pick_sessions_onto_branch(
        project_index=project_index,
        source_session_ids=source_session_ids,
        target_branch_name=target_branch_name,
        activate_head=activate_head,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["branch_cherry_pick_result"] = cherry_pick_result
    return payload



def squash_project_sessions_into_commit(
    project_index: dict,
    source_session_ids: list[str],
    target_branch_name: str,
    session_id: Optional[str] = None,
    session_name: Optional[str] = None,
    activate_head: bool = True,
) -> dict:
    updated, squash_result = squash_sessions_into_lineage_commit(
        project_index=project_index,
        source_session_ids=source_session_ids,
        target_branch_name=target_branch_name,
        session_id=session_id,
        session_name=session_name,
        activate_head=activate_head,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["branch_squash_result"] = squash_result
    return payload


def load_sample_catalog(base_dir: str | Path) -> List[dict]:
    base_dir = Path(base_dir)
    samples: List[dict] = []

    manifests = [
        base_dir / "corpus" / "runtime_state_corpus_manifest.json",
        base_dir / "corpus" / "hardening_corpus_manifest_v0_2.json",
    ]

    seen = set()
    for manifest_path in manifests:
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest.get("entries", []):
            sid = entry["id"]
            if sid in seen:
                continue
            seen.add(sid)
            samples.append({
                "id": sid,
                "profile": entry["profile"],
                "text": entry["text"],
                "tags": entry.get("tags", []),
                "initial_state": entry.get("initial_state"),
            })

    samples.sort(key=lambda x: x["id"])
    return samples


def reset_project_branch_head(
    project_index: dict,
    branch_name: str,
    target_session_id: str,
    activate_head: bool = True,
) -> dict:
    updated, reset_result = reset_branch_head_to_historical_session(
        project_index=project_index,
        branch_name=branch_name,
        target_session_id=target_session_id,
        activate_head=activate_head,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["branch_reset_result"] = reset_result
    return payload




def create_project_tag_release_point(
    project_index: dict,
    tag_name: str,
    target_session_id: str,
    point_kind: str = "tag",
    note: Optional[str] = None,
) -> dict:
    updated, tag_result = create_tag_release_in_project(
        project_index=project_index,
        tag_name=tag_name,
        target_session_id=target_session_id,
        point_kind=point_kind,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["tag_release_result"] = tag_result
    return payload



def create_project_snapshot_export(
    project_index: dict,
    source_point_name: str,
    snapshot_name: Optional[str] = None,
    note: Optional[str] = None,
) -> dict:
    updated, snapshot_result, snapshot_package = create_snapshot_export_in_project(
        project_index=project_index,
        source_point_name=source_point_name,
        snapshot_name=snapshot_name,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_export_result"] = snapshot_result
    payload["snapshot_export_package"] = snapshot_package
    return payload


def restore_project_from_snapshot_export(
    snapshot_package: dict,
    restored_project_name: Optional[str] = None,
    restore_name: Optional[str] = None,
    activate_anchor: bool = True,
) -> dict:
    updated, snapshot_restore_result = create_snapshot_restore_in_project(
        snapshot_package=snapshot_package,
        restored_project_name=restored_project_name,
        restore_name=restore_name,
        activate_anchor=activate_anchor,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_restore_result"] = snapshot_restore_result
    return payload


def preview_project_snapshot_restore(
    current_project_index: dict,
    snapshot_package: dict,
    restored_project_name: Optional[str] = None,
    activate_anchor: bool = True,
) -> dict:
    return create_snapshot_restore_preview(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        restored_project_name=restored_project_name,
        activate_anchor=activate_anchor,
    )


def partial_import_project_from_snapshot(
    current_project_index: dict,
    snapshot_package: dict,
    import_name: Optional[str] = None,
    selected_session_ids: Optional[list[str]] = None,
    selected_tag_point_names: Optional[list[str]] = None,
    selected_snapshot_export_names: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> dict:
    updated, partial_import_result = create_partial_snapshot_import_in_project(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        import_name=import_name,
        selected_session_ids=selected_session_ids,
        selected_tag_point_names=selected_tag_point_names,
        selected_snapshot_export_names=selected_snapshot_export_names,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["partial_snapshot_import_result"] = partial_import_result
    return payload


def reconcile_snapshot_into_project_lineage(
    current_project_index: dict,
    snapshot_package: dict,
    reconcile_name: Optional[str] = None,
    selected_session_ids: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    activate_last_reconciled: bool = True,
) -> dict:
    updated, snapshot_reconcile_result = create_snapshot_reconcile_in_project(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        reconcile_name=reconcile_name,
        selected_session_ids=selected_session_ids,
        target_branch_name=target_branch_name,
        activate_last_reconciled=activate_last_reconciled,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_reconcile_result"] = snapshot_reconcile_result
    return payload


def preview_snapshot_reconcile_in_project_lineage(
    current_project_index: dict,
    snapshot_package: dict,
    selected_session_ids: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    reconcile_name: Optional[str] = None,
) -> dict:
    return create_snapshot_reconcile_preview(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        selected_session_ids=selected_session_ids,
        target_branch_name=target_branch_name,
        reconcile_name=reconcile_name,
    )


def resolve_snapshot_reconcile_conflicts_in_project_lineage(
    current_project_index: dict,
    snapshot_package: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: Optional[str] = None,
    selected_session_ids: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    activate_last_resolved: bool = True,
) -> dict:
    updated, snapshot_reconcile_resolution_result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        decisions=decisions,
        resolution_name=resolution_name,
        selected_session_ids=selected_session_ids,
        target_branch_name=target_branch_name,
        activate_last_resolved=activate_last_resolved,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_reconcile_resolution_result"] = snapshot_reconcile_resolution_result
    return payload


def commit_snapshot_reconcile_resolution_in_project_lineage(
    project_index: dict,
    snapshot_reconcile_resolution_result: dict,
    commit_name: Optional[str] = None,
    promote_point_name: Optional[str] = None,
    promote_point_kind: str = "release",
    note: Optional[str] = None,
) -> dict:
    updated, snapshot_reconcile_commit_result = create_snapshot_reconcile_commit_in_project(
        project_index=project_index,
        snapshot_reconcile_resolution_result=snapshot_reconcile_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_reconcile_commit_result"] = snapshot_reconcile_commit_result
    return payload


def compare_snapshot_reconcile_commit_outcomes(
    project_index: dict,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    return compare_snapshot_reconcile_commit_sets(
        project_index=project_index,
        left_commit_name=left_commit_name,
        right_commit_name=right_commit_name,
    )


def export_snapshot_reconcile_commit_as_package(
    project_index: dict,
    commit_name: str,
    package_name: Optional[str] = None,
    note: Optional[str] = None,
) -> dict:
    updated, snapshot_reconcile_commit_package_result, snapshot_reconcile_commit_package = create_snapshot_reconcile_commit_package_export_in_project(
        project_index=project_index,
        commit_name=commit_name,
        package_name=package_name,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_reconcile_commit_package_result"] = snapshot_reconcile_commit_package_result
    payload["snapshot_reconcile_commit_package"] = snapshot_reconcile_commit_package
    return payload


def import_snapshot_reconcile_commit_package_into_project(
    current_project_index: dict,
    package: dict,
    import_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> dict:
    updated, snapshot_reconcile_commit_package_import_result = create_snapshot_reconcile_commit_package_import_in_project(
        current_project_index=current_project_index,
        package=package,
        import_name=import_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_reconcile_commit_package_import_result"] = snapshot_reconcile_commit_package_import_result
    return payload


def preview_snapshot_reconcile_commit_package_import_into_project(
    current_project_index: dict,
    package: dict,
    import_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> dict:
    return create_snapshot_reconcile_commit_package_import_preview_in_project(
        current_project_index=current_project_index,
        package=package,
        import_name=import_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )


def resolve_snapshot_reconcile_commit_package_import_conflicts_in_project(
    current_project_index: dict,
    package: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> dict:
    updated, snapshot_reconcile_commit_package_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
        current_project_index=current_project_index,
        package=package,
        decisions=decisions,
        resolution_name=resolution_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_reconcile_commit_package_resolution_result"] = snapshot_reconcile_commit_package_resolution_result
    return payload


def commit_snapshot_reconcile_commit_package_resolution_in_project(
    project_index: dict,
    snapshot_reconcile_commit_package_resolution_result: dict,
    commit_name: Optional[str] = None,
    promote_point_name: Optional[str] = None,
    promote_point_kind: str = "release",
    note: Optional[str] = None,
) -> dict:
    updated, snapshot_reconcile_commit_package_commit_result = create_snapshot_reconcile_commit_package_import_commit_in_project(
        project_index=project_index,
        snapshot_reconcile_commit_package_resolution_result=snapshot_reconcile_commit_package_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["snapshot_reconcile_commit_package_commit_result"] = snapshot_reconcile_commit_package_commit_result
    return payload


def compare_local_imported_promoted_outcomes(
    project_index: dict,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    return compare_local_outcome_sets_in_project(
        project_index=project_index,
        left_commit_name=left_commit_name,
        right_commit_name=right_commit_name,
    )


def commit_imported_resolution_into_local_outcome_set_in_project(
    project_index: dict,
    package_resolution_result: dict,
    commit_name: str | None = None,
    promote_point_name: str | None = None,
    promote_point_kind: str = "release",
    note: str | None = None,
) -> dict:
    updated, local_outcome_commit_result = create_snapshot_reconcile_commit_package_import_commit_in_project(
        project_index=project_index,
        snapshot_reconcile_commit_package_resolution_result=package_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["local_outcome_commit_result"] = local_outcome_commit_result
    return payload


def export_local_outcome_set_as_portable_package(
    project_index: dict,
    commit_name: str,
    package_name: Optional[str] = None,
    note: Optional[str] = None,
) -> dict:
    updated, local_outcome_set_package_result, local_outcome_set_package = create_local_outcome_set_package_export_in_project(
        project_index=project_index,
        commit_name=commit_name,
        package_name=package_name,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["local_outcome_set_package_result"] = local_outcome_set_package_result
    payload["local_outcome_set_package"] = local_outcome_set_package
    return payload


def import_local_outcome_set_package_into_project(
    current_project_index: dict,
    package: dict,
    import_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> dict:
    updated, local_outcome_set_package_import_result = create_local_outcome_set_package_import_in_project(
        current_project_index=current_project_index,
        package=package,
        import_name=import_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["local_outcome_set_package_import_result"] = local_outcome_set_package_import_result
    return payload


def preview_portable_local_outcome_set_package_import(
    current_project_index: dict,
    package_data: dict,
    import_name: str | None = None,
    target_branch_name: str | None = None,
) -> dict:
    return preview_local_outcome_set_package_before_import_in_project(
        current_project_index=current_project_index,
        package_data=package_data,
        import_name=import_name,
        target_branch_name=target_branch_name,
    )


def resolve_local_outcome_set_package_import_conflicts_in_project(
    current_project_index: dict,
    package_data: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_imported: bool = True,
) -> dict:
    updated, local_outcome_set_package_resolution_result = create_local_outcome_set_package_import_resolution_in_project(
        current_project_index=current_project_index,
        package_data=package_data,
        decisions=decisions,
        resolution_name=resolution_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["local_outcome_set_package_resolution_result"] = local_outcome_set_package_resolution_result
    return payload


def commit_portable_local_outcome_package_resolution_in_project(
    project_index: dict,
    local_outcome_set_package_resolution_result: dict,
    commit_name: str | None = None,
    promote_point_name: str | None = None,
    promote_point_kind: str = "release",
    note: str | None = None,
) -> dict:
    updated, local_outcome_set_package_commit_result = create_local_outcome_set_package_import_commit_in_project(
        project_index=project_index,
        local_outcome_set_package_resolution_result=local_outcome_set_package_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["local_outcome_set_package_commit_result"] = local_outcome_set_package_commit_result
    return payload


def compare_committed_portable_local_outcome_packages(
    project_index: dict,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    return compare_portable_local_outcome_package_commits_in_project(
        project_index=project_index,
        left_commit_name=left_commit_name,
        right_commit_name=right_commit_name,
    )


def compare_or_three_way_merge_committed_portable_local_outcomes(
    project_index: dict,
    base_commit_name: str,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    return compare_baseline_or_three_way_portable_local_outcomes_in_project(
        project_index=project_index,
        base_commit_name=base_commit_name,
        left_commit_name=left_commit_name,
        right_commit_name=right_commit_name,
    )


def resolve_portable_local_outcome_package_three_way_merge_conflicts_in_project(
    project_index: dict,
    merge_result: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_resolved: bool = True,
) -> dict:
    updated, merge_resolution_result = create_portable_local_outcome_package_three_way_merge_resolution_in_project(
        project_index=project_index,
        merge_result=merge_result,
        decisions=decisions,
        resolution_name=resolution_name,
        target_branch_name=target_branch_name,
        activate_last_resolved=activate_last_resolved,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["portable_local_outcome_package_merge_resolution_result"] = merge_resolution_result
    return payload


def commit_portable_local_outcome_package_three_way_merge_resolution_in_project(
    project_index: dict,
    merge_resolution_result: dict,
    commit_name: str | None = None,
    promote_point_name: str | None = None,
    promote_point_kind: str = "release",
    note: str | None = None,
) -> dict:
    updated, merge_commit_result = create_portable_local_outcome_package_three_way_merge_commit_in_project(
        project_index=project_index,
        merge_resolution_result=merge_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    payload = workspace_to_inspector_payload(updated)
    payload["portable_local_outcome_package_merge_commit_result"] = merge_commit_result
    return payload
```


## FILE: tooling/semascript_parser.py

Size: 5821 bytes

```file

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


class ParseError(Exception):
    """Raised when a SEMASCRIPT construction cannot be parsed."""


@dataclass
class Node:
    class_name: str
    root: str
    modifiers: List[str] = field(default_factory=list)
    roles: Dict[str, "Value"] = field(default_factory=dict)


Value = Union[Node, List["Value"], str]


class Parser:
    def __init__(self, text: str):
        self.text = text
        self.i = 0
        self.n = len(text)

    def parse(self) -> Node:
        self._skip_ws()
        node = self._parse_node()
        self._skip_ws()
        if self.i != self.n:
            raise ParseError(f"Unexpected trailing content at position {self.i}")
        return node

    def _parse_node(self) -> Node:
        self._skip_ws()
        self._expect("[")
        self._skip_ws()

        header = self._parse_identifier()
        if ":" not in header:
            raise ParseError(f"Header must contain CLASS:ROOT, got {header!r}")

        class_name, root = header.split(":", 1)
        if not class_name or not root:
            raise ParseError(f"Invalid CLASS:ROOT header: {header!r}")

        modifiers: List[str] = []
        roles: Dict[str, Value] = {}

        self._skip_ws()
        if self._peek() == "{":
            modifiers = self._parse_modifiers()
            self._skip_ws()

        if self._peek() == "<":
            roles = self._parse_roles()
            self._skip_ws()

        self._expect("]")
        return Node(class_name=class_name, root=root, modifiers=modifiers, roles=roles)

    def _parse_modifiers(self) -> List[str]:
        self._expect("{")
        mods: List[str] = []
        token = []
        while True:
            ch = self._peek()
            if ch is None:
                raise ParseError("Unterminated modifier block")
            if ch == "}":
                if token:
                    mods.append("".join(token).strip())
                self.i += 1
                break
            if ch in ", " or ch.isspace():
                if token:
                    mods.append("".join(token).strip())
                    token = []
                self.i += 1
                continue
            token.append(ch)
            self.i += 1
        return [m for m in mods if m]

    def _parse_roles(self) -> Dict[str, Value]:
        self._expect("<")
        roles: Dict[str, Value] = {}
        while True:
            self._skip_ws()
            if self._peek() == ">":
                self.i += 1
                break

            role = self._parse_identifier()
            self._skip_ws()
            self._expect("=")
            self._skip_ws()
            value = self._parse_value()
            roles[role] = value
            self._skip_ws()

            ch = self._peek()
            if ch == ";":
                self.i += 1
                continue
            if ch == ">":
                self.i += 1
                break
            raise ParseError(f"Expected ';' or '>' after role assignment at position {self.i}")
        return roles

    def _parse_value(self) -> Value:
        self._skip_ws()
        if self._peek() == "[":
            if self._looks_like_list():
                return self._parse_list()
            return self._parse_node()
        return self._parse_identifier()

    def _looks_like_list(self) -> bool:
        # Current position points to '['
        j = self.i + 1
        while j < self.n and self.text[j].isspace():
            j += 1
        if j >= self.n:
            return False
        # Empty list or list of nested values starts as a list
        return self.text[j] in {"[", "]"}

    def _parse_list(self) -> List[Value]:
            self._expect("[")
            values: List[Value] = []
            expect_value = True

            while True:
                self._skip_ws()
                ch = self._peek()
                if ch is None:
                    raise ParseError("Unterminated list")

                if ch == "]":
                    if expect_value and values:
                        raise ParseError("Trailing separator in list")
                    self.i += 1
                    break

                if not expect_value:
                    raise ParseError(f"Expected list separator at position {self.i}")

                value = self._parse_value()
                values.append(value)
                expect_value = False
                self._skip_ws()

                ch = self._peek()
                if ch in {";", ","}:
                    self.i += 1
                    expect_value = True
                    continue
                if ch == "]":
                    self.i += 1
                    break
                raise ParseError(f"Expected ';', ',' or ']' after list item at position {self.i}")
            return values

    def _parse_identifier(self) -> str:
        self._skip_ws()
        start = self.i
        allowed_stop = set("[]{}<>;=,\n\r\t ")
        while self.i < self.n and self.text[self.i] not in allowed_stop:
            self.i += 1
        if self.i == start:
            raise ParseError(f"Expected identifier at position {self.i}")
        return self.text[start:self.i]

    def _skip_ws(self) -> None:
        while self.i < self.n and self.text[self.i].isspace():
            self.i += 1

    def _peek(self) -> Optional[str]:
        if self.i >= self.n:
            return None
        return self.text[self.i]

    def _expect(self, char: str) -> None:
        if self._peek() != char:
            found = self._peek()
            raise ParseError(f"Expected {char!r} at position {self.i}, found {found!r}")
        self.i += 1


def parse(text: str) -> Node:
    return Parser(text).parse()
```


## FILE: tooling/semascript_ast.py

Size: 3985 bytes

```file

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union, Optional

from semascript_parser import Node, parse


ASTValue = Dict[str, Any]


def _value_to_ast(value: Any) -> ASTValue:
    if isinstance(value, Node):
        return node_to_ast(value)
    if isinstance(value, list):
        return {
            "kind": "list",
            "items": [_value_to_ast(v) for v in value],
        }
    return {
        "kind": "raw_token",
        "value": str(value),
    }


def node_to_ast(node: Node, source_profile: Optional[str] = None) -> Dict[str, Any]:
    ast_node: Dict[str, Any] = {
        "kind": "node",
        "class_name": node.class_name,
        "root": node.root,
        "modifiers": list(node.modifiers),
        "roles": [
            {
                "name": role,
                "value": _value_to_ast(value),
            }
            for role, value in node.roles.items()
        ],
    }
    if source_profile:
        ast_node["source_profile"] = source_profile
    return ast_node


def text_to_ast_document(text: str, source_profile: str = "core", source_text: Optional[str] = None) -> Dict[str, Any]:
    node = parse(text)
    return {
        "schema_version": "SEMASCRIPT_AST_SCHEMA_v0.1",
        "source_profile": source_profile,
        "source_text": source_text if source_text is not None else text,
        "ast": node_to_ast(node, source_profile=source_profile),
        "validation_annotations": [],
        "metadata": {},
    }


def _ast_value_to_runtime(value: Dict[str, Any]) -> Any:
    kind = value["kind"]
    if kind == "node":
        return ast_to_node(value)
    if kind == "list":
        return [_ast_value_to_runtime(v) for v in value["items"]]
    if kind == "typed_literal":
        from semascript_parser import Node as ParserNode
        return ParserNode(class_name=value["class_name"], root=value["root"], modifiers=[], roles={})
    if kind == "raw_token":
        return value["value"]
    raise ValueError(f"Unsupported AST value kind: {kind}")


def ast_to_node(ast_node: Dict[str, Any]) -> Node:
    if ast_node.get("kind") != "node":
        raise ValueError("ast_to_node expects a node dict")
    roles = {}
    for role in ast_node.get("roles", []):
        roles[role["name"]] = _ast_value_to_runtime(role["value"])
    return Node(
        class_name=ast_node["class_name"],
        root=ast_node["root"],
        modifiers=list(ast_node.get("modifiers", [])),
        roles=roles,
    )


def _ast_value_to_slinear(value: Dict[str, Any]) -> str:
    kind = value["kind"]
    if kind == "node":
        return ast_to_slinear(value)
    if kind == "list":
        return "[" + "; ".join(_ast_value_to_slinear(v) for v in value["items"]) + "]"
    if kind == "typed_literal":
        if "value" in value and value["value"] is not None:
            return f"[{value['class_name']}:{value['root']}={value['value']}]"
        return f"[{value['class_name']}:{value['root']}]"
    if kind == "raw_token":
        return value["value"]
    raise ValueError(f"Unsupported AST value kind: {kind}")


def ast_to_slinear(ast_node: Dict[str, Any]) -> str:
    if ast_node.get("kind") != "node":
        raise ValueError("ast_to_slinear expects a node dict")
    header = f"[{ast_node['class_name']}:{ast_node['root']}"
    mods = ast_node.get("modifiers", [])
    if mods:
        header += " {" + " ".join(mods) + "}"
    roles = ast_node.get("roles", [])
    if roles:
        role_str = "; ".join(f"{role['name']}={_ast_value_to_slinear(role['value'])}" for role in roles)
        header += f" <{role_str}>"
    header += "]"
    return header


def load_ast_document(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_ast_document(doc: Dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
```


## FILE: tooling/semascript_validator.py

Size: 6858 bytes

```file

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Union

from semascript_parser import Node, parse

Value = Union[Node, List["Value"], str]

CORE_CLASSES: Set[str] = {"ENT", "PRC", "STA", "REL", "MOD", "FRM", "IDX"}
EXT_CLASSES: Set[str] = {"PAT", "TIME", "LAW", "VAL"}
EXEC_CLASSES: Set[str] = {"EXEC"}

ALL_CLASSES: Set[str] = CORE_CLASSES | EXT_CLASSES | EXEC_CLASSES

CORE_ROLES: Set[str] = {
    "agt", "obj", "src", "dst", "ctx", "res", "cau", "dep", "mod",
    "ins", "loc", "tim", "scp", "axis", "scope", "code", "core",
    "law", "mode", "qty", "time", "invariant", "left", "right"
}

EXEC_REQUIRED: Dict[str, Set[str]] = {
    "TRANSFER": {"src", "dst", "obj"},
    "CREATE": {"dst", "obj"},
    "DESTROY": {"obj"},
    "ACT": {"agt"},
    "OBSERVE": {"agt", "obj"},
    "CHANGE": {"obj"},
}


@dataclass
class ValidationResult:
    valid: bool
    errors: List[Tuple[str, str]] = field(default_factory=list)

    def add(self, code: str, message: str) -> None:
        self.errors.append((code, message))

    def finish(self) -> "ValidationResult":
        self.valid = not self.errors
        return self


def validate_core_text(text: str) -> ValidationResult:
    try:
        node = parse(text)
    except Exception as exc:
        return ValidationResult(valid=False, errors=[("P000", f"Parse error: {exc}")])
    return validate_core_node(node)


def validate_exec_text(text: str) -> ValidationResult:
    try:
        node = parse(text)
    except Exception as exc:
        return ValidationResult(valid=False, errors=[("P000", f"Parse error: {exc}")])
    return validate_exec_node(node)


def validate_core_node(node: Node) -> ValidationResult:
    result = ValidationResult(valid=True)
    _validate_node_recursive(node, result, is_top=True)

    if node.class_name == "MOD":
        result.add("C005", "Standalone MOD node is not a valid complete construction")
    if node.class_name == "FRM" and node.root in {"INV", "TIME", "CND"} and "scp" not in node.roles:
        result.add("C004", f"Frame {node.root} requires scp role")
    if node.class_name == "FRM" and node.root == "INV" and "law" not in node.roles:
        result.add("C004", "FRM:INV requires law role")
    if node.class_name == "FRM" and node.root == "TIME" and "mode" not in node.roles:
        result.add("C004", "FRM:TIME requires mode role")
    if node.class_name == "PAT":
        _validate_pattern(node, result)

    return result.finish()


def validate_exec_node(node: Node) -> ValidationResult:
    result = ValidationResult(valid=True)
    _validate_node_recursive(node, result, is_top=True)

    if node.class_name != "EXEC":
        result.add("X001", "Exec validation requires top-level EXEC node")
        return result.finish()

    required = EXEC_REQUIRED.get(node.root)
    if required is None:
        result.add("X001", f"Unsupported EXEC operation: {node.root}")
        return result.finish()

    for role in sorted(required):
        if role not in node.roles:
            result.add("X002", f"Missing required role for EXEC:{node.root}: {role}")

    for role, value in node.roles.items():
        _validate_exec_value(role, value, result)

    return result.finish()


def _validate_exec_value(role: str, value: Value, result: ValidationResult) -> None:
    if isinstance(value, list):
        result.add("X010", f"List value is not supported in exec role {role}")
        return

    if isinstance(value, Node):
        if role == "time":
            if value.class_name != "TIME":
                result.add("X008", "time role must be [TIME:...]")
        elif role == "invariant":
            if value.class_name != "LAW":
                result.add("X007", "invariant role must be [LAW:...]")
        elif value.class_name == "PAT":
            result.add("X006", "Pattern macros cannot be executed directly")
        elif value.class_name == "EXEC":
            result.add("X010", "Nested EXEC blocks are not supported in MVP")
        return

    # raw string
    if role in {"time", "invariant"}:
        result.add("X010", f"{role} must be typed, not raw token")
    else:
        result.add("X003", f"Untyped executable operand for role {role}: {value}")


def _validate_node_recursive(node: Node, result: ValidationResult, is_top: bool = False) -> None:
    if node.class_name not in ALL_CLASSES:
        result.add("C002", f"Unknown class: {node.class_name}")

    if not node.root:
        result.add("C002", "Missing root")

    if node.class_name in CORE_CLASSES | {"PAT"}:
        for role in node.roles:
            if role not in CORE_ROLES:
                result.add("C003", f"Unknown or unsupported role: {role}")

    for role, value in node.roles.items():
        _validate_value_recursive(role, value, result)

    if is_top and node.class_name == "MOD":
        result.add("C005", "Top-level modifier has no target")

    if node.class_name == "STA" and node.root == "ZSUM":
        result.add("E206", "ZSUM is invariant logic, not a state")

    if node.class_name == "FRM":
        if node.root == "INV":
            if "scp" not in node.roles:
                result.add("C004", "FRM:INV missing scp")
            if "law" not in node.roles:
                result.add("C004", "FRM:INV missing law")
        if node.root == "TIME":
            if "scp" not in node.roles:
                result.add("E203", "FRM:TIME missing scp")
            if "mode" not in node.roles:
                result.add("C004", "FRM:TIME missing mode")

    if node.class_name == "PAT":
        _validate_pattern(node, result)


def _validate_value_recursive(role: str, value: Value, result: ValidationResult) -> None:
    if isinstance(value, Node):
        _validate_node_recursive(value, result, is_top=False)
        return

    if isinstance(value, list):
        if role in {"scp", "scope"} and len(value) == 0:
            result.add("C004", f"Empty scope list in role {role}")
        for item in value:
            _validate_value_recursive(role, item, result)
        return

    if role in {"scp", "scope"} and not value:
        result.add("C004", f"Empty scope in role {role}")


def _validate_pattern(node: Node, result: ValidationResult) -> None:
    if node.root == "SPR":
        if "core" not in node.roles or "res" not in node.roles:
            result.add("E201", "PAT:SPR requires core and res roles")
    elif node.root == "GEN":
        if "code" not in node.roles or "dst" not in node.roles:
            result.add("E201", "PAT:GEN requires code and dst roles")
    elif node.root == "PAL":
        if "axis" not in node.roles or not ("scope" in node.roles or "scp" in node.roles):
            result.add("E201", "PAT:PAL requires axis and scope/scp roles")
    else:
        result.add("E202", f"Unsupported pattern macro: {node.root}")
```


## FILE: tooling/parse_to_ast.py

Size: 1176 bytes

```file

from __future__ import annotations

import argparse
import json
from pathlib import Path

from human_normalizer import normalize
from semascript_ast import text_to_ast_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse SEMASCRIPT text into AST JSON")
    parser.add_argument("file", help="Path to input text file")
    parser.add_argument("--profile", choices=["human", "core", "exec"], default="core")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    source_text = Path(args.file).read_text(encoding="utf-8").strip()
    normalized = normalize(source_text) if args.profile == "human" else source_text

    doc = text_to_ast_document(
        normalized,
        source_profile="normalized" if args.profile == "human" else args.profile,
        source_text=source_text,
    )
    if args.profile == "human":
        doc["metadata"]["normalized_text"] = normalized

    payload = json.dumps(doc, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
```


## FILE: tooling/validate_ast.py

Size: 1491 bytes

```file

from __future__ import annotations

import argparse
import json
from pathlib import Path

from semascript_ast import load_ast_document, ast_to_node
from semascript_validator import validate_core_node, validate_exec_node


def build_report(doc: dict, mode: str) -> dict:
    node = ast_to_node(doc["ast"])
    result = validate_core_node(node) if mode == "core" else validate_exec_node(node)
    annotations = [
        {"code": code, "level": "error", "message": message}
        for code, message in result.errors
    ]
    return {
        "schema_version": doc.get("schema_version"),
        "mode": mode,
        "valid": result.valid,
        "errors": annotations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SEMASCRIPT AST JSON")
    parser.add_argument("file", help="Path to AST JSON file")
    parser.add_argument("--mode", choices=["core", "exec", "auto"], default="auto")
    parser.add_argument("--output", help="Optional output report JSON path")
    args = parser.parse_args()

    doc = load_ast_document(args.file)
    top_class = doc["ast"]["class_name"]
    mode = "exec" if args.mode == "auto" and top_class == "EXEC" else ("core" if args.mode == "auto" else args.mode)
    report = build_report(doc, mode)

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
```


## FILE: tooling/validate_cli.py

Size: 910 bytes

```file

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from semascript_validator import validate_core_text, validate_exec_text


def main() -> None:
    parser = argparse.ArgumentParser(description="SEMASCRIPT parser/validator MVP")
    parser.add_argument("file", help="Path to file with a single SEMASCRIPT construction")
    parser.add_argument("--mode", choices=["core", "exec"], default="core")
    args = parser.parse_args()

    text = Path(args.file).read_text(encoding="utf-8").strip()
    fn: Callable[[str], object] = validate_core_text if args.mode == "core" else validate_exec_text
    result = fn(text)

    print(f"mode={args.mode}")
    print(f"valid={result.valid}")
    if result.errors:
        print("errors:")
        for code, message in result.errors:
            print(f" - {code}: {message}")


if __name__ == "__main__":
    main()
```


## FILE: tooling/normalize_cli.py

Size: 478 bytes

```file

from __future__ import annotations

import argparse
from pathlib import Path

from human_normalizer import normalize


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize SEMASCRIPT Human shorthand to Core form")
    parser.add_argument("file", help="Path to file with Human shorthand")
    args = parser.parse_args()

    text = Path(args.file).read_text(encoding="utf-8").strip()
    print(normalize(text))


if __name__ == "__main__":
    main()
```


## FILE: tooling/execute_runtime.py

Size: 1023 bytes

```file

from __future__ import annotations

import argparse
import json
from pathlib import Path

from exec_runtime import execute_text, load_and_execute


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute SEMASCRIPT runtime semantics v0.1")
    parser.add_argument("file", help="Input file")
    parser.add_argument("--input-format", choices=["text", "ast"], default="text")
    parser.add_argument("--profile", choices=["human", "core", "exec"], default="exec")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    if args.input_format == "ast":
        result = load_and_execute(args.file)
    else:
        text = Path(args.file).read_text(encoding="utf-8").strip()
        result = execute_text(text, profile=args.profile)

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
```


## FILE: tooling/exec_runtime.py

Size: 14804 bytes

```file

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from human_normalizer import normalize
from semascript_ast import (
    ast_to_slinear,
    load_ast_document,
    save_ast_document,
    text_to_ast_document,
)
from pattern_decomposer import decompose_ast_document, PatternDecompositionError


ASTNode = Dict[str, Any]
ASTValue = Dict[str, Any]


class ExecRuntimeError(Exception):
    """Raised when runtime execution cannot proceed."""


def _role_map(node: ASTNode) -> Dict[str, ASTValue]:
    return {entry["name"]: entry["value"] for entry in node.get("roles", [])}


def _value_label(value: ASTValue) -> str:
    kind = value["kind"]
    if kind == "node":
        return ast_to_slinear(value)
    if kind == "list":
        return "[" + "; ".join(_value_label(v) for v in value["items"]) + "]"
    if kind == "typed_literal":
        if value.get("value") is not None:
            return f"[{value['class_name']}:{value['root']}={value['value']}]"
        return f"[{value['class_name']}:{value['root']}]"
    if kind == "raw_token":
        return value["value"]
    return "<UNKNOWN>"


def _value_token(value: Optional[ASTValue]) -> Optional[str]:
    if value is None:
        return None
    kind = value["kind"]
    if kind == "raw_token":
        return value["value"]
    if kind == "typed_literal":
        return value["root"]
    if kind == "node":
        return value["root"]
    return None


def _normalize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(context)
    out.setdefault("time_mode", None)
    out.setdefault("invariant_law", None)
    out.setdefault("schedule", None)
    out.setdefault("notes", [])
    return out


def _make_step(op_family: str, op_name: str, roles: Dict[str, str], context: Dict[str, Any], reversible: bool, effect_class: str) -> Dict[str, Any]:
    return {
        "op_family": op_family,
        "op_name": op_name,
        "roles": roles,
        "constraints": {
            "time_mode": context.get("time_mode"),
            "invariant_law": context.get("invariant_law"),
            "schedule": context.get("schedule"),
        },
        "reversible": reversible,
        "effect_class": effect_class,
    }


def _combine_results(results: List[Dict[str, Any]], context: Dict[str, Any], entry_kind: str) -> Dict[str, Any]:
    plan = []
    errors = []
    notes = []
    accepted = True
    decomposition_count = 0

    for result in results:
        plan.extend(result.get("plan", []))
        errors.extend(result.get("errors", []))
        notes.extend(result.get("notes", []))
        decomposition_count += result.get("decomposition_count", 0)
        if not result.get("accepted", False):
            accepted = False

    return {
        "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
        "accepted": accepted and not errors,
        "entry_kind": entry_kind,
        "context": {
            "time_mode": context.get("time_mode"),
            "invariant_law": context.get("invariant_law"),
            "schedule": context.get("schedule"),
        },
        "plan": plan,
        "errors": errors,
        "notes": notes,
        "decomposition_count": decomposition_count,
    }


def _runtime_error(code: str, message: str, context: Dict[str, Any], entry_kind: str) -> Dict[str, Any]:
    return {
        "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
        "accepted": False,
        "entry_kind": entry_kind,
        "context": {
            "time_mode": context.get("time_mode"),
            "invariant_law": context.get("invariant_law"),
            "schedule": context.get("schedule"),
        },
        "plan": [],
        "errors": [{"code": code, "message": message}],
        "notes": [],
        "decomposition_count": 0,
    }


def _execute_scope(value: ASTValue, context: Dict[str, Any]) -> Dict[str, Any]:
    kind = value["kind"]
    if kind == "list":
        items = value["items"]
        results = []
        ctx = dict(context)

        if ctx.get("time_mode") == "LIN":
            ctx["schedule"] = "sequential"
        elif ctx.get("time_mode") == "CYC":
            ctx["schedule"] = "cyclical"
        elif ctx.get("time_mode") == "BRN":
            ctx["schedule"] = "branch_set"
        elif ctx.get("time_mode") == "REC":
            ctx["schedule"] = "recursive"
        elif ctx.get("time_mode") == "REV":
            ctx["schedule"] = "reversible_sequence"
        elif ctx.get("time_mode") == "ATM":
            ctx["schedule"] = "atemporal_set"
        else:
            ctx["schedule"] = "sequential" if len(items) > 1 else None

        if ctx.get("time_mode") == "BRN":
            # branch set is representable but not automatically selected
            notes = ["branch_set_deferred_selection"]
            base = _combine_results([_execute_node(item, ctx) for item in items], ctx, "branch_scope")
            base["notes"].extend(notes)
            return base

        results = [_execute_node(item, ctx) for item in items]
        return _combine_results(results, ctx, "list_scope")

    if kind == "node":
        return _execute_node(value, context)

    return _runtime_error("R_SCOPE", f"Unsupported scope value kind: {kind}", context, "scope")


def _exec_operation(node: ASTNode, context: Dict[str, Any]) -> Dict[str, Any]:
    roles = _role_map(node)
    op = node["root"]

    required = {
        "TRANSFER": {"src", "dst", "obj"},
        "CREATE": {"dst", "obj"},
        "DESTROY": {"obj"},
        "ACT": {"agt"},
        "OBSERVE": {"agt", "obj"},
        "CHANGE": {"obj"},
    }.get(op)

    if required is None:
        return _runtime_error("R_EXEC_OP", f"Unsupported runtime EXEC operation: {op}", context, "exec")

    missing = [r for r in sorted(required) if r not in roles]
    if missing:
        return _runtime_error("R_EXEC_ROLE", f"Missing required roles: {', '.join(missing)}", context, "exec")

    invariant = context.get("invariant_law")
    time_mode = context.get("time_mode")

    if invariant == "ZSUM" and op in {"CREATE", "DESTROY"}:
        return _runtime_error("R_INV_ZSUM", f"{op} violates ZSUM invariant", context, "exec")
    if invariant == "NZSUM" and op == "TRANSFER":
        return _runtime_error("R_INV_NZSUM", "TRANSFER does not satisfy NZSUM by itself", context, "exec")
    if invariant == "BAL":
        return _runtime_error("R_INV_BAL", "BAL is not an operational invariant law in runtime v0.1", context, "exec")
    if time_mode == "REV" and op in {"CREATE", "DESTROY"}:
        return _runtime_error("R_TIME_REV", f"{op} is not reversible under REV runtime mode", context, "exec")

    reversible = op in {"TRANSFER", "CHANGE", "OBSERVE", "ACT"}
    if time_mode == "REV" and not reversible:
        return _runtime_error("R_TIME_REV", f"{op} is not reversible under REV runtime mode", context, "exec")

    role_labels = {name: _value_label(value) for name, value in roles.items()}
    effect_class = {
        "TRANSFER": "redistribution",
        "CREATE": "net_growth",
        "DESTROY": "net_loss",
        "ACT": "action",
        "OBSERVE": "observation",
        "CHANGE": "state_transition",
    }[op]

    step = _make_step("EXEC", op, role_labels, context, reversible, effect_class)
    return {
        "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
        "accepted": True,
        "entry_kind": "exec",
        "context": {
            "time_mode": context.get("time_mode"),
            "invariant_law": context.get("invariant_law"),
            "schedule": context.get("schedule"),
        },
        "plan": [step],
        "errors": [],
        "notes": [],
        "decomposition_count": 0,
    }


def _core_runtime(node: ASTNode, context: Dict[str, Any]) -> Dict[str, Any]:
    roles = _role_map(node)

    if node["class_name"] == "PRC" and node["root"] == "EXP":
        step = _make_step(
            "CORE",
            "EXPAND",
            {name: _value_label(value) for name, value in roles.items()},
            context,
            reversible=False,
            effect_class="structural_growth",
        )
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": True,
            "entry_kind": "core_runtime",
            "context": {
                "time_mode": context.get("time_mode"),
                "invariant_law": context.get("invariant_law"),
                "schedule": context.get("schedule"),
            },
            "plan": [step],
            "errors": [],
            "notes": ["decomposed_pattern_runtime"],
            "decomposition_count": 0,
        }

    if node["class_name"] == "REL" and node["root"] == "DEP":
        step = _make_step(
            "CORE",
            "DEPENDENCY",
            {name: _value_label(value) for name, value in roles.items()},
            context,
            reversible=False,
            effect_class="dependency_relation",
        )
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": True,
            "entry_kind": "core_runtime",
            "context": {
                "time_mode": context.get("time_mode"),
                "invariant_law": context.get("invariant_law"),
                "schedule": context.get("schedule"),
            },
            "plan": [step],
            "errors": [],
            "notes": ["decomposed_pattern_runtime"],
            "decomposition_count": 0,
        }

    if node["class_name"] == "REL" and node["root"] == "CAU":
        cause = roles.get("cau")
        result = roles.get("res")
        if cause is None or result is None:
            return _runtime_error("R_CAU", "REL:CAU requires cau and res", context, "core_runtime")
        ctx = dict(context)
        ctx["schedule"] = "causal_sequence"
        return _combine_results([_execute_scope(cause, ctx), _execute_scope(result, ctx)], ctx, "causal_chain")

    if node["class_name"] == "STA":
        step = _make_step(
            "CORE",
            "ASSERT_STATE",
            {name: _value_label(value) for name, value in roles.items()},
            context,
            reversible=False,
            effect_class="state_assertion",
        )
        step["state_root"] = node["root"]
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": True,
            "entry_kind": "core_runtime",
            "context": {
                "time_mode": context.get("time_mode"),
                "invariant_law": context.get("invariant_law"),
                "schedule": context.get("schedule"),
            },
            "plan": [step],
            "errors": [],
            "notes": [],
            "decomposition_count": 0,
        }

    return _runtime_error(
        "R_CORE_NODE",
        f"Unsupported core runtime node: {node['class_name']}:{node['root']}",
        context,
        "core_runtime",
    )


def _execute_node(node: ASTNode, context: Dict[str, Any]) -> Dict[str, Any]:
    context = _normalize_context(context)

    if node["class_name"] == "FRM":
        roles = _role_map(node)

        if node["root"] == "TIME":
            scope = roles.get("scp")
            if scope is None:
                return _runtime_error("R_TIME_SCOPE", "FRM:TIME requires scp", context, "frame")
            new_context = dict(context)
            new_context["time_mode"] = _value_token(roles.get("mode"))
            return _execute_scope(scope, new_context)

        if node["root"] == "INV":
            scope = roles.get("scp")
            if scope is None:
                return _runtime_error("R_INV_SCOPE", "FRM:INV requires scp", context, "frame")
            new_context = dict(context)
            new_context["invariant_law"] = _value_token(roles.get("law"))
            return _execute_scope(scope, new_context)

        if node["root"] == "SCN":
            scope = roles.get("scp")
            if scope is None:
                return _runtime_error("R_SCN_SCOPE", "FRM:SCN requires scp", context, "frame")
            new_context = dict(context)
            new_context["notes"] = list(new_context.get("notes", [])) + ["scene_wrapper"]
            return _execute_scope(scope, new_context)

        return _runtime_error("R_FRAME", f"Unsupported frame root in runtime: {node['root']}", context, "frame")

    if node["class_name"] == "EXEC":
        return _exec_operation(node, context)

    if node["class_name"] == "PAT":
        return _runtime_error("R_PATTERN", "Pattern macro remained undecomposed in runtime path", context, "pattern")

    return _core_runtime(node, context)


def execute_ast_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    try:
        decomposed = decompose_ast_document(doc)
    except PatternDecompositionError as exc:
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": False,
            "entry_kind": "decomposition",
            "context": {"time_mode": None, "invariant_law": None, "schedule": None},
            "plan": [],
            "errors": [{"code": "R_DECOMP", "message": str(exc)}],
            "notes": [],
            "decomposition_count": 0,
        }

    result = _execute_node(decomposed["ast"], {})
    result["decomposition_count"] = decomposed.get("metadata", {}).get("pattern_decomposition_count", 0)
    return result


def execute_text(text: str, profile: str = "exec") -> Dict[str, Any]:
    try:
        normalized = normalize(text) if profile == "human" else text
    except Exception as exc:
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": False,
            "entry_kind": "normalization",
            "context": {"time_mode": None, "invariant_law": None, "schedule": None},
            "plan": [],
            "errors": [{"code": "R_NORMALIZE", "message": str(exc)}],
            "notes": [],
            "decomposition_count": 0,
        }

    try:
        doc = text_to_ast_document(
            normalized,
            source_profile="normalized" if profile == "human" else profile,
            source_text=text,
        )
    except Exception as exc:
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": False,
            "entry_kind": "parse",
            "context": {"time_mode": None, "invariant_law": None, "schedule": None},
            "plan": [],
            "errors": [{"code": "R_PARSE", "message": str(exc)}],
            "notes": [],
            "decomposition_count": 0,
        }

    if profile == "human":
        doc["metadata"]["normalized_text"] = normalized
    return execute_ast_document(doc)


def load_and_execute(path: str) -> Dict[str, Any]:
    doc = load_ast_document(path)
    return execute_ast_document(doc)
```


## FILE: tooling/state_model.py

Size: 10461 bytes

```file

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional, Tuple
import json
from pathlib import Path

from exec_runtime import execute_text, load_and_execute

State = Dict[str, Any]
RuntimeReport = Dict[str, Any]


class StateModelError(Exception):
    """Raised when execution state cannot be updated."""


def create_empty_state() -> State:
    return {
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {
            "applied_steps": 0,
            "last_schedule": None,
        },
    }


def load_state(path: str | Path) -> State:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_state(state: State, path: str | Path) -> None:
    Path(path).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _label_parts(label: str) -> Tuple[Optional[str], str]:
    if label.startswith("[") and label.endswith("]") and ":" in label:
        body = label[1:-1]
        class_name, root = body.split(":", 1)
        return class_name, root
    return None, label


def _entity_token(label: Optional[str]) -> str:
    if not label:
        raise StateModelError("Missing entity label")
    class_name, root = _label_parts(label)
    if class_name != "ENT":
        raise StateModelError(f"Expected ENT label, got {label}")
    return root


def _state_token(label: Optional[str]) -> str:
    if not label:
        raise StateModelError("Missing state label")
    class_name, root = _label_parts(label)
    if class_name != "STA":
        raise StateModelError(f"Expected STA label, got {label}")
    return root


def _resource_token(label: Optional[str]) -> str:
    if not label:
        raise StateModelError("Missing resource label")
    class_name, root = _label_parts(label)
    if class_name != "ENT":
        raise StateModelError(f"Expected ENT resource label, got {label}")
    return root


def _qty_value(label: Optional[str]) -> int:
    if not label:
        return 1
    class_name, root = _label_parts(label)
    if class_name == "VAL":
        if root.isdigit():
            return int(root)
        if "=" in root:
            maybe = root.split("=", 1)[1]
            if maybe.isdigit():
                return int(maybe)
    if label.isdigit():
        return int(label)
    return 1


def _resource_total(state: State) -> int:
    total = 0
    for _, inventory in state["resources"].items():
        for _, qty in inventory.items():
            total += int(qty)
    return total


def _ensure_entity(state: State, entity: str) -> None:
    state["resources"].setdefault(entity, {})
    state["states"].setdefault(entity, [])


def _append_history(state: State, step: Dict[str, Any], note: Optional[str] = None) -> None:
    entry = {
        "op_name": step["op_name"],
        "op_family": step["op_family"],
        "roles": dict(step["roles"]),
        "constraints": dict(step.get("constraints", {})),
    }
    if note:
        entry["note"] = note
    state["history"].append(entry)
    state["metadata"]["applied_steps"] += 1
    state["metadata"]["last_schedule"] = step.get("constraints", {}).get("schedule")


def apply_runtime_report(runtime_report: RuntimeReport, initial_state: Optional[State] = None) -> Dict[str, Any]:
    state = deepcopy(initial_state) if initial_state is not None else create_empty_state()

    if not runtime_report.get("accepted", False):
        return {
            "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
            "accepted": False,
            "initial_state": initial_state if initial_state is not None else create_empty_state(),
            "final_state": state,
            "runtime_report": runtime_report,
            "errors": runtime_report.get("errors", []),
        }

    schedule = runtime_report.get("context", {}).get("schedule")
    if schedule == "branch_set":
        return {
            "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
            "accepted": False,
            "initial_state": initial_state if initial_state is not None else create_empty_state(),
            "final_state": state,
            "runtime_report": runtime_report,
            "errors": [{"code": "S_BRANCH_DEFERRED", "message": "branch_set requires external branch selection before state application"}],
        }

    invariant = runtime_report.get("context", {}).get("invariant_law")
    total_before = _resource_total(state)

    for step in runtime_report.get("plan", []):
        op = step["op_name"]
        roles = step["roles"]

        if op == "TRANSFER":
            src = _entity_token(roles.get("src"))
            dst = _entity_token(roles.get("dst"))
            obj = _resource_token(roles.get("obj"))
            qty = _qty_value(roles.get("qty"))
            _ensure_entity(state, src)
            _ensure_entity(state, dst)
            src_qty = int(state["resources"][src].get(obj, 0))
            if src_qty < qty:
                return {
                    "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
                    "accepted": False,
                    "initial_state": initial_state if initial_state is not None else create_empty_state(),
                    "final_state": state,
                    "runtime_report": runtime_report,
                    "errors": [{"code": "S_BALANCE", "message": f"Insufficient balance for {src}:{obj}"}],
                }
            state["resources"][src][obj] = src_qty - qty
            state["resources"][dst][obj] = int(state["resources"][dst].get(obj, 0)) + qty
            _append_history(state, step)

        elif op == "CREATE":
            dst = _entity_token(roles.get("dst"))
            obj = _resource_token(roles.get("obj"))
            qty = _qty_value(roles.get("qty"))
            _ensure_entity(state, dst)
            state["resources"][dst][obj] = int(state["resources"][dst].get(obj, 0)) + qty
            _append_history(state, step)

        elif op == "DESTROY":
            ctx = roles.get("ctx")
            obj = _resource_token(roles.get("obj"))
            qty = _qty_value(roles.get("qty"))
            target = _entity_token(ctx) if ctx else "GLOBAL"
            _ensure_entity(state, target)
            cur = int(state["resources"][target].get(obj, 0))
            if cur < qty:
                return {
                    "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
                    "accepted": False,
                    "initial_state": initial_state if initial_state is not None else create_empty_state(),
                    "final_state": state,
                    "runtime_report": runtime_report,
                    "errors": [{"code": "S_BALANCE", "message": f"Insufficient balance for destroy on {target}:{obj}"}],
                }
            state["resources"][target][obj] = cur - qty
            _append_history(state, step)

        elif op == "ACT":
            state["actions"].append({
                "agt": roles.get("agt"),
                "obj": roles.get("obj"),
                "ctx": roles.get("ctx"),
            })
            _append_history(state, step)

        elif op == "OBSERVE":
            state["observations"].append({
                "agt": roles.get("agt"),
                "obj": roles.get("obj"),
            })
            _append_history(state, step)

        elif op == "CHANGE":
            obj = roles.get("obj")
            res = roles.get("res")
            if obj:
                entity = _entity_token(obj)
                _ensure_entity(state, entity)
                if res:
                    token = _state_token(res)
                    if token not in state["states"][entity]:
                        state["states"][entity].append(token)
            _append_history(state, step)

        elif op == "DEPENDENCY":
            state["dependencies"].append({
                "dst": roles.get("dst"),
                "src": roles.get("src"),
            })
            _append_history(state, step)

        elif op == "EXPAND":
            state["expansions"].append({
                "src": roles.get("src"),
                "res": roles.get("res"),
            })
            _append_history(state, step)

        elif op == "ASSERT_STATE":
            ctx = roles.get("ctx")
            if ctx:
                entity = _entity_token(ctx)
                _ensure_entity(state, entity)
                token = step.get("state_root")
                if token and token not in state["states"][entity]:
                    state["states"][entity].append(token)
            _append_history(state, step)

        else:
            return {
                "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
                "accepted": False,
                "initial_state": initial_state if initial_state is not None else create_empty_state(),
                "final_state": state,
                "runtime_report": runtime_report,
                "errors": [{"code": "S_OP", "message": f"Unsupported state operation: {op}"}],
            }

    if invariant == "ZSUM" and _resource_total(state) != total_before:
        return {
            "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
            "accepted": False,
            "initial_state": initial_state if initial_state is not None else create_empty_state(),
            "final_state": state,
            "runtime_report": runtime_report,
            "errors": [{"code": "S_INV_ZSUM", "message": "ZSUM invariant violated by resulting state"}],
        }

    return {
        "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "accepted": True,
        "initial_state": initial_state if initial_state is not None else create_empty_state(),
        "final_state": state,
        "runtime_report": runtime_report,
        "errors": [],
    }


def execute_text_with_state(text: str, profile: str = "exec", initial_state: Optional[State] = None) -> Dict[str, Any]:
    runtime_report = execute_text(text, profile=profile)
    return apply_runtime_report(runtime_report, initial_state=initial_state)


def execute_ast_with_state(path: str, initial_state: Optional[State] = None) -> Dict[str, Any]:
    runtime_report = load_and_execute(path)
    return apply_runtime_report(runtime_report, initial_state=initial_state)
```


## FILE: tooling/session_model.py

Size: 5823 bytes

```file

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json
from copy import deepcopy



class SessionModelError(Exception):
    """Raised when session model cannot be created or restored."""


def empty_ui_state() -> dict:
    return {
        "selected_entity_id": None,
        "preview_mode": "raw",
        "decompose": True,
        "viewport": {"scroll_x": 0, "scroll_y": 0, "zoom": 1.0},
        "panels": {
            "svg": True,
            "ast": True,
            "runtime": True,
            "state": True,
            "graph_json": True,
        },
    }


def create_session_from_text(
    text: str,
    profile: str = "core",
    decompose: bool = True,
    initial_state: Optional[dict] = None,
    session_name: Optional[str] = None,
) -> dict:
    from inspector_service import analyze_input
    analysis = analyze_input(
        text=text,
        profile=profile,
        decompose=decompose,
        initial_state=initial_state,
    )
    return {
        "session_version": "SEMASCRIPT_PROJECT_SESSION_v0.1",
        "session_name": session_name or "Untitled SEMASCRIPT Session",
        "project": {
            "profile": profile,
            "source_mode": "text",
            "source_text": analysis["source_text"],
            "normalized_text": analysis["normalized_text"],
            "slinear": analysis["slinear"],
            "decomposed_slinear": analysis.get("decomposed_slinear"),
            "initial_state": deepcopy(initial_state),
        },
        "documents": {
            "ast_document": analysis["ast_document"],
            "decomposed_ast_document": analysis.get("decomposed_ast_document"),
            "graph_document": analysis.get("graph_document"),
            "decomposed_graph_document": analysis.get("decomposed_graph_document"),
        },
        "reports": {
            "validation": analysis["validation"],
            "runtime_report": analysis["runtime_report"],
            "state_report": analysis["state_report"],
        },
        "render": {
            "svg_raw": analysis["svg_raw"],
            "svg_decomposed": analysis.get("svg_decomposed"),
        },
        "ui_state": empty_ui_state(),
        "metadata": {
            "generated_from": "text_input",
        },
    }


def create_session_from_graph(
    graph_document: dict,
    profile: str = "core",
    decompose: bool = True,
    initial_state: Optional[dict] = None,
    session_name: Optional[str] = None,
    ui_state: Optional[dict] = None,
) -> dict:
    from inspector_service import analyze_graph
    analysis = analyze_graph(
        graph_document=graph_document,
        profile=profile,
        decompose=decompose,
        initial_state=initial_state,
    )
    session = {
        "session_version": "SEMASCRIPT_PROJECT_SESSION_v0.1",
        "session_name": session_name or "Untitled SEMASCRIPT Graph Session",
        "project": {
            "profile": profile,
            "source_mode": "graph",
            "source_text": analysis["source_text"],
            "normalized_text": analysis["normalized_text"],
            "slinear": analysis["slinear"],
            "decomposed_slinear": analysis.get("decomposed_slinear"),
            "initial_state": deepcopy(initial_state),
        },
        "documents": {
            "ast_document": analysis["ast_document"],
            "decomposed_ast_document": analysis.get("decomposed_ast_document"),
            "graph_document": analysis.get("graph_document"),
            "decomposed_graph_document": analysis.get("decomposed_graph_document"),
        },
        "reports": {
            "validation": analysis["validation"],
            "runtime_report": analysis["runtime_report"],
            "state_report": analysis["state_report"],
        },
        "render": {
            "svg_raw": analysis["svg_raw"],
            "svg_decomposed": analysis.get("svg_decomposed"),
        },
        "ui_state": deepcopy(ui_state) if ui_state is not None else empty_ui_state(),
        "metadata": {
            "generated_from": "graph_input",
        },
    }
    return session


def save_session(session: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def load_session(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def session_to_inspector_payload(session: dict) -> dict:
    if session.get("session_version") != "SEMASCRIPT_PROJECT_SESSION_v0.1":
        raise SessionModelError("Unsupported session_version")

    project = session["project"]
    documents = session["documents"]
    reports = session["reports"]
    render = session["render"]

    payload = {
        "source_text": project["source_text"],
        "profile": project["profile"],
        "normalized_text": project["normalized_text"],
        "slinear": project["slinear"],
        "decomposed_slinear": project.get("decomposed_slinear"),
        "ast_document": documents["ast_document"],
        "decomposed_ast_document": documents.get("decomposed_ast_document"),
        "graph_document": documents.get("graph_document"),
        "decomposed_graph_document": documents.get("decomposed_graph_document"),
        "validation": reports["validation"],
        "runtime_report": reports["runtime_report"],
        "state_report": reports["state_report"],
        "svg_raw": render["svg_raw"],
        "svg_decomposed": render.get("svg_decomposed"),
        "session_name": session.get("session_name"),
        "ui_state": session.get("ui_state", empty_ui_state()),
    }
    return payload


def create_project_index(session_files: list[dict]) -> dict:
    return {
        "project_index_version": "SEMASCRIPT_PROJECT_INDEX_v0.1",
        "sessions": session_files,
    }
```


## FILE: tooling/session_diff.py

Size: 5089 bytes

```file

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Set

from workspace_navigation import summarize_session_entry


def _entry_by_id(project_index: dict, session_id: str) -> dict:
    for entry in project_index.get("sessions", []):
        if entry["session_id"] == session_id:
            return entry
    raise ValueError(f"Unknown session_id: {session_id}")


def _session_metrics(entry: dict) -> dict:
    session = entry["session"]
    nav = summarize_session_entry(entry)
    runtime = session.get("reports", {}).get("runtime_report", {}) or {}
    state = session.get("reports", {}).get("state_report", {}) or {}
    final_state = state.get("final_state", {}) or {}
    history = state.get("runtime_report", {}).get("history", []) if isinstance(state.get("runtime_report"), dict) else []

    runtime_ops = [step.get("op_name") for step in runtime.get("plan", []) if step.get("op_name")]
    return {
        "session_id": entry["session_id"],
        "session_name": entry.get("session_name"),
        "profile": entry.get("profile"),
        "source_mode": entry.get("source_mode"),
        "slinear": session.get("project", {}).get("slinear"),
        "decomposed_slinear": session.get("project", {}).get("decomposed_slinear"),
        "entities": nav["entities"],
        "inputs": nav["inputs"],
        "outputs": nav["outputs"],
        "state_nodes": nav["state_nodes"],
        "runtime_accepted": bool(runtime.get("accepted")),
        "state_accepted": bool(state.get("accepted")),
        "runtime_ops": runtime_ops,
        "dependency_count": len(final_state.get("dependencies", []) or []),
        "expansion_count": len(final_state.get("expansions", []) or []),
        "action_count": len(final_state.get("actions", []) or []),
        "observation_count": len(final_state.get("observations", []) or []),
        "history_len": len(final_state.get("history", []) or []),
    }


def _set_diff(left: list[str], right: list[str]) -> dict:
    left_set = set(left)
    right_set = set(right)
    return {
        "shared": sorted(left_set & right_set),
        "left_only": sorted(left_set - right_set),
        "right_only": sorted(right_set - left_set),
    }


def _scalar_diff(left_value, right_value) -> dict:
    return {
        "left": left_value,
        "right": right_value,
        "changed": left_value != right_value,
    }


def compare_sessions(project_index: dict, left_session_id: str, right_session_id: str) -> dict:
    left_entry = _entry_by_id(project_index, left_session_id)
    right_entry = _entry_by_id(project_index, right_session_id)

    left = _session_metrics(left_entry)
    right = _session_metrics(right_entry)

    diff = {
        "compare_version": "SEMASCRIPT_CROSS_SESSION_DIFF_v0.1",
        "project_name": project_index.get("project_name"),
        "left_session_id": left_session_id,
        "right_session_id": right_session_id,
        "left_session_name": left.get("session_name"),
        "right_session_name": right.get("session_name"),
        "identity": {
            "profile": _scalar_diff(left["profile"], right["profile"]),
            "source_mode": _scalar_diff(left["source_mode"], right["source_mode"]),
        },
        "structure": {
            "slinear": _scalar_diff(left["slinear"], right["slinear"]),
            "decomposed_slinear": _scalar_diff(left["decomposed_slinear"], right["decomposed_slinear"]),
            "entities": _set_diff(left["entities"], right["entities"]),
            "inputs": _set_diff(left["inputs"], right["inputs"]),
            "outputs": _set_diff(left["outputs"], right["outputs"]),
            "state_nodes": _set_diff(left["state_nodes"], right["state_nodes"]),
        },
        "execution": {
            "runtime_accepted": _scalar_diff(left["runtime_accepted"], right["runtime_accepted"]),
            "state_accepted": _scalar_diff(left["state_accepted"], right["state_accepted"]),
            "runtime_ops": _set_diff(left["runtime_ops"], right["runtime_ops"]),
            "dependency_count": _scalar_diff(left["dependency_count"], right["dependency_count"]),
            "expansion_count": _scalar_diff(left["expansion_count"], right["expansion_count"]),
            "action_count": _scalar_diff(left["action_count"], right["action_count"]),
            "observation_count": _scalar_diff(left["observation_count"], right["observation_count"]),
            "history_len": _scalar_diff(left["history_len"], right["history_len"]),
        },
        "summary": {
            "same_profile": left["profile"] == right["profile"],
            "same_source_mode": left["source_mode"] == right["source_mode"],
            "shared_entities_count": len(set(left["entities"]) & set(right["entities"])),
            "left_only_entities_count": len(set(left["entities"]) - set(right["entities"])),
            "right_only_entities_count": len(set(right["entities"]) - set(left["entities"])),
            "runtime_ops_overlap_count": len(set(left["runtime_ops"]) & set(right["runtime_ops"])),
        },
    }
    return diff
```


## FILE: tooling/session_merge.py

Size: 6304 bytes

```file

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from session_model import create_session_from_text, create_session_from_graph


class SessionMergeConflict(Exception):
    """Raised when merge cannot be finalized."""


def _entry_by_id(project_index: dict, session_id: str) -> dict:
    for entry in project_index.get("sessions", []):
        if entry["session_id"] == session_id:
            return entry
    raise ValueError(f"Unknown session_id: {session_id}")


def _changed(base: Any, other: Any) -> bool:
    return base != other


def _three_way_merge_value(base: Any, left: Any, right: Any, path: str, conflicts: List[dict]) -> Any:
    if left == right:
        return deepcopy(left)
    if left == base:
        return deepcopy(right)
    if right == base:
        return deepcopy(left)

    if isinstance(base, dict) and isinstance(left, dict) and isinstance(right, dict):
        out = {}
        keys = set(base.keys()) | set(left.keys()) | set(right.keys())
        for key in sorted(keys):
            out[key] = _three_way_merge_value(
                base.get(key),
                left.get(key),
                right.get(key),
                f"{path}.{key}" if path else key,
                conflicts,
            )
        return out

    if isinstance(base, list) and isinstance(left, list) and isinstance(right, list):
        # Conservative policy for lists in v0.1:
        # identical or one-sided changes are allowed; concurrent divergent list edits conflict.
        conflicts.append({
            "path": path,
            "base": deepcopy(base),
            "left": deepcopy(left),
            "right": deepcopy(right),
            "reason": "concurrent_list_change",
        })
        return deepcopy(left)

    conflicts.append({
        "path": path,
        "base": deepcopy(base),
        "left": deepcopy(left),
        "right": deepcopy(right),
        "reason": "concurrent_scalar_change",
    })
    return deepcopy(left)



def _merged_session_name(base_session: dict, left_session: dict, right_session: dict) -> str:
    base_name = base_session.get("session_name")
    left_name = left_session.get("session_name")
    right_name = right_session.get("session_name")

    if left_name == right_name:
        return left_name or right_name or "Merged Session"
    if left_name == base_name:
        return right_name or left_name or "Merged Session"
    if right_name == base_name:
        return left_name or right_name or "Merged Session"
    return f"Merged: {left_name or 'left'} + {right_name or 'right'}"

def _source_payload(session: dict) -> dict:
    project = session.get("project", {}) or {}
    documents = session.get("documents", {}) or {}
    source_mode = project.get("source_mode")
    payload = {
        "profile": project.get("profile"),
        "source_mode": source_mode,
        "source_text": project.get("source_text"),
        "initial_state": project.get("initial_state"),
        "ui_state": session.get("ui_state"),
    }
    if source_mode == "graph":
        payload["graph_document"] = documents.get("graph_document")
    return payload


def finalize_merged_source(merged_source: dict) -> dict:
    return _finalize_merged_session(merged_source)


def _finalize_merged_session(merged_source: dict) -> dict:
    source_mode = merged_source.get("source_mode")
    profile = merged_source.get("profile") or "core"
    session_name = merged_source.get("session_name") or "Merged Session"
    initial_state = merged_source.get("initial_state")
    ui_state = merged_source.get("ui_state")

    if source_mode == "text":
        text = merged_source.get("source_text")
        if not text:
            raise SessionMergeConflict("Merged text session has no source_text")
        return create_session_from_text(
            text=text,
            profile=profile,
            decompose=bool(ui_state.get("decompose", True)) if isinstance(ui_state, dict) else True,
            initial_state=initial_state,
            session_name=session_name,
        )

    if source_mode == "graph":
        graph_document = merged_source.get("graph_document")
        if not graph_document:
            raise SessionMergeConflict("Merged graph session has no graph_document")
        return create_session_from_graph(
            graph_document=graph_document,
            profile=profile,
            decompose=bool(ui_state.get("decompose", True)) if isinstance(ui_state, dict) else True,
            initial_state=initial_state,
            session_name=session_name,
            ui_state=ui_state,
        )

    raise SessionMergeConflict(f"Unsupported source_mode for merge: {source_mode!r}")


def merge_sessions_three_way(
    project_index: dict,
    base_session_id: str,
    left_session_id: str,
    right_session_id: str,
) -> dict:
    base_entry = _entry_by_id(project_index, base_session_id)
    left_entry = _entry_by_id(project_index, left_session_id)
    right_entry = _entry_by_id(project_index, right_session_id)

    base_source = _source_payload(base_entry["session"])
    left_source = _source_payload(left_entry["session"])
    right_source = _source_payload(right_entry["session"])

    conflicts: List[dict] = []
    merged_source = _three_way_merge_value(base_source, left_source, right_source, "", conflicts)
    merged_source["session_name"] = _merged_session_name(base_entry["session"], left_entry["session"], right_entry["session"])

    result = {
        "merge_version": "SEMASCRIPT_THREE_WAY_SESSION_MERGE_v0.1",
        "project_name": project_index.get("project_name"),
        "base_session_id": base_session_id,
        "left_session_id": left_session_id,
        "right_session_id": right_session_id,
        "base_session_name": base_entry.get("session_name"),
        "left_session_name": left_entry.get("session_name"),
        "right_session_name": right_entry.get("session_name"),
        "conflicts": conflicts,
        "summary": {
            "conflict_count": len(conflicts),
            "auto_merged": len(conflicts) == 0,
        },
        "merged_source": merged_source,
    }

    if not conflicts:
        merged_session = _finalize_merged_session(merged_source)
        result["merged_session"] = merged_session

    return result
```


## FILE: tooling/session_conflict_resolution.py

Size: 3143 bytes

```file

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from session_merge import finalize_merged_source


class ConflictResolutionError(Exception):
    """Raised when manual conflict resolution is invalid."""


def _set_path_value(obj: dict, path: str, value: Any) -> dict:
    out = deepcopy(obj)
    if not path:
        return deepcopy(value)
    parts = path.split(".")
    cursor = out
    for part in parts[:-1]:
        if part not in cursor or not isinstance(cursor[part], dict):
            cursor[part] = {}
        cursor = cursor[part]
    cursor[parts[-1]] = deepcopy(value)
    return out


def _decision_value(conflict: dict, decision: dict) -> Any:
    choice = decision.get("choice")
    if choice not in {"base", "left", "right", "custom"}:
        raise ConflictResolutionError(f"Unsupported decision choice: {choice!r}")
    if choice == "custom":
        if "value" not in decision:
            raise ConflictResolutionError("Custom decision requires 'value'")
        return deepcopy(decision["value"])
    return deepcopy(conflict[choice])


def resolve_merge_result_conflicts(merge_result: dict, decisions: dict[str, dict]) -> dict:
    out = {
        "resolution_version": "SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_v0.1",
        "merge_version": merge_result.get("merge_version"),
        "base_session_id": merge_result.get("base_session_id"),
        "left_session_id": merge_result.get("left_session_id"),
        "right_session_id": merge_result.get("right_session_id"),
        "summary": {},
        "applied_decisions": [],
        "unresolved_conflicts": [],
        "resolved_source": deepcopy(merge_result.get("merged_source")),
    }

    conflicts = merge_result.get("conflicts", []) or []
    if not conflicts:
        out["summary"] = {
            "conflict_count": 0,
            "resolved_count": 0,
            "unresolved_count": 0,
            "finalized": "merged_session" in merge_result,
        }
        if "merged_session" in merge_result:
            out["merged_session"] = deepcopy(merge_result["merged_session"])
        return out

    resolved_source = deepcopy(merge_result.get("merged_source"))
    applied = []
    unresolved = []

    for conflict in conflicts:
        path = conflict["path"]
        decision = decisions.get(path)
        if not decision:
            unresolved.append(deepcopy(conflict))
            continue
        value = _decision_value(conflict, decision)
        resolved_source = _set_path_value(resolved_source, path, value)
        applied.append({
            "path": path,
            "choice": decision.get("choice"),
            "value": deepcopy(value),
        })

    out["applied_decisions"] = applied
    out["unresolved_conflicts"] = unresolved
    out["resolved_source"] = resolved_source
    out["summary"] = {
        "conflict_count": len(conflicts),
        "resolved_count": len(applied),
        "unresolved_count": len(unresolved),
        "finalized": len(unresolved) == 0,
    }

    if not unresolved:
        out["merged_session"] = finalize_merged_source(resolved_source)

    return out
```


## FILE: tooling/project_model.py

Size: 42478 bytes

```file
from __future__ import annotations

from project_local_outcome_set_package_preview import preview_portable_local_outcome_package_before_import
from project_local_outcome_set_package_resolution import ensure_local_outcome_set_package_resolution_state, local_outcome_set_package_resolution_summary, resolve_portable_local_outcome_package_import_with_decisions
from project_local_outcome_set_package_commit import ensure_local_outcome_set_package_commit_state, local_outcome_set_package_commit_summary, commit_portable_local_outcome_package_import_resolution
from project_local_outcome_set_package_commit_compare import compare_portable_local_outcome_package_commits
from project_local_outcome_set_package_commit_merge import compare_baseline_or_three_way_merge_portable_local_outcome_package_commits
from project_local_outcome_set_package_commit_merge_resolution import ensure_portable_local_outcome_package_merge_resolution_state, portable_local_outcome_package_merge_resolution_summary, resolve_portable_local_outcome_package_three_way_conflicts_with_decisions
from project_local_outcome_set_package_commit_merge_commit import ensure_portable_local_outcome_package_merge_commit_state, portable_local_outcome_package_merge_commit_summary, commit_portable_local_outcome_package_three_way_merge_resolution


from pathlib import Path
from typing import Optional
import json
from copy import deepcopy

from session_model import session_to_inspector_payload
from workspace_navigation import build_workspace_dependency_map
from workspace_timeline import build_workspace_timeline, ensure_workspace_history, append_history_event
from project_branching import ensure_branching_state, branch_summary, create_named_branch, build_named_merge_lineage_graph
from project_tags import ensure_tag_point_state, tag_point_summary, create_tag_release_point
from project_snapshot import ensure_snapshot_state, snapshot_export_summary, create_immutable_snapshot_export
from project_snapshot_restore import ensure_snapshot_restore_state, snapshot_restore_summary, restore_workspace_from_snapshot_export
from project_snapshot_diff import preview_snapshot_restore_before_apply
from project_snapshot_partial_import import ensure_partial_snapshot_import_state, partial_snapshot_import_summary, import_selective_snapshot_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state, snapshot_reconcile_summary, reconcile_snapshot_state_with_current_lineage
from project_snapshot_reconcile_preview import preview_snapshot_reconcile_before_apply
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state, snapshot_reconcile_resolution_summary, resolve_snapshot_reconcile_conflicts_with_decisions
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state, snapshot_reconcile_commit_summary, commit_snapshot_reconcile_resolution_set
from project_snapshot_reconcile_commit_compare import compare_promoted_reconcile_outcomes
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state, snapshot_reconcile_commit_package_summary, snapshot_reconcile_commit_package_import_summary, export_reconcile_commit_as_standalone_package, import_standalone_reconcile_outcome_package
from project_snapshot_reconcile_commit_package_preview import preview_standalone_reconcile_outcome_package_import
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state, snapshot_reconcile_commit_package_resolution_summary, resolve_standalone_reconcile_outcome_package_import_with_decisions
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state, snapshot_reconcile_commit_package_commit_summary, commit_standalone_reconcile_outcome_package_import_resolution

from project_snapshot_reconcile_commit_package_commit_compare import compare_local_outcome_sets
from project_local_outcome_set_package import ensure_local_outcome_set_package_state, local_outcome_set_package_summary, local_outcome_set_package_import_summary, export_local_outcome_set_as_portable_package, import_local_outcome_set_portable_package


class ProjectModelError(Exception):
    """Raised when project workspace model is invalid."""


def create_workspace(session_entries: Optional[list[dict]] = None, project_name: str = "Untitled SEMASCRIPT Project") -> dict:
    sessions = deepcopy(session_entries or [])
    active_session_id = sessions[0]["session_id"] if sessions else None
    base = {
        "project_index_version": "SEMASCRIPT_PROJECT_INDEX_v0.1",
        "project_name": project_name,
        "active_session_id": active_session_id,
        "active_branch_name": "main",
        "branches": {},
        "sessions": sessions,
        "metadata": {
            "workspace_kind": "multi_session",
        },
        "history": {
            "events": [],
            "next_seq": 1,
        },
    }
    return ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(base))))))))))))))


def _derive_session_id(session: dict) -> str:
    raw = session.get("session_name", "session").strip()
    token = "".join(ch if ch.isalnum() else "_" for ch in raw).strip("_")
    return token.lower() or "session"


def make_project_entry(session: dict, session_id: Optional[str] = None, file_name: Optional[str] = None, tags: Optional[list[str]] = None, entry_metadata: Optional[dict] = None) -> dict:
    sid = session_id or _derive_session_id(session)
    return {
        "session_id": sid,
        "session_name": session.get("session_name", sid),
        "profile": session.get("project", {}).get("profile"),
        "source_mode": session.get("project", {}).get("source_mode"),
        "file_name": file_name,
        "tags": list(tags or []),
        "entry_metadata": deepcopy(entry_metadata or {}),
        "session": deepcopy(session),
    }


def add_session_to_workspace(
    project_index: dict,
    session: dict,
    session_id: Optional[str] = None,
    file_name: Optional[str] = None,
    tags: Optional[list[str]] = None,
    entry_metadata: Optional[dict] = None,
    branch_name: Optional[str] = None,
) -> dict:
    new_project = ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index))))))))))))))
    target_branch = branch_name or new_project.get("active_branch_name") or "main"
    if target_branch not in new_project.get("branches", {}):
        new_project["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(new_project["branches"]),
        }

    meta = deepcopy(entry_metadata or {})
    branching = deepcopy(meta.get("branching", {}))
    branching["branch_name"] = target_branch

    if branching.get("parent_session_ids") is None:
        merge_info = meta.get("merge_commit", {}) or {}
        parents = [sid for sid in [merge_info.get("base_session_id"), merge_info.get("left_session_id"), merge_info.get("right_session_id")] if sid]
        if not parents:
            head = new_project["branches"][target_branch].get("head_session_id")
            parents = [head] if head else []
        branching["parent_session_ids"] = list(dict.fromkeys(parents))

    if not branching.get("lineage_kind"):
        if meta.get("commit_kind") == "merge_commit" or len(branching["parent_session_ids"]) > 1:
            branching["lineage_kind"] = "merge_commit"
        elif not branching["parent_session_ids"]:
            branching["lineage_kind"] = "root"
        else:
            branching["lineage_kind"] = "commit"
    meta["branching"] = branching

    entry = make_project_entry(session=session, session_id=session_id, file_name=file_name, tags=tags, entry_metadata=meta)
    existing = {item["session_id"] for item in new_project.get("sessions", [])}
    base_id = entry["session_id"]
    if base_id in existing:
        n = 2
        while f"{base_id}_{n}" in existing:
            n += 1
        entry["session_id"] = f"{base_id}_{n}"

    new_project.setdefault("sessions", []).append(entry)
    new_project["active_branch_name"] = target_branch
    new_project["branches"][target_branch]["manual_head_session_id"] = entry["session_id"]
    new_project["branches"][target_branch]["head_session_id"] = entry["session_id"]

    if not new_project.get("active_session_id"):
        new_project["active_session_id"] = entry["session_id"]
        new_project = append_history_event(
            new_project,
            "active_session_set",
            f"Active session set: {entry['session_name']}",
            session_id=entry["session_id"],
            session_name=entry["session_name"],
        )
    new_project = append_history_event(
        new_project,
        "session_added",
        f"Session added: {entry['session_name']}",
        session_id=entry["session_id"],
        session_name=entry["session_name"],
        payload={"profile": entry.get("profile"), "source_mode": entry.get("source_mode"), "branch_name": target_branch},
    )
    return ensure_tag_point_state(ensure_branching_state(new_project))


def set_active_session(project_index: dict, session_id: str) -> dict:
    project_index = ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index))))))))))))))
    ids = {item["session_id"] for item in project_index.get("sessions", [])}
    if session_id not in ids:
        raise ProjectModelError(f"Unknown session_id: {session_id}")
    out = deepcopy(project_index)
    previous = out.get("active_session_id")
    out["active_session_id"] = session_id
    active = next((item for item in out.get("sessions", []) if item["session_id"] == session_id), None)
    if active:
        out["active_branch_name"] = active.get("entry_metadata", {}).get("branching", {}).get("branch_name", out.get("active_branch_name", "main"))
    if previous != session_id:
        out = append_history_event(
            out,
            "active_session_switched",
            f"Active session switched: {active.get('session_name', session_id) if active else session_id}",
            session_id=session_id,
            session_name=active.get("session_name") if active else session_id,
            payload={"previous_session_id": previous, "branch_name": out.get("active_branch_name")},
        )
    return ensure_tag_point_state(ensure_branching_state(out))


def create_branch_from_session(project_index: dict, source_session_id: str, branch_name: str) -> dict:
    out = create_named_branch(project_index, source_session_id, branch_name)
    source = next((item for item in out.get("sessions", []) if item["session_id"] == source_session_id), None)
    out = append_history_event(
        out,
        "branch_created",
        f"Branch created: {branch_name}",
        session_id=source_session_id,
        session_name=source.get("session_name") if source else source_session_id,
        payload={"branch_name": branch_name},
    )
    return ensure_tag_point_state(ensure_branching_state(out))


def create_tag_release_in_project(project_index: dict, tag_name: str, target_session_id: str, point_kind: str = "tag", note: Optional[str] = None) -> tuple[dict, dict]:
    updated, result = create_tag_release_point(project_index, tag_name=tag_name, target_session_id=target_session_id, point_kind=point_kind, note=note)
    return ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))), result


def create_snapshot_export_in_project(
    project_index: dict,
    source_point_name: str,
    snapshot_name: Optional[str] = None,
    note: Optional[str] = None,
) -> tuple[dict, dict, dict]:
    updated, result, package = create_immutable_snapshot_export(
        project_index=project_index,
        source_point_name=source_point_name,
        snapshot_name=snapshot_name,
        note=note,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result, package


def create_snapshot_restore_in_project(
    snapshot_package: dict,
    restored_project_name: Optional[str] = None,
    restore_name: Optional[str] = None,
    activate_anchor: bool = True,
) -> tuple[dict, dict]:
    updated, result = restore_workspace_from_snapshot_export(
        snapshot_package=snapshot_package,
        restored_project_name=restored_project_name,
        restore_name=restore_name,
        activate_anchor=activate_anchor,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result


def create_snapshot_restore_preview(
    current_project_index: dict,
    snapshot_package: dict,
    restored_project_name: Optional[str] = None,
    activate_anchor: bool = True,
) -> dict:
    return preview_snapshot_restore_before_apply(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        restored_project_name=restored_project_name,
        activate_anchor=activate_anchor,
    )


def create_partial_snapshot_import_in_project(
    current_project_index: dict,
    snapshot_package: dict,
    import_name: Optional[str] = None,
    selected_session_ids: Optional[list[str]] = None,
    selected_tag_point_names: Optional[list[str]] = None,
    selected_snapshot_export_names: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    updated, result = import_selective_snapshot_state(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        import_name=import_name,
        selected_session_ids=selected_session_ids,
        selected_tag_point_names=selected_tag_point_names,
        selected_snapshot_export_names=selected_snapshot_export_names,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result


def create_snapshot_reconcile_in_project(
    current_project_index: dict,
    snapshot_package: dict,
    reconcile_name: Optional[str] = None,
    selected_session_ids: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    activate_last_reconciled: bool = True,
) -> tuple[dict, dict]:
    updated, result = reconcile_snapshot_state_with_current_lineage(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        reconcile_name=reconcile_name,
        selected_session_ids=selected_session_ids,
        target_branch_name=target_branch_name,
        activate_last_reconciled=activate_last_reconciled,
    )
    return ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated)))))), result


def create_snapshot_reconcile_preview(
    current_project_index: dict,
    snapshot_package: dict,
    selected_session_ids: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    reconcile_name: Optional[str] = None,
) -> dict:
    return preview_snapshot_reconcile_before_apply(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        selected_session_ids=selected_session_ids,
        target_branch_name=target_branch_name,
        reconcile_name=reconcile_name,
    )


def create_snapshot_reconcile_resolution_in_project(
    current_project_index: dict,
    snapshot_package: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: Optional[str] = None,
    selected_session_ids: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    activate_last_resolved: bool = True,
) -> tuple[dict, dict]:
    updated, result = resolve_snapshot_reconcile_conflicts_with_decisions(
        current_project_index=current_project_index,
        snapshot_package=snapshot_package,
        decisions=decisions,
        resolution_name=resolution_name,
        selected_session_ids=selected_session_ids,
        target_branch_name=target_branch_name,
        activate_last_resolved=activate_last_resolved,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result


def create_snapshot_reconcile_commit_in_project(
    project_index: dict,
    snapshot_reconcile_resolution_result: dict,
    commit_name: Optional[str] = None,
    promote_point_name: Optional[str] = None,
    promote_point_kind: str = "release",
    note: Optional[str] = None,
) -> tuple[dict, dict]:
    updated, result = commit_snapshot_reconcile_resolution_set(
        project_index=project_index,
        snapshot_reconcile_resolution_result=snapshot_reconcile_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result


def compare_snapshot_reconcile_commit_sets(
    project_index: dict,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    return compare_promoted_reconcile_outcomes(
        project_index=project_index,
        left_commit_name=left_commit_name,
        right_commit_name=right_commit_name,
    )


def create_snapshot_reconcile_commit_package_export_in_project(
    project_index: dict,
    commit_name: str,
    package_name: Optional[str] = None,
    note: Optional[str] = None,
) -> tuple[dict, dict, dict]:
    updated, result, package = export_reconcile_commit_as_standalone_package(
        project_index=project_index,
        commit_name=commit_name,
        package_name=package_name,
        note=note,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result, package


def create_snapshot_reconcile_commit_package_import_in_project(
    current_project_index: dict,
    package: dict,
    import_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    updated, result = import_standalone_reconcile_outcome_package(
        current_project_index=current_project_index,
        package=package,
        import_name=import_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result


def create_snapshot_reconcile_commit_package_import_preview_in_project(
    current_project_index: dict,
    package: dict,
    import_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> dict:
    return preview_standalone_reconcile_outcome_package_import(
        current_project_index=current_project_index,
        package=package,
        import_name=import_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )


def create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index: dict,
    package: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    updated, result = resolve_standalone_reconcile_outcome_package_import_with_decisions(
        current_project_index=current_project_index,
        package=package,
        decisions=decisions,
        resolution_name=resolution_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result



def create_snapshot_reconcile_commit_package_import_commit_in_project(
    project_index: dict,
    snapshot_reconcile_commit_package_resolution_result: dict,
    commit_name: Optional[str] = None,
    promote_point_name: Optional[str] = None,
    promote_point_kind: str = "release",
    note: Optional[str] = None,
) -> tuple[dict, dict]:
    updated, result = commit_standalone_reconcile_outcome_package_import_resolution(
        project_index=project_index,
        snapshot_reconcile_commit_package_resolution_result=snapshot_reconcile_commit_package_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))), result





def commit_imported_resolution_into_local_outcome_set_in_project(
    current_project_index: dict,
    package_resolution_result: dict,
    commit_name: Optional[str] = None,
    promote_point_name: Optional[str] = None,
    promote_point_kind: Optional[str] = None,
    note: Optional[str] = None,
) -> tuple[dict, dict]:
    updated, result = commit_standalone_reconcile_outcome_package_import_resolution(
        project_index=current_project_index,
        snapshot_reconcile_commit_package_resolution_result=package_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind or "release",
        note=note,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(updated), result


def resolve_snapshot_reconcile_commit_package_conflicts_in_project(
    current_project_index: dict,
    package_data: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: Optional[str] = None,
    selected_session_ids: Optional[list[str]] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    # selected_session_ids is accepted for API symmetry; v0.1 package-resolution resolves packaged sessions as a set.
    updated, result = resolve_standalone_reconcile_outcome_package_import_with_decisions(
        current_project_index=current_project_index,
        package=package_data,
        decisions=decisions,
        resolution_name=resolution_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    return ensure_snapshot_reconcile_commit_package_commit_state(updated), result


def compare_local_outcome_sets_in_project(
    project_index: dict,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    return compare_local_outcome_sets(
        project_index=project_index,
        left_commit_name=left_commit_name,
        right_commit_name=right_commit_name,
    )



def create_local_outcome_set_package_export_in_project(
    project_index: dict,
    commit_name: str,
    package_name: Optional[str] = None,
    note: Optional[str] = None,
) -> tuple[dict, dict, dict]:
    updated, result, package = export_local_outcome_set_as_portable_package(
        project_index=project_index,
        commit_name=commit_name,
        package_name=package_name,
        note=note,
    )
    return ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))))), result, package


def create_local_outcome_set_package_import_in_project(
    current_project_index: dict,
    package: dict,
    import_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    updated, result = import_local_outcome_set_portable_package(
        current_project_index=current_project_index,
        package=package,
        import_name=import_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    return ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))))), result



def preview_local_outcome_set_package_before_import_in_project(
    current_project_index: dict,
    package_data: dict,
    import_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
) -> dict:
    return preview_portable_local_outcome_package_before_import(
        current_project_index=current_project_index,
        package_data=package_data,
        import_name=import_name,
        target_branch_name=target_branch_name,
    )


def create_local_outcome_set_package_import_resolution_in_project(
    current_project_index: dict,
    package_data: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    updated, result = resolve_portable_local_outcome_package_import_with_decisions(
        current_project_index=current_project_index,
        package_data=package_data,
        decisions=decisions,
        resolution_name=resolution_name,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    return ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))))))))))), result



def create_local_outcome_set_package_import_commit_in_project(
    project_index: dict,
    local_outcome_set_package_resolution_result: dict,
    commit_name: Optional[str] = None,
    promote_point_name: Optional[str] = None,
    promote_point_kind: str = "release",
    note: Optional[str] = None,
) -> tuple[dict, dict]:
    updated, result = commit_portable_local_outcome_package_import_resolution(
        project_index=project_index,
        local_outcome_set_package_resolution_result=local_outcome_set_package_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    return ensure_local_outcome_set_package_commit_state(ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated)))))))))))))), result



def compare_portable_local_outcome_package_commits_in_project(
    project_index: dict,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    return compare_portable_local_outcome_package_commits(
        project_index=project_index,
        left_commit_name=left_commit_name,
        right_commit_name=right_commit_name,
    )



def compare_baseline_or_three_way_portable_local_outcomes_in_project(
    project_index: dict,
    base_commit_name: str,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    return compare_baseline_or_three_way_merge_portable_local_outcome_package_commits(
        project_index=project_index,
        base_commit_name=base_commit_name,
        left_commit_name=left_commit_name,
        right_commit_name=right_commit_name,
    )



def create_portable_local_outcome_package_three_way_merge_resolution_in_project(
    project_index: dict,
    merge_result: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: Optional[str] = None,
    target_branch_name: Optional[str] = None,
    activate_last_resolved: bool = True,
) -> tuple[dict, dict]:
    updated, result = resolve_portable_local_outcome_package_three_way_conflicts_with_decisions(
        project_index=project_index,
        merge_result=merge_result,
        decisions=decisions,
        resolution_name=resolution_name,
        target_branch_name=target_branch_name,
        activate_last_resolved=activate_last_resolved,
    )
    return ensure_portable_local_outcome_package_merge_resolution_state(updated), result


def create_portable_local_outcome_package_three_way_merge_commit_in_project(
    project_index: dict,
    merge_resolution_result: dict,
    commit_name: Optional[str] = None,
    promote_point_name: Optional[str] = None,
    promote_point_kind: str = "release",
    note: Optional[str] = None,
) -> tuple[dict, dict]:
    updated, result = commit_portable_local_outcome_package_three_way_merge_resolution(
        project_index=project_index,
        merge_resolution_result=merge_resolution_result,
        commit_name=commit_name,
        promote_point_name=promote_point_name,
        promote_point_kind=promote_point_kind,
        note=note,
    )
    return ensure_portable_local_outcome_package_merge_commit_state(
        ensure_portable_local_outcome_package_merge_resolution_state(updated)
    ), result


def get_active_session(project_index: dict) -> dict:
    active_id = project_index.get("active_session_id")
    for item in project_index.get("sessions", []):
        if item["session_id"] == active_id:
            return deepcopy(item["session"])
    raise ProjectModelError("Active session not found")


def workspace_summary(project_index: dict) -> list[dict]:
    project_index = ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(project_index)))))))))))))
    return [
        {
            "session_id": item["session_id"],
            "session_name": item["session_name"],
            "profile": item.get("profile"),
            "source_mode": item.get("source_mode"),
            "tags": item.get("tags", []),
            "file_name": item.get("file_name"),
            "entry_metadata": item.get("entry_metadata", {}),
            "branch_name": item.get("entry_metadata", {}).get("branching", {}).get("branch_name"),
            "is_active": item["session_id"] == project_index.get("active_session_id"),
        }
        for item in project_index.get("sessions", [])
    ]


def commit_merged_session_to_workspace(
    project_index: dict,
    merge_or_resolution_result: dict,
    session_id: Optional[str] = None,
    session_name: Optional[str] = None,
    activate: bool = True,
    tags: Optional[list[str]] = None,
    branch_name: Optional[str] = None,
) -> dict:
    project_index = ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index))))

    merged_session = merge_or_resolution_result.get("merged_session")
    if not merged_session:
        raise ProjectModelError("Merge commit requires finalized merged_session")

    committed_session = deepcopy(merged_session)
    if session_name:
        committed_session["session_name"] = session_name

    summary = merge_or_resolution_result.get("summary", {}) or {}
    base_session_id = merge_or_resolution_result.get("base_session_id")
    left_session_id = merge_or_resolution_result.get("left_session_id")
    right_session_id = merge_or_resolution_result.get("right_session_id")

    target_branch = branch_name or project_index.get("active_branch_name") or "main"

    commit_tags = list(tags or [])
    if "merge-commit" not in commit_tags:
        commit_tags.append("merge-commit")

    entry_metadata = {
        "commit_kind": "merge_commit",
        "merge_commit": {
            "base_session_id": base_session_id,
            "left_session_id": left_session_id,
            "right_session_id": right_session_id,
            "conflict_count": summary.get("conflict_count", 0),
            "resolved_count": summary.get("resolved_count"),
            "unresolved_count": summary.get("unresolved_count"),
            "finalized": summary.get("finalized", "merged_session" in merge_or_resolution_result),
        },
        "branching": {
            "branch_name": target_branch,
            "parent_session_ids": [sid for sid in [base_session_id, left_session_id, right_session_id] if sid],
            "lineage_kind": "merge_commit",
        },
    }

    updated = add_session_to_workspace(
        project_index=project_index,
        session=committed_session,
        session_id=session_id,
        file_name=None,
        tags=commit_tags,
        entry_metadata=entry_metadata,
        branch_name=target_branch,
    )
    committed_entry = updated["sessions"][-1]
    updated = append_history_event(
        updated,
        "merge_committed",
        f"Merge committed: {committed_entry['session_name']}",
        session_id=committed_entry["session_id"],
        session_name=committed_entry["session_name"],
        payload={
            "base_session_id": base_session_id,
            "left_session_id": left_session_id,
            "right_session_id": right_session_id,
            "conflict_count": summary.get("conflict_count", 0),
            "branch_name": target_branch,
        },
    )
    if activate:
        updated = set_active_session(updated, committed_entry["session_id"])
    return ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(updated))))


def workspace_to_inspector_payload(project_index: dict) -> dict:
    project_index = ensure_local_outcome_set_package_resolution_state(ensure_local_outcome_set_package_state(ensure_snapshot_reconcile_commit_package_commit_state(ensure_snapshot_reconcile_commit_package_resolution_state(ensure_snapshot_reconcile_commit_package_state(ensure_snapshot_reconcile_commit_state(ensure_snapshot_reconcile_resolution_state(ensure_snapshot_reconcile_state(ensure_partial_snapshot_import_state(ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index))))))))))))))
    active_session = get_active_session(project_index)
    payload = session_to_inspector_payload(active_session)
    payload["project_index"] = deepcopy(project_index)
    payload["workspace_summary"] = workspace_summary(project_index)
    payload["workspace_dependency_map"] = build_workspace_dependency_map(project_index)
    payload["workspace_timeline"] = build_workspace_timeline(project_index)
    payload["branch_summary"] = branch_summary(project_index)
    payload["workspace_lineage_graph"] = build_named_merge_lineage_graph(project_index)
    payload["tag_point_summary"] = tag_point_summary(project_index)
    payload["snapshot_export_summary"] = snapshot_export_summary(project_index)
    payload["snapshot_restore_summary"] = snapshot_restore_summary(project_index)
    payload["partial_snapshot_import_summary"] = partial_snapshot_import_summary(project_index)
    payload["snapshot_reconcile_summary"] = snapshot_reconcile_summary(project_index)
    payload["snapshot_reconcile_resolution_summary"] = snapshot_reconcile_resolution_summary(project_index)
    payload["snapshot_reconcile_commit_summary"] = snapshot_reconcile_commit_summary(project_index)
    payload["snapshot_reconcile_commit_package_summary"] = snapshot_reconcile_commit_package_summary(project_index)
    payload["snapshot_reconcile_commit_package_import_summary"] = snapshot_reconcile_commit_package_import_summary(project_index)
    payload["snapshot_reconcile_commit_package_resolution_summary"] = snapshot_reconcile_commit_package_resolution_summary(project_index)
    payload["local_outcome_set_package_summary"] = local_outcome_set_package_summary(project_index)
    payload["local_outcome_set_package_import_summary"] = local_outcome_set_package_import_summary(project_index)
    payload["local_outcome_set_package_resolution_summary"] = local_outcome_set_package_resolution_summary(project_index)
    payload["portable_local_outcome_package_merge_resolution_summary"] = portable_local_outcome_package_merge_resolution_summary(project_index)
    payload["portable_local_outcome_package_merge_commit_summary"] = portable_local_outcome_package_merge_commit_summary(project_index)
    payload["local_outcome_set_package_commit_summary"] = local_outcome_set_package_commit_summary(project_index)
    return payload


def save_project_index(project_index: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(project_index, ensure_ascii=False, indent=2), encoding="utf-8")


def load_project_index(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
```


## FILE: tooling/project_branching.py

Size: 9628 bytes

```file

from __future__ import annotations

from copy import deepcopy


def _find_entry(project_index: dict, session_id: str) -> dict | None:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    return None


def _branch_session_ids(project_index: dict, branch_name: str) -> list[str]:
    return [
        item["session_id"]
        for item in project_index.get("sessions", [])
        if item.get("entry_metadata", {}).get("branching", {}).get("branch_name") == branch_name
    ]


def ensure_branching_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("branches", {})
    out.setdefault("active_branch_name", "main")
    sessions = out.setdefault("sessions", [])

    if not out["branches"]:
        out["branches"]["main"] = {
            "branch_name": "main",
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": 0,
        }

    last_in_branch = {}
    for item in sessions:
        meta = item.setdefault("entry_metadata", {})
        branching = meta.setdefault("branching", {})

        branch_name = branching.get("branch_name") or out.get("active_branch_name") or "main"
        if branch_name not in out["branches"]:
            out["branches"][branch_name] = {
                "branch_name": branch_name,
                "root_session_id": None,
                "head_session_id": None,
                "manual_head_session_id": None,
                "color_index": len(out["branches"]),
            }
        branch = out["branches"][branch_name]

        parents = branching.get("parent_session_ids")
        if parents is None:
            merge_info = meta.get("merge_commit", {}) or {}
            derived = [sid for sid in [merge_info.get("base_session_id"), merge_info.get("left_session_id"), merge_info.get("right_session_id")] if sid]
            if not derived:
                prev = last_in_branch.get(branch_name)
                derived = [prev] if prev else []
            parents = list(dict.fromkeys(derived))
        branching["parent_session_ids"] = parents
        branching["branch_name"] = branch_name

        if not branching.get("lineage_kind"):
            commit_kind = meta.get("commit_kind")
            if commit_kind == "merge_commit" or len(parents) > 1:
                branching["lineage_kind"] = "merge_commit"
            elif commit_kind == "rebase_replay":
                branching["lineage_kind"] = "rebase_replay"
            elif commit_kind == "cherry_pick":
                branching["lineage_kind"] = "cherry_pick"
            elif commit_kind == "squash_fold":
                branching["lineage_kind"] = "squash_fold"
            elif commit_kind == "snapshot_partial_import":
                branching["lineage_kind"] = "snapshot_partial_import"
            elif commit_kind == "snapshot_reconcile":
                branching["lineage_kind"] = "snapshot_reconcile"
            elif commit_kind == "snapshot_reconcile_resolution":
                branching["lineage_kind"] = "snapshot_reconcile_resolution"
            elif commit_kind == "local_outcome_set_package_import":
                branching["lineage_kind"] = "local_outcome_set_package_import"
            elif commit_kind == "local_outcome_set_package_import_resolution":
                branching["lineage_kind"] = "local_outcome_set_package_import_resolution"
            elif not parents:
                branching["lineage_kind"] = "root"
            else:
                branching["lineage_kind"] = "commit"

        branching["branch_order"] = branch["color_index"]

        if branch["root_session_id"] is None:
            branch["root_session_id"] = item["session_id"]
        branch["head_session_id"] = item["session_id"]
        last_in_branch[branch_name] = item["session_id"]

    # Respect manual head overrides when valid for the branch.
    for branch_name, branch in out.get("branches", {}).items():
        valid_session_ids = set(_branch_session_ids(out, branch_name))
        manual_head = branch.get("manual_head_session_id")
        if manual_head and manual_head in valid_session_ids:
            branch["head_session_id"] = manual_head
        elif manual_head and manual_head not in valid_session_ids:
            branch["manual_head_session_id"] = None

    active = _find_entry(out, out.get("active_session_id"))
    if active:
        out["active_branch_name"] = active.get("entry_metadata", {}).get("branching", {}).get("branch_name", out.get("active_branch_name", "main"))

    return out


def branch_summary(project_index: dict) -> list[dict]:
    project_index = ensure_branching_state(project_index)
    out = []
    for branch_name, branch in project_index.get("branches", {}).items():
        count = 0
        for item in project_index.get("sessions", []):
            if item.get("entry_metadata", {}).get("branching", {}).get("branch_name") == branch_name:
                count += 1
        out.append({
            "branch_name": branch_name,
            "root_session_id": branch.get("root_session_id"),
            "head_session_id": branch.get("head_session_id"),
            "manual_head_session_id": branch.get("manual_head_session_id"),
            "is_active_branch": branch_name == project_index.get("active_branch_name"),
            "session_count": count,
            "color_index": branch.get("color_index", 0),
        })
    out.sort(key=lambda x: (x["color_index"], x["branch_name"]))
    return out


def create_named_branch(project_index: dict, source_session_id: str, branch_name: str) -> dict:
    if not branch_name or not branch_name.strip():
        raise ValueError("branch_name is required")
    project_index = ensure_branching_state(project_index)
    if branch_name in project_index.get("branches", {}):
        raise ValueError(f"Branch already exists: {branch_name}")
    source_entry = _find_entry(project_index, source_session_id)
    if not source_entry:
        raise ValueError(f"Unknown source_session_id: {source_session_id}")

    out = deepcopy(project_index)
    out["branches"][branch_name] = {
        "branch_name": branch_name,
        "root_session_id": source_session_id,
        "head_session_id": source_session_id,
        "manual_head_session_id": source_session_id,
        "color_index": len(out["branches"]),
    }
    out["active_branch_name"] = branch_name
    return out


def build_named_merge_lineage_graph(project_index: dict) -> dict:
    project_index = ensure_branching_state(project_index)
    summary = branch_summary(project_index)
    branch_order = {item["branch_name"]: idx for idx, item in enumerate(summary)}
    head_by_branch = {item["branch_name"]: item["head_session_id"] for item in summary}
    branch_rows = {}

    nodes = []
    for item in project_index.get("sessions", []):
        meta = item.get("entry_metadata", {})
        branching = meta.get("branching", {})
        branch_name = branching.get("branch_name", "main")
        row = branch_rows.get(branch_name, 0)
        branch_rows[branch_name] = row + 1

        x = 120 + branch_order.get(branch_name, 0) * 240
        y = 70 + row * 115

        attached_points = []
        for point_name, point in (project_index.get("tag_points") or {}).items():
            if point.get("target_session_id") == item["session_id"]:
                attached_points.append({"tag_name": point_name, "point_kind": point.get("point_kind", "tag")})

        nodes.append({
            "session_id": item["session_id"],
            "session_name": item["session_name"],
            "branch_name": branch_name,
            "lineage_kind": branching.get("lineage_kind", "commit"),
            "tags": item.get("tags", []),
            "is_active": item["session_id"] == project_index.get("active_session_id"),
            "is_branch_head": item["session_id"] == head_by_branch.get(branch_name),
            "attached_points": attached_points,
            "x": x,
            "y": y,
        })

    edges = []
    for item in project_index.get("sessions", []):
        meta = item.get("entry_metadata", {})
        branching = meta.get("branching", {})
        parents = branching.get("parent_session_ids", []) or []
        relation = "merge_parent" if len(parents) > 1 or branching.get("lineage_kind") == "merge_commit" else "parent"
        for parent_id in parents:
            edges.append({
                "from_session_id": parent_id,
                "to_session_id": item["session_id"],
                "relation": relation,
                "branch_name": branching.get("branch_name", "main"),
            })

        squash_info = meta.get("squash_fold", {}) or {}
        for source_session_id in squash_info.get("source_session_ids", []) or []:
            edges.append({
                "from_session_id": source_session_id,
                "to_session_id": item["session_id"],
                "relation": "squash_origin",
                "branch_name": branching.get("branch_name", "main"),
            })

    return {
        "lineage_graph_version": "SEMASCRIPT_NAMED_MERGE_LINEAGE_GRAPH_v0.1",
        "project_name": project_index.get("project_name"),
        "active_session_id": project_index.get("active_session_id"),
        "active_branch_name": project_index.get("active_branch_name"),
        "branches": summary,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "branch_count": len(summary),
            "session_count": len(nodes),
            "edge_count": len(edges),
        },
    }
```


## FILE: tooling/project_snapshot.py

Size: 5775 bytes

```file

from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state, branch_summary, build_named_merge_lineage_graph
from project_tags import ensure_tag_point_state, tag_point_summary
from workspace_navigation import build_workspace_dependency_map
from workspace_timeline import ensure_workspace_history, append_history_event, build_workspace_timeline


class ProjectSnapshotError(Exception):
    """Raised when immutable workspace snapshot export is invalid."""


def ensure_snapshot_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_exports", {})
    return out


def snapshot_export_summary(project_index: dict) -> list[dict]:
    project_index = ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index))))
    out = []
    for snapshot_name, package in (project_index.get("snapshot_exports") or {}).items():
        out.append({
            "snapshot_name": snapshot_name,
            "source_point_name": package.get("source_point_name"),
            "source_point_kind": package.get("source_point_kind"),
            "target_session_id": package.get("target_session_id"),
            "branch_name": package.get("anchor", {}).get("branch_name"),
            "is_release": package.get("source_point_kind") == "release",
            "note": package.get("note"),
        })
    out.sort(key=lambda x: (x["source_point_kind"], x["snapshot_name"]))
    return out


def _workspace_summary_min(project_index: dict) -> list[dict]:
    return [
        {
            "session_id": item["session_id"],
            "session_name": item["session_name"],
            "profile": item.get("profile"),
            "source_mode": item.get("source_mode"),
            "branch_name": item.get("entry_metadata", {}).get("branching", {}).get("branch_name"),
            "tags": item.get("tags", []),
            "is_active": item["session_id"] == project_index.get("active_session_id"),
        }
        for item in project_index.get("sessions", [])
    ]


def _frozen_project_index(project_index: dict) -> dict:
    frozen = deepcopy(project_index)
    frozen.pop("snapshot_exports", None)
    return frozen


def create_immutable_snapshot_export(
    project_index: dict,
    source_point_name: str,
    snapshot_name: str | None = None,
    note: str | None = None,
) -> tuple[dict, dict, dict]:
    project_index = ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index))))

    point = (project_index.get("tag_points") or {}).get(source_point_name)
    if not point:
        raise ProjectSnapshotError(f"Unknown source_point_name: {source_point_name}")

    resolved_snapshot_name = (snapshot_name or f"{source_point_name}_snapshot").strip()
    if not resolved_snapshot_name:
        raise ProjectSnapshotError("snapshot_name is required")
    if resolved_snapshot_name in project_index.get("snapshot_exports", {}):
        raise ProjectSnapshotError(f"Snapshot export already exists: {resolved_snapshot_name}")

    frozen_project = _frozen_project_index(project_index)
    package = {
        "snapshot_version": "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1",
        "snapshot_name": resolved_snapshot_name,
        "project_name": project_index.get("project_name"),
        "source_point_name": source_point_name,
        "source_point_kind": point.get("point_kind", "tag"),
        "target_session_id": point.get("target_session_id"),
        "target_session_name": point.get("target_session_name"),
        "note": note.strip() if isinstance(note, str) and note.strip() else point.get("note"),
        "immutability": {
            "frozen": True,
            "mutable": False,
            "source": "tag_release_point",
        },
        "anchor": deepcopy(point),
        "export_state": {
            "active_session_id": project_index.get("active_session_id"),
            "active_branch_name": project_index.get("active_branch_name"),
            "workspace_summary": _workspace_summary_min(project_index),
            "branch_summary": branch_summary(project_index),
            "lineage_graph": build_named_merge_lineage_graph(project_index),
            "dependency_map": build_workspace_dependency_map(project_index),
            "timeline": build_workspace_timeline(project_index),
            "tag_point_summary": tag_point_summary(project_index),
            "project_index_frozen": frozen_project,
        },
    }

    out = deepcopy(project_index)
    out.setdefault("snapshot_exports", {})[resolved_snapshot_name] = package
    out = append_history_event(
        out,
        "snapshot_exported",
        f"Snapshot exported: {resolved_snapshot_name}",
        session_id=point.get("target_session_id"),
        session_name=point.get("target_session_name"),
        payload={
            "snapshot_name": resolved_snapshot_name,
            "source_point_name": source_point_name,
            "source_point_kind": point.get("point_kind", "tag"),
            "branch_name": point.get("branch_name"),
        },
    )

    result = {
        "snapshot_export_version": "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1",
        "project_name": out.get("project_name"),
        "snapshot_name": resolved_snapshot_name,
        "source_point_name": source_point_name,
        "source_point_kind": point.get("point_kind", "tag"),
        "target_session_id": point.get("target_session_id"),
        "summary": {
            "created": True,
            "immutable": True,
            "is_release_source": point.get("point_kind") == "release",
        },
    }
    return ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(out))), result, package
```


## FILE: tooling/project_snapshot_reconcile.py

Size: 11477 bytes

```file

from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectSnapshotReconcileError(Exception):
    """Raised when snapshot merge / reconcile with current lineage is invalid."""


def ensure_snapshot_reconcile_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_reconciles", {})
    return out


def snapshot_reconcile_summary(project_index: dict) -> list[dict]:
    project_index = ensure_snapshot_reconcile_state(
        ensure_partial_snapshot_import_state(
            ensure_snapshot_restore_state(
                ensure_snapshot_state(
                    ensure_tag_point_state(
                        ensure_branching_state(
                            ensure_workspace_history(project_index)
                        )
                    )
                )
            )
        )
    )
    out = []
    for reconcile_name, entry in (project_index.get("snapshot_reconciles") or {}).items():
        out.append({
            "reconcile_name": reconcile_name,
            "snapshot_name": entry.get("snapshot_name"),
            "source_point_name": entry.get("source_point_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "reconciled_session_count": len(entry.get("reconciled_session_ids") or []),
            "conflict_like_count": entry.get("conflict_like_count", 0),
        })
    out.sort(key=lambda x: x["reconcile_name"])
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_snapshot_reconcile_state(
        ensure_partial_snapshot_import_state(
            ensure_snapshot_restore_state(
                ensure_snapshot_state(
                    ensure_tag_point_state(
                        ensure_branching_state(
                            ensure_workspace_history(deepcopy(project_index))
                        )
                    )
                )
            )
        )
    )


def _derive_unique_name(existing: set[str], base: str, suffix: str) -> str:
    candidate = f"{base}{suffix}"
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    n = 2
    while f"{candidate}_{n}" in existing:
        n += 1
    resolved = f"{candidate}_{n}"
    existing.add(resolved)
    return resolved


def _session_entry_by_id(project_index: dict, session_id: str) -> dict:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    raise ProjectSnapshotReconcileError(f"Unknown snapshot session_id: {session_id}")


def reconcile_snapshot_state_with_current_lineage(
    current_project_index: dict,
    snapshot_package: dict,
    reconcile_name: str | None = None,
    selected_session_ids: list[str] | None = None,
    target_branch_name: str | None = None,
    activate_last_reconciled: bool = True,
) -> tuple[dict, dict]:
    if not isinstance(snapshot_package, dict):
        raise ProjectSnapshotReconcileError("snapshot_package must be an object")
    if snapshot_package.get("snapshot_version") != "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1":
        raise ProjectSnapshotReconcileError("Unsupported or missing snapshot_version")

    export_state = snapshot_package.get("export_state") or {}
    frozen_project = export_state.get("project_index_frozen")
    if not isinstance(frozen_project, dict):
        raise ProjectSnapshotReconcileError("snapshot export_state.project_index_frozen is missing")

    current = _normalize(current_project_index)
    snapshot_project = _normalize(frozen_project)
    anchor = deepcopy(snapshot_package.get("anchor") or {})

    session_ids = [item.strip() for item in (selected_session_ids or []) if str(item).strip()]
    if not session_ids:
        raise ProjectSnapshotReconcileError("At least one selected_session_id is required")

    resolved_reconcile_name = (reconcile_name or f"{snapshot_package.get('snapshot_name', 'snapshot')}_reconcile").strip()
    if not resolved_reconcile_name:
        raise ProjectSnapshotReconcileError("reconcile_name is required")
    if resolved_reconcile_name in current.get("snapshot_reconciles", {}):
        raise ProjectSnapshotReconcileError(f"Snapshot reconcile already exists: {resolved_reconcile_name}")

    out = deepcopy(current)
    target_branch = (target_branch_name or anchor.get("branch_name") or out.get("active_branch_name") or "main").strip()
    if target_branch not in out.get("branches", {}):
        out["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(out["branches"]),
        }

    existing_session_ids = {item["session_id"] for item in out.get("sessions", [])}
    previous_parent = out["branches"].get(target_branch, {}).get("head_session_id")

    reconciled_session_ids: list[str] = []
    reconcile_pairs: list[dict] = []
    conflict_like_count = 0

    for idx, original_session_id in enumerate(session_ids, start=1):
        source_entry = _session_entry_by_id(snapshot_project, original_session_id)
        current_head_entry = next((item for item in out.get("sessions", []) if item["session_id"] == previous_parent), None)

        source_branch_name = source_entry.get("entry_metadata", {}).get("branching", {}).get("branch_name")
        source_text = source_entry.get("session", {}).get("project", {}).get("source_text")
        head_text = current_head_entry.get("session", {}).get("project", {}).get("source_text") if current_head_entry else None
        source_profile = source_entry.get("profile")
        head_profile = current_head_entry.get("profile") if current_head_entry else None

        same_source_as_head = bool(source_text is not None and head_text is not None and source_text == head_text)
        same_profile_as_head = bool(source_profile is not None and head_profile is not None and source_profile == head_profile)
        conflict_like = current_head_entry is not None and not same_source_as_head
        if conflict_like:
            conflict_like_count += 1

        new_session_id = _derive_unique_name(existing_session_ids, original_session_id, "_reconcile")

        session_copy = deepcopy(source_entry["session"])
        entry_metadata = deepcopy(source_entry.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "snapshot_reconcile"
        entry_metadata["snapshot_reconcile"] = {
            "reconcile_name": resolved_reconcile_name,
            "source_snapshot_name": snapshot_package.get("snapshot_name"),
            "source_point_name": snapshot_package.get("source_point_name"),
            "original_session_id": original_session_id,
            "source_branch_name": source_branch_name,
            "target_branch_name": target_branch,
            "reconciled_with_head_session_id": previous_parent,
            "reconcile_index": idx,
            "same_source_as_head": same_source_as_head,
            "same_profile_as_head": same_profile_as_head,
            "conflict_like": conflict_like,
        }
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "snapshot_reconcile",
        }

        entry = {
            "session_id": new_session_id,
            "session_name": source_entry.get("session_name"),
            "profile": source_entry.get("profile"),
            "source_mode": source_entry.get("source_mode"),
            "file_name": None,
            "tags": list(dict.fromkeys(list(source_entry.get("tags", [])) + ["snapshot-reconcile"])),
            "entry_metadata": entry_metadata,
            "session": session_copy,
        }
        out.setdefault("sessions", []).append(entry)
        if out["branches"][target_branch].get("root_session_id") is None:
            out["branches"][target_branch]["root_session_id"] = new_session_id
        out["branches"][target_branch]["head_session_id"] = new_session_id
        out["branches"][target_branch]["manual_head_session_id"] = new_session_id
        out["active_branch_name"] = target_branch

        reconcile_pairs.append({
            "original_session_id": original_session_id,
            "reconciled_session_id": new_session_id,
            "reconciled_with_head_session_id": previous_parent,
            "same_source_as_head": same_source_as_head,
            "same_profile_as_head": same_profile_as_head,
            "conflict_like": conflict_like,
        })

        previous_parent = new_session_id
        reconciled_session_ids.append(new_session_id)

    if activate_last_reconciled and reconciled_session_ids:
        out["active_session_id"] = reconciled_session_ids[-1]
        out["active_branch_name"] = target_branch

    out.setdefault("snapshot_reconciles", {})[resolved_reconcile_name] = {
        "reconcile_name": resolved_reconcile_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "source_point_kind": snapshot_package.get("source_point_kind"),
        "target_branch_name": target_branch,
        "reconciled_session_ids": reconciled_session_ids,
        "reconcile_pairs": reconcile_pairs,
        "conflict_like_count": conflict_like_count,
    }

    history_session_id = reconciled_session_ids[-1] if reconciled_session_ids else anchor.get("target_session_id")
    history_session_name = None
    if history_session_id:
        match = next((item for item in out.get("sessions", []) if item["session_id"] == history_session_id), None)
        history_session_name = match.get("session_name") if match else None

    out = append_history_event(
        out,
        "snapshot_reconciled",
        f"Snapshot reconciled: {resolved_reconcile_name}",
        session_id=history_session_id,
        session_name=history_session_name,
        payload={
            "snapshot_name": snapshot_package.get("snapshot_name"),
            "source_point_name": snapshot_package.get("source_point_name"),
            "target_branch_name": target_branch,
            "reconciled_session_count": len(reconciled_session_ids),
            "conflict_like_count": conflict_like_count,
        },
    )

    result = {
        "snapshot_reconcile_version": "SEMASCRIPT_SNAPSHOT_MERGE_RECONCILE_v0.1",
        "reconcile_name": resolved_reconcile_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "target_branch_name": target_branch,
        "reconciled_session_ids": reconciled_session_ids,
        "reconcile_pairs": reconcile_pairs,
        "summary": {
            "reconciled_session_count": len(reconciled_session_ids),
            "conflict_like_count": conflict_like_count,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_snapshot_reconcile_commit.py

Size: 7898 bytes

```file

from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state, create_tag_release_point
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectSnapshotReconcileCommitError(Exception):
    """Raised when snapshot reconcile commit / promote is invalid."""


def ensure_snapshot_reconcile_commit_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_reconcile_commits", {})
    return out


def snapshot_reconcile_commit_summary(project_index: dict) -> list[dict]:
    project_index = ensure_snapshot_reconcile_commit_state(
        ensure_snapshot_reconcile_resolution_state(
            ensure_snapshot_reconcile_state(
                ensure_partial_snapshot_import_state(
                    ensure_snapshot_restore_state(
                        ensure_snapshot_state(
                            ensure_tag_point_state(
                                ensure_branching_state(
                                    ensure_workspace_history(project_index)
                                )
                            )
                        )
                    )
                )
            )
        )
    )
    out = []
    for commit_name, entry in (project_index.get("snapshot_reconcile_commits") or {}).items():
        out.append({
            "commit_name": commit_name,
            "resolution_name": entry.get("resolution_name"),
            "snapshot_name": entry.get("snapshot_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "promoted_point_name": entry.get("promoted_point_name"),
            "promoted_point_kind": entry.get("promoted_point_kind"),
        })
    out.sort(key=lambda x: x["commit_name"])
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_snapshot_reconcile_commit_state(
        ensure_snapshot_reconcile_resolution_state(
            ensure_snapshot_reconcile_state(
                ensure_partial_snapshot_import_state(
                    ensure_snapshot_restore_state(
                        ensure_snapshot_state(
                            ensure_tag_point_state(
                                ensure_branching_state(
                                    ensure_workspace_history(deepcopy(project_index))
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def commit_snapshot_reconcile_resolution_set(
    project_index: dict,
    snapshot_reconcile_resolution_result: dict,
    commit_name: str | None = None,
    promote_point_name: str | None = None,
    promote_point_kind: str = "release",
    note: str | None = None,
) -> tuple[dict, dict]:
    project_index = _normalize(project_index)

    if not isinstance(snapshot_reconcile_resolution_result, dict):
        raise ProjectSnapshotReconcileCommitError("snapshot_reconcile_resolution_result must be an object")
    resolved_session_ids = list(snapshot_reconcile_resolution_result.get("resolved_session_ids") or [])
    if not resolved_session_ids:
        raise ProjectSnapshotReconcileCommitError("No resolved_session_ids to commit")

    resolved_commit_name = (commit_name or f"{snapshot_reconcile_resolution_result.get('resolution_name', 'reconcile_resolution')}_commit").strip()
    if not resolved_commit_name:
        raise ProjectSnapshotReconcileCommitError("commit_name is required")
    if resolved_commit_name in project_index.get("snapshot_reconcile_commits", {}):
        raise ProjectSnapshotReconcileCommitError(f"Snapshot reconcile commit already exists: {resolved_commit_name}")

    out = deepcopy(project_index)
    last_resolved_session_id = resolved_session_ids[-1]
    last_entry = next((item for item in out.get("sessions", []) if item["session_id"] == last_resolved_session_id), None)
    if not last_entry:
        raise ProjectSnapshotReconcileCommitError(f"Resolved session not found in project: {last_resolved_session_id}")

    promoted_point_result = None
    promoted_point_name_resolved = None
    promoted_point_kind_resolved = None
    if promote_point_name and promote_point_name.strip():
        promoted_point_name_resolved = promote_point_name.strip()
        promoted_point_kind_resolved = (promote_point_kind or "release").strip() or "release"
        out, promoted_point_result = create_tag_release_point(
            out,
            tag_name=promoted_point_name_resolved,
            target_session_id=last_resolved_session_id,
            point_kind=promoted_point_kind_resolved,
            note=note,
        )

    out.setdefault("snapshot_reconcile_commits", {})[resolved_commit_name] = {
        "commit_name": resolved_commit_name,
        "resolution_name": snapshot_reconcile_resolution_result.get("resolution_name"),
        "snapshot_name": snapshot_reconcile_resolution_result.get("snapshot_name"),
        "source_point_name": snapshot_reconcile_resolution_result.get("source_point_name"),
        "target_branch_name": snapshot_reconcile_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": list(snapshot_reconcile_resolution_result.get("skipped_session_ids") or []),
        "resolution_pairs": deepcopy(snapshot_reconcile_resolution_result.get("resolution_pairs") or []),
        "promoted_point_name": promoted_point_name_resolved,
        "promoted_point_kind": promoted_point_kind_resolved,
        "note": note.strip() if isinstance(note, str) and note.strip() else None,
    }

    out = append_history_event(
        out,
        "snapshot_reconcile_committed",
        f"Snapshot reconcile committed: {resolved_commit_name}",
        session_id=last_resolved_session_id,
        session_name=last_entry.get("session_name"),
        payload={
            "commit_name": resolved_commit_name,
            "resolution_name": snapshot_reconcile_resolution_result.get("resolution_name"),
            "snapshot_name": snapshot_reconcile_resolution_result.get("snapshot_name"),
            "target_branch_name": snapshot_reconcile_resolution_result.get("target_branch_name"),
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
        },
    )

    result = {
        "snapshot_reconcile_commit_version": "SEMASCRIPT_SNAPSHOT_RECONCILE_COMMIT_PROMOTE_v0.1",
        "commit_name": resolved_commit_name,
        "resolution_name": snapshot_reconcile_resolution_result.get("resolution_name"),
        "snapshot_name": snapshot_reconcile_resolution_result.get("snapshot_name"),
        "target_branch_name": snapshot_reconcile_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "promoted_point_result": promoted_point_result,
        "summary": {
            "committed": True,
            "resolved_session_count": len(resolved_session_ids),
            "promoted": promoted_point_result is not None,
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_snapshot_reconcile_commit_package.py

Size: 16863 bytes

```file

from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state, create_tag_release_point
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectSnapshotReconcileCommitPackageError(Exception):
    """Raised when standalone promoted outcome package export/import is invalid."""


def ensure_snapshot_reconcile_commit_package_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_reconcile_commit_packages", {})
    out.setdefault("snapshot_reconcile_commit_package_imports", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_snapshot_reconcile_commit_package_state(
        ensure_snapshot_reconcile_commit_state(
            ensure_snapshot_reconcile_resolution_state(
                ensure_snapshot_reconcile_state(
                    ensure_partial_snapshot_import_state(
                        ensure_snapshot_restore_state(
                            ensure_snapshot_state(
                                ensure_tag_point_state(
                                    ensure_branching_state(
                                        ensure_workspace_history(deepcopy(project_index))
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def snapshot_reconcile_commit_package_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for package_name, entry in (project_index.get("snapshot_reconcile_commit_packages") or {}).items():
        out.append({
            "package_name": package_name,
            "commit_name": entry.get("commit_name"),
            "snapshot_name": entry.get("snapshot_name"),
            "resolution_name": entry.get("resolution_name"),
            "resolved_session_count": entry.get("resolved_session_count", 0),
            "promoted_point_name": entry.get("promoted_point_name"),
            "promoted_point_kind": entry.get("promoted_point_kind"),
        })
    out.sort(key=lambda x: x["package_name"])
    return out


def snapshot_reconcile_commit_package_import_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for import_name, entry in (project_index.get("snapshot_reconcile_commit_package_imports") or {}).items():
        out.append({
            "import_name": import_name,
            "package_name": entry.get("package_name"),
            "imported_commit_name": entry.get("imported_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "imported_session_count": entry.get("imported_session_count", 0),
            "imported_point_name": entry.get("imported_point_name"),
            "imported_point_kind": entry.get("imported_point_kind"),
        })
    out.sort(key=lambda x: x["import_name"])
    return out


def _commit_entry(project_index: dict, commit_name: str) -> dict:
    entry = (project_index.get("snapshot_reconcile_commits") or {}).get(commit_name)
    if not entry:
        raise ProjectSnapshotReconcileCommitPackageError(f"Unknown snapshot reconcile commit: {commit_name}")
    return entry


def _session_entry(project_index: dict, session_id: str) -> dict:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    raise ProjectSnapshotReconcileCommitPackageError(f"Session not found: {session_id}")


def _unique_name(existing: set[str], base: str, suffix: str) -> str:
    candidate = f"{base}{suffix}"
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    n = 2
    while f"{candidate}_{n}" in existing:
        n += 1
    resolved = f"{candidate}_{n}"
    existing.add(resolved)
    return resolved


def export_reconcile_commit_as_standalone_package(
    project_index: dict,
    commit_name: str,
    package_name: str | None = None,
    note: str | None = None,
) -> tuple[dict, dict, dict]:
    project_index = _normalize(project_index)
    commit_entry = deepcopy(_commit_entry(project_index, commit_name))

    resolved_package_name = (package_name or f"{commit_name}_package").strip()
    if not resolved_package_name:
        raise ProjectSnapshotReconcileCommitPackageError("package_name is required")
    if resolved_package_name in (project_index.get("snapshot_reconcile_commit_packages") or {}):
        raise ProjectSnapshotReconcileCommitPackageError(f"Package already exists: {resolved_package_name}")

    resolved_sessions = []
    for sid in commit_entry.get("resolved_session_ids") or []:
        entry = _session_entry(project_index, sid)
        resolved_sessions.append({
            "session_id": entry["session_id"],
            "session_name": entry.get("session_name"),
            "profile": entry.get("profile"),
            "source_mode": entry.get("source_mode"),
            "tags": deepcopy(entry.get("tags", [])),
            "entry_metadata": deepcopy(entry.get("entry_metadata", {})),
            "session": deepcopy(entry.get("session", {})),
        })

    promoted_point = None
    promoted_point_name = commit_entry.get("promoted_point_name")
    if promoted_point_name:
        promoted_point = deepcopy((project_index.get("tag_points") or {}).get(promoted_point_name))

    package = {
        "resolution_set_package_version": "SEMASCRIPT_PROMOTED_RECONCILE_OUTCOME_PACKAGE_v0.1",
        "package_name": resolved_package_name,
        "exported_from_project_name": project_index.get("project_name"),
        "commit_name": commit_name,
        "note": note if note is not None else commit_entry.get("note"),
        "exported_commit": commit_entry,
        "resolved_sessions": resolved_sessions,
        "promoted_point": promoted_point,
        "immutability": {
            "portable": True,
            "standalone": True,
            "source": "snapshot_reconcile_commit",
        },
    }

    out = deepcopy(project_index)
    out.setdefault("snapshot_reconcile_commit_packages", {})[resolved_package_name] = {
        "package_name": resolved_package_name,
        "commit_name": commit_name,
        "snapshot_name": commit_entry.get("snapshot_name"),
        "resolution_name": commit_entry.get("resolution_name"),
        "resolved_session_count": len(commit_entry.get("resolved_session_ids") or []),
        "promoted_point_name": commit_entry.get("promoted_point_name"),
        "promoted_point_kind": commit_entry.get("promoted_point_kind"),
        "note": package.get("note"),
    }
    last_sid = (commit_entry.get("resolved_session_ids") or [None])[-1]
    last_name = None
    if last_sid:
        try:
            last_name = _session_entry(out, last_sid).get("session_name")
        except Exception:
            last_name = None
    out = append_history_event(
        out,
        "snapshot_reconcile_commit_package_exported",
        f"Standalone reconcile package exported: {resolved_package_name}",
        session_id=last_sid,
        session_name=last_name,
        payload={
            "package_name": resolved_package_name,
            "commit_name": commit_name,
            "snapshot_name": commit_entry.get("snapshot_name"),
        },
    )

    result = {
        "snapshot_reconcile_commit_package_export_version": "SEMASCRIPT_PROMOTED_RECONCILE_OUTCOME_PACKAGE_v0.1",
        "package_name": resolved_package_name,
        "commit_name": commit_name,
        "summary": {
            "resolved_session_count": len(commit_entry.get("resolved_session_ids") or []),
            "has_promoted_point": bool(promoted_point),
            "portable": True,
        },
    }
    return _normalize(out), result, package


def import_standalone_reconcile_outcome_package(
    current_project_index: dict,
    package: dict,
    import_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    current_project_index = _normalize(current_project_index)
    if not isinstance(package, dict):
        raise ProjectSnapshotReconcileCommitPackageError("package must be an object")
    if package.get("resolution_set_package_version") != "SEMASCRIPT_PROMOTED_RECONCILE_OUTCOME_PACKAGE_v0.1":
        raise ProjectSnapshotReconcileCommitPackageError("Unsupported or missing resolution_set_package_version")

    exported_commit = deepcopy(package.get("exported_commit") or {})
    resolved_sessions = list(package.get("resolved_sessions") or [])
    if not exported_commit or not resolved_sessions:
        raise ProjectSnapshotReconcileCommitPackageError("Package is missing exported_commit or resolved_sessions")

    resolved_import_name = (import_name or f"{package.get('package_name', 'package')}_import").strip()
    if not resolved_import_name:
        raise ProjectSnapshotReconcileCommitPackageError("import_name is required")
    if resolved_import_name in (current_project_index.get("snapshot_reconcile_commit_package_imports") or {}):
        raise ProjectSnapshotReconcileCommitPackageError(f"Package import already exists: {resolved_import_name}")

    out = deepcopy(current_project_index)
    target_branch = (target_branch_name or exported_commit.get("target_branch_name") or out.get("active_branch_name") or "main").strip()
    if target_branch not in out.get("branches", {}):
        out["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(out["branches"]),
        }

    existing_session_ids = {item["session_id"] for item in out.get("sessions", [])}
    previous_parent = out["branches"].get(target_branch, {}).get("head_session_id")
    id_map = {}

    for idx, packaged in enumerate(resolved_sessions, start=1):
        original_session_id = packaged["session_id"]
        new_session_id = _unique_name(existing_session_ids, original_session_id, "_pkg")
        entry_metadata = deepcopy(packaged.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "snapshot_reconcile_commit_package_import"
        entry_metadata["snapshot_reconcile_commit_package_import"] = {
            "import_name": resolved_import_name,
            "package_name": package.get("package_name"),
            "source_commit_name": package.get("commit_name"),
            "source_snapshot_name": exported_commit.get("snapshot_name"),
            "original_session_id": original_session_id,
            "target_branch_name": target_branch,
            "imported_with_head_session_id": previous_parent,
            "import_index": idx,
        }
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "snapshot_reconcile_commit_package_import",
        }
        entry = {
            "session_id": new_session_id,
            "session_name": packaged.get("session_name"),
            "profile": packaged.get("profile"),
            "source_mode": packaged.get("source_mode"),
            "file_name": None,
            "tags": list(dict.fromkeys(list(packaged.get("tags", [])) + ["snapshot-reconcile-package-import"])),
            "entry_metadata": entry_metadata,
            "session": deepcopy(packaged.get("session", {})),
        }
        out.setdefault("sessions", []).append(entry)
        if out["branches"][target_branch].get("root_session_id") is None:
            out["branches"][target_branch]["root_session_id"] = new_session_id
        out["branches"][target_branch]["head_session_id"] = new_session_id
        out["branches"][target_branch]["manual_head_session_id"] = new_session_id
        out["active_branch_name"] = target_branch
        id_map[original_session_id] = new_session_id
        previous_parent = new_session_id

    imported_commit_name = _unique_name(set((out.get("snapshot_reconcile_commits") or {}).keys()), package.get("commit_name", "reconcile_commit"), "_import")
    imported_pairs = []
    for pair in exported_commit.get("resolution_pairs") or []:
        copied = deepcopy(pair)
        if copied.get("resolved_session_id") in id_map:
            copied["resolved_session_id"] = id_map[copied["resolved_session_id"]]
        imported_pairs.append(copied)

    imported_point_name = None
    imported_point_kind = None
    promoted_point = deepcopy(package.get("promoted_point"))
    if promoted_point and previous_parent:
        desired_name = promoted_point.get("tag_name") or promoted_point.get("point_name") or exported_commit.get("promoted_point_name") or f"{resolved_import_name}_point"
        existing_points = set((out.get("tag_points") or {}).keys())
        base = desired_name if desired_name not in existing_points else f"{desired_name}_import"
        n = 2
        imported_point_name = base
        while imported_point_name in existing_points:
            imported_point_name = f"{base}_{n}"
            n += 1
        imported_point_kind = promoted_point.get("point_kind") or exported_commit.get("promoted_point_kind") or "release"
        out, _ = create_tag_release_point(
            out,
            tag_name=imported_point_name,
            target_session_id=previous_parent,
            point_kind=imported_point_kind,
            note=promoted_point.get("note"),
        )

    out.setdefault("snapshot_reconcile_commits", {})[imported_commit_name] = {
        "commit_name": imported_commit_name,
        "resolution_name": exported_commit.get("resolution_name"),
        "snapshot_name": exported_commit.get("snapshot_name"),
        "source_point_name": exported_commit.get("source_point_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": [id_map[sid] for sid in exported_commit.get("resolved_session_ids") or [] if sid in id_map],
        "skipped_session_ids": list(exported_commit.get("skipped_session_ids") or []),
        "resolution_pairs": imported_pairs,
        "promoted_point_name": imported_point_name,
        "promoted_point_kind": imported_point_kind,
        "note": exported_commit.get("note"),
        "imported_from_package_name": package.get("package_name"),
        "import_name": resolved_import_name,
    }

    out.setdefault("snapshot_reconcile_commit_package_imports", {})[resolved_import_name] = {
        "import_name": resolved_import_name,
        "package_name": package.get("package_name"),
        "imported_commit_name": imported_commit_name,
        "target_branch_name": target_branch,
        "imported_session_count": len(id_map),
        "imported_point_name": imported_point_name,
        "imported_point_kind": imported_point_kind,
    }

    if activate_last_imported and previous_parent:
        out["active_session_id"] = previous_parent
        out["active_branch_name"] = target_branch

    last_name = None
    if previous_parent:
        try:
            last_name = _session_entry(out, previous_parent).get("session_name")
        except Exception:
            last_name = None
    out = append_history_event(
        out,
        "snapshot_reconcile_commit_package_imported",
        f"Standalone reconcile package imported: {resolved_import_name}",
        session_id=previous_parent,
        session_name=last_name,
        payload={
            "package_name": package.get("package_name"),
            "import_name": resolved_import_name,
            "imported_commit_name": imported_commit_name,
            "target_branch_name": target_branch,
            "imported_session_count": len(id_map),
        },
    )

    result = {
        "snapshot_reconcile_commit_package_import_version": "SEMASCRIPT_PROMOTED_RECONCILE_OUTCOME_PACKAGE_v0.1",
        "import_name": resolved_import_name,
        "package_name": package.get("package_name"),
        "imported_commit_name": imported_commit_name,
        "summary": {
            "imported_session_count": len(id_map),
            "imported_point": bool(imported_point_name),
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_snapshot_reconcile_commit_package_resolution.py

Size: 16292 bytes

```file

from __future__ import annotations

from copy import deepcopy

from session_model import create_session_from_text
from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_preview import preview_standalone_reconcile_outcome_package_import
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectSnapshotReconcileCommitPackageResolutionError(Exception):
    """Raised when standalone package conflict resolution / manual import decisions are invalid."""


def ensure_snapshot_reconcile_commit_package_resolution_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_reconcile_commit_package_resolutions", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_snapshot_reconcile_commit_package_resolution_state(
        ensure_snapshot_reconcile_commit_package_state(
            ensure_snapshot_reconcile_commit_state(
                ensure_snapshot_reconcile_resolution_state(
                    ensure_snapshot_reconcile_state(
                        ensure_partial_snapshot_import_state(
                            ensure_snapshot_restore_state(
                                ensure_snapshot_state(
                                    ensure_tag_point_state(
                                        ensure_branching_state(
                                            ensure_workspace_history(deepcopy(project_index))
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def snapshot_reconcile_commit_package_resolution_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for resolution_name, entry in (project_index.get("snapshot_reconcile_commit_package_resolutions") or {}).items():
        out.append({
            "resolution_name": resolution_name,
            "package_name": entry.get("package_name"),
            "source_commit_name": entry.get("source_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "skipped_session_count": len(entry.get("skipped_session_ids") or []),
            "conflict_like_count": entry.get("conflict_like_count", 0),
            "decision_counts": deepcopy(entry.get("decision_counts") or {}),
        })
    out.sort(key=lambda x: x["resolution_name"])
    return out


def _unique_name(existing: set[str], base: str, suffix: str) -> str:
    candidate = f"{base}{suffix}"
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    n = 2
    while f"{candidate}_{n}" in existing:
        n += 1
    resolved = f"{candidate}_{n}"
    existing.add(resolved)
    return resolved


def _build_custom_text_session(base_entry: dict | None, custom_text: str) -> tuple[dict, str, str, str]:
    if not base_entry:
        raise ProjectSnapshotReconcileCommitPackageResolutionError("custom_text requires a base session")
    profile = base_entry.get("profile") or "core"
    source_mode = base_entry.get("source_mode") or (base_entry.get("session", {}) or {}).get("project", {}).get("source_mode")
    if source_mode != "text":
        raise ProjectSnapshotReconcileCommitPackageResolutionError("custom_text is supported only for text sessions in v0.1")
    initial_state = deepcopy((base_entry.get("session", {}) or {}).get("project", {}).get("initial_state"))
    session_name = base_entry.get("session_name")
    session = create_session_from_text(
        text=custom_text,
        profile=profile,
        decompose=True,
        initial_state=initial_state,
        session_name=session_name,
    )
    return session, profile, "text", session.get("session_name") or session_name


def resolve_standalone_reconcile_outcome_package_import_with_decisions(
    current_project_index: dict,
    package: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    current_project_index = _normalize(current_project_index)
    if not isinstance(package, dict):
        raise ProjectSnapshotReconcileCommitPackageResolutionError("package must be an object")
    if package.get("resolution_set_package_version") != "SEMASCRIPT_PROMOTED_RECONCILE_OUTCOME_PACKAGE_v0.1":
        raise ProjectSnapshotReconcileCommitPackageResolutionError("Unsupported or missing resolution_set_package_version")

    preview = preview_standalone_reconcile_outcome_package_import(
        current_project_index=current_project_index,
        package=package,
        import_name=resolution_name or None,
        target_branch_name=target_branch_name,
        activate_last_imported=activate_last_imported,
    )
    exported_commit = deepcopy(package.get("exported_commit") or {})
    resolved_sessions = list(package.get("resolved_sessions") or [])
    if not exported_commit or not resolved_sessions:
        raise ProjectSnapshotReconcileCommitPackageResolutionError("Package is missing exported_commit or resolved_sessions")

    target_branch = preview["import_target"]["target_branch_name"]
    resolved_resolution_name = (resolution_name or f"{package.get('package_name', 'package')}_resolution").strip()
    if not resolved_resolution_name:
        raise ProjectSnapshotReconcileCommitPackageResolutionError("resolution_name is required")
    if resolved_resolution_name in (current_project_index.get("snapshot_reconcile_commit_package_resolutions") or {}):
        raise ProjectSnapshotReconcileCommitPackageResolutionError(f"Package resolution already exists: {resolved_resolution_name}")

    decisions = deepcopy(decisions or {})
    out = deepcopy(current_project_index)
    if target_branch not in out.get("branches", {}):
        out["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(out.get("branches", {})),
        }

    existing_session_ids = {item["session_id"] for item in out.get("sessions", [])}
    previous_parent = out["branches"].get(target_branch, {}).get("head_session_id")

    resolved_session_ids = []
    skipped_session_ids = []
    resolution_pairs = []
    decision_counts = {"use_package": 0, "use_current": 0, "skip": 0, "custom_text": 0}
    conflict_like_count = 0
    conflict_resolved_count = 0

    packaged_by_id = {item.get("session_id"): item for item in resolved_sessions}

    for idx, preview_item in enumerate(preview.get("preview_items") or [], start=1):
        original_session_id = preview_item["original_session_id"]
        packaged = deepcopy(packaged_by_id.get(original_session_id) or {})
        if not packaged:
            raise ProjectSnapshotReconcileCommitPackageResolutionError(f"Packaged session not found: {original_session_id}")

        current_head_entry = next((item for item in out.get("sessions", []) if item["session_id"] == previous_parent), None)
        decision = decisions.get(original_session_id, {}) or {}
        choice = (decision.get("choice") or "use_package").strip()
        if choice not in {"use_package", "use_current", "skip", "custom_text"}:
            raise ProjectSnapshotReconcileCommitPackageResolutionError(f"Unsupported decision choice: {choice}")

        if preview_item.get("conflict_like"):
            conflict_like_count += 1

        if choice == "skip":
            skipped_session_ids.append(original_session_id)
            decision_counts["skip"] += 1
            resolution_pairs.append({
                "original_session_id": original_session_id,
                "resolved_session_id": None,
                "resolved_with_head_session_id": previous_parent,
                "decision_choice": "skip",
                "preview_status": preview_item.get("status"),
                "conflict_like": preview_item.get("conflict_like", False),
            })
            continue

        if choice == "use_package":
            session_copy = deepcopy(packaged.get("session", {}))
            profile = packaged.get("profile")
            source_mode = packaged.get("source_mode")
            session_name = packaged.get("session_name")
            decision_counts["use_package"] += 1
        elif choice == "use_current":
            if not current_head_entry:
                raise ProjectSnapshotReconcileCommitPackageResolutionError(
                    f"use_current requires a current head for packaged session {original_session_id}"
                )
            session_copy = deepcopy(current_head_entry.get("session", {}))
            profile = current_head_entry.get("profile")
            source_mode = current_head_entry.get("source_mode")
            session_name = current_head_entry.get("session_name")
            decision_counts["use_current"] += 1
        else:
            custom_text = (decision.get("custom_text") or "").strip()
            if not custom_text:
                raise ProjectSnapshotReconcileCommitPackageResolutionError(
                    f"custom_text decision requires custom_text for packaged session {original_session_id}"
                )
            base_entry = current_head_entry if current_head_entry else packaged
            session_copy, profile, source_mode, session_name = _build_custom_text_session(base_entry, custom_text)
            decision_counts["custom_text"] += 1

        if preview_item.get("conflict_like"):
            conflict_resolved_count += 1

        new_session_id = _unique_name(existing_session_ids, original_session_id, "_pkg_resolved")
        entry_metadata = deepcopy(packaged.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "snapshot_reconcile_commit_package_import_resolution"
        entry_metadata["snapshot_reconcile_commit_package_import_resolution"] = {
            "resolution_name": resolved_resolution_name,
            "package_name": package.get("package_name"),
            "source_commit_name": package.get("commit_name"),
            "source_snapshot_name": exported_commit.get("snapshot_name"),
            "original_session_id": original_session_id,
            "target_branch_name": target_branch,
            "resolved_with_head_session_id": previous_parent,
            "resolution_index": idx,
            "decision_choice": choice,
            "preview_status": preview_item.get("status"),
            "conflict_like": preview_item.get("conflict_like", False),
            "same_profile_as_compare": preview_item.get("same_profile_as_compare", False),
            "same_source_mode_as_compare": preview_item.get("same_source_mode_as_compare", False),
            "same_source_text_as_compare": preview_item.get("same_source_text_as_compare", False),
        }
        if choice == "custom_text":
            entry_metadata["snapshot_reconcile_commit_package_import_resolution"]["custom_text"] = (decision.get("custom_text") or "").strip()
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "snapshot_reconcile_commit_package_import_resolution",
        }

        entry = {
            "session_id": new_session_id,
            "session_name": session_name,
            "profile": profile,
            "source_mode": source_mode,
            "file_name": None,
            "tags": list(dict.fromkeys(list(packaged.get("tags", [])) + ["snapshot-reconcile-commit-package-resolution"])),
            "entry_metadata": entry_metadata,
            "session": session_copy,
        }
        out.setdefault("sessions", []).append(entry)
        if out["branches"][target_branch].get("root_session_id") is None:
            out["branches"][target_branch]["root_session_id"] = new_session_id
        out["branches"][target_branch]["head_session_id"] = new_session_id
        out["branches"][target_branch]["manual_head_session_id"] = new_session_id
        out["active_branch_name"] = target_branch

        resolution_pairs.append({
            "original_session_id": original_session_id,
            "resolved_session_id": new_session_id,
            "resolved_with_head_session_id": previous_parent,
            "decision_choice": choice,
            "preview_status": preview_item.get("status"),
            "conflict_like": preview_item.get("conflict_like", False),
        })

        previous_parent = new_session_id
        resolved_session_ids.append(new_session_id)

    if activate_last_imported and resolved_session_ids:
        out["active_session_id"] = resolved_session_ids[-1]
        out["active_branch_name"] = target_branch

    out.setdefault("snapshot_reconcile_commit_package_resolutions", {})[resolved_resolution_name] = {
        "resolution_name": resolved_resolution_name,
        "package_name": package.get("package_name"),
        "source_commit_name": package.get("commit_name"),
        "source_snapshot_name": exported_commit.get("snapshot_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "resolution_pairs": resolution_pairs,
        "decision_counts": decision_counts,
        "conflict_like_count": conflict_like_count,
        "conflict_resolved_count": conflict_resolved_count,
    }

    history_session_id = resolved_session_ids[-1] if resolved_session_ids else None
    history_session_name = None
    if history_session_id:
        match = next((item for item in out.get("sessions", []) if item["session_id"] == history_session_id), None)
        history_session_name = match.get("session_name") if match else None

    out = append_history_event(
        out,
        "snapshot_reconcile_commit_package_import_resolved",
        f"Standalone reconcile package import resolved: {resolved_resolution_name}",
        session_id=history_session_id,
        session_name=history_session_name,
        payload={
            "package_name": package.get("package_name"),
            "source_commit_name": package.get("commit_name"),
            "target_branch_name": target_branch,
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
            "conflict_like_count": conflict_like_count,
        },
    )

    result = {
        "snapshot_reconcile_commit_package_resolution_version": "SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_CONFLICT_RESOLUTION_v0.1",
        "resolution_name": resolved_resolution_name,
        "package_name": package.get("package_name"),
        "source_commit_name": package.get("commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "resolution_pairs": resolution_pairs,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
            "conflict_like_count": conflict_like_count,
            "conflict_resolved_count": conflict_resolved_count,
            "decision_counts": decision_counts,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_snapshot_reconcile_commit_package_commit.py

Size: 8766 bytes

```file

from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state, create_tag_release_point
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectSnapshotReconcileCommitPackageCommitError(Exception):
    """Raised when standalone outcome package commit/promote is invalid."""


def ensure_snapshot_reconcile_commit_package_commit_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_reconcile_commit_package_commits", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_snapshot_reconcile_commit_package_commit_state(
        ensure_snapshot_reconcile_commit_package_resolution_state(
            ensure_snapshot_reconcile_commit_package_state(
                ensure_snapshot_reconcile_commit_state(
                    ensure_snapshot_reconcile_resolution_state(
                        ensure_snapshot_reconcile_state(
                            ensure_partial_snapshot_import_state(
                                ensure_snapshot_restore_state(
                                    ensure_snapshot_state(
                                        ensure_tag_point_state(
                                            ensure_branching_state(
                                                ensure_workspace_history(deepcopy(project_index))
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def snapshot_reconcile_commit_package_commit_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for commit_name, entry in (project_index.get("snapshot_reconcile_commit_package_commits") or {}).items():
        out.append({
            "commit_name": commit_name,
            "resolution_name": entry.get("resolution_name"),
            "package_name": entry.get("package_name"),
            "source_commit_name": entry.get("source_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "promoted_point_name": entry.get("promoted_point_name"),
            "promoted_point_kind": entry.get("promoted_point_kind"),
        })
    out.sort(key=lambda x: x["commit_name"])
    return out


def commit_standalone_reconcile_outcome_package_import_resolution(
    project_index: dict,
    snapshot_reconcile_commit_package_resolution_result: dict,
    commit_name: str | None = None,
    promote_point_name: str | None = None,
    promote_point_kind: str = "release",
    note: str | None = None,
) -> tuple[dict, dict]:
    project_index = _normalize(project_index)

    if not isinstance(snapshot_reconcile_commit_package_resolution_result, dict):
        raise ProjectSnapshotReconcileCommitPackageCommitError(
            "snapshot_reconcile_commit_package_resolution_result must be an object"
        )
    resolved_session_ids = list(snapshot_reconcile_commit_package_resolution_result.get("resolved_session_ids") or [])
    if not resolved_session_ids:
        raise ProjectSnapshotReconcileCommitPackageCommitError("No resolved_session_ids to commit")

    resolved_commit_name = (
        commit_name
        or f"{snapshot_reconcile_commit_package_resolution_result.get('resolution_name', 'package_import_resolution')}_commit"
    ).strip()
    if not resolved_commit_name:
        raise ProjectSnapshotReconcileCommitPackageCommitError("commit_name is required")
    if resolved_commit_name in (project_index.get("snapshot_reconcile_commit_package_commits") or {}):
        raise ProjectSnapshotReconcileCommitPackageCommitError(
            f"Standalone outcome package commit already exists: {resolved_commit_name}"
        )

    out = deepcopy(project_index)
    last_resolved_session_id = resolved_session_ids[-1]
    last_entry = next((item for item in out.get("sessions", []) if item["session_id"] == last_resolved_session_id), None)
    if not last_entry:
        raise ProjectSnapshotReconcileCommitPackageCommitError(
            f"Resolved imported session not found in project: {last_resolved_session_id}"
        )

    promoted_point_result = None
    promoted_point_name_resolved = None
    promoted_point_kind_resolved = None
    if promote_point_name and promote_point_name.strip():
        promoted_point_name_resolved = promote_point_name.strip()
        promoted_point_kind_resolved = (promote_point_kind or "release").strip() or "release"
        out, promoted_point_result = create_tag_release_point(
            out,
            tag_name=promoted_point_name_resolved,
            target_session_id=last_resolved_session_id,
            point_kind=promoted_point_kind_resolved,
            note=note,
        )

    out.setdefault("snapshot_reconcile_commit_package_commits", {})[resolved_commit_name] = {
        "commit_name": resolved_commit_name,
        "resolution_name": snapshot_reconcile_commit_package_resolution_result.get("resolution_name"),
        "package_name": snapshot_reconcile_commit_package_resolution_result.get("package_name"),
        "source_commit_name": snapshot_reconcile_commit_package_resolution_result.get("source_commit_name"),
        "target_branch_name": snapshot_reconcile_commit_package_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": list(snapshot_reconcile_commit_package_resolution_result.get("skipped_session_ids") or []),
        "resolution_pairs": deepcopy(snapshot_reconcile_commit_package_resolution_result.get("resolution_pairs") or []),
        "promoted_point_name": promoted_point_name_resolved,
        "promoted_point_kind": promoted_point_kind_resolved,
        "note": note,
    }

    out = append_history_event(
        out,
        "snapshot_reconcile_commit_package_committed",
        f"Standalone outcome package committed: {resolved_commit_name}",
        session_id=last_resolved_session_id,
        session_name=last_entry.get("session_name"),
        payload={
            "commit_name": resolved_commit_name,
            "resolution_name": snapshot_reconcile_commit_package_resolution_result.get("resolution_name"),
            "package_name": snapshot_reconcile_commit_package_resolution_result.get("package_name"),
            "source_commit_name": snapshot_reconcile_commit_package_resolution_result.get("source_commit_name"),
            "target_branch_name": snapshot_reconcile_commit_package_resolution_result.get("target_branch_name"),
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
        },
    )

    result = {
        "snapshot_reconcile_commit_package_commit_version": "SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_COMMIT_PROMOTE_v0.1",
        "commit_name": resolved_commit_name,
        "resolution_name": snapshot_reconcile_commit_package_resolution_result.get("resolution_name"),
        "package_name": snapshot_reconcile_commit_package_resolution_result.get("package_name"),
        "source_commit_name": snapshot_reconcile_commit_package_resolution_result.get("source_commit_name"),
        "target_branch_name": snapshot_reconcile_commit_package_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "promoted": promoted_point_result is not None,
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_local_outcome_set_package.py

Size: 17603 bytes

```file
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state, create_tag_release_point
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectLocalOutcomeSetPackageError(Exception):
    """Raised when local outcome set portable package export/import is invalid."""


def ensure_local_outcome_set_package_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("local_outcome_set_packages", {})
    out.setdefault("local_outcome_set_package_imports", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_local_outcome_set_package_state(
        ensure_snapshot_reconcile_commit_package_commit_state(
            ensure_snapshot_reconcile_commit_package_resolution_state(
                ensure_snapshot_reconcile_commit_package_state(
                    ensure_snapshot_reconcile_commit_state(
                        ensure_snapshot_reconcile_resolution_state(
                            ensure_snapshot_reconcile_state(
                                ensure_partial_snapshot_import_state(
                                    ensure_snapshot_restore_state(
                                        ensure_snapshot_state(
                                            ensure_tag_point_state(
                                                ensure_branching_state(
                                                    ensure_workspace_history(deepcopy(project_index))
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def local_outcome_set_package_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for package_name, entry in (project_index.get("local_outcome_set_packages") or {}).items():
        out.append({
            "package_name": package_name,
            "commit_name": entry.get("commit_name"),
            "resolution_name": entry.get("resolution_name"),
            "package_kind": entry.get("package_kind"),
            "source_commit_name": entry.get("source_commit_name"),
            "resolved_session_count": entry.get("resolved_session_count", 0),
            "promoted_point_name": entry.get("promoted_point_name"),
            "promoted_point_kind": entry.get("promoted_point_kind"),
        })
    out.sort(key=lambda x: x["package_name"])
    return out


def local_outcome_set_package_import_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for import_name, entry in (project_index.get("local_outcome_set_package_imports") or {}).items():
        out.append({
            "import_name": import_name,
            "package_name": entry.get("package_name"),
            "imported_commit_name": entry.get("imported_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "imported_session_count": entry.get("imported_session_count", 0),
            "imported_point_name": entry.get("imported_point_name"),
            "imported_point_kind": entry.get("imported_point_kind"),
        })
    out.sort(key=lambda x: x["import_name"])
    return out


def _commit_entry(project_index: dict, commit_name: str) -> dict:
    entry = (project_index.get("snapshot_reconcile_commit_package_commits") or {}).get(commit_name)
    if not entry:
        raise ProjectLocalOutcomeSetPackageError(f"Unknown local outcome set commit: {commit_name}")
    return entry


def _session_entry(project_index: dict, session_id: str) -> dict:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    raise ProjectLocalOutcomeSetPackageError(f"Session not found: {session_id}")


def _unique_name(existing: set[str], base: str, suffix: str) -> str:
    candidate = f"{base}{suffix}"
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    n = 2
    while f"{candidate}_{n}" in existing:
        n += 1
    resolved = f"{candidate}_{n}"
    existing.add(resolved)
    return resolved


def export_local_outcome_set_as_portable_package(
    project_index: dict,
    commit_name: str,
    package_name: str | None = None,
    note: str | None = None,
) -> tuple[dict, dict, dict]:
    project_index = _normalize(project_index)
    commit_entry = deepcopy(_commit_entry(project_index, commit_name))

    resolved_package_name = (package_name or f"{commit_name}_local_package").strip()
    if not resolved_package_name:
        raise ProjectLocalOutcomeSetPackageError("package_name is required")
    if resolved_package_name in (project_index.get("local_outcome_set_packages") or {}):
        raise ProjectLocalOutcomeSetPackageError(f"Local outcome set package already exists: {resolved_package_name}")

    resolved_sessions = []
    for sid in commit_entry.get("resolved_session_ids") or []:
        entry = _session_entry(project_index, sid)
        resolved_sessions.append({
            "session_id": entry["session_id"],
            "session_name": entry.get("session_name"),
            "profile": entry.get("profile"),
            "source_mode": entry.get("source_mode"),
            "tags": deepcopy(entry.get("tags", [])),
            "entry_metadata": deepcopy(entry.get("entry_metadata", {})),
            "session": deepcopy(entry.get("session", {})),
        })

    promoted_point = None
    promoted_point_name = commit_entry.get("promoted_point_name")
    if promoted_point_name:
        promoted_point = deepcopy((project_index.get("tag_points") or {}).get(promoted_point_name))

    package = {
        "local_outcome_set_package_version": "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1",
        "package_name": resolved_package_name,
        "package_kind": "local_outcome_set",
        "exported_from_project_name": project_index.get("project_name"),
        "commit_name": commit_name,
        "note": note if note is not None else commit_entry.get("note"),
        "exported_local_outcome_commit": commit_entry,
        "resolved_sessions": resolved_sessions,
        "promoted_point": promoted_point,
        "immutability": {
            "portable": True,
            "standalone": True,
            "source": "local_outcome_set_commit",
        },
    }

    out = deepcopy(project_index)
    out.setdefault("local_outcome_set_packages", {})[resolved_package_name] = {
        "package_name": resolved_package_name,
        "package_kind": "local_outcome_set",
        "commit_name": commit_name,
        "resolution_name": commit_entry.get("resolution_name"),
        "source_commit_name": commit_entry.get("source_commit_name"),
        "resolved_session_count": len(commit_entry.get("resolved_session_ids") or []),
        "promoted_point_name": commit_entry.get("promoted_point_name"),
        "promoted_point_kind": commit_entry.get("promoted_point_kind"),
        "note": package.get("note"),
    }

    last_sid = (commit_entry.get("resolved_session_ids") or [None])[-1]
    last_name = None
    if last_sid:
        try:
            last_name = _session_entry(out, last_sid).get("session_name")
        except Exception:
            last_name = None

    out = append_history_event(
        out,
        "local_outcome_set_package_exported",
        f"Local outcome set package exported: {resolved_package_name}",
        session_id=last_sid,
        session_name=last_name,
        payload={
            "package_name": resolved_package_name,
            "commit_name": commit_name,
            "resolution_name": commit_entry.get("resolution_name"),
        },
    )

    result = {
        "local_outcome_set_package_export_version": "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1",
        "package_name": resolved_package_name,
        "commit_name": commit_name,
        "summary": {
            "resolved_session_count": len(commit_entry.get("resolved_session_ids") or []),
            "has_promoted_point": bool(promoted_point),
            "portable": True,
        },
    }
    return _normalize(out), result, package


def import_local_outcome_set_portable_package(
    current_project_index: dict,
    package: dict,
    import_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    current_project_index = _normalize(current_project_index)
    if not isinstance(package, dict):
        raise ProjectLocalOutcomeSetPackageError("package must be an object")
    if package.get("local_outcome_set_package_version") != "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1":
        raise ProjectLocalOutcomeSetPackageError("Unsupported or missing local_outcome_set_package_version")

    exported_commit = deepcopy(package.get("exported_local_outcome_commit") or {})
    resolved_sessions = list(package.get("resolved_sessions") or [])
    if not exported_commit or not resolved_sessions:
        raise ProjectLocalOutcomeSetPackageError("Package is missing exported_local_outcome_commit or resolved_sessions")

    resolved_import_name = (import_name or f"{package.get('package_name', 'local_package')}_import").strip()
    if not resolved_import_name:
        raise ProjectLocalOutcomeSetPackageError("import_name is required")
    if resolved_import_name in (current_project_index.get("local_outcome_set_package_imports") or {}):
        raise ProjectLocalOutcomeSetPackageError(f"Local outcome set package import already exists: {resolved_import_name}")

    out = deepcopy(current_project_index)
    target_branch = (target_branch_name or exported_commit.get("target_branch_name") or out.get("active_branch_name") or "main").strip()
    if target_branch not in out.get("branches", {}):
        out["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(out["branches"]),
        }

    existing_session_ids = {item["session_id"] for item in out.get("sessions", [])}
    previous_parent = out["branches"].get(target_branch, {}).get("head_session_id")
    id_map = {}

    for idx, packaged in enumerate(resolved_sessions, start=1):
        original_session_id = packaged["session_id"]
        new_session_id = _unique_name(existing_session_ids, original_session_id, "_localpkg")
        entry_metadata = deepcopy(packaged.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "local_outcome_set_package_import"
        entry_metadata["local_outcome_set_package_import"] = {
            "import_name": resolved_import_name,
            "package_name": package.get("package_name"),
            "source_commit_name": package.get("commit_name"),
            "original_session_id": original_session_id,
            "target_branch_name": target_branch,
            "imported_with_head_session_id": previous_parent,
            "import_index": idx,
        }
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "local_outcome_set_package_import",
        }
        entry = {
            "session_id": new_session_id,
            "session_name": packaged.get("session_name"),
            "profile": packaged.get("profile"),
            "source_mode": packaged.get("source_mode"),
            "file_name": None,
            "tags": list(dict.fromkeys(list(packaged.get("tags", [])) + ["local-outcome-set-package-import"])),
            "entry_metadata": entry_metadata,
            "session": deepcopy(packaged.get("session", {})),
        }
        out.setdefault("sessions", []).append(entry)
        if out["branches"][target_branch].get("root_session_id") is None:
            out["branches"][target_branch]["root_session_id"] = new_session_id
        out["branches"][target_branch]["head_session_id"] = new_session_id
        out["branches"][target_branch]["manual_head_session_id"] = new_session_id
        out["active_branch_name"] = target_branch
        id_map[original_session_id] = new_session_id
        previous_parent = new_session_id

    imported_commit_name = _unique_name(set((out.get("snapshot_reconcile_commit_package_commits") or {}).keys()), package.get("commit_name", "local_outcome_commit"), "_localpkg_import")
    imported_pairs = []
    for pair in exported_commit.get("resolution_pairs") or []:
        copied = deepcopy(pair)
        if copied.get("resolved_session_id") in id_map:
            copied["resolved_session_id"] = id_map[copied["resolved_session_id"]]
        imported_pairs.append(copied)

    imported_point_name = None
    imported_point_kind = None
    promoted_point = deepcopy(package.get("promoted_point"))
    if promoted_point and previous_parent:
        desired_name = promoted_point.get("tag_name") or promoted_point.get("point_name") or exported_commit.get("promoted_point_name") or f"{resolved_import_name}_point"
        existing_points = set((out.get("tag_points") or {}).keys())
        base = desired_name if desired_name not in existing_points else f"{desired_name}_import"
        n = 2
        imported_point_name = base
        while imported_point_name in existing_points:
            imported_point_name = f"{base}_{n}"
            n += 1
        imported_point_kind = promoted_point.get("point_kind") or exported_commit.get("promoted_point_kind") or "release"
        out, _ = create_tag_release_point(
            out,
            tag_name=imported_point_name,
            target_session_id=previous_parent,
            point_kind=imported_point_kind,
            note=promoted_point.get("note"),
        )

    out.setdefault("snapshot_reconcile_commit_package_commits", {})[imported_commit_name] = {
        "commit_name": imported_commit_name,
        "resolution_name": exported_commit.get("resolution_name"),
        "package_name": package.get("package_name"),
        "source_commit_name": exported_commit.get("source_commit_name") or exported_commit.get("commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": [id_map[sid] for sid in exported_commit.get("resolved_session_ids") or [] if sid in id_map],
        "skipped_session_ids": list(exported_commit.get("skipped_session_ids") or []),
        "resolution_pairs": imported_pairs,
        "promoted_point_name": imported_point_name,
        "promoted_point_kind": imported_point_kind,
        "note": exported_commit.get("note"),
        "imported_from_local_outcome_set_package": package.get("package_name"),
        "import_name": resolved_import_name,
    }

    out.setdefault("local_outcome_set_package_imports", {})[resolved_import_name] = {
        "import_name": resolved_import_name,
        "package_name": package.get("package_name"),
        "imported_commit_name": imported_commit_name,
        "target_branch_name": target_branch,
        "imported_session_count": len(id_map),
        "imported_point_name": imported_point_name,
        "imported_point_kind": imported_point_kind,
    }

    if activate_last_imported and previous_parent:
        out["active_session_id"] = previous_parent
        out["active_branch_name"] = target_branch

    out = append_history_event(
        out,
        "local_outcome_set_package_imported",
        f"Local outcome set package imported: {resolved_import_name}",
        session_id=previous_parent,
        session_name=next((item.get("session_name") for item in out.get("sessions", []) if item["session_id"] == previous_parent), None),
        payload={
            "import_name": resolved_import_name,
            "package_name": package.get("package_name"),
            "imported_commit_name": imported_commit_name,
            "target_branch_name": target_branch,
            "imported_point_name": imported_point_name,
        },
    )

    result = {
        "local_outcome_set_package_import_version": "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1",
        "import_name": resolved_import_name,
        "package_name": package.get("package_name"),
        "imported_commit_name": imported_commit_name,
        "summary": {
            "imported_session_count": len(id_map),
            "target_branch_name": target_branch,
            "has_promoted_point": bool(imported_point_name),
            "active_session_id": out.get("active_session_id"),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_local_outcome_set_package_resolution.py

Size: 16639 bytes

```file

from __future__ import annotations

from copy import deepcopy

from session_model import create_session_from_text
from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state
from project_local_outcome_set_package import ensure_local_outcome_set_package_state
from project_local_outcome_set_package_preview import preview_portable_local_outcome_package_before_import
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectLocalOutcomeSetPackageResolutionError(Exception):
    """Raised when portable local outcome package manual import resolution is invalid."""


def ensure_local_outcome_set_package_resolution_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("local_outcome_set_package_resolutions", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_local_outcome_set_package_resolution_state(
        ensure_local_outcome_set_package_state(
            ensure_snapshot_reconcile_commit_package_commit_state(
                ensure_snapshot_reconcile_commit_package_resolution_state(
                    ensure_snapshot_reconcile_commit_package_state(
                        ensure_snapshot_reconcile_commit_state(
                            ensure_snapshot_reconcile_resolution_state(
                                ensure_snapshot_reconcile_state(
                                    ensure_partial_snapshot_import_state(
                                        ensure_snapshot_restore_state(
                                            ensure_snapshot_state(
                                                ensure_tag_point_state(
                                                    ensure_branching_state(
                                                        ensure_workspace_history(deepcopy(project_index))
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def local_outcome_set_package_resolution_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for resolution_name, entry in (project_index.get("local_outcome_set_package_resolutions") or {}).items():
        out.append({
            "resolution_name": resolution_name,
            "package_name": entry.get("package_name"),
            "source_commit_name": entry.get("source_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "skipped_session_count": len(entry.get("skipped_session_ids") or []),
            "conflict_like_count": entry.get("conflict_like_count", 0),
            "decision_counts": deepcopy(entry.get("decision_counts") or {}),
        })
    out.sort(key=lambda x: x["resolution_name"])
    return out


def _unique_name(existing: set[str], base: str, suffix: str) -> str:
    candidate = f"{base}{suffix}"
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    n = 2
    while f"{candidate}_{n}" in existing:
        n += 1
    resolved = f"{candidate}_{n}"
    existing.add(resolved)
    return resolved


def _build_custom_text_session(base_entry: dict, custom_text: str) -> tuple[dict, str, str, str]:
    profile = base_entry.get("profile") or "core"
    source_mode = base_entry.get("source_mode") or base_entry.get("session", {}).get("project", {}).get("source_mode") or "text"
    if source_mode != "text":
        raise ProjectLocalOutcomeSetPackageResolutionError("custom_text is supported only for text sessions in v0.1")
    initial_state = deepcopy(base_entry.get("session", {}).get("project", {}).get("initial_state"))
    session_name = base_entry.get("session_name") or "Resolved Package Session"
    session = create_session_from_text(
        text=custom_text,
        profile=profile,
        decompose=True,
        initial_state=initial_state,
        session_name=session_name,
    )
    return session, profile, "text", session_name


def resolve_portable_local_outcome_package_import_with_decisions(
    current_project_index: dict,
    package_data: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    current_project_index = _normalize(current_project_index)
    if not isinstance(package_data, dict):
        raise ProjectLocalOutcomeSetPackageResolutionError("package_data must be an object")
    if package_data.get("local_outcome_set_package_version") != "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1":
        raise ProjectLocalOutcomeSetPackageResolutionError("Unsupported or missing local_outcome_set_package_version")

    preview = preview_portable_local_outcome_package_before_import(
        current_project_index=current_project_index,
        package_data=package_data,
        import_name=resolution_name or None,
        target_branch_name=target_branch_name,
    )
    exported_commit = deepcopy(package_data.get("exported_local_outcome_commit") or {})
    resolved_sessions = list(package_data.get("resolved_sessions") or [])
    if not exported_commit or not resolved_sessions:
        raise ProjectLocalOutcomeSetPackageResolutionError("Package is missing exported_local_outcome_commit or resolved_sessions")

    target_branch = preview["import_target"]["target_branch_name"]
    resolved_resolution_name = (resolution_name or f"{package_data.get('package_name', 'local_package')}_resolution").strip()
    if not resolved_resolution_name:
        raise ProjectLocalOutcomeSetPackageResolutionError("resolution_name is required")
    if resolved_resolution_name in (current_project_index.get("local_outcome_set_package_resolutions") or {}):
        raise ProjectLocalOutcomeSetPackageResolutionError(f"Local outcome package resolution already exists: {resolved_resolution_name}")

    decisions = deepcopy(decisions or {})
    out = deepcopy(current_project_index)
    if target_branch not in out.get("branches", {}):
        out["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(out.get("branches", {})),
        }

    existing_session_ids = {item["session_id"] for item in out.get("sessions", [])}
    previous_parent = out["branches"].get(target_branch, {}).get("head_session_id")

    resolved_session_ids = []
    skipped_session_ids = []
    resolution_pairs = []
    decision_counts = {"use_package": 0, "use_current": 0, "skip": 0, "custom_text": 0}
    conflict_like_count = 0
    conflict_resolved_count = 0

    packaged_by_id = {item.get("session_id"): item for item in resolved_sessions}

    for idx, preview_item in enumerate(preview.get("preview_items") or [], start=1):
        original_session_id = preview_item["original_session_id"]
        packaged = deepcopy(packaged_by_id.get(original_session_id) or {})
        if not packaged:
            raise ProjectLocalOutcomeSetPackageResolutionError(f"Packaged session not found: {original_session_id}")

        current_head_entry = next((item for item in out.get("sessions", []) if item["session_id"] == previous_parent), None)
        decision = decisions.get(original_session_id, {}) or {}
        choice = (decision.get("choice") or "use_package").strip()
        if choice not in {"use_package", "use_current", "skip", "custom_text"}:
            raise ProjectLocalOutcomeSetPackageResolutionError(f"Unsupported decision choice: {choice}")

        if preview_item.get("conflict_like"):
            conflict_like_count += 1

        if choice == "skip":
            skipped_session_ids.append(original_session_id)
            decision_counts["skip"] += 1
            resolution_pairs.append({
                "original_session_id": original_session_id,
                "resolved_session_id": None,
                "resolved_with_head_session_id": previous_parent,
                "decision_choice": "skip",
                "preview_status": preview_item.get("status"),
                "conflict_like": preview_item.get("conflict_like", False),
            })
            continue

        if choice == "use_package":
            session_copy = deepcopy(packaged.get("session", {}))
            profile = packaged.get("profile")
            source_mode = packaged.get("source_mode")
            session_name = packaged.get("session_name")
            decision_counts["use_package"] += 1
        elif choice == "use_current":
            if not current_head_entry:
                raise ProjectLocalOutcomeSetPackageResolutionError(
                    f"use_current requires a current head for packaged session {original_session_id}"
                )
            session_copy = deepcopy(current_head_entry.get("session", {}))
            profile = current_head_entry.get("profile")
            source_mode = current_head_entry.get("source_mode")
            session_name = current_head_entry.get("session_name")
            decision_counts["use_current"] += 1
        else:
            custom_text = (decision.get("custom_text") or "").strip()
            if not custom_text:
                raise ProjectLocalOutcomeSetPackageResolutionError(
                    f"custom_text decision requires custom_text for packaged session {original_session_id}"
                )
            base_entry = current_head_entry if current_head_entry else packaged
            session_copy, profile, source_mode, session_name = _build_custom_text_session(base_entry, custom_text)
            decision_counts["custom_text"] += 1

        if preview_item.get("conflict_like"):
            conflict_resolved_count += 1

        new_session_id = _unique_name(existing_session_ids, original_session_id, "_localpkg_resolved")
        entry_metadata = deepcopy(packaged.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "local_outcome_set_package_import_resolution"
        entry_metadata["local_outcome_set_package_import_resolution"] = {
            "resolution_name": resolved_resolution_name,
            "package_name": package_data.get("package_name"),
            "source_commit_name": package_data.get("commit_name"),
            "original_session_id": original_session_id,
            "target_branch_name": target_branch,
            "resolved_with_head_session_id": previous_parent,
            "resolution_index": idx,
            "decision_choice": choice,
            "preview_status": preview_item.get("status"),
            "conflict_like": preview_item.get("conflict_like", False),
            "same_profile_as_compare": preview_item.get("same_profile_as_compare", False),
            "same_source_mode_as_compare": preview_item.get("same_source_mode_as_compare", False),
            "same_source_text_as_compare": preview_item.get("same_source_text_as_compare", False),
        }
        if choice == "custom_text":
            entry_metadata["local_outcome_set_package_import_resolution"]["custom_text"] = (decision.get("custom_text") or "").strip()
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "local_outcome_set_package_import_resolution",
        }
        entry = {
            "session_id": new_session_id,
            "session_name": session_name,
            "profile": profile,
            "source_mode": source_mode,
            "file_name": None,
            "tags": list(dict.fromkeys(list(packaged.get("tags", [])) + ["local-outcome-set-package-resolution"])),
            "entry_metadata": entry_metadata,
            "session": session_copy,
        }
        out.setdefault("sessions", []).append(entry)
        if out["branches"][target_branch].get("root_session_id") is None:
            out["branches"][target_branch]["root_session_id"] = new_session_id
        out["branches"][target_branch]["head_session_id"] = new_session_id
        out["branches"][target_branch]["manual_head_session_id"] = new_session_id
        out["active_branch_name"] = target_branch
        previous_parent = new_session_id
        resolved_session_ids.append(new_session_id)
        resolution_pairs.append({
            "original_session_id": original_session_id,
            "resolved_session_id": new_session_id,
            "resolved_with_head_session_id": entry_metadata["local_outcome_set_package_import_resolution"]["resolved_with_head_session_id"],
            "decision_choice": choice,
            "preview_status": preview_item.get("status"),
            "conflict_like": preview_item.get("conflict_like", False),
        })

    if activate_last_imported and resolved_session_ids:
        out["active_session_id"] = resolved_session_ids[-1]
        out["active_branch_name"] = target_branch

    out.setdefault("local_outcome_set_package_resolutions", {})[resolved_resolution_name] = {
        "resolution_name": resolved_resolution_name,
        "package_name": package_data.get("package_name"),
        "source_commit_name": package_data.get("commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "resolution_pairs": resolution_pairs,
        "decision_counts": decision_counts,
        "conflict_like_count": conflict_like_count,
        "conflict_resolved_count": conflict_resolved_count,
    }

    history_session_id = resolved_session_ids[-1] if resolved_session_ids else previous_parent
    history_session_name = next((item.get("session_name") for item in out.get("sessions", []) if item["session_id"] == history_session_id), None)
    out = append_history_event(
        out,
        "local_outcome_set_package_import_resolved",
        f"Local outcome set package import resolved: {resolved_resolution_name}",
        session_id=history_session_id,
        session_name=history_session_name,
        payload={
            "resolution_name": resolved_resolution_name,
            "package_name": package_data.get("package_name"),
            "source_commit_name": package_data.get("commit_name"),
            "target_branch_name": target_branch,
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
        },
    )

    result = {
        "local_outcome_set_package_resolution_version": "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_IMPORT_RESOLUTION_v0.1",
        "resolution_name": resolved_resolution_name,
        "package_name": package_data.get("package_name"),
        "source_commit_name": package_data.get("commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "resolution_pairs": resolution_pairs,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
            "conflict_like_count": conflict_like_count,
            "conflict_resolved_count": conflict_resolved_count,
            "decision_counts": decision_counts,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_local_outcome_set_package_commit.py

Size: 9294 bytes

```file

from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state, create_tag_release_point
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state
from project_local_outcome_set_package import ensure_local_outcome_set_package_state
from project_local_outcome_set_package_resolution import ensure_local_outcome_set_package_resolution_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectLocalOutcomeSetPackageCommitError(Exception):
    """Raised when portable local outcome package resolution commit/promote is invalid."""


def ensure_local_outcome_set_package_commit_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("local_outcome_set_package_commits", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_local_outcome_set_package_commit_state(
        ensure_local_outcome_set_package_resolution_state(
            ensure_local_outcome_set_package_state(
                ensure_snapshot_reconcile_commit_package_commit_state(
                    ensure_snapshot_reconcile_commit_package_resolution_state(
                        ensure_snapshot_reconcile_commit_package_state(
                            ensure_snapshot_reconcile_commit_state(
                                ensure_snapshot_reconcile_resolution_state(
                                    ensure_snapshot_reconcile_state(
                                        ensure_partial_snapshot_import_state(
                                            ensure_snapshot_restore_state(
                                                ensure_snapshot_state(
                                                    ensure_tag_point_state(
                                                        ensure_branching_state(
                                                            ensure_workspace_history(deepcopy(project_index))
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def local_outcome_set_package_commit_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for commit_name, entry in (project_index.get("local_outcome_set_package_commits") or {}).items():
        out.append({
            "commit_name": commit_name,
            "resolution_name": entry.get("resolution_name"),
            "package_name": entry.get("package_name"),
            "source_commit_name": entry.get("source_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "promoted_point_name": entry.get("promoted_point_name"),
            "promoted_point_kind": entry.get("promoted_point_kind"),
            "note": entry.get("note"),
        })
    out.sort(key=lambda x: x["commit_name"])
    return out


def commit_portable_local_outcome_package_import_resolution(
    project_index: dict,
    local_outcome_set_package_resolution_result: dict,
    commit_name: str | None = None,
    promote_point_name: str | None = None,
    promote_point_kind: str = "release",
    note: str | None = None,
) -> tuple[dict, dict]:
    project_index = _normalize(project_index)

    if not isinstance(local_outcome_set_package_resolution_result, dict):
        raise ProjectLocalOutcomeSetPackageCommitError("local_outcome_set_package_resolution_result must be an object")

    resolved_session_ids = list(local_outcome_set_package_resolution_result.get("resolved_session_ids") or [])
    if not resolved_session_ids:
        raise ProjectLocalOutcomeSetPackageCommitError("No resolved_session_ids to commit")

    resolved_commit_name = (
        commit_name
        or f"{local_outcome_set_package_resolution_result.get('resolution_name', 'local_outcome_pkg_resolution')}_commit"
    ).strip()
    if not resolved_commit_name:
        raise ProjectLocalOutcomeSetPackageCommitError("commit_name is required")
    if resolved_commit_name in (project_index.get("snapshot_reconcile_commit_package_commits") or {}):
        raise ProjectLocalOutcomeSetPackageCommitError(f"Portable local outcome package commit already exists: {resolved_commit_name}")

    out = deepcopy(project_index)
    last_resolved_session_id = resolved_session_ids[-1]
    last_entry = next((item for item in out.get("sessions", []) if item["session_id"] == last_resolved_session_id), None)
    if not last_entry:
        raise ProjectLocalOutcomeSetPackageCommitError(f"Resolved imported session not found in project: {last_resolved_session_id}")

    promoted_point_result = None
    promoted_point_name_resolved = None
    promoted_point_kind_resolved = None
    if promote_point_name and promote_point_name.strip():
        promoted_point_name_resolved = promote_point_name.strip()
        promoted_point_kind_resolved = (promote_point_kind or "release").strip() or "release"
        out, promoted_point_result = create_tag_release_point(
            out,
            tag_name=promoted_point_name_resolved,
            target_session_id=last_resolved_session_id,
            point_kind=promoted_point_kind_resolved,
            note=note,
        )

    commit_entry = {
        "commit_name": resolved_commit_name,
        "resolution_name": local_outcome_set_package_resolution_result.get("resolution_name"),
        "package_name": local_outcome_set_package_resolution_result.get("package_name"),
        "source_commit_name": local_outcome_set_package_resolution_result.get("source_commit_name"),
        "target_branch_name": local_outcome_set_package_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": list(local_outcome_set_package_resolution_result.get("skipped_session_ids") or []),
        "resolution_pairs": deepcopy(local_outcome_set_package_resolution_result.get("resolution_pairs") or []),
        "promoted_point_name": promoted_point_name_resolved,
        "promoted_point_kind": promoted_point_kind_resolved,
        "note": note,
    }

    out.setdefault("snapshot_reconcile_commit_package_commits", {})[resolved_commit_name] = deepcopy(commit_entry)
    out.setdefault("local_outcome_set_package_commits", {})[resolved_commit_name] = deepcopy(commit_entry)

    out = append_history_event(
        out,
        "local_outcome_set_package_committed",
        f"Portable local outcome package committed: {resolved_commit_name}",
        session_id=last_resolved_session_id,
        session_name=last_entry.get("session_name"),
        payload={
            "commit_name": resolved_commit_name,
            "resolution_name": local_outcome_set_package_resolution_result.get("resolution_name"),
            "package_name": local_outcome_set_package_resolution_result.get("package_name"),
            "source_commit_name": local_outcome_set_package_resolution_result.get("source_commit_name"),
            "target_branch_name": local_outcome_set_package_resolution_result.get("target_branch_name"),
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
        },
    )

    result = {
        "local_outcome_set_package_commit_version": "SEMASCRIPT_LOCAL_OUTCOME_SET_PACKAGE_COMMIT_v0.1",
        "commit_name": resolved_commit_name,
        "resolution_name": local_outcome_set_package_resolution_result.get("resolution_name"),
        "package_name": local_outcome_set_package_resolution_result.get("package_name"),
        "source_commit_name": local_outcome_set_package_resolution_result.get("source_commit_name"),
        "target_branch_name": local_outcome_set_package_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "promoted": bool(promoted_point_result),
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_local_outcome_set_package_commit_merge.py

Size: 9519 bytes

```file

from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state
from project_local_outcome_set_package import ensure_local_outcome_set_package_state
from project_local_outcome_set_package_resolution import ensure_local_outcome_set_package_resolution_state
from project_local_outcome_set_package_commit import ensure_local_outcome_set_package_commit_state
from workspace_timeline import ensure_workspace_history


class ProjectPortableLocalOutcomePackageThreeWayMergeError(Exception):
    """Raised when portable local outcome package three-way merge is invalid."""


def _normalize(project_index: dict) -> dict:
    return ensure_local_outcome_set_package_commit_state(
        ensure_local_outcome_set_package_resolution_state(
            ensure_local_outcome_set_package_state(
                ensure_snapshot_reconcile_commit_package_commit_state(
                    ensure_snapshot_reconcile_commit_package_resolution_state(
                        ensure_snapshot_reconcile_commit_package_state(
                            ensure_snapshot_reconcile_commit_state(
                                ensure_snapshot_reconcile_resolution_state(
                                    ensure_snapshot_reconcile_state(
                                        ensure_partial_snapshot_import_state(
                                            ensure_snapshot_restore_state(
                                                ensure_snapshot_state(
                                                    ensure_tag_point_state(
                                                        ensure_branching_state(
                                                            ensure_workspace_history(deepcopy(project_index))
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def _index_sessions(project_index: dict) -> dict[str, dict]:
    return {item["session_id"]: item for item in project_index.get("sessions", [])}


def _commit_entry(project_index: dict, commit_name: str) -> dict:
    registry = project_index.get("local_outcome_set_package_commits") or {}
    entry = deepcopy(registry.get(commit_name))
    if not entry:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeError(f"Unknown commit_name: {commit_name}")
    return entry


def _original_id_map(commit_entry: dict, sessions: dict[str, dict]) -> dict[str, dict]:
    out = {}
    for pair in (commit_entry.get("resolution_pairs") or []):
        original_id = pair.get("original_session_id")
        resolved_id = pair.get("resolved_session_id")
        if not original_id:
            continue
        entry = sessions.get(resolved_id or "")
        out[original_id] = {
            "original_session_id": original_id,
            "resolved_session_id": resolved_id,
            "decision_choice": pair.get("decision_choice"),
            "conflict_like": pair.get("conflict_like", False),
            "source_text": (entry or {}).get("session", {}).get("project", {}).get("source_text"),
            "session_name": (entry or {}).get("session_name"),
            "profile": (entry or {}).get("profile"),
            "source_mode": (entry or {}).get("source_mode"),
        }
    return out


def compare_baseline_or_three_way_merge_portable_local_outcome_package_commits(
    project_index: dict,
    base_commit_name: str,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    project_index = _normalize(project_index)
    sessions = _index_sessions(project_index)

    base_entry = _commit_entry(project_index, base_commit_name)
    left_entry = _commit_entry(project_index, left_commit_name)
    right_entry = _commit_entry(project_index, right_commit_name)

    base_map = _original_id_map(base_entry, sessions)
    left_map = _original_id_map(left_entry, sessions)
    right_map = _original_id_map(right_entry, sessions)

    original_ids = sorted(set(base_map) | set(left_map) | set(right_map))
    merge_items = []
    auto_merged = []
    conflict_count = 0

    for original_id in original_ids:
        base_text = (base_map.get(original_id) or {}).get("source_text")
        left_text = (left_map.get(original_id) or {}).get("source_text")
        right_text = (right_map.get(original_id) or {}).get("source_text")

        if left_text == base_text and right_text == base_text:
            status = "unchanged"
            merged_text = base_text
            conflict = False
        elif left_text == right_text and left_text != base_text:
            status = "same_change"
            merged_text = left_text
            conflict = False
        elif left_text != base_text and right_text == base_text:
            status = "left_only_change"
            merged_text = left_text
            conflict = False
        elif right_text != base_text and left_text == base_text:
            status = "right_only_change"
            merged_text = right_text
            conflict = False
        else:
            status = "conflict"
            merged_text = None
            conflict = True
            conflict_count += 1

        item = {
            "original_session_id": original_id,
            "base": deepcopy(base_map.get(original_id) or {"source_text": None}),
            "left": deepcopy(left_map.get(original_id) or {"source_text": None}),
            "right": deepcopy(right_map.get(original_id) or {"source_text": None}),
            "status": status,
            "conflict": conflict,
            "merged_source_text": merged_text,
        }
        merge_items.append(item)
        if not conflict and merged_text is not None:
            auto_merged.append({
                "original_session_id": original_id,
                "status": status,
                "merged_source_text": merged_text,
            })

    result = {
        "portable_local_outcome_package_baseline_three_way_merge_version": "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_BASELINE_THREE_WAY_MERGE_v0.1",
        "base_commit_name": base_commit_name,
        "left_commit_name": left_commit_name,
        "right_commit_name": right_commit_name,
        "identity": {
            "same_package_triplet": (
                base_entry.get("package_name") == left_entry.get("package_name") == right_entry.get("package_name")
            ),
            "same_source_commit_triplet": (
                base_entry.get("source_commit_name") == left_entry.get("source_commit_name") == right_entry.get("source_commit_name")
            ),
        },
        "metadata": {
            "base": {
                "resolution_name": base_entry.get("resolution_name"),
                "package_name": base_entry.get("package_name"),
                "source_commit_name": base_entry.get("source_commit_name"),
                "target_branch_name": base_entry.get("target_branch_name"),
                "promoted_point_name": base_entry.get("promoted_point_name"),
                "promoted_point_kind": base_entry.get("promoted_point_kind"),
            },
            "left": {
                "resolution_name": left_entry.get("resolution_name"),
                "package_name": left_entry.get("package_name"),
                "source_commit_name": left_entry.get("source_commit_name"),
                "target_branch_name": left_entry.get("target_branch_name"),
                "promoted_point_name": left_entry.get("promoted_point_name"),
                "promoted_point_kind": left_entry.get("promoted_point_kind"),
            },
            "right": {
                "resolution_name": right_entry.get("resolution_name"),
                "package_name": right_entry.get("package_name"),
                "source_commit_name": right_entry.get("source_commit_name"),
                "target_branch_name": right_entry.get("target_branch_name"),
                "promoted_point_name": right_entry.get("promoted_point_name"),
                "promoted_point_kind": right_entry.get("promoted_point_kind"),
            },
        },
        "merge_items": merge_items,
        "auto_merged_items": auto_merged,
        "summary": {
            "original_session_count": len(original_ids),
            "auto_merged_count": len(auto_merged),
            "conflict_count": conflict_count,
            "has_conflicts": conflict_count > 0,
        },
    }
    return result
```


## FILE: tooling/project_local_outcome_set_package_commit_merge_resolution.py

Size: 17464 bytes

```file

from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state
from project_local_outcome_set_package import ensure_local_outcome_set_package_state
from project_local_outcome_set_package_resolution import (
    ensure_local_outcome_set_package_resolution_state,
    _unique_name,
    _build_custom_text_session,
)
from project_local_outcome_set_package_commit import ensure_local_outcome_set_package_commit_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(Exception):
    """Raised when portable local outcome package three-way merge resolution is invalid."""


def ensure_portable_local_outcome_package_merge_resolution_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("portable_local_outcome_set_package_merge_resolutions", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_portable_local_outcome_package_merge_resolution_state(
        ensure_local_outcome_set_package_commit_state(
            ensure_local_outcome_set_package_resolution_state(
                ensure_local_outcome_set_package_state(
                    ensure_snapshot_reconcile_commit_package_commit_state(
                        ensure_snapshot_reconcile_commit_package_resolution_state(
                            ensure_snapshot_reconcile_commit_package_state(
                                ensure_snapshot_reconcile_commit_state(
                                    ensure_snapshot_reconcile_resolution_state(
                                        ensure_snapshot_reconcile_state(
                                            ensure_partial_snapshot_import_state(
                                                ensure_snapshot_restore_state(
                                                    ensure_snapshot_state(
                                                        ensure_tag_point_state(
                                                            ensure_branching_state(
                                                                ensure_workspace_history(deepcopy(project_index))
                                                            )
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def portable_local_outcome_package_merge_resolution_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for resolution_name, entry in (project_index.get("portable_local_outcome_set_package_merge_resolutions") or {}).items():
        out.append({
            "resolution_name": resolution_name,
            "base_commit_name": entry.get("base_commit_name"),
            "left_commit_name": entry.get("left_commit_name"),
            "right_commit_name": entry.get("right_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "conflict_count": entry.get("conflict_count", 0),
            "decision_counts": deepcopy(entry.get("decision_counts") or {}),
        })
    out.sort(key=lambda x: x["resolution_name"])
    return out


def _session_index(project_index: dict) -> dict[str, dict]:
    return {item["session_id"]: item for item in project_index.get("sessions", [])}


def _role_entry(item: dict, sessions: dict[str, dict]) -> dict | None:
    sid = (item or {}).get("resolved_session_id")
    return deepcopy(sessions.get(sid)) if sid else None


def resolve_portable_local_outcome_package_three_way_conflicts_with_decisions(
    project_index: dict,
    merge_result: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_resolved: bool = True,
) -> tuple[dict, dict]:
    project_index = _normalize(project_index)
    if not isinstance(merge_result, dict):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError("merge_result must be an object")
    if merge_result.get("portable_local_outcome_package_baseline_three_way_merge_version") != "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_BASELINE_THREE_WAY_MERGE_v0.1":
        raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError("Unsupported or missing merge preview version")

    resolved_name = (resolution_name or f"{merge_result.get('left_commit_name', 'portable_local_merge')}_merge_resolution").strip()
    if not resolved_name:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError("resolution_name is required")
    if resolved_name in (project_index.get("portable_local_outcome_set_package_merge_resolutions") or {}):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"Portable local outcome merge resolution already exists: {resolved_name}")

    out = deepcopy(project_index)
    target_branch = (
        (target_branch_name or "").strip()
        or (merge_result.get("metadata", {}).get("left", {}) or {}).get("target_branch_name")
        or out.get("active_branch_name")
        or "main"
    )
    if target_branch not in out.get("branches", {}):
        out["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(out.get("branches", {})),
        }

    existing_ids = {item["session_id"] for item in out.get("sessions", [])}
    previous_parent = out["branches"][target_branch].get("head_session_id")
    sessions = _session_index(out)
    decisions = deepcopy(decisions or {})

    resolved_session_ids = []
    skipped_session_ids = []
    merge_pairs = []
    decision_counts = {"use_auto": 0, "use_base": 0, "use_left": 0, "use_right": 0, "skip": 0, "custom_text": 0}
    conflict_count = 0
    conflict_resolved_count = 0

    for idx, item in enumerate(merge_result.get("merge_items") or [], start=1):
        original_id = item["original_session_id"]
        decision = decisions.get(original_id, {}) or {}
        choice = (decision.get("choice") or ("use_auto" if not item.get("conflict") else "")).strip()

        if item.get("conflict"):
            conflict_count += 1
            if not choice:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(
                    f"Conflict requires a decision for original_session_id: {original_id}"
                )

        if choice not in {"use_auto", "use_base", "use_left", "use_right", "skip", "custom_text"}:
            raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"Unsupported merge decision choice: {choice or '<empty>'}")

        base_entry = _role_entry(item.get("base"), sessions)
        left_entry = _role_entry(item.get("left"), sessions)
        right_entry = _role_entry(item.get("right"), sessions)

        if choice == "skip":
            skipped_session_ids.append(original_id)
            decision_counts["skip"] += 1
            merge_pairs.append({
                "original_session_id": original_id,
                "resolved_session_id": None,
                "resolved_with_head_session_id": previous_parent,
                "decision_choice": "skip",
                "merge_status": item.get("status"),
                "conflict": item.get("conflict", False),
            })
            continue

        if choice == "use_auto":
            status = item.get("status")
            if status == "unchanged":
                selected_entry = base_entry or left_entry or right_entry
            elif status in {"same_change", "left_only_change"}:
                selected_entry = left_entry or right_entry or base_entry
            elif status == "right_only_change":
                selected_entry = right_entry or left_entry or base_entry
            else:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(
                    f"use_auto is not allowed for conflict item: {original_id}"
                )
            session_copy = deepcopy((selected_entry or {}).get("session", {}))
            profile = (selected_entry or {}).get("profile")
            source_mode = (selected_entry or {}).get("source_mode")
            session_name = (selected_entry or {}).get("session_name") or original_id
            decision_counts["use_auto"] += 1
        elif choice == "use_base":
            if not base_entry:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"use_base requires base entry for {original_id}")
            session_copy = deepcopy(base_entry.get("session", {}))
            profile = base_entry.get("profile")
            source_mode = base_entry.get("source_mode")
            session_name = base_entry.get("session_name")
            decision_counts["use_base"] += 1
        elif choice == "use_left":
            if not left_entry:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"use_left requires left entry for {original_id}")
            session_copy = deepcopy(left_entry.get("session", {}))
            profile = left_entry.get("profile")
            source_mode = left_entry.get("source_mode")
            session_name = left_entry.get("session_name")
            decision_counts["use_left"] += 1
        elif choice == "use_right":
            if not right_entry:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"use_right requires right entry for {original_id}")
            session_copy = deepcopy(right_entry.get("session", {}))
            profile = right_entry.get("profile")
            source_mode = right_entry.get("source_mode")
            session_name = right_entry.get("session_name")
            decision_counts["use_right"] += 1
        else:
            custom_text = (decision.get("custom_text") or "").strip()
            if not custom_text:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(
                    f"custom_text decision requires custom_text for {original_id}"
                )
            template_entry = left_entry or right_entry or base_entry
            if not template_entry:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"No template entry for custom_text on {original_id}")
            session_copy, profile, source_mode, session_name = _build_custom_text_session(template_entry, custom_text)
            decision_counts["custom_text"] += 1

        if item.get("conflict"):
            conflict_resolved_count += 1

        new_session_id = _unique_name(existing_ids, original_id, "_localpkg_merge_resolved")
        entry_metadata = deepcopy((left_entry or right_entry or base_entry or {}).get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "portable_local_outcome_package_three_way_merge_resolution"
        entry_metadata["portable_local_outcome_package_three_way_merge_resolution"] = {
            "resolution_name": resolved_name,
            "base_commit_name": merge_result.get("base_commit_name"),
            "left_commit_name": merge_result.get("left_commit_name"),
            "right_commit_name": merge_result.get("right_commit_name"),
            "original_session_id": original_id,
            "target_branch_name": target_branch,
            "resolved_with_head_session_id": previous_parent,
            "resolution_index": idx,
            "decision_choice": choice,
            "merge_status": item.get("status"),
            "conflict": item.get("conflict", False),
        }
        if choice == "custom_text":
            entry_metadata["portable_local_outcome_package_three_way_merge_resolution"]["custom_text"] = (decision.get("custom_text") or "").strip()
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "portable_local_outcome_package_three_way_merge_resolution",
        }
        entry = {
            "session_id": new_session_id,
            "session_name": session_name,
            "profile": profile,
            "source_mode": source_mode,
            "file_name": None,
            "tags": list(dict.fromkeys(list((left_entry or right_entry or base_entry or {}).get("tags", [])) + ["portable-local-outcome-package-merge-resolution"])),
            "entry_metadata": entry_metadata,
            "session": session_copy,
        }
        out.setdefault("sessions", []).append(entry)
        if out["branches"][target_branch].get("root_session_id") is None:
            out["branches"][target_branch]["root_session_id"] = new_session_id
        out["branches"][target_branch]["head_session_id"] = new_session_id
        out["branches"][target_branch]["manual_head_session_id"] = new_session_id
        out["active_branch_name"] = target_branch
        previous_parent = new_session_id
        resolved_session_ids.append(new_session_id)
        merge_pairs.append({
            "original_session_id": original_id,
            "resolved_session_id": new_session_id,
            "resolved_with_head_session_id": entry_metadata["portable_local_outcome_package_three_way_merge_resolution"]["resolved_with_head_session_id"],
            "decision_choice": choice,
            "merge_status": item.get("status"),
            "conflict": item.get("conflict", False),
        })

    if activate_last_resolved and resolved_session_ids:
        out["active_session_id"] = resolved_session_ids[-1]

    out.setdefault("portable_local_outcome_set_package_merge_resolutions", {})[resolved_name] = {
        "resolution_name": resolved_name,
        "base_commit_name": merge_result.get("base_commit_name"),
        "left_commit_name": merge_result.get("left_commit_name"),
        "right_commit_name": merge_result.get("right_commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "merge_pairs": merge_pairs,
        "decision_counts": deepcopy(decision_counts),
        "conflict_count": conflict_count,
        "conflict_resolved_count": conflict_resolved_count,
    }

    if resolved_session_ids:
        last = next(item for item in out["sessions"] if item["session_id"] == resolved_session_ids[-1])
        out = append_history_event(
            out,
            "portable_local_outcome_package_three_way_merge_resolved",
            f"Portable local outcome package three-way merge resolved: {resolved_name}",
            session_id=last["session_id"],
            session_name=last["session_name"],
            payload={
                "resolution_name": resolved_name,
                "base_commit_name": merge_result.get("base_commit_name"),
                "left_commit_name": merge_result.get("left_commit_name"),
                "right_commit_name": merge_result.get("right_commit_name"),
                "target_branch_name": target_branch,
                "conflict_count": conflict_count,
                "conflict_resolved_count": conflict_resolved_count,
            },
        )

    result = {
        "portable_local_outcome_package_three_way_merge_resolution_version": "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_RESOLUTION_v0.1",
        "resolution_name": resolved_name,
        "base_commit_name": merge_result.get("base_commit_name"),
        "left_commit_name": merge_result.get("left_commit_name"),
        "right_commit_name": merge_result.get("right_commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "merge_pairs": merge_pairs,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
            "conflict_count": conflict_count,
            "conflict_resolved_count": conflict_resolved_count,
            "decision_counts": deepcopy(decision_counts),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/project_local_outcome_set_package_commit_merge_commit.py

Size: 12855 bytes

```file
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state, create_tag_release_point
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state
from project_local_outcome_set_package import ensure_local_outcome_set_package_state
from project_local_outcome_set_package_resolution import ensure_local_outcome_set_package_resolution_state
from project_local_outcome_set_package_commit import ensure_local_outcome_set_package_commit_state
from project_local_outcome_set_package_commit_merge_resolution import (
    ensure_portable_local_outcome_package_merge_resolution_state,
)
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectPortableLocalOutcomePackageThreeWayMergeCommitError(Exception):
    """Raised when portable local outcome package three-way merge commit/promote is invalid."""


def ensure_portable_local_outcome_package_merge_commit_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("portable_local_outcome_set_package_merge_commits", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_portable_local_outcome_package_merge_commit_state(
        ensure_portable_local_outcome_package_merge_resolution_state(
            ensure_local_outcome_set_package_commit_state(
                ensure_local_outcome_set_package_resolution_state(
                    ensure_local_outcome_set_package_state(
                        ensure_snapshot_reconcile_commit_package_commit_state(
                            ensure_snapshot_reconcile_commit_package_resolution_state(
                                ensure_snapshot_reconcile_commit_package_state(
                                    ensure_snapshot_reconcile_commit_state(
                                        ensure_snapshot_reconcile_resolution_state(
                                            ensure_snapshot_reconcile_state(
                                                ensure_partial_snapshot_import_state(
                                                    ensure_snapshot_restore_state(
                                                        ensure_snapshot_state(
                                                            ensure_tag_point_state(
                                                                ensure_branching_state(
                                                                    ensure_workspace_history(deepcopy(project_index))
                                                                )
                                                            )
                                                        )
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def portable_local_outcome_package_merge_commit_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for commit_name, entry in (project_index.get("portable_local_outcome_set_package_merge_commits") or {}).items():
        out.append({
            "commit_name": commit_name,
            "resolution_name": entry.get("resolution_name"),
            "base_commit_name": entry.get("base_commit_name"),
            "left_commit_name": entry.get("left_commit_name"),
            "right_commit_name": entry.get("right_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "promoted_point_name": entry.get("promoted_point_name"),
            "promoted_point_kind": entry.get("promoted_point_kind"),
            "note": entry.get("note"),
        })
    out.sort(key=lambda x: x["commit_name"])
    return out


def _derive_shared_metadata(project_index: dict, resolution_result: dict) -> tuple[str | None, str | None]:
    registry = project_index.get("local_outcome_set_package_commits") or {}
    commit_names = [
        resolution_result.get("base_commit_name"),
        resolution_result.get("left_commit_name"),
        resolution_result.get("right_commit_name"),
    ]
    entries = [deepcopy(registry.get(name)) for name in commit_names if name and registry.get(name)]
    if not entries:
        return None, None

    package_names = {entry.get("package_name") for entry in entries}
    source_commit_names = {entry.get("source_commit_name") for entry in entries}
    package_name = package_names.pop() if len(package_names) == 1 else None
    source_commit_name = source_commit_names.pop() if len(source_commit_names) == 1 else None
    return package_name, source_commit_name


def _resolution_pairs_from_merge_pairs(merge_pairs: list[dict]) -> list[dict]:
    out = []
    for item in merge_pairs or []:
        out.append({
            "original_session_id": item.get("original_session_id"),
            "resolved_session_id": item.get("resolved_session_id"),
            "decision_choice": item.get("decision_choice"),
            "conflict_like": item.get("conflict", False),
            "merge_status": item.get("merge_status"),
        })
    return out


def commit_portable_local_outcome_package_three_way_merge_resolution(
    project_index: dict,
    merge_resolution_result: dict,
    commit_name: str | None = None,
    promote_point_name: str | None = None,
    promote_point_kind: str = "release",
    note: str | None = None,
) -> tuple[dict, dict]:
    project_index = _normalize(project_index)

    if not isinstance(merge_resolution_result, dict):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError("merge_resolution_result must be an object")
    if merge_resolution_result.get("portable_local_outcome_package_three_way_merge_resolution_version") != "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_RESOLUTION_v0.1":
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError("Unsupported or missing portable local outcome merge resolution version")

    resolved_session_ids = list(merge_resolution_result.get("resolved_session_ids") or [])
    if not resolved_session_ids:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError("No resolved_session_ids to commit")

    resolved_commit_name = (
        commit_name or f"{merge_resolution_result.get('resolution_name', 'portable_local_merge_resolution')}_commit"
    ).strip()
    if not resolved_commit_name:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError("commit_name is required")
    if resolved_commit_name in (project_index.get("portable_local_outcome_set_package_merge_commits") or {}):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError(
            f"Portable local outcome package merge commit already exists: {resolved_commit_name}"
        )
    if resolved_commit_name in (project_index.get("local_outcome_set_package_commits") or {}):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError(
            f"Local outcome set package commit already exists: {resolved_commit_name}"
        )

    out = deepcopy(project_index)
    last_resolved_session_id = resolved_session_ids[-1]
    last_entry = next((item for item in out.get("sessions", []) if item["session_id"] == last_resolved_session_id), None)
    if not last_entry:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError(
            f"Resolved merged session not found in project: {last_resolved_session_id}"
        )

    promoted_point_result = None
    promoted_point_name_resolved = None
    promoted_point_kind_resolved = None
    if promote_point_name and promote_point_name.strip():
        promoted_point_name_resolved = promote_point_name.strip()
        promoted_point_kind_resolved = (promote_point_kind or "release").strip() or "release"
        out, promoted_point_result = create_tag_release_point(
            out,
            tag_name=promoted_point_name_resolved,
            target_session_id=last_resolved_session_id,
            point_kind=promoted_point_kind_resolved,
            note=note,
        )

    package_name, source_commit_name = _derive_shared_metadata(project_index, merge_resolution_result)
    commit_entry = {
        "commit_name": resolved_commit_name,
        "resolution_name": merge_resolution_result.get("resolution_name"),
        "package_name": package_name,
        "source_commit_name": source_commit_name,
        "base_commit_name": merge_resolution_result.get("base_commit_name"),
        "left_commit_name": merge_resolution_result.get("left_commit_name"),
        "right_commit_name": merge_resolution_result.get("right_commit_name"),
        "target_branch_name": merge_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": list(merge_resolution_result.get("skipped_session_ids") or []),
        "merge_pairs": deepcopy(merge_resolution_result.get("merge_pairs") or []),
        "resolution_pairs": _resolution_pairs_from_merge_pairs(merge_resolution_result.get("merge_pairs") or []),
        "decision_counts": deepcopy((merge_resolution_result.get("summary") or {}).get("decision_counts") or {}),
        "promoted_point_name": promoted_point_name_resolved,
        "promoted_point_kind": promoted_point_kind_resolved,
        "note": note,
        "commit_kind": "portable_local_outcome_package_three_way_merge_commit",
    }

    out.setdefault("portable_local_outcome_set_package_merge_commits", {})[resolved_commit_name] = deepcopy(commit_entry)
    out.setdefault("local_outcome_set_package_commits", {})[resolved_commit_name] = deepcopy(commit_entry)

    out = append_history_event(
        out,
        "portable_local_outcome_package_three_way_merge_committed",
        f"Portable local outcome package three-way merge committed: {resolved_commit_name}",
        session_id=last_resolved_session_id,
        session_name=last_entry.get("session_name"),
        payload={
            "commit_name": resolved_commit_name,
            "resolution_name": merge_resolution_result.get("resolution_name"),
            "base_commit_name": merge_resolution_result.get("base_commit_name"),
            "left_commit_name": merge_resolution_result.get("left_commit_name"),
            "right_commit_name": merge_resolution_result.get("right_commit_name"),
            "target_branch_name": merge_resolution_result.get("target_branch_name"),
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
        },
    )

    result = {
        "portable_local_outcome_package_three_way_merge_commit_version": "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_COMMIT_PROMOTE_v0.1",
        "commit_name": resolved_commit_name,
        "resolution_name": merge_resolution_result.get("resolution_name"),
        "base_commit_name": merge_resolution_result.get("base_commit_name"),
        "left_commit_name": merge_resolution_result.get("left_commit_name"),
        "right_commit_name": merge_resolution_result.get("right_commit_name"),
        "target_branch_name": merge_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(merge_resolution_result.get("skipped_session_ids") or []),
            "promoted": promoted_point_result is not None,
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
```


## FILE: tooling/workspace_navigation.py

Size: 6689 bytes

```file

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Set, Tuple
import re

ENT_RE = re.compile(r"\[ENT:([A-Z0-9_]+)\]")
STATE_RE = re.compile(r"\[STA:([A-Z0-9_]+)")

PRODUCER_ROLES = {"dst", "res", "right"}
CONSUMER_ROLES = {"src", "code", "cau", "left", "obj", "ctx", "agt"}
STATE_ROLES = {"ctx"}


def _parse_label_tokens(label: str | None) -> Set[str]:
    if not label:
        return set()
    return set(ENT_RE.findall(label))


def _parse_state_tokens(label: str | None) -> Set[str]:
    if not label:
        return set()
    return set(STATE_RE.findall(label))


def _collect_from_value(value: dict, role_name: str | None, signals: dict) -> None:
    kind = value["kind"]
    if kind == "node":
        class_name = value["class_name"]
        root = value["root"]
        if class_name == "ENT":
            signals["entities"].add(root)
            if role_name in PRODUCER_ROLES:
                signals["outputs"].add(root)
            if role_name in CONSUMER_ROLES:
                signals["inputs"].add(root)
        elif class_name == "STA":
            signals["state_nodes"].add(root)
        for role in value.get("roles", []):
            _collect_from_value(role["value"], role["name"], signals)
    elif kind == "list":
        for item in value.get("items", []):
            _collect_from_value(item, role_name, signals)
    elif kind == "typed_literal":
        if value.get("class_name") == "STA":
            signals["state_nodes"].add(value["root"])


def summarize_session_entry(entry: dict) -> dict:
    session = entry["session"]
    doc = session.get("documents", {}).get("decomposed_ast_document") or session.get("documents", {}).get("ast_document")
    signals = {
        "entities": set(),
        "inputs": set(),
        "outputs": set(),
        "state_nodes": set(),
    }
    if doc and doc.get("ast"):
        _collect_from_value(doc["ast"], None, signals)

    final_state = session.get("reports", {}).get("state_report", {}).get("final_state", {}) or {}
    for dep in final_state.get("dependencies", []):
        signals["outputs"].update(_parse_label_tokens(dep.get("dst")))
        signals["inputs"].update(_parse_label_tokens(dep.get("src")))
        signals["entities"].update(_parse_label_tokens(dep.get("dst")))
        signals["entities"].update(_parse_label_tokens(dep.get("src")))

    for exp in final_state.get("expansions", []):
        signals["inputs"].update(_parse_label_tokens(exp.get("src")))
        signals["outputs"].update(_parse_label_tokens(exp.get("res")))
        signals["entities"].update(_parse_label_tokens(exp.get("src")))
        signals["entities"].update(_parse_label_tokens(exp.get("res")))

    for action in final_state.get("actions", []):
        signals["inputs"].update(_parse_label_tokens(action.get("agt")))
        signals["entities"].update(_parse_label_tokens(action.get("agt")))
        signals["entities"].update(_parse_label_tokens(action.get("obj")))

    for obs in final_state.get("observations", []):
        signals["inputs"].update(_parse_label_tokens(obs.get("agt")))
        signals["entities"].update(_parse_label_tokens(obs.get("agt")))
        signals["entities"].update(_parse_label_tokens(obs.get("obj")))

    states = final_state.get("states", {}) or {}
    for entity_name, state_list in states.items():
        signals["entities"].add(entity_name)
        for st in state_list:
            signals["state_nodes"].add(st)

    return {
        "session_id": entry["session_id"],
        "session_name": entry["session_name"],
        "profile": entry.get("profile"),
        "source_mode": entry.get("source_mode"),
        "tags": list(entry.get("tags", [])),
        "entities": sorted(signals["entities"]),
        "inputs": sorted(signals["inputs"]),
        "outputs": sorted(signals["outputs"]),
        "state_nodes": sorted(signals["state_nodes"]),
    }


def _grid_position(index: int, cols: int = 3) -> tuple[int, int]:
    col = index % cols
    row = index // cols
    return 120 + col * 240, 80 + row * 170


def build_workspace_dependency_map(project_index: dict) -> dict:
    summaries = [summarize_session_entry(entry) for entry in project_index.get("sessions", [])]
    nodes = []
    for idx, summary in enumerate(summaries):
        x, y = _grid_position(idx)
        nodes.append({
            "session_id": summary["session_id"],
            "session_name": summary["session_name"],
            "profile": summary.get("profile"),
            "tags": summary.get("tags", []),
            "entities": summary["entities"],
            "inputs": summary["inputs"],
            "outputs": summary["outputs"],
            "state_nodes": summary["state_nodes"],
            "x": x,
            "y": y,
            "is_active": summary["session_id"] == project_index.get("active_session_id"),
        })

    links = []
    seen_shared = set()
    for i, a in enumerate(summaries):
        for j, b in enumerate(summaries):
            if i == j:
                continue
            flow_tokens = sorted(set(a["outputs"]) & set(b["inputs"]))
            if flow_tokens:
                links.append({
                    "from_session_id": a["session_id"],
                    "to_session_id": b["session_id"],
                    "relation": "flow",
                    "tokens": flow_tokens,
                    "weight": len(flow_tokens),
                })

        for j in range(i + 1, len(summaries)):
            b = summaries[j]
            shared_tokens = sorted((set(a["entities"]) & set(b["entities"])) - (set(a["outputs"]) & set(b["inputs"])) - (set(b["outputs"]) & set(a["inputs"])))
            if shared_tokens:
                key = (a["session_id"], b["session_id"])
                if key not in seen_shared:
                    seen_shared.add(key)
                    links.append({
                        "from_session_id": a["session_id"],
                        "to_session_id": b["session_id"],
                        "relation": "shared",
                        "tokens": shared_tokens,
                        "weight": len(shared_tokens),
                    })

    return {
        "dependency_map_version": "SEMASCRIPT_WORKSPACE_NAVIGATION_MAP_v0.1",
        "project_name": project_index.get("project_name"),
        "active_session_id": project_index.get("active_session_id"),
        "nodes": nodes,
        "links": links,
        "summary": {
            "session_count": len(nodes),
            "flow_link_count": sum(1 for link in links if link["relation"] == "flow"),
            "shared_link_count": sum(1 for link in links if link["relation"] == "shared"),
        },
    }
```


## FILE: tooling/workspace_timeline.py

Size: 3297 bytes

```file

from __future__ import annotations

from copy import deepcopy
from typing import Optional


def _history_container(project_index: dict) -> dict:
    history = project_index.setdefault("history", {})
    history.setdefault("events", [])
    history.setdefault("next_seq", 1)
    return history


def _make_event(seq: int, event_type: str, title: str, session_id: Optional[str] = None, session_name: Optional[str] = None, payload: Optional[dict] = None) -> dict:
    return {
        "seq": seq,
        "event_type": event_type,
        "title": title,
        "session_id": session_id,
        "session_name": session_name,
        "payload": deepcopy(payload or {}),
    }


def append_history_event(
    project_index: dict,
    event_type: str,
    title: str,
    session_id: Optional[str] = None,
    session_name: Optional[str] = None,
    payload: Optional[dict] = None,
) -> dict:
    out = deepcopy(project_index)
    history = _history_container(out)
    seq = history["next_seq"]
    history["events"].append(_make_event(seq, event_type, title, session_id=session_id, session_name=session_name, payload=payload))
    history["next_seq"] = seq + 1
    return out


def ensure_workspace_history(project_index: dict) -> dict:
    out = deepcopy(project_index)
    history = _history_container(out)
    if history["events"]:
        return out

    out = append_history_event(
        out,
        "workspace_created",
        f"Workspace created: {out.get('project_name', 'Untitled SEMASCRIPT Project')}",
        payload={"project_name": out.get("project_name")},
    )
    for item in out.get("sessions", []):
        out = append_history_event(
            out,
            "session_added",
            f"Session added: {item.get('session_name', item['session_id'])}",
            session_id=item["session_id"],
            session_name=item.get("session_name"),
            payload={"profile": item.get("profile"), "source_mode": item.get("source_mode")},
        )
    active_id = out.get("active_session_id")
    if active_id:
        active = next((item for item in out.get("sessions", []) if item["session_id"] == active_id), None)
        out = append_history_event(
            out,
            "active_session_set",
            f"Active session set: {active.get('session_name', active_id) if active else active_id}",
            session_id=active_id,
            session_name=active.get("session_name") if active else active_id,
        )
    return out


def build_workspace_timeline(project_index: dict) -> dict:
    project_index = ensure_workspace_history(project_index)
    events = deepcopy(project_index.get("history", {}).get("events", []))
    for idx, event in enumerate(events):
        event["x"] = 80 + idx * 170
        event["y"] = 44 if idx % 2 == 0 else 112
        event["is_active_session_event"] = event.get("session_id") == project_index.get("active_session_id")
    return {
        "timeline_version": "SEMASCRIPT_WORKSPACE_TIMELINE_v0.1",
        "project_name": project_index.get("project_name"),
        "active_session_id": project_index.get("active_session_id"),
        "events": events,
        "summary": {
            "event_count": len(events),
            "session_event_count": sum(1 for e in events if e.get("session_id")),
        },
    }
```


## FILE: tooling/graph_model.py

Size: 6604 bytes

```file

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import json


GraphEntity = Dict[str, Any]
GraphEdge = Dict[str, Any]
GraphDoc = Dict[str, Any]
ASTValue = Dict[str, Any]


class GraphModelError(Exception):
    """Raised when graph model cannot be converted."""


def _entity_kind_label(entity: GraphEntity) -> str:
    kind = entity["kind"]
    if kind == "node":
        return f"{entity['class_name']}:{entity['root']}"
    if kind == "list":
        return "LIST"
    if kind == "raw_token":
        return entity["value"]
    if kind == "typed_literal":
        if entity.get("value") is not None:
            return f"{entity['class_name']}:{entity['root']}={entity['value']}"
        return f"{entity['class_name']}:{entity['root']}"
    return entity["id"]


def _new_entity_id(counter: List[int]) -> str:
    counter[0] += 1
    return f"e{counter[0]}"


def _value_to_graph(value: ASTValue, entities: List[GraphEntity], edges: List[GraphEdge], counter: List[int], x: float, y: float) -> str:
    kind = value["kind"]
    eid = _new_entity_id(counter)

    if kind == "node":
        entity = {
            "id": eid,
            "kind": "node",
            "class_name": value["class_name"],
            "root": value["root"],
            "modifiers": list(value.get("modifiers", [])),
            "x": x,
            "y": y,
        }
        entities.append(entity)
        child_y = y + 120
        for index, role in enumerate(value.get("roles", [])):
            child_id = _value_to_graph(role["value"], entities, edges, counter, x + (index - 1) * 180, child_y + index * 24)
            edges.append({
                "id": f"edge_{eid}_{child_id}_{index}",
                "from_id": eid,
                "to_id": child_id,
                "role": role["name"],
                "order": index,
            })
        return eid

    if kind == "list":
        entity = {
            "id": eid,
            "kind": "list",
            "label": "LIST",
            "x": x,
            "y": y,
        }
        entities.append(entity)
        child_y = y + 110
        for index, item in enumerate(value.get("items", [])):
            child_id = _value_to_graph(item, entities, edges, counter, x + (index - 1) * 180, child_y + index * 24)
            edges.append({
                "id": f"edge_{eid}_{child_id}_{index}",
                "from_id": eid,
                "to_id": child_id,
                "role": f"item_{index}",
                "order": index,
            })
        return eid

    if kind == "raw_token":
        entities.append({
            "id": eid,
            "kind": "raw_token",
            "value": value["value"],
            "x": x,
            "y": y,
        })
        return eid

    if kind == "typed_literal":
        entities.append({
            "id": eid,
            "kind": "typed_literal",
            "class_name": value["class_name"],
            "root": value["root"],
            "value": value.get("value"),
            "x": x,
            "y": y,
        })
        return eid

    raise GraphModelError(f"Unsupported AST value kind: {kind}")


def ast_document_to_graph_document(ast_doc: Dict[str, Any]) -> GraphDoc:
    entities: List[GraphEntity] = []
    edges: List[GraphEdge] = []
    counter = [0]
    root_id = _value_to_graph(ast_doc["ast"], entities, edges, counter, 320, 80)
    return {
        "graph_version": "SEMASCRIPT_GRAPH_MODEL_v0.1",
        "profile": ast_doc.get("source_profile", "core"),
        "source_text": ast_doc.get("source_text"),
        "root_entity_id": root_id,
        "entities": entities,
        "edges": edges,
        "metadata": {
            "generated_from_ast": True,
        },
    }


def _entity_index(graph_doc: GraphDoc) -> Dict[str, GraphEntity]:
    return {entity["id"]: entity for entity in graph_doc.get("entities", [])}


def _outgoing_edges(graph_doc: GraphDoc, entity_id: str) -> List[GraphEdge]:
    edges = [edge for edge in graph_doc.get("edges", []) if edge["from_id"] == entity_id]
    edges.sort(key=lambda e: (e.get("order", 0), e["role"], e["to_id"]))
    return edges


def _entity_to_ast(entity_id: str, graph_doc: GraphDoc, index: Dict[str, GraphEntity]) -> ASTValue:
    if entity_id not in index:
        raise GraphModelError(f"Missing entity: {entity_id}")

    entity = index[entity_id]
    kind = entity["kind"]

    if kind == "node":
        roles = []
        for edge in _outgoing_edges(graph_doc, entity_id):
            roles.append({
                "name": edge["role"],
                "value": _entity_to_ast(edge["to_id"], graph_doc, index),
            })
        return {
            "kind": "node",
            "class_name": entity["class_name"],
            "root": entity["root"],
            "modifiers": list(entity.get("modifiers", [])),
            "roles": roles,
        }

    if kind == "list":
        items = []
        for edge in _outgoing_edges(graph_doc, entity_id):
            items.append(_entity_to_ast(edge["to_id"], graph_doc, index))
        return {
            "kind": "list",
            "items": items,
        }

    if kind == "raw_token":
        return {
            "kind": "raw_token",
            "value": entity["value"],
        }

    if kind == "typed_literal":
        return {
            "kind": "typed_literal",
            "class_name": entity["class_name"],
            "root": entity["root"],
            "value": entity.get("value"),
        }

    raise GraphModelError(f"Unsupported graph entity kind: {kind}")


def graph_document_to_ast_document(graph_doc: GraphDoc) -> Dict[str, Any]:
    root_id = graph_doc.get("root_entity_id")
    if not root_id:
        raise GraphModelError("Graph document has no root_entity_id")

    index = _entity_index(graph_doc)
    root_value = _entity_to_ast(root_id, graph_doc, index)
    if root_value["kind"] != "node":
        raise GraphModelError("Graph root must resolve to AST node")

    return {
        "schema_version": "SEMASCRIPT_AST_SCHEMA_v0.1",
        "source_profile": graph_doc.get("profile", "core"),
        "source_text": graph_doc.get("source_text"),
        "ast": root_value,
        "validation_annotations": [],
        "metadata": {
            "generated_from_graph": True,
        },
    }


def save_graph_document(graph_doc: GraphDoc, path: str | Path) -> None:
    Path(path).write_text(json.dumps(graph_doc, ensure_ascii=False, indent=2), encoding="utf-8")


def load_graph_document(path: str | Path) -> GraphDoc:
    return json.loads(Path(path).read_text(encoding="utf-8"))
```


## FILE: tooling/run_v0_2_hardening_suite.py

Size: 1761 bytes

```file

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    base = Path(__file__).parent
    scripts = [
        "run_environment_bootstrap_checks.py",
        "run_fixture_validation.py",
        "run_human_normalization_checks.py",
        "run_pattern_decomposition_checks.py",
        "run_exec_runtime_checks.py",
        "run_state_model_checks.py",
        "run_batch_runtime_state_corpus_checks.py",
        "run_svg_renderer_checks.py",
        "run_hardening_human_checks.py",
        "run_hardening_runtime_checks.py",
        "run_hardening_state_checks.py",
        "run_inspector_smoke_checks.py",
        "run_inspector_http_smoke_checks.py",
        "run_inspector_http_e2e_checks.py",
        "run_inspector_http_project_ops_e2e_checks.py",
        "run_inspector_http_lifecycle_import_e2e_checks.py",
        "run_inspector_http_graph_session_e2e_checks.py",
    ]
    expected_markers = {
        "run_environment_bootstrap_checks.py": "env_bootstrap_self_check: passed=",
    }

    ok = True
    for script in scripts:
        proc = subprocess.run([sys.executable, str(base / script)], cwd=str(base), capture_output=True, text=True, check=False)
        print(proc.stdout.strip())
        if proc.returncode != 0:
            ok = False
        expected_marker = expected_markers.get(script)
        if expected_marker and expected_marker not in proc.stdout:
            ok = False
        if "failed=0" not in proc.stdout and "passed=1 failed=0" not in proc.stdout:
            ok = False

    if ok:
        print("v0_2_hardening_suite: passed=1 failed=0 total=1")
    else:
        print("v0_2_hardening_suite: passed=0 failed=1 total=1")


if __name__ == "__main__":
    main()
```


## FILE: inspector/index.html

Size: 32496 bytes

```file
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <title>SEMASCRIPT Inspector — Interactive Merge Workstation v2</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="/styles.css" />
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <h1>SEMASCRIPT Inspector</h1>
        <p>Interactive Merge Workstation v2 for portable local outcome reconciliation</p>
      </div>

      <div class="panel">
        <label for="profile">Profile</label>
        <select id="profile">
          <option value="human" selected>human</option>
          <option value="core">core</option>
          <option value="exec">exec</option>
        </select>
        <p id="profileHint" class="field-hint">
          Human-friendly shorthand and aliases. Example: <code>gen(template -&gt; instance)</code>
        </p>

        <label class="checkbox">
          <input type="checkbox" id="decompose" checked />
          <span>Decompose patterns</span>
        </label>

        <label for="sessionName">Session name</label>
        <input id="sessionName" type="text" placeholder="Untitled SEMASCRIPT Session" />
        <label for="projectName">Project name</label>
        <input id="projectName" type="text" placeholder="Untitled SEMASCRIPT Project" />
        <label for="inputText">Input</label>
        <textarea id="inputText" spellcheck="false" placeholder="gen(template -&gt; instance)"></textarea>
        <label for="initialState">Initial state (JSON, optional)</label>
        <textarea id="initialState" class="small" spellcheck="false"></textarea>

        <div class="actions triple">
          <button id="analyzeBtn">Analyze text</button>
          <button id="importGraphBtn">Text → graph</button>
          <button id="clearBtn" class="secondary">Clear</button>
        </div>
      </div>

      <div class="panel">
        <div class="samples-head">
          <h2>Samples</h2>
          <button id="reloadSamples" class="secondary">Reload</button>
        </div>
        <div id="samplesList" class="samples-list"></div>
      </div>

      <div class="panel">
        <div class="samples-head"><h2>Session actions</h2></div>
        <div class="actions triple">
          <button id="exportTextSessionBtn">Export text session</button>
          <button id="exportGraphSessionBtn">Export graph session</button>
          <button id="downloadSessionBtn" class="secondary">Download</button>
        </div>
        <label for="sessionJson">Session JSON</label>
        <textarea id="sessionJson" class="small" spellcheck="false"></textarea>
        <button id="importSessionBtn">Import session</button>
      </div>

      <div class="panel">
        <div class="samples-head"><h2>Project workspace</h2></div>
        <div class="actions triple">
          <button id="addCurrentToProjectBtn">Add current session</button>
          <button id="exportProjectBtn">Export project</button>
          <button id="downloadProjectBtn" class="secondary">Download</button>
        </div>
        <label for="projectJson">Project index JSON</label>
        <textarea id="projectJson" class="small" spellcheck="false"></textarea>
        <div class="actions triple">
          <button id="importProjectBtn">Import project</button>
          <button id="reloadProjectBtn" class="secondary">Refresh list</button>
          <button id="clearProjectBtn" class="secondary">Clear project</button>
        </div>
        <div id="projectSessionsList" class="samples-list"></div>
        <div class="samples-head">
          <h2>Dependency map</h2>
        </div>
        <div id="projectDependencyMap" class="project-map"></div>
        <div class="samples-head">
          <h2>Workspace timeline</h2>
        </div>
        <div id="projectTimeline" class="project-timeline"></div>
        <div class="samples-head">
          <h2>Named merge lineage graph</h2>
        </div>
        <div id="projectLineageGraph" class="project-map"></div>
      </div>

      <div class="panel">
        <div class="samples-head"><h2>Branch / release points</h2></div>
        <label for="newBranchName">New branch name</label>
        <input id="newBranchName" type="text" placeholder="feature_branch_v1" />
        <button id="createBranchBtn">Create branch from active session</button>
        <div id="branchList" class="samples-list"></div>

        <div class="samples-head">
          <h2>Tag / release points</h2>
        </div>
        <label for="tagPointName">Point name</label>
        <input id="tagPointName" type="text" placeholder="release_v1" />
        <label for="tagPointKind">Point kind</label>
        <select id="tagPointKind">
          <option value="tag" selected>tag</option>
          <option value="release">release</option>
        </select>
        <label for="tagTargetSession">Target session</label>
        <select id="tagTargetSession"></select>
        <label for="tagPointNote">Point note</label>
        <input id="tagPointNote" type="text" placeholder="mark project milestone" />
        <button id="createTagPointBtn">Create tag / release point</button>
        <div id="tagPointList" class="samples-list"></div>
        <pre id="tagPointResultText" class="codeblock compact"></pre>
      </div>

      <div class="panel">
        <div class="samples-head"><h2>Snapshot workflows</h2></div>
        <label for="snapshotSourcePoint">Snapshot source point</label>
        <select id="snapshotSourcePoint"></select>
        <label for="snapshotName">Snapshot name</label>
        <input id="snapshotName" type="text" placeholder="snapshot_v1" />
        <label for="snapshotNote">Snapshot note</label>
        <input id="snapshotNote" type="text" placeholder="portable project snapshot" />
        <div class="actions triple">
          <button id="createSnapshotBtn">Create snapshot export</button>
          <button id="downloadSnapshotBtn" class="secondary">Download current snapshot</button>
          <button id="refreshSnapshotSelectorsBtn" class="secondary">Refresh snapshot selectors</button>
        </div>
        <div id="snapshotList" class="samples-list"></div>
        <pre id="snapshotResultText" class="codeblock compact"></pre>

        <div class="samples-head">
          <h2>Snapshot restore / partial import</h2>
        </div>
        <label for="snapshotRestoreJson">Snapshot package JSON</label>
        <textarea id="snapshotRestoreJson" class="small" spellcheck="false" placeholder="Paste snapshot export package JSON here"></textarea>
        <div id="snapshotPackageHint" class="package-guidance"></div>
        <label for="restoredProjectName">Restored project name</label>
        <input id="restoredProjectName" type="text" placeholder="restored_project_v1" />
        <label for="snapshotRestoreName">Restore name</label>
        <input id="snapshotRestoreName" type="text" placeholder="snapshot_restore_v1" />
        <label class="checkbox">
          <input type="checkbox" id="activateRestoredAnchor" checked />
          <span>Activate restored anchor</span>
        </label>
        <div class="actions triple">
          <button id="loadCurrentSnapshotForRestoreBtn">Use current snapshot</button>
          <button id="previewSnapshotRestoreBtn" class="secondary">Preview restore</button>
          <button id="restoreFromSnapshotBtn">Restore from snapshot</button>
        </div>
        <div class="actions triple">
          <button id="clearSnapshotRestoreBtn" class="secondary">Clear restore input</button>
        </div>
        <pre id="snapshotRestorePreviewText" class="codeblock compact"></pre>
        <pre id="snapshotRestoreResultText" class="codeblock compact"></pre>

        <label for="partialImportSessionIds">Partial import session ids (CSV)</label>
        <input id="partialImportSessionIds" type="text" placeholder="session_a, session_b" />
        <label for="partialImportTagNames">Partial import tag names (CSV)</label>
        <input id="partialImportTagNames" type="text" placeholder="release_v1, tag_v2" />
        <label for="partialImportSnapshotNames">Partial import snapshot names (CSV)</label>
        <input id="partialImportSnapshotNames" type="text" placeholder="snapshot_v1" />
        <div id="partialImportSelectionHint" class="field-hint"></div>
        <label for="partialImportTargetBranch">Partial import target branch</label>
        <select id="partialImportTargetBranch"></select>
        <label for="partialImportName">Partial import name</label>
        <input id="partialImportName" type="text" placeholder="partial_import_v1" />
        <label class="checkbox">
          <input type="checkbox" id="activatePartialImportHead" checked />
          <span>Activate last imported head</span>
        </label>
        <div class="actions triple">
          <button id="useCurrentSnapshotForPartialBtn">Use current snapshot</button>
          <button id="partialImportFromSnapshotBtn">Apply partial import</button>
          <button id="clearPartialImportBtn" class="secondary">Clear partial import</button>
        </div>
        <pre id="partialImportResultText" class="codeblock compact"></pre>

        <div class="samples-head">
          <h2>Snapshot reconcile</h2>
        </div>
        <label for="snapshotReconcileSessionIds">Reconcile session ids (CSV)</label>
        <input id="snapshotReconcileSessionIds" type="text" placeholder="session_a, session_b" />
        <div id="snapshotReconcileSessionHint" class="field-hint"></div>
        <label for="snapshotReconcileTargetBranch">Reconcile target branch</label>
        <select id="snapshotReconcileTargetBranch"></select>
        <label for="snapshotReconcileName">Reconcile name</label>
        <input id="snapshotReconcileName" type="text" placeholder="snapshot_reconcile_v1" />
        <label class="checkbox">
          <input type="checkbox" id="activateSnapshotReconcileHead" checked />
          <span>Activate reconciled head</span>
        </label>
        <div class="actions triple">
          <button id="useCurrentSnapshotForReconcileBtn">Use current snapshot</button>
          <button id="previewSnapshotReconcileBtn" class="secondary">Preview reconcile</button>
          <button id="reconcileSnapshotBtn">Reconcile snapshot</button>
        </div>
        <div class="actions triple">
          <button id="clearSnapshotReconcileBtn" class="secondary">Clear reconcile input</button>
        </div>
        <div id="snapshotReconcileList" class="samples-list"></div>
        <pre id="snapshotReconcilePreviewText" class="codeblock compact"></pre>
        <div id="snapshotReconcileDecisionList" class="conflict-list"></div>
        <div class="actions triple">
          <button id="useSnapshotForAllReconcileBtn">Use snapshot for all</button>
          <button id="useCurrentForAllConflictsBtn">Use current for conflicts</button>
          <button id="applySnapshotReconcileDecisionsBtn" class="secondary">Apply decisions</button>
        </div>
        <pre id="snapshotReconcileResultText" class="codeblock compact"></pre>

        <label for="snapshotReconcileCommitName">Reconcile commit name</label>
        <input id="snapshotReconcileCommitName" type="text" placeholder="snapshot_reconcile_commit_v1" />
        <label for="snapshotReconcilePromotePointName">Promote point name</label>
        <input id="snapshotReconcilePromotePointName" type="text" placeholder="snapshot_reconcile_release_v1" />
        <label for="snapshotReconcilePromotePointKind">Promote point kind</label>
        <select id="snapshotReconcilePromotePointKind">
          <option value="release" selected>release</option>
          <option value="tag">tag</option>
        </select>
        <label for="snapshotReconcileCommitNote">Commit note</label>
        <input id="snapshotReconcileCommitNote" type="text" placeholder="commit reconciled snapshot outcome" />
        <button id="commitSnapshotReconcileBtn">Commit reconciled snapshot outcome</button>
        <div id="snapshotReconcileCommitList" class="samples-list"></div>
        <pre id="snapshotReconcileCommitResultText" class="codeblock compact"></pre>

        <div class="samples-head">
          <h2>Reconciled outcome compare</h2>
        </div>
        <label for="compareReconcileCommitLeft">Left reconcile commit</label>
        <select id="compareReconcileCommitLeft"></select>
        <label for="compareReconcileCommitRight">Right reconcile commit</label>
        <select id="compareReconcileCommitRight"></select>
        <button id="compareReconcileCommitsBtn">Compare reconciled outcomes</button>
        <pre id="compareReconcileCommitResultText" class="codeblock compact"></pre>
      </div>

      <div class="panel">
        <div class="samples-head"><h2>Project operations / packages</h2></div>

<div class="samples-head">
  <h2>Cross-session compare</h2>
</div>
<label for="compareLeftSession">Left session</label>
<select id="compareLeftSession"></select>
<label for="compareRightSession">Right session</label>
<select id="compareRightSession"></select>
<button id="compareSessionsBtn">Compare sessions</button>
<pre id="compareResultText" class="codeblock compact"></pre>

<div class="samples-head">
  <h2>Three-way merge / conflicts</h2>
</div>
<label for="mergeBaseSession">Base session</label>
<select id="mergeBaseSession"></select>
<label for="mergeLeftSession">Left session</label>
<select id="mergeLeftSession"></select>
<label for="mergeRightSession">Right session</label>
<select id="mergeRightSession"></select>
<button id="mergeSessionsBtn">Run three-way merge</button>
<pre id="mergeResultText" class="codeblock compact"></pre>

<div class="samples-head">
  <h2>Interactive conflict resolution</h2>
</div>
<div id="mergeConflictList" class="conflict-list"></div>
<div class="actions triple">
  <button id="useLeftForAllConflictsBtn">Use left for all</button>
  <button id="useRightForAllConflictsBtn">Use right for all</button>
  <button id="applyMergeDecisionsBtn" class="secondary">Apply decisions</button>
</div>
<pre id="resolvedMergeText" class="codeblock compact"></pre>

<div class="samples-head">
  <h2>Merge commit</h2>
</div>
<label for="mergeCommitSessionId">Commit session id</label>
<input id="mergeCommitSessionId" type="text" placeholder="merge_commit_session" />
<label for="mergeCommitSessionName">Commit session name</label>
<input id="mergeCommitSessionName" type="text" placeholder="Merged Session Commit" />
<label for="mergeCommitBranchName">Target branch</label>
<input id="mergeCommitBranchName" type="text" placeholder="main" />
<label class="checkbox">
  <input type="checkbox" id="activateCommittedSession" checked />
  <span>Activate committed session</span>
</label>
<button id="commitMergedSessionBtn">Commit merged session to workspace</button>
<pre id="mergeCommitResultText" class="codeblock compact"></pre>

<div class="samples-head">
  <h2>Branch operations</h2>
</div>
<label for="rebaseSourceBranch">Rebase source branch</label>
<select id="rebaseSourceBranch"></select>
<label for="rebaseTargetBranch">Rebase target branch</label>
<select id="rebaseTargetBranch"></select>
<label class="checkbox">
  <input type="checkbox" id="activateRebasedHead" checked />
  <span>Activate rebased head</span>
</label>
<button id="rebaseBranchBtn">Rebase branch onto target</button>
<pre id="rebaseResultText" class="codeblock compact"></pre>

<label for="resetBranchName">Reset branch</label>
<select id="resetBranchName"></select>
<label for="resetTargetSession">Reset target session</label>
<select id="resetTargetSession"></select>
<label class="checkbox">
  <input type="checkbox" id="activateResetHead" checked />
  <span>Activate reset head</span>
</label>
<button id="resetBranchHeadBtn">Reset branch head</button>
<pre id="branchResetResultText" class="codeblock compact"></pre>

<label for="cherryPickSessionIds">Cherry-pick session ids (CSV)</label>
<input id="cherryPickSessionIds" type="text" placeholder="session_a, session_b" />
<label for="cherryPickTargetBranch">Cherry-pick target branch</label>
<select id="cherryPickTargetBranch"></select>
<label class="checkbox">
  <input type="checkbox" id="activateCherryPickedHead" checked />
  <span>Activate cherry-picked head</span>
</label>
<button id="cherryPickSessionsBtn">Cherry-pick sessions</button>
<pre id="cherryPickResultText" class="codeblock compact"></pre>

<label for="squashSessionIds">Squash session ids (CSV)</label>
<input id="squashSessionIds" type="text" placeholder="session_a, session_b" />
<label for="squashTargetBranch">Squash target branch</label>
<select id="squashTargetBranch"></select>
<label for="squashSessionId">Squash commit session id</label>
<input id="squashSessionId" type="text" placeholder="squash_commit_v1" />
<label for="squashSessionName">Squash commit session name</label>
<input id="squashSessionName" type="text" placeholder="Squashed Session Commit" />
<label class="checkbox">
  <input type="checkbox" id="activateSquashedHead" checked />
  <span>Activate squashed head</span>
</label>
<button id="squashSessionsBtn">Squash sessions into commit</button>
<pre id="squashResultText" class="codeblock compact"></pre>



<div class="samples-head">
  <h2>Standalone outcome package diff / compatibility</h2>
</div>
<label for="exportReconcileCommitName">Promoted outcome commit</label>
<select id="exportReconcileCommitName"></select>
<label for="exportReconcileCommitPackageName">Package name</label>
<input id="exportReconcileCommitPackageName" type="text" placeholder="outcome_package_v1" />
<button id="exportReconcileCommitPackageBtn">Export standalone package</button>
<div id="reconcileCommitPackageCurrentSummary" class="package-guidance"></div>

<label for="importReconcileCommitPackageJson">Standalone package JSON</label>
<textarea id="importReconcileCommitPackageJson" class="small" spellcheck="false" placeholder="Paste standalone promoted outcome package JSON here"></textarea>
<div id="reconcileCommitPackageHint" class="package-guidance"></div>
<label for="importReconcileCommitPackageName">Import name</label>
<input id="importReconcileCommitPackageName" type="text" placeholder="outcome_import_v1" />
<label for="importReconcileCommitTargetBranch">Target branch</label>
<select id="importReconcileCommitTargetBranch"></select>
<label class="checkbox">
  <input type="checkbox" id="activateImportedReconcileCommit" checked />
  <span>Activate imported head</span>
</label>
<div class="actions triple">
  <button id="useCurrentReconcileCommitPackageBtn">Use current exported package</button>
  <button id="previewReconcileCommitPackageBtn" class="secondary">Preview package compatibility</button>
  <button id="importReconcileCommitPackageBtn">Import standalone package</button>
</div>
<div class="actions triple">
  <button id="clearReconcileCommitPackageBtn" class="secondary">Clear package input</button>
</div>
<div id="reconcileCommitPackageList" class="samples-list"></div>
<pre id="reconcileCommitPackagePreviewText" class="codeblock compact"></pre>

<div class="samples-head">
  <h2>Standalone outcome package conflict resolution / manual import decisions</h2>
</div>
<div id="reconcileCommitPackageDecisionList" class="conflict-list"></div>
<div class="actions triple">
  <button id="usePackageForAllImportBtn">Use package for all</button>
  <button id="useCurrentForImportConflictsBtn">Use current for conflicts</button>
  <button id="applyReconcileCommitPackageDecisionsBtn" class="secondary">Apply import decisions</button>
</div>

<pre id="reconcileCommitPackageResultText" class="codeblock compact"></pre>

<div class="samples-head">
  <h2>Standalone outcome package commit / promote imported resolution</h2>
</div>
<label for="reconcileCommitPackageCommitName">Commit / local outcome set name</label>
<input id="reconcileCommitPackageCommitName" type="text" placeholder="local_outcome_set_v1" />
<label for="reconcileCommitPackagePromotePointName">Promote point name</label>
<input id="reconcileCommitPackagePromotePointName" type="text" placeholder="local_release_v1" />
<label for="reconcileCommitPackagePromotePointKind">Promote point kind</label>
<select id="reconcileCommitPackagePromotePointKind">
  <option value="release" selected>release</option>
  <option value="tag">tag</option>
</select>
<label for="reconcileCommitPackageCommitNote">Commit note</label>
<input id="reconcileCommitPackageCommitNote" type="text" placeholder="promote imported outcome" />
<button id="commitReconcileCommitPackageBtn">Commit / promote imported resolution</button>


<div class="samples-head">
  <h2>Local outcome set export / import as portable package</h2>
</div>
<label for="exportLocalOutcomeSetCommit">Local outcome set</label>
<select id="exportLocalOutcomeSetCommit"></select>
<label for="localOutcomeSetPackageName">Package name</label>
<input id="localOutcomeSetPackageName" type="text" placeholder="local_outcome_pkg_v1" />
<label for="localOutcomeSetPackageNote">Package note</label>
<input id="localOutcomeSetPackageNote" type="text" placeholder="portable local outcome package" />
<button id="exportLocalOutcomeSetPackageBtn">Export local outcome package</button>
<div id="localOutcomeSetPackageCurrentSummary" class="package-guidance"></div>

<label for="importLocalOutcomeSetPackageJson">Local outcome package JSON</label>
<textarea id="importLocalOutcomeSetPackageJson" class="small" spellcheck="false" placeholder="Paste portable local outcome package JSON here"></textarea>
<div id="localOutcomeSetPackageHint" class="package-guidance"></div>
<label for="importLocalOutcomeSetPackageNameInput">Import name</label>
<input id="importLocalOutcomeSetPackageNameInput" type="text" placeholder="local_outcome_pkg_import_v1" />
<label for="importLocalOutcomeSetTargetBranch">Target branch</label>
<select id="importLocalOutcomeSetTargetBranch"></select>
<label class="checkbox">
  <input type="checkbox" id="activateImportedLocalOutcomeSet" checked />
  <span>Activate last imported session</span>
</label>
<div class="actions triple">
  <button id="useCurrentLocalOutcomeSetPackageBtn">Use current local package</button>
  <button id="previewLocalOutcomeSetPackageBtn" class="secondary">Preview local package import</button>
  <button id="importLocalOutcomeSetPackageBtn">Import local outcome package</button>
</div>
<div class="actions triple">
  <button id="clearLocalOutcomeSetPackageBtn" class="secondary">Clear local package</button>
</div>
<div id="localOutcomeSetPackageList" class="samples-list"></div>
<pre id="localOutcomeSetPackagePreviewResultText" class="codeblock compact"></pre>
<div id="localOutcomeSetPackageDecisionList" class="conflict-list"></div>
  <div class="actions triple">
    <button id="usePackageForAllLocalOutcomeBtn">Use package for all</button>
    <button id="useCurrentForAllLocalOutcomeConflictsBtn">Use current for conflicts</button>
    <button id="applyLocalOutcomePackageDecisionsBtn" class="secondary">Apply import decisions</button>
  </div>
<pre id="localOutcomeSetPackageResultText" class="codeblock compact"></pre>

  <label for="localOutcomeSetPackageCommitName">Commit name</label>
  <input id="localOutcomeSetPackageCommitName" type="text" placeholder="local_outcome_portable_commit_v1" />
  <label for="localOutcomeSetPackagePromotePointName">Promote point name</label>
  <input id="localOutcomeSetPackagePromotePointName" type="text" placeholder="local_outcome_portable_release_v1" />
  <label for="localOutcomeSetPackagePromotePointKind">Promote point kind</label>
  <select id="localOutcomeSetPackagePromotePointKind">
    <option value="release" selected>release</option>
    <option value="tag">tag</option>
  </select>
  <label for="localOutcomeSetPackageCommitNote">Commit note</label>
  <input id="localOutcomeSetPackageCommitNote" type="text" placeholder="promote resolved portable local outcome package" />
  <button id="commitLocalOutcomeSetPackageBtn">Commit / promote local outcome resolution</button>

  <div class="samples-head">
    <h2>Portable local outcome package baseline / three-way merge</h2>
  </div>
<label for="basePortableLocalOutcomeCommit">Base committed portable local outcome</label>
<select id="basePortableLocalOutcomeCommit"></select>
<label for="leftPortableLocalOutcomeCommit">Left committed portable local outcome</label>
<select id="leftPortableLocalOutcomeCommit"></select>
<label for="rightPortableLocalOutcomeCommit">Right committed portable local outcome</label>
<select id="rightPortableLocalOutcomeCommit"></select>
<button id="compareThreeWayPortableLocalOutcomeBtn">Compare baseline / three-way merge</button>
<pre id="portableLocalOutcomeThreeWayMergeResultText" class="codeblock compact"></pre>


<div class="samples-head">
  <h2>Portable local outcome package three-way conflict resolution</h2>
</div>
<label for="portableLocalOutcomeMergeResolutionName">Merge resolution name</label>
<input id="portableLocalOutcomeMergeResolutionName" type="text" placeholder="portable_local_merge_resolution_v1" />
<label for="portableLocalOutcomeMergeTargetBranch">Target branch</label>
<select id="portableLocalOutcomeMergeTargetBranch"></select>
<div id="portableLocalOutcomeMergeDecisionList" class="conflict-list"></div>
<div class="actions triple">
  <button id="useLeftForAllPortableLocalMergeBtn">Use left for all</button>
  <button id="useRightForAllPortableLocalMergeConflictsBtn">Use right for conflicts</button>
  <button id="applyPortableLocalOutcomeMergeDecisionsBtn" class="secondary">Apply merge decisions</button>
</div>
<pre id="portableLocalOutcomeMergeResolutionResultText" class="codeblock compact"></pre>
<label for="portableLocalOutcomeMergeCommitName">Merge commit name</label>
<input id="portableLocalOutcomeMergeCommitName" type="text" placeholder="portable_local_merge_commit_v1" />
<label for="portableLocalOutcomeMergePromotePointName">Promote point name</label>
<input id="portableLocalOutcomeMergePromotePointName" type="text" placeholder="portable_local_merge_release_v1" />
<label for="portableLocalOutcomeMergePromotePointKind">Promote point kind</label>
<select id="portableLocalOutcomeMergePromotePointKind">
  <option value="release" selected>release</option>
  <option value="tag">tag</option>
</select>
<label for="portableLocalOutcomeMergeCommitNote">Commit note</label>
<input id="portableLocalOutcomeMergeCommitNote" type="text" placeholder="promote resolved portable local merge" />
<button id="commitPortableLocalOutcomeMergeBtn">Commit / promote resolved merge</button>
<pre id="portableLocalOutcomeMergeCommitResultText" class="codeblock compact"></pre>




      </div>

      <div class="panel">
        <div class="samples-head"><h2>Graph actions</h2></div>
        <label for="newEntityKind">Add entity</label>
        <div class="inline-row">
          <select id="newEntityKind">
            <option value="node">node</option>
            <option value="list">list</option>
            <option value="raw_token">raw_token</option>
            <option value="typed_literal">typed_literal</option>
          </select>
          <button id="addEntityBtn">Add</button>
        </div>

        <div class="inline-row">
          <button id="setRootBtn">Set selected as root</button>
          <button id="deleteEntityBtn" class="secondary">Delete selected</button>
        </div>

        <label for="edgeRoleInput">Create edge from selected</label>
        <input id="edgeRoleInput" type="text" placeholder="role name" />
        <label for="edgeTargetSelect">Target entity</label>
        <select id="edgeTargetSelect"></select>
        <button id="addEdgeBtn">Add edge</button>
      </div>

      <div class="panel">
        <div class="samples-head"><h2>Selected entity</h2></div>
        <label>ID</label>
        <input id="entityId" type="text" readonly />
        <label>Kind</label>
        <select id="entityKind">
          <option value="node">node</option>
          <option value="list">list</option>
          <option value="raw_token">raw_token</option>
          <option value="typed_literal">typed_literal</option>
        </select>
        <label>Class</label>
        <input id="entityClass" type="text" />
        <label>Root</label>
        <input id="entityRoot" type="text" />
        <label>Value</label>
        <input id="entityValue" type="text" />
        <label>Modifiers (space separated)</label>
        <input id="entityModifiers" type="text" />
        <button id="saveEntityBtn">Save entity</button>
      </div>
    </aside>

    <main class="main">
      <div class="statusbar"><span id="statusText">Ready</span></div>
      <div class="grid">
        <section class="card wide merge-workstation-card">
          <div class="card-header merge-workstation-header">
            <div>
              <div class="eyebrow">Portable Local Outcome Package</div>
              <h2>Interactive Merge Workstation v2</h2>
            </div>
            <div id="portableMergeOverview" class="merge-overview"></div>
          </div>
          <div class="merge-workstation-shell">
            <section class="merge-lane">
              <div class="merge-lane-head">
                <h3>Merge Queue</h3>
                <span id="portableMergeFocusMeta" class="merge-lane-meta"></span>
              </div>
              <div id="portableMergeSessionList" class="merge-session-list"></div>
            </section>

            <section class="merge-lane merge-lane-detail">
              <div class="merge-lane-head">
                <h3>Decision Studio</h3>
                <span id="portableMergeDecisionMeta" class="merge-lane-meta"></span>
              </div>
              <div id="portableMergeDetail" class="merge-detail-empty">
                Run a portable local three-way merge to open the workstation.
              </div>
            </section>
          </div>
        </section>

        <section class="card wide">
          <div class="card-header">
            <h2>Visual graph workspace</h2>
            <div class="toggle-group"><button id="analyzeGraphBtn" class="tab-btn active">Analyze graph</button></div>
          </div>
          <div class="graph-toolbar"><span id="graphMeta"></span></div>
          <div id="graphWorkspace" class="graph-workspace">
            <svg id="graphEdges" class="graph-edges"></svg>
            <div id="graphNodes" class="graph-nodes"></div>
          </div>
        </section>

        <section class="card"><div class="card-header"><h2>Normalized / S-Linear</h2></div><pre id="normalizedText" class="codeblock"></pre></section>
        <section class="card"><div class="card-header"><h2>Validation</h2></div><pre id="validationText" class="codeblock"></pre></section>
        <section class="card"><div class="card-header"><h2>AST</h2></div><pre id="astText" class="codeblock"></pre></section>
        <section class="card"><div class="card-header"><h2>Graph JSON</h2></div><pre id="graphJsonText" class="codeblock"></pre></section>
        <section class="card"><div class="card-header"><h2>Runtime</h2></div><pre id="runtimeText" class="codeblock"></pre></section>
        <section class="card"><div class="card-header"><h2>State</h2></div><pre id="stateText" class="codeblock"></pre></section>

        <section class="card wide">
          <div class="card-header">
            <h2>SVG Preview</h2>
            <div class="toggle-group">
              <button class="tab-btn active svg-tab" data-preview="raw">raw</button>
              <button class="tab-btn svg-tab" data-preview="decomposed">decomposed</button>
            </div>
          </div>
          <div id="svgPanel" class="svg-panel"></div>
        </section>
      </div>
    </main>
  </div>
  <script src="/inspector-package-guidance.js"></script>
  <script src="/snapshot-reconcile-workflow.js"></script>
  <script src="/reconcile-commit-package-workflow.js"></script>
  <script src="/local-outcome-set-package-workflow.js"></script>
<script src="/project-workspace-workflow.js"></script>
<script src="/project-lifecycle-workflow.js"></script>
<script src="/project-operations-workflow.js"></script>
<script src="/graph-session-workspace.js"></script>
<script src="/inspector-core-workflow.js"></script>
<script src="/inspector-panel-workflow.js"></script>
<script src="/inspector-action-workflow.js"></script>
<script src="/inspector-bootstrap-workflow.js"></script>
<script src="/portable-merge-workstation.js"></script>
<script src="/app.js"></script>
</body>
</html>
```


## FILE: inspector/app.js

Size: 66389 bytes

```file

const els = {
  profile: document.getElementById("profile"),
  profileHint: document.getElementById("profileHint"),
  decompose: document.getElementById("decompose"),
  sessionName: document.getElementById("sessionName"),
  projectName: document.getElementById("projectName"),
  inputText: document.getElementById("inputText"),
  initialState: document.getElementById("initialState"),
  sessionJson: document.getElementById("sessionJson"),
  projectJson: document.getElementById("projectJson"),
  analyzeBtn: document.getElementById("analyzeBtn"),
  importGraphBtn: document.getElementById("importGraphBtn"),
  clearBtn: document.getElementById("clearBtn"),
  reloadSamples: document.getElementById("reloadSamples"),
  exportTextSessionBtn: document.getElementById("exportTextSessionBtn"),
  exportGraphSessionBtn: document.getElementById("exportGraphSessionBtn"),
  downloadSessionBtn: document.getElementById("downloadSessionBtn"),
  importSessionBtn: document.getElementById("importSessionBtn"),
  addCurrentToProjectBtn: document.getElementById("addCurrentToProjectBtn"),
  exportProjectBtn: document.getElementById("exportProjectBtn"),
  downloadProjectBtn: document.getElementById("downloadProjectBtn"),
  importProjectBtn: document.getElementById("importProjectBtn"),
  reloadProjectBtn: document.getElementById("reloadProjectBtn"),
  clearProjectBtn: document.getElementById("clearProjectBtn"),
  projectSessionsList: document.getElementById("projectSessionsList"),
  newBranchName: document.getElementById("newBranchName"),
  createBranchBtn: document.getElementById("createBranchBtn"),
  branchList: document.getElementById("branchList"),
  tagPointName: document.getElementById("tagPointName"),
  tagPointKind: document.getElementById("tagPointKind"),
  tagTargetSession: document.getElementById("tagTargetSession"),
  tagPointNote: document.getElementById("tagPointNote"),
  createTagPointBtn: document.getElementById("createTagPointBtn"),
  tagPointList: document.getElementById("tagPointList"),
  tagPointResultText: document.getElementById("tagPointResultText"),
  snapshotSourcePoint: document.getElementById("snapshotSourcePoint"),
  snapshotName: document.getElementById("snapshotName"),
  snapshotNote: document.getElementById("snapshotNote"),
  createSnapshotBtn: document.getElementById("createSnapshotBtn"),
  downloadSnapshotBtn: document.getElementById("downloadSnapshotBtn"),
  refreshSnapshotSelectorsBtn: document.getElementById("refreshSnapshotSelectorsBtn"),
  snapshotList: document.getElementById("snapshotList"),
  snapshotResultText: document.getElementById("snapshotResultText"),
  snapshotRestoreJson: document.getElementById("snapshotRestoreJson"),
  snapshotPackageHint: document.getElementById("snapshotPackageHint"),
  restoredProjectName: document.getElementById("restoredProjectName"),
  snapshotRestoreName: document.getElementById("snapshotRestoreName"),
  activateRestoredAnchor: document.getElementById("activateRestoredAnchor"),
  loadCurrentSnapshotForRestoreBtn: document.getElementById("loadCurrentSnapshotForRestoreBtn"),
  previewSnapshotRestoreBtn: document.getElementById("previewSnapshotRestoreBtn"),
  restoreFromSnapshotBtn: document.getElementById("restoreFromSnapshotBtn"),
  clearSnapshotRestoreBtn: document.getElementById("clearSnapshotRestoreBtn"),
  snapshotRestorePreviewText: document.getElementById("snapshotRestorePreviewText"),
  snapshotRestoreResultText: document.getElementById("snapshotRestoreResultText"),
  partialImportSessionIds: document.getElementById("partialImportSessionIds"),
  partialImportTagNames: document.getElementById("partialImportTagNames"),
  partialImportSnapshotNames: document.getElementById("partialImportSnapshotNames"),
  partialImportSelectionHint: document.getElementById("partialImportSelectionHint"),
  partialImportTargetBranch: document.getElementById("partialImportTargetBranch"),
  partialImportName: document.getElementById("partialImportName"),
  activatePartialImportHead: document.getElementById("activatePartialImportHead"),
  useCurrentSnapshotForPartialBtn: document.getElementById("useCurrentSnapshotForPartialBtn"),
  partialImportFromSnapshotBtn: document.getElementById("partialImportFromSnapshotBtn"),
  clearPartialImportBtn: document.getElementById("clearPartialImportBtn"),
  partialImportResultText: document.getElementById("partialImportResultText"),
  snapshotReconcileSessionIds: document.getElementById("snapshotReconcileSessionIds"),
  snapshotReconcileSessionHint: document.getElementById("snapshotReconcileSessionHint"),
  snapshotReconcileTargetBranch: document.getElementById("snapshotReconcileTargetBranch"),
  snapshotReconcileName: document.getElementById("snapshotReconcileName"),
  activateSnapshotReconcileHead: document.getElementById("activateSnapshotReconcileHead"),
  useCurrentSnapshotForReconcileBtn: document.getElementById("useCurrentSnapshotForReconcileBtn"),
  previewSnapshotReconcileBtn: document.getElementById("previewSnapshotReconcileBtn"),
  reconcileSnapshotBtn: document.getElementById("reconcileSnapshotBtn"),
  clearSnapshotReconcileBtn: document.getElementById("clearSnapshotReconcileBtn"),
  snapshotReconcileList: document.getElementById("snapshotReconcileList"),
  snapshotReconcilePreviewText: document.getElementById("snapshotReconcilePreviewText"),
  snapshotReconcileDecisionList: document.getElementById("snapshotReconcileDecisionList"),
  useSnapshotForAllReconcileBtn: document.getElementById("useSnapshotForAllReconcileBtn"),
  useCurrentForAllConflictsBtn: document.getElementById("useCurrentForAllConflictsBtn"),
  applySnapshotReconcileDecisionsBtn: document.getElementById("applySnapshotReconcileDecisionsBtn"),
  snapshotReconcileResultText: document.getElementById("snapshotReconcileResultText"),
  snapshotReconcileCommitName: document.getElementById("snapshotReconcileCommitName"),
  snapshotReconcilePromotePointName: document.getElementById("snapshotReconcilePromotePointName"),
  snapshotReconcilePromotePointKind: document.getElementById("snapshotReconcilePromotePointKind"),
  snapshotReconcileCommitNote: document.getElementById("snapshotReconcileCommitNote"),
  commitSnapshotReconcileBtn: document.getElementById("commitSnapshotReconcileBtn"),
  snapshotReconcileCommitList: document.getElementById("snapshotReconcileCommitList"),
  snapshotReconcileCommitResultText: document.getElementById("snapshotReconcileCommitResultText"),
  compareReconcileCommitLeft: document.getElementById("compareReconcileCommitLeft"),
  compareReconcileCommitRight: document.getElementById("compareReconcileCommitRight"),
  compareReconcileCommitsBtn: document.getElementById("compareReconcileCommitsBtn"),
  compareReconcileCommitResultText: document.getElementById("compareReconcileCommitResultText"),
  exportReconcileCommitName: document.getElementById("exportReconcileCommitName"),
  exportReconcileCommitPackageName: document.getElementById("exportReconcileCommitPackageName"),
  exportReconcileCommitPackageBtn: document.getElementById("exportReconcileCommitPackageBtn"),
  reconcileCommitPackageCurrentSummary: document.getElementById("reconcileCommitPackageCurrentSummary"),
  importReconcileCommitPackageJson: document.getElementById("importReconcileCommitPackageJson"),
  reconcileCommitPackageHint: document.getElementById("reconcileCommitPackageHint"),
  importReconcileCommitPackageName: document.getElementById("importReconcileCommitPackageName"),
  importReconcileCommitTargetBranch: document.getElementById("importReconcileCommitTargetBranch"),
  activateImportedReconcileCommit: document.getElementById("activateImportedReconcileCommit"),
  useCurrentReconcileCommitPackageBtn: document.getElementById("useCurrentReconcileCommitPackageBtn"),
  previewReconcileCommitPackageBtn: document.getElementById("previewReconcileCommitPackageBtn"),
  importReconcileCommitPackageBtn: document.getElementById("importReconcileCommitPackageBtn"),
  clearReconcileCommitPackageBtn: document.getElementById("clearReconcileCommitPackageBtn"),
  reconcileCommitPackageList: document.getElementById("reconcileCommitPackageList"),
  reconcileCommitPackagePreviewText: document.getElementById("reconcileCommitPackagePreviewText"),
  reconcileCommitPackageDecisionList: document.getElementById("reconcileCommitPackageDecisionList"),
  usePackageForAllImportBtn: document.getElementById("usePackageForAllImportBtn"),
  useCurrentForImportConflictsBtn: document.getElementById("useCurrentForImportConflictsBtn"),
  applyReconcileCommitPackageDecisionsBtn: document.getElementById("applyReconcileCommitPackageDecisionsBtn"),
  reconcileCommitPackageResultText: document.getElementById("reconcileCommitPackageResultText"),
  reconcileCommitPackageCommitName: document.getElementById("reconcileCommitPackageCommitName"),
  reconcileCommitPackagePromotePointName: document.getElementById("reconcileCommitPackagePromotePointName"),
  reconcileCommitPackagePromotePointKind: document.getElementById("reconcileCommitPackagePromotePointKind"),
  reconcileCommitPackageCommitNote: document.getElementById("reconcileCommitPackageCommitNote"),
  commitReconcileCommitPackageBtn: document.getElementById("commitReconcileCommitPackageBtn"),
  exportLocalOutcomeSetCommit: document.getElementById("exportLocalOutcomeSetCommit"),
  localOutcomeSetPackageName: document.getElementById("localOutcomeSetPackageName"),
  localOutcomeSetPackageNote: document.getElementById("localOutcomeSetPackageNote"),
  exportLocalOutcomeSetPackageBtn: document.getElementById("exportLocalOutcomeSetPackageBtn"),
  localOutcomeSetPackageCurrentSummary: document.getElementById("localOutcomeSetPackageCurrentSummary"),
  importLocalOutcomeSetPackageJson: document.getElementById("importLocalOutcomeSetPackageJson"),
  localOutcomeSetPackageHint: document.getElementById("localOutcomeSetPackageHint"),
  importLocalOutcomeSetPackageNameInput: document.getElementById("importLocalOutcomeSetPackageNameInput"),
  importLocalOutcomeSetTargetBranch: document.getElementById("importLocalOutcomeSetTargetBranch"),
  activateImportedLocalOutcomeSet: document.getElementById("activateImportedLocalOutcomeSet"),
  useCurrentLocalOutcomeSetPackageBtn: document.getElementById("useCurrentLocalOutcomeSetPackageBtn"),
  previewLocalOutcomeSetPackageBtn: document.getElementById("previewLocalOutcomeSetPackageBtn"),
  importLocalOutcomeSetPackageBtn: document.getElementById("importLocalOutcomeSetPackageBtn"),
  clearLocalOutcomeSetPackageBtn: document.getElementById("clearLocalOutcomeSetPackageBtn"),
  localOutcomeSetPackageList: document.getElementById("localOutcomeSetPackageList"),
  localOutcomeSetPackagePreviewResultText: document.getElementById("localOutcomeSetPackagePreviewResultText"),
  localOutcomeSetPackageDecisionList: document.getElementById("localOutcomeSetPackageDecisionList"),
  usePackageForAllLocalOutcomeBtn: document.getElementById("usePackageForAllLocalOutcomeBtn"),
  useCurrentForAllLocalOutcomeConflictsBtn: document.getElementById("useCurrentForAllLocalOutcomeConflictsBtn"),
  applyLocalOutcomePackageDecisionsBtn: document.getElementById("applyLocalOutcomePackageDecisionsBtn"),
  localOutcomeSetPackageCommitName: document.getElementById("localOutcomeSetPackageCommitName"),
  localOutcomeSetPackagePromotePointName: document.getElementById("localOutcomeSetPackagePromotePointName"),
  localOutcomeSetPackagePromotePointKind: document.getElementById("localOutcomeSetPackagePromotePointKind"),
  localOutcomeSetPackageCommitNote: document.getElementById("localOutcomeSetPackageCommitNote"),
  commitLocalOutcomeSetPackageBtn: document.getElementById("commitLocalOutcomeSetPackageBtn"),
  localOutcomeSetPackageResultText: document.getElementById("localOutcomeSetPackageResultText"),
  basePortableLocalOutcomeCommit: document.getElementById("basePortableLocalOutcomeCommit"),
  leftPortableLocalOutcomeCommit: document.getElementById("leftPortableLocalOutcomeCommit"),
  rightPortableLocalOutcomeCommit: document.getElementById("rightPortableLocalOutcomeCommit"),
  compareThreeWayPortableLocalOutcomeBtn: document.getElementById("compareThreeWayPortableLocalOutcomeBtn"),
  portableLocalOutcomeThreeWayMergeResultText: document.getElementById("portableLocalOutcomeThreeWayMergeResultText"),
  portableLocalOutcomeMergeResolutionName: document.getElementById("portableLocalOutcomeMergeResolutionName"),
  portableLocalOutcomeMergeTargetBranch: document.getElementById("portableLocalOutcomeMergeTargetBranch"),
  portableLocalOutcomeMergeDecisionList: document.getElementById("portableLocalOutcomeMergeDecisionList"),
  useLeftForAllPortableLocalMergeBtn: document.getElementById("useLeftForAllPortableLocalMergeBtn"),
  useRightForAllPortableLocalMergeConflictsBtn: document.getElementById("useRightForAllPortableLocalMergeConflictsBtn"),
  applyPortableLocalOutcomeMergeDecisionsBtn: document.getElementById("applyPortableLocalOutcomeMergeDecisionsBtn"),
  portableLocalOutcomeMergeResolutionResultText: document.getElementById("portableLocalOutcomeMergeResolutionResultText"),
  portableLocalOutcomeMergeCommitName: document.getElementById("portableLocalOutcomeMergeCommitName"),
  portableLocalOutcomeMergePromotePointName: document.getElementById("portableLocalOutcomeMergePromotePointName"),
  portableLocalOutcomeMergePromotePointKind: document.getElementById("portableLocalOutcomeMergePromotePointKind"),
  portableLocalOutcomeMergeCommitNote: document.getElementById("portableLocalOutcomeMergeCommitNote"),
  commitPortableLocalOutcomeMergeBtn: document.getElementById("commitPortableLocalOutcomeMergeBtn"),
  portableLocalOutcomeMergeCommitResultText: document.getElementById("portableLocalOutcomeMergeCommitResultText"),
  portableMergeOverview: document.getElementById("portableMergeOverview"),
  portableMergeSessionList: document.getElementById("portableMergeSessionList"),
  portableMergeDetail: document.getElementById("portableMergeDetail"),
  portableMergeFocusMeta: document.getElementById("portableMergeFocusMeta"),
  portableMergeDecisionMeta: document.getElementById("portableMergeDecisionMeta"),
  rebaseSourceBranch: document.getElementById("rebaseSourceBranch"),
  rebaseTargetBranch: document.getElementById("rebaseTargetBranch"),
  activateRebasedHead: document.getElementById("activateRebasedHead"),
  rebaseBranchBtn: document.getElementById("rebaseBranchBtn"),
  rebaseResultText: document.getElementById("rebaseResultText"),
  resetBranchName: document.getElementById("resetBranchName"),
  resetTargetSession: document.getElementById("resetTargetSession"),
  activateResetHead: document.getElementById("activateResetHead"),
  resetBranchHeadBtn: document.getElementById("resetBranchHeadBtn"),
  branchResetResultText: document.getElementById("branchResetResultText"),
  cherryPickSessionIds: document.getElementById("cherryPickSessionIds"),
  cherryPickTargetBranch: document.getElementById("cherryPickTargetBranch"),
  activateCherryPickedHead: document.getElementById("activateCherryPickedHead"),
  cherryPickSessionsBtn: document.getElementById("cherryPickSessionsBtn"),
  cherryPickResultText: document.getElementById("cherryPickResultText"),
  squashSessionIds: document.getElementById("squashSessionIds"),
  squashTargetBranch: document.getElementById("squashTargetBranch"),
  squashSessionId: document.getElementById("squashSessionId"),
  squashSessionName: document.getElementById("squashSessionName"),
  activateSquashedHead: document.getElementById("activateSquashedHead"),
  squashSessionsBtn: document.getElementById("squashSessionsBtn"),
  squashResultText: document.getElementById("squashResultText"),
  projectDependencyMap: document.getElementById("projectDependencyMap"),
  projectTimeline: document.getElementById("projectTimeline"),
  projectLineageGraph: document.getElementById("projectLineageGraph"),
  compareLeftSession: document.getElementById("compareLeftSession"),
  compareRightSession: document.getElementById("compareRightSession"),
  compareSessionsBtn: document.getElementById("compareSessionsBtn"),
  compareResultText: document.getElementById("compareResultText"),
  mergeBaseSession: document.getElementById("mergeBaseSession"),
  mergeLeftSession: document.getElementById("mergeLeftSession"),
  mergeRightSession: document.getElementById("mergeRightSession"),
  mergeSessionsBtn: document.getElementById("mergeSessionsBtn"),
  mergeResultText: document.getElementById("mergeResultText"),
  mergeConflictList: document.getElementById("mergeConflictList"),
  useLeftForAllConflictsBtn: document.getElementById("useLeftForAllConflictsBtn"),
  useRightForAllConflictsBtn: document.getElementById("useRightForAllConflictsBtn"),
  applyMergeDecisionsBtn: document.getElementById("applyMergeDecisionsBtn"),
  resolvedMergeText: document.getElementById("resolvedMergeText"),
  mergeCommitSessionId: document.getElementById("mergeCommitSessionId"),
  mergeCommitSessionName: document.getElementById("mergeCommitSessionName"),
  mergeCommitBranchName: document.getElementById("mergeCommitBranchName"),
  activateCommittedSession: document.getElementById("activateCommittedSession"),
  commitMergedSessionBtn: document.getElementById("commitMergedSessionBtn"),
  mergeCommitResultText: document.getElementById("mergeCommitResultText"),
  samplesList: document.getElementById("samplesList"),
  statusText: document.getElementById("statusText"),
  normalizedText: document.getElementById("normalizedText"),
  validationText: document.getElementById("validationText"),
  astText: document.getElementById("astText"),
  graphJsonText: document.getElementById("graphJsonText"),
  runtimeText: document.getElementById("runtimeText"),
  stateText: document.getElementById("stateText"),
  svgPanel: document.getElementById("svgPanel"),
  graphWorkspace: document.getElementById("graphWorkspace"),
  graphEdges: document.getElementById("graphEdges"),
  graphNodes: document.getElementById("graphNodes"),
  graphMeta: document.getElementById("graphMeta"),
  analyzeGraphBtn: document.getElementById("analyzeGraphBtn"),
  newEntityKind: document.getElementById("newEntityKind"),
  addEntityBtn: document.getElementById("addEntityBtn"),
  setRootBtn: document.getElementById("setRootBtn"),
  deleteEntityBtn: document.getElementById("deleteEntityBtn"),
  edgeRoleInput: document.getElementById("edgeRoleInput"),
  edgeTargetSelect: document.getElementById("edgeTargetSelect"),
  addEdgeBtn: document.getElementById("addEdgeBtn"),
  entityId: document.getElementById("entityId"),
  entityKind: document.getElementById("entityKind"),
  entityClass: document.getElementById("entityClass"),
  entityRoot: document.getElementById("entityRoot"),
  entityValue: document.getElementById("entityValue"),
  entityModifiers: document.getElementById("entityModifiers"),
  saveEntityBtn: document.getElementById("saveEntityBtn"),
};

let currentResult = null;
let previewMode = "raw";
let graphDoc = null;
let selectedEntityId = null;
let dragState = null;
let currentSession = null;
let currentProject = null;
let currentProjectMap = null;
let currentProjectTimeline = null;
let currentBranchSummary = null;
let currentLineageGraph = null;
let currentBranchRebaseResult = null;
let currentBranchResetResult = null;
let currentTagSummary = null;
let currentTagPointResult = null;
let currentSnapshotSummary = null;
let currentSnapshotResult = null;
let currentSnapshotPackage = null;
let currentSnapshotRestoreSummary = null;
let currentSnapshotRestorePreview = null;
let currentSnapshotRestoreResult = null;
let currentPartialSnapshotImportSummary = null;
let currentPartialSnapshotImportResult = null;
let currentSnapshotReconcileSummary = null;
let currentSnapshotReconcilePreview = null;
let currentSnapshotReconcileDecisions = {};
let currentSnapshotReconcileResult = null;
let currentSnapshotReconcileCommitSummary = null;
let currentSnapshotReconcileCommitResult = null;
let currentSnapshotReconcileCommitCompareResult = null;
let currentSnapshotReconcileCommitPackageSummary = null;
let currentSnapshotReconcileCommitPackageImportSummary = null;
let currentSnapshotReconcileCommitPackagePreview = null;
let currentSnapshotReconcileCommitPackageImportDecisions = {};
let currentSnapshotReconcileCommitPackageResolutionSummary = null;
let currentSnapshotReconcileCommitPackageCommitSummary = null;
let currentSnapshotReconcileCommitPackageResult = null;
let currentSnapshotReconcileCommitPackage = null;
let currentLocalOutcomeSetPackageSummary = null;
let currentLocalOutcomeSetPackageImportSummary = null;
let currentLocalOutcomeSetPackageResolutionSummary = null;
let currentLocalOutcomeSetPackage = null;
let currentLocalOutcomeSetPackagePreviewResult = null;
let currentLocalOutcomeSetPackageImportDecisions = {};
let currentLocalOutcomeSetPackageResult = null;
let currentPortableLocalOutcomeThreeWayMergeResult = null;
let currentPortableLocalOutcomeMergeDecisions = {};
let currentPortableLocalOutcomeMergeResolutionSummary = null;
let currentPortableLocalOutcomeMergeResolutionResult = null;
let currentPortableLocalOutcomeMergeCommitResult = null;
let selectedPortableLocalOutcomeMergeItemId = null;
let portableLocalOutcomeMergeController = null;
let snapshotReconcileWorkflowController = null;
let reconcileCommitPackageWorkflowController = null;
let localOutcomeSetPackageWorkflowController = null;
let projectOperationsWorkflowController = null;
let projectWorkspaceWorkflowController = null;
let projectLifecycleWorkflowController = null;
let graphSessionWorkspaceController = null;
let inspectorBootstrapController = null;
let inspectorCoreController = null;
let inspectorPanelController = null;
let inspectorActionController = null;
let currentBranchCherryPickResult = null;
let currentBranchSquashResult = null;
let currentCompareResult = null;
let currentMergeResult = null;
let currentResolvedMergeResult = null;
let currentConflictDecisions = {};
let currentMergeCommitResult = null;

function setStatus(text) { els.statusText.textContent = text; }
function pretty(obj) { return JSON.stringify(obj, null, 2); }
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
function parseInitialState() { const raw = els.initialState.value.trim(); if (!raw) return null; return JSON.parse(raw); }
function entityLabel(entity) {
  if (entity.kind === "node") return `${entity.class_name}:${entity.root}`;
  if (entity.kind === "list") return "LIST";
  if (entity.kind === "raw_token") return entity.value || "raw";
  if (entity.kind === "typed_literal") return entity.value ? `${entity.class_name}:${entity.root}=${entity.value}` : `${entity.class_name}:${entity.root}`;
  return entity.id;
}

function renderResult(result) {
  getInspectorCoreController().renderResult(result);
}
function renderSvg() {
  getGraphSessionWorkspaceController().renderSvg();
}
function renderGraph() {
  getGraphSessionWorkspaceController().renderGraph();
}
async function postJson(url, payload) {
  const res = await fetch(url, { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload) });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

function getPortableLocalOutcomeMergeController() {
  if (!portableLocalOutcomeMergeController) {
    const factory = window.PortableLocalOutcomeMergeWorkstation?.createPortableLocalOutcomeMergeController;
    if (!factory) {
      throw new Error("Portable local outcome merge workstation module is not loaded");
    }
    portableLocalOutcomeMergeController = factory({
      els,
      getCurrentProject: () => currentProject,
      getMergeResult: () => currentPortableLocalOutcomeThreeWayMergeResult,
      setMergeResult: (value) => { currentPortableLocalOutcomeThreeWayMergeResult = value; },
      getMergeDecisions: () => currentPortableLocalOutcomeMergeDecisions,
      setMergeDecisions: (value) => { currentPortableLocalOutcomeMergeDecisions = value; },
      setMergeResolutionSummary: (value) => { currentPortableLocalOutcomeMergeResolutionSummary = value; },
      getMergeResolutionResult: () => currentPortableLocalOutcomeMergeResolutionResult,
      setMergeResolutionResult: (value) => { currentPortableLocalOutcomeMergeResolutionResult = value; },
      getMergeCommitResult: () => currentPortableLocalOutcomeMergeCommitResult,
      setMergeCommitResult: (value) => { currentPortableLocalOutcomeMergeCommitResult = value; },
      getSelectedItemId: () => selectedPortableLocalOutcomeMergeItemId,
      setSelectedItemId: (value) => { selectedPortableLocalOutcomeMergeItemId = value; },
      escapeHtml,
      pretty,
      postJson,
      renderResult,
      setStatus,
    });
  }
  return portableLocalOutcomeMergeController;
}

function refreshProjectUiForSnapshotReconcileWorkflow() {
  getInspectorCoreController().refreshProjectUiForSnapshotReconcileWorkflow();
}

function renderSupplementaryPanelsForSnapshotReconcileWorkflow() {
  getInspectorCoreController().renderSupplementaryPanelsForSnapshotReconcileWorkflow();
}

function getSnapshotReconcileWorkflowState() {
  return {
    currentProject,
    currentProjectMap,
    currentProjectTimeline,
    currentBranchSummary,
    currentLineageGraph,
    currentTagSummary,
    currentSnapshotSummary,
    currentSnapshotPackage,
    currentSnapshotRestoreSummary,
    currentPartialSnapshotImportSummary,
    currentSnapshotReconcileSummary,
    currentSnapshotReconcilePreview,
    currentSnapshotReconcileDecisions,
    currentSnapshotReconcileResult,
    currentSnapshotReconcileCommitSummary,
    currentSnapshotReconcileCommitResult,
    currentSnapshotReconcileCommitCompareResult,
  };
}

function setSnapshotReconcileWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentProjectMap" in patch) currentProjectMap = patch.currentProjectMap;
  if ("currentProjectTimeline" in patch) currentProjectTimeline = patch.currentProjectTimeline;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentLineageGraph" in patch) currentLineageGraph = patch.currentLineageGraph;
  if ("currentTagSummary" in patch) currentTagSummary = patch.currentTagSummary;
  if ("currentSnapshotSummary" in patch) currentSnapshotSummary = patch.currentSnapshotSummary;
  if ("currentSnapshotPackage" in patch) currentSnapshotPackage = patch.currentSnapshotPackage;
  if ("currentSnapshotRestoreSummary" in patch) currentSnapshotRestoreSummary = patch.currentSnapshotRestoreSummary;
  if ("currentPartialSnapshotImportSummary" in patch) currentPartialSnapshotImportSummary = patch.currentPartialSnapshotImportSummary;
  if ("currentSnapshotReconcileSummary" in patch) currentSnapshotReconcileSummary = patch.currentSnapshotReconcileSummary;
  if ("currentSnapshotReconcilePreview" in patch) currentSnapshotReconcilePreview = patch.currentSnapshotReconcilePreview;
  if ("currentSnapshotReconcileDecisions" in patch) currentSnapshotReconcileDecisions = patch.currentSnapshotReconcileDecisions;
  if ("currentSnapshotReconcileResult" in patch) currentSnapshotReconcileResult = patch.currentSnapshotReconcileResult;
  if ("currentSnapshotReconcileCommitSummary" in patch) currentSnapshotReconcileCommitSummary = patch.currentSnapshotReconcileCommitSummary;
  if ("currentSnapshotReconcileCommitResult" in patch) currentSnapshotReconcileCommitResult = patch.currentSnapshotReconcileCommitResult;
  if ("currentSnapshotReconcileCommitCompareResult" in patch) currentSnapshotReconcileCommitCompareResult = patch.currentSnapshotReconcileCommitCompareResult;
}

function getSnapshotReconcileWorkflowController() {
  if (!snapshotReconcileWorkflowController) {
    const factory = window.SnapshotReconcileWorkflow?.createSnapshotReconcileController;
    if (!factory) {
      throw new Error("Snapshot reconcile workflow module is not loaded");
    }
    snapshotReconcileWorkflowController = factory({
      els,
      getState: getSnapshotReconcileWorkflowState,
      setState: setSnapshotReconcileWorkflowState,
      pretty,
      parseCsvList,
      postJson,
      renderResult,
      setStatus,
      refreshProjectUi: refreshProjectUiForSnapshotReconcileWorkflow,
      renderSupplementaryPanels: renderSupplementaryPanelsForSnapshotReconcileWorkflow,
      updateReconcileCommitPackageSelectors: () => getInspectorPanelController().updateReconcileCommitPackageSelectors(),
      renderReconcileCommitPackageList: () => getInspectorPanelController().renderReconcileCommitPackageList(),
    });
  }
  return snapshotReconcileWorkflowController;
}

function refreshProjectUiForReconcileCommitPackageWorkflow() {
  getInspectorCoreController().refreshProjectUiForReconcileCommitPackageWorkflow();
}

function renderLocalOutcomeSetPackagePanels() {
  getInspectorCoreController().renderLocalOutcomeSetPackagePanels();
}

function getReconcileCommitPackageWorkflowState() {
  return {
    currentProject,
    currentProjectMap,
    currentProjectTimeline,
    currentBranchSummary,
    currentLineageGraph,
    currentTagSummary,
    currentSnapshotReconcileCommitSummary,
    currentSnapshotReconcileCommitPackageSummary,
    currentSnapshotReconcileCommitPackageImportSummary,
    currentSnapshotReconcileCommitPackagePreview,
    currentSnapshotReconcileCommitPackageImportDecisions,
    currentSnapshotReconcileCommitPackageResolutionSummary,
    currentSnapshotReconcileCommitPackageCommitSummary,
    currentSnapshotReconcileCommitPackageResult,
    currentSnapshotReconcileCommitPackage,
    currentLocalOutcomeSetPackageSummary,
    currentLocalOutcomeSetPackageImportSummary,
    currentLocalOutcomeSetPackageResolutionSummary,
    currentLocalOutcomeSetPackage,
    currentLocalOutcomeSetPackagePreviewResult,
    currentLocalOutcomeSetPackageImportDecisions,
    currentLocalOutcomeSetPackageResult,
  };
}

function setReconcileCommitPackageWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentProjectMap" in patch) currentProjectMap = patch.currentProjectMap;
  if ("currentProjectTimeline" in patch) currentProjectTimeline = patch.currentProjectTimeline;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentLineageGraph" in patch) currentLineageGraph = patch.currentLineageGraph;
  if ("currentTagSummary" in patch) currentTagSummary = patch.currentTagSummary;
  if ("currentSnapshotReconcileCommitSummary" in patch) currentSnapshotReconcileCommitSummary = patch.currentSnapshotReconcileCommitSummary;
  if ("currentSnapshotReconcileCommitPackageSummary" in patch) currentSnapshotReconcileCommitPackageSummary = patch.currentSnapshotReconcileCommitPackageSummary;
  if ("currentSnapshotReconcileCommitPackageImportSummary" in patch) currentSnapshotReconcileCommitPackageImportSummary = patch.currentSnapshotReconcileCommitPackageImportSummary;
  if ("currentSnapshotReconcileCommitPackagePreview" in patch) currentSnapshotReconcileCommitPackagePreview = patch.currentSnapshotReconcileCommitPackagePreview;
  if ("currentSnapshotReconcileCommitPackageImportDecisions" in patch) currentSnapshotReconcileCommitPackageImportDecisions = patch.currentSnapshotReconcileCommitPackageImportDecisions;
  if ("currentSnapshotReconcileCommitPackageResolutionSummary" in patch) currentSnapshotReconcileCommitPackageResolutionSummary = patch.currentSnapshotReconcileCommitPackageResolutionSummary;
  if ("currentSnapshotReconcileCommitPackageCommitSummary" in patch) currentSnapshotReconcileCommitPackageCommitSummary = patch.currentSnapshotReconcileCommitPackageCommitSummary;
  if ("currentSnapshotReconcileCommitPackageResult" in patch) currentSnapshotReconcileCommitPackageResult = patch.currentSnapshotReconcileCommitPackageResult;
  if ("currentSnapshotReconcileCommitPackage" in patch) currentSnapshotReconcileCommitPackage = patch.currentSnapshotReconcileCommitPackage;
  if ("currentLocalOutcomeSetPackageSummary" in patch) currentLocalOutcomeSetPackageSummary = patch.currentLocalOutcomeSetPackageSummary;
  if ("currentLocalOutcomeSetPackageImportSummary" in patch) currentLocalOutcomeSetPackageImportSummary = patch.currentLocalOutcomeSetPackageImportSummary;
  if ("currentLocalOutcomeSetPackageResolutionSummary" in patch) currentLocalOutcomeSetPackageResolutionSummary = patch.currentLocalOutcomeSetPackageResolutionSummary;
  if ("currentLocalOutcomeSetPackage" in patch) currentLocalOutcomeSetPackage = patch.currentLocalOutcomeSetPackage;
  if ("currentLocalOutcomeSetPackagePreviewResult" in patch) currentLocalOutcomeSetPackagePreviewResult = patch.currentLocalOutcomeSetPackagePreviewResult;
  if ("currentLocalOutcomeSetPackageImportDecisions" in patch) currentLocalOutcomeSetPackageImportDecisions = patch.currentLocalOutcomeSetPackageImportDecisions;
  if ("currentLocalOutcomeSetPackageResult" in patch) currentLocalOutcomeSetPackageResult = patch.currentLocalOutcomeSetPackageResult;
}

function getReconcileCommitPackageWorkflowController() {
  if (!reconcileCommitPackageWorkflowController) {
    const factory = window.ReconcileCommitPackageWorkflow?.createReconcileCommitPackageController;
    if (!factory) {
      throw new Error("Reconcile commit package workflow module is not loaded");
    }
    reconcileCommitPackageWorkflowController = factory({
      els,
      getState: getReconcileCommitPackageWorkflowState,
      setState: setReconcileCommitPackageWorkflowState,
      pretty,
      postJson,
      renderResult,
      setStatus,
      refreshProjectUi: refreshProjectUiForReconcileCommitPackageWorkflow,
      updateLocalOutcomeSetPackageSelectors: () => getInspectorPanelController().updateLocalOutcomeSetPackageSelectors(),
      renderLocalOutcomeSetPackagePanels,
    });
  }
  return reconcileCommitPackageWorkflowController;
}

function getLocalOutcomeSetPackageWorkflowState() {
  return {
    currentProject,
    currentBranchSummary,
    currentSnapshotReconcileCommitPackageCommitSummary,
    currentLocalOutcomeSetPackageSummary,
    currentLocalOutcomeSetPackageImportSummary,
    currentLocalOutcomeSetPackageResolutionSummary,
    currentLocalOutcomeSetPackage,
    currentLocalOutcomeSetPackagePreviewResult,
    currentLocalOutcomeSetPackageImportDecisions,
    currentLocalOutcomeSetPackageResult,
  };
}

function setLocalOutcomeSetPackageWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentSnapshotReconcileCommitPackageCommitSummary" in patch) currentSnapshotReconcileCommitPackageCommitSummary = patch.currentSnapshotReconcileCommitPackageCommitSummary;
  if ("currentLocalOutcomeSetPackageSummary" in patch) currentLocalOutcomeSetPackageSummary = patch.currentLocalOutcomeSetPackageSummary;
  if ("currentLocalOutcomeSetPackageImportSummary" in patch) currentLocalOutcomeSetPackageImportSummary = patch.currentLocalOutcomeSetPackageImportSummary;
  if ("currentLocalOutcomeSetPackageResolutionSummary" in patch) currentLocalOutcomeSetPackageResolutionSummary = patch.currentLocalOutcomeSetPackageResolutionSummary;
  if ("currentLocalOutcomeSetPackage" in patch) currentLocalOutcomeSetPackage = patch.currentLocalOutcomeSetPackage;
  if ("currentLocalOutcomeSetPackagePreviewResult" in patch) currentLocalOutcomeSetPackagePreviewResult = patch.currentLocalOutcomeSetPackagePreviewResult;
  if ("currentLocalOutcomeSetPackageImportDecisions" in patch) currentLocalOutcomeSetPackageImportDecisions = patch.currentLocalOutcomeSetPackageImportDecisions;
  if ("currentLocalOutcomeSetPackageResult" in patch) currentLocalOutcomeSetPackageResult = patch.currentLocalOutcomeSetPackageResult;
}

function getLocalOutcomeSetPackageWorkflowController() {
  if (!localOutcomeSetPackageWorkflowController) {
    const factory = window.LocalOutcomeSetPackageWorkflow?.createLocalOutcomeSetPackageController;
    if (!factory) {
      throw new Error("Local outcome set package workflow module is not loaded");
    }
    localOutcomeSetPackageWorkflowController = factory({
      els,
      getState: getLocalOutcomeSetPackageWorkflowState,
      setState: setLocalOutcomeSetPackageWorkflowState,
      pretty,
      postJson,
      renderResult,
      setStatus,
      updatePortableLocalOutcomeMergeSelectors: () => getInspectorPanelController().updatePortableLocalOutcomeMergeSelectors(),
    });
  }
  return localOutcomeSetPackageWorkflowController;
}

function getProjectOperationsWorkflowState() {
  return {
    currentProject,
    currentBranchSummary,
    currentCompareResult,
    currentMergeResult,
    currentResolvedMergeResult,
    currentConflictDecisions,
    currentMergeCommitResult,
    currentBranchRebaseResult,
    currentBranchResetResult,
    currentBranchCherryPickResult,
    currentBranchSquashResult,
  };
}

function setProjectOperationsWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentCompareResult" in patch) currentCompareResult = patch.currentCompareResult;
  if ("currentMergeResult" in patch) currentMergeResult = patch.currentMergeResult;
  if ("currentResolvedMergeResult" in patch) currentResolvedMergeResult = patch.currentResolvedMergeResult;
  if ("currentConflictDecisions" in patch) currentConflictDecisions = patch.currentConflictDecisions;
  if ("currentMergeCommitResult" in patch) currentMergeCommitResult = patch.currentMergeCommitResult;
  if ("currentBranchRebaseResult" in patch) currentBranchRebaseResult = patch.currentBranchRebaseResult;
  if ("currentBranchResetResult" in patch) currentBranchResetResult = patch.currentBranchResetResult;
  if ("currentBranchCherryPickResult" in patch) currentBranchCherryPickResult = patch.currentBranchCherryPickResult;
  if ("currentBranchSquashResult" in patch) currentBranchSquashResult = patch.currentBranchSquashResult;
}

function getProjectOperationsWorkflowController() {
  if (!projectOperationsWorkflowController) {
    const factory = window.ProjectOperationsWorkflow?.createProjectOperationsController;
    if (!factory) {
      throw new Error("Project operations workflow module is not loaded");
    }
    projectOperationsWorkflowController = factory({
      els,
      getState: getProjectOperationsWorkflowState,
      setState: setProjectOperationsWorkflowState,
      pretty,
      postJson,
      renderResult,
      setStatus,
    });
  }
  return projectOperationsWorkflowController;
}

function getProjectWorkspaceWorkflowState() {
  return {
    currentProject,
    currentProjectMap,
    currentProjectTimeline,
    currentBranchSummary,
    currentLineageGraph,
    currentBranchRebaseResult,
    currentBranchResetResult,
    currentTagSummary,
    currentTagPointResult,
    currentSnapshotSummary,
    currentSnapshotResult,
    currentSnapshotPackage,
    currentSnapshotRestoreSummary,
    currentSnapshotRestoreResult,
    currentPartialSnapshotImportSummary,
    currentPartialSnapshotImportResult,
    currentSnapshotReconcileSummary,
    currentSnapshotReconcilePreview,
    currentSnapshotReconcileResult,
    currentSnapshotReconcileCommitSummary,
    currentSnapshotReconcileCommitResult,
    currentSnapshotReconcileCommitCompareResult,
    currentSnapshotReconcileCommitPackageSummary,
    currentSnapshotReconcileCommitPackageImportSummary,
    currentSnapshotReconcileCommitPackagePreview,
    currentSnapshotReconcileCommitPackageResolutionSummary,
    currentSnapshotReconcileCommitPackageCommitSummary,
    currentSnapshotReconcileCommitPackageResult,
    currentSnapshotReconcileCommitPackage,
    currentLocalOutcomeSetPackageSummary,
    currentLocalOutcomeSetPackageImportSummary,
    currentLocalOutcomeSetPackageResolutionSummary,
    currentLocalOutcomeSetPackage,
    currentLocalOutcomeSetPackagePreviewResult,
    currentLocalOutcomeSetPackageResult,
    currentPortableLocalOutcomeMergeResolutionSummary,
    currentPortableLocalOutcomeMergeResolutionResult,
    currentPortableLocalOutcomeMergeCommitResult,
    currentBranchCherryPickResult,
    currentBranchSquashResult,
  };
}

function setProjectWorkspaceWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentProjectMap" in patch) currentProjectMap = patch.currentProjectMap;
  if ("currentProjectTimeline" in patch) currentProjectTimeline = patch.currentProjectTimeline;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentLineageGraph" in patch) currentLineageGraph = patch.currentLineageGraph;
  if ("currentBranchRebaseResult" in patch) currentBranchRebaseResult = patch.currentBranchRebaseResult;
  if ("currentBranchResetResult" in patch) currentBranchResetResult = patch.currentBranchResetResult;
  if ("currentTagSummary" in patch) currentTagSummary = patch.currentTagSummary;
  if ("currentTagPointResult" in patch) currentTagPointResult = patch.currentTagPointResult;
  if ("currentSnapshotSummary" in patch) currentSnapshotSummary = patch.currentSnapshotSummary;
  if ("currentSnapshotResult" in patch) currentSnapshotResult = patch.currentSnapshotResult;
  if ("currentSnapshotPackage" in patch) currentSnapshotPackage = patch.currentSnapshotPackage;
  if ("currentSnapshotRestoreSummary" in patch) currentSnapshotRestoreSummary = patch.currentSnapshotRestoreSummary;
  if ("currentSnapshotRestoreResult" in patch) currentSnapshotRestoreResult = patch.currentSnapshotRestoreResult;
  if ("currentPartialSnapshotImportSummary" in patch) currentPartialSnapshotImportSummary = patch.currentPartialSnapshotImportSummary;
  if ("currentPartialSnapshotImportResult" in patch) currentPartialSnapshotImportResult = patch.currentPartialSnapshotImportResult;
  if ("currentSnapshotReconcileSummary" in patch) currentSnapshotReconcileSummary = patch.currentSnapshotReconcileSummary;
  if ("currentSnapshotReconcilePreview" in patch) currentSnapshotReconcilePreview = patch.currentSnapshotReconcilePreview;
  if ("currentSnapshotReconcileResult" in patch) currentSnapshotReconcileResult = patch.currentSnapshotReconcileResult;
  if ("currentSnapshotReconcileCommitSummary" in patch) currentSnapshotReconcileCommitSummary = patch.currentSnapshotReconcileCommitSummary;
  if ("currentSnapshotReconcileCommitResult" in patch) currentSnapshotReconcileCommitResult = patch.currentSnapshotReconcileCommitResult;
  if ("currentSnapshotReconcileCommitCompareResult" in patch) currentSnapshotReconcileCommitCompareResult = patch.currentSnapshotReconcileCommitCompareResult;
  if ("currentSnapshotReconcileCommitPackageSummary" in patch) currentSnapshotReconcileCommitPackageSummary = patch.currentSnapshotReconcileCommitPackageSummary;
  if ("currentSnapshotReconcileCommitPackageImportSummary" in patch) currentSnapshotReconcileCommitPackageImportSummary = patch.currentSnapshotReconcileCommitPackageImportSummary;
  if ("currentSnapshotReconcileCommitPackagePreview" in patch) currentSnapshotReconcileCommitPackagePreview = patch.currentSnapshotReconcileCommitPackagePreview;
  if ("currentSnapshotReconcileCommitPackageResolutionSummary" in patch) currentSnapshotReconcileCommitPackageResolutionSummary = patch.currentSnapshotReconcileCommitPackageResolutionSummary;
  if ("currentSnapshotReconcileCommitPackageCommitSummary" in patch) currentSnapshotReconcileCommitPackageCommitSummary = patch.currentSnapshotReconcileCommitPackageCommitSummary;
  if ("currentSnapshotReconcileCommitPackageResult" in patch) currentSnapshotReconcileCommitPackageResult = patch.currentSnapshotReconcileCommitPackageResult;
  if ("currentSnapshotReconcileCommitPackage" in patch) currentSnapshotReconcileCommitPackage = patch.currentSnapshotReconcileCommitPackage;
  if ("currentLocalOutcomeSetPackageSummary" in patch) currentLocalOutcomeSetPackageSummary = patch.currentLocalOutcomeSetPackageSummary;
  if ("currentLocalOutcomeSetPackageImportSummary" in patch) currentLocalOutcomeSetPackageImportSummary = patch.currentLocalOutcomeSetPackageImportSummary;
  if ("currentLocalOutcomeSetPackageResolutionSummary" in patch) currentLocalOutcomeSetPackageResolutionSummary = patch.currentLocalOutcomeSetPackageResolutionSummary;
  if ("currentLocalOutcomeSetPackage" in patch) currentLocalOutcomeSetPackage = patch.currentLocalOutcomeSetPackage;
  if ("currentLocalOutcomeSetPackagePreviewResult" in patch) currentLocalOutcomeSetPackagePreviewResult = patch.currentLocalOutcomeSetPackagePreviewResult;
  if ("currentLocalOutcomeSetPackageResult" in patch) currentLocalOutcomeSetPackageResult = patch.currentLocalOutcomeSetPackageResult;
  if ("currentPortableLocalOutcomeMergeResolutionSummary" in patch) currentPortableLocalOutcomeMergeResolutionSummary = patch.currentPortableLocalOutcomeMergeResolutionSummary;
  if ("currentPortableLocalOutcomeMergeResolutionResult" in patch) currentPortableLocalOutcomeMergeResolutionResult = patch.currentPortableLocalOutcomeMergeResolutionResult;
  if ("currentPortableLocalOutcomeMergeCommitResult" in patch) currentPortableLocalOutcomeMergeCommitResult = patch.currentPortableLocalOutcomeMergeCommitResult;
  if ("currentBranchCherryPickResult" in patch) currentBranchCherryPickResult = patch.currentBranchCherryPickResult;
  if ("currentBranchSquashResult" in patch) currentBranchSquashResult = patch.currentBranchSquashResult;
}

function getProjectWorkspaceWorkflowController() {
  if (!projectWorkspaceWorkflowController) {
    const factory = window.ProjectWorkspaceWorkflow?.createProjectWorkspaceController;
    if (!factory) {
      throw new Error("Project workspace workflow module is not loaded");
    }
    projectWorkspaceWorkflowController = factory({
      els,
      getState: getProjectWorkspaceWorkflowState,
      setState: setProjectWorkspaceWorkflowState,
      pretty,
      postJson,
      renderResult,
      setStatus,
    });
  }
  return projectWorkspaceWorkflowController;
}

function refreshProjectHydratedPanels() {
  getInspectorCoreController().refreshProjectHydratedPanels();
}

function getInspectorCoreWorkflowState() {
  return {
    currentResult,
    previewMode,
    graphDoc,
    selectedEntityId,
    currentSession,
  };
}

function setInspectorCoreWorkflowState(patch) {
  if ("currentResult" in patch) currentResult = patch.currentResult;
  if ("previewMode" in patch) previewMode = patch.previewMode;
  if ("graphDoc" in patch) graphDoc = patch.graphDoc;
  if ("selectedEntityId" in patch) selectedEntityId = patch.selectedEntityId;
  if ("currentSession" in patch) currentSession = patch.currentSession;
}

function getInspectorCoreController() {
  if (!inspectorCoreController) {
    const factory = window.InspectorCoreWorkflow?.createInspectorCoreController;
    if (!factory) {
      throw new Error("Inspector core workflow module is not loaded");
    }
    inspectorCoreController = factory({
      els,
      getState: getInspectorCoreWorkflowState,
      setState: setInspectorCoreWorkflowState,
      pretty,
      hydrateProjectResult: (result) => getProjectWorkspaceWorkflowController().hydrateProjectResult(result),
      renderSvg,
      renderGraph,
      renderers: {
        renderProjectSessions: () => getInspectorPanelController().renderProjectSessions(),
        renderProjectMap: () => getInspectorPanelController().renderProjectMap(),
        renderProjectTimeline: () => getInspectorPanelController().renderProjectTimeline(),
        renderBranchList: () => getInspectorPanelController().renderBranchList(),
        renderTagPointList: () => getInspectorPanelController().renderTagPointList(),
        renderSnapshotList: () => getInspectorPanelController().renderSnapshotList(),
        renderSnapshotReconcileList: () => getInspectorPanelController().renderSnapshotReconcileList(),
        renderSnapshotReconcileCommitList: () => getInspectorPanelController().renderSnapshotReconcileCommitList(),
        renderReconcileCommitPackageList: () => getInspectorPanelController().renderReconcileCommitPackageList(),
        renderReconcileCommitPackagePreview: () => getInspectorPanelController().renderReconcileCommitPackagePreview(),
        renderReconcileCommitPackageDecisionList: () => getInspectorPanelController().renderReconcileCommitPackageDecisionList(),
        renderReconcileCommitPackageResult: () => getInspectorPanelController().renderReconcileCommitPackageResult(),
        renderSnapshotReconcileCommitCompareResult: () => getInspectorPanelController().renderSnapshotReconcileCommitCompareResult(),
        renderLineageGraph: () => getInspectorPanelController().renderLineageGraph(),
        renderTagPointResult: () => getInspectorPanelController().renderTagPointResult(),
        renderSnapshotResult: () => getInspectorPanelController().renderSnapshotResult(),
        renderSnapshotRestorePreview: () => getInspectorPanelController().renderSnapshotRestorePreview(),
        renderSnapshotRestoreResult: () => getInspectorPanelController().renderSnapshotRestoreResult(),
        renderPartialImportResult: () => getInspectorPanelController().renderPartialImportResult(),
        renderSnapshotReconcileResult: () => getInspectorPanelController().renderSnapshotReconcileResult(),
        renderSnapshotReconcileCommitResult: () => getInspectorPanelController().renderSnapshotReconcileCommitResult(),
        renderCompareResult: () => getInspectorPanelController().renderCompareResult(),
        renderMergeResult: () => getInspectorPanelController().renderMergeResult(),
        renderResolvedMergeResult: () => getInspectorPanelController().renderResolvedMergeResult(),
        renderMergeCommitResult: () => getInspectorPanelController().renderMergeCommitResult(),
        renderBranchResetResult: () => getInspectorPanelController().renderBranchResetResult(),
        renderBranchRebaseResult: () => getInspectorPanelController().renderBranchRebaseResult(),
        renderBranchCherryPickResult: () => getInspectorPanelController().renderBranchCherryPickResult(),
        renderBranchSquashResult: () => getInspectorPanelController().renderBranchSquashResult(),
        renderLocalOutcomeSetPackageList: () => getInspectorPanelController().renderLocalOutcomeSetPackageList(),
        renderLocalOutcomeSetPackagePreviewResult: () => getInspectorPanelController().renderLocalOutcomeSetPackagePreviewResult(),
        renderLocalOutcomeSetPackageDecisionList: () => getInspectorPanelController().renderLocalOutcomeSetPackageDecisionList(),
        renderLocalOutcomeSetPackageResult: () => getInspectorPanelController().renderLocalOutcomeSetPackageResult(),
        renderPortableLocalOutcomeThreeWayMergeResult: () => getInspectorPanelController().renderPortableLocalOutcomeThreeWayMergeResult(),
        renderPortableLocalOutcomeMergeDecisionList: () => getInspectorPanelController().renderPortableLocalOutcomeMergeDecisionList(),
        renderPortableLocalOutcomeMergeResolutionResult: () => getInspectorPanelController().renderPortableLocalOutcomeMergeResolutionResult(),
        renderPortableLocalOutcomeMergeCommitResult: () => getInspectorPanelController().renderPortableLocalOutcomeMergeCommitResult(),
        renderPortableLocalOutcomeWorkstation: () => getInspectorPanelController().renderPortableLocalOutcomeWorkstation(),
      },
      updaters: {
        updateTagTargetSessions: () => getInspectorPanelController().updateTagTargetSessions(),
        updatePartialImportSelectors: () => getInspectorPanelController().updatePartialImportSelectors(),
        updateSnapshotSelectors: () => getInspectorPanelController().updateSnapshotSelectors(),
        updateResetSelectors: () => getInspectorPanelController().updateResetSelectors(),
        updateRebaseSelectors: () => getInspectorPanelController().updateRebaseSelectors(),
        updateCherryPickSelectors: () => getInspectorPanelController().updateCherryPickSelectors(),
        updateSquashSelectors: () => getInspectorPanelController().updateSquashSelectors(),
        updateCompareSelectors: () => getInspectorPanelController().updateCompareSelectors(),
        updateMergeSelectors: () => getInspectorPanelController().updateMergeSelectors(),
        updateReconcileCommitPackageSelectors: () => getInspectorPanelController().updateReconcileCommitPackageSelectors(),
        updateLocalOutcomeSetPackageSelectors: () => getInspectorPanelController().updateLocalOutcomeSetPackageSelectors(),
        updatePortableLocalOutcomeMergeSelectors: () => getInspectorPanelController().updatePortableLocalOutcomeMergeSelectors(),
        updateSnapshotReconcileSelectors: () => getInspectorPanelController().updateSnapshotReconcileSelectors(),
      },
    });
  }
  return inspectorCoreController;
}

function getProjectLifecycleWorkflowState() {
  return {
    currentProject,
    currentProjectMap,
    currentProjectTimeline,
    currentBranchSummary,
    currentLineageGraph,
    currentBranchRebaseResult,
    currentBranchResetResult,
    currentTagSummary,
    currentTagPointResult,
    currentSnapshotSummary,
    currentSnapshotResult,
    currentSnapshotPackage,
    currentSnapshotRestoreSummary,
    currentSnapshotRestorePreview,
    currentSnapshotRestoreResult,
    currentPartialSnapshotImportSummary,
    currentPartialSnapshotImportResult,
    currentSnapshotReconcileSummary,
    currentSnapshotReconcilePreview,
    currentSnapshotReconcileResult,
    currentSnapshotReconcileCommitSummary,
    currentSnapshotReconcileCommitResult,
    currentSnapshotReconcileCommitCompareResult,
    currentSnapshotReconcileCommitPackageSummary,
    currentSnapshotReconcileCommitPackageImportSummary,
    currentSnapshotReconcileCommitPackagePreview,
    currentSnapshotReconcileCommitPackageResolutionSummary,
    currentSnapshotReconcileCommitPackageCommitSummary,
    currentSnapshotReconcileCommitPackageResult,
    currentSnapshotReconcileCommitPackage,
    currentLocalOutcomeSetPackageSummary,
    currentLocalOutcomeSetPackageImportSummary,
    currentLocalOutcomeSetPackageResolutionSummary,
    currentLocalOutcomeSetPackage,
    currentLocalOutcomeSetPackagePreviewResult,
    currentLocalOutcomeSetPackageImportDecisions,
    currentLocalOutcomeSetPackageResult,
    currentPortableLocalOutcomeThreeWayMergeResult,
    currentPortableLocalOutcomeMergeDecisions,
    currentPortableLocalOutcomeMergeResolutionSummary,
    currentPortableLocalOutcomeMergeResolutionResult,
    currentPortableLocalOutcomeMergeCommitResult,
    selectedPortableLocalOutcomeMergeItemId,
    currentCompareResult,
    currentMergeResult,
    currentResolvedMergeResult,
    currentConflictDecisions,
    currentMergeCommitResult,
    currentBranchCherryPickResult,
    currentBranchSquashResult,
  };
}

function setProjectLifecycleWorkflowState(patch) {
  if ("currentProject" in patch) currentProject = patch.currentProject;
  if ("currentProjectMap" in patch) currentProjectMap = patch.currentProjectMap;
  if ("currentProjectTimeline" in patch) currentProjectTimeline = patch.currentProjectTimeline;
  if ("currentBranchSummary" in patch) currentBranchSummary = patch.currentBranchSummary;
  if ("currentLineageGraph" in patch) currentLineageGraph = patch.currentLineageGraph;
  if ("currentBranchRebaseResult" in patch) currentBranchRebaseResult = patch.currentBranchRebaseResult;
  if ("currentBranchResetResult" in patch) currentBranchResetResult = patch.currentBranchResetResult;
  if ("currentTagSummary" in patch) currentTagSummary = patch.currentTagSummary;
  if ("currentTagPointResult" in patch) currentTagPointResult = patch.currentTagPointResult;
  if ("currentSnapshotSummary" in patch) currentSnapshotSummary = patch.currentSnapshotSummary;
  if ("currentSnapshotResult" in patch) currentSnapshotResult = patch.currentSnapshotResult;
  if ("currentSnapshotPackage" in patch) currentSnapshotPackage = patch.currentSnapshotPackage;
  if ("currentSnapshotRestoreSummary" in patch) currentSnapshotRestoreSummary = patch.currentSnapshotRestoreSummary;
  if ("currentSnapshotRestorePreview" in patch) currentSnapshotRestorePreview = patch.currentSnapshotRestorePreview;
  if ("currentSnapshotRestoreResult" in patch) currentSnapshotRestoreResult = patch.currentSnapshotRestoreResult;
  if ("currentPartialSnapshotImportSummary" in patch) currentPartialSnapshotImportSummary = patch.currentPartialSnapshotImportSummary;
  if ("currentPartialSnapshotImportResult" in patch) currentPartialSnapshotImportResult = patch.currentPartialSnapshotImportResult;
  if ("currentSnapshotReconcileSummary" in patch) currentSnapshotReconcileSummary = patch.currentSnapshotReconcileSummary;
  if ("currentSnapshotReconcilePreview" in patch) currentSnapshotReconcilePreview = patch.currentSnapshotReconcilePreview;
  if ("currentSnapshotReconcileResult" in patch) currentSnapshotReconcileResult = patch.currentSnapshotReconcileResult;
  if ("currentSnapshotReconcileCommitSummary" in patch) currentSnapshotReconcileCommitSummary = patch.currentSnapshotReconcileCommitSummary;
  if ("currentSnapshotReconcileCommitResult" in patch) currentSnapshotReconcileCommitResult = patch.currentSnapshotReconcileCommitResult;
  if ("currentSnapshotReconcileCommitCompareResult" in patch) currentSnapshotReconcileCommitCompareResult = patch.currentSnapshotReconcileCommitCompareResult;
  if ("currentSnapshotReconcileCommitPackageSummary" in patch) currentSnapshotReconcileCommitPackageSummary = patch.currentSnapshotReconcileCommitPackageSummary;
  if ("currentSnapshotReconcileCommitPackageImportSummary" in patch) currentSnapshotReconcileCommitPackageImportSummary = patch.currentSnapshotReconcileCommitPackageImportSummary;
  if ("currentSnapshotReconcileCommitPackagePreview" in patch) currentSnapshotReconcileCommitPackagePreview = patch.currentSnapshotReconcileCommitPackagePreview;
  if ("currentSnapshotReconcileCommitPackageResolutionSummary" in patch) currentSnapshotReconcileCommitPackageResolutionSummary = patch.currentSnapshotReconcileCommitPackageResolutionSummary;
  if ("currentSnapshotReconcileCommitPackageCommitSummary" in patch) currentSnapshotReconcileCommitPackageCommitSummary = patch.currentSnapshotReconcileCommitPackageCommitSummary;
  if ("currentSnapshotReconcileCommitPackageResult" in patch) currentSnapshotReconcileCommitPackageResult = patch.currentSnapshotReconcileCommitPackageResult;
  if ("currentSnapshotReconcileCommitPackage" in patch) currentSnapshotReconcileCommitPackage = patch.currentSnapshotReconcileCommitPackage;
  if ("currentLocalOutcomeSetPackageSummary" in patch) currentLocalOutcomeSetPackageSummary = patch.currentLocalOutcomeSetPackageSummary;
  if ("currentLocalOutcomeSetPackageImportSummary" in patch) currentLocalOutcomeSetPackageImportSummary = patch.currentLocalOutcomeSetPackageImportSummary;
  if ("currentLocalOutcomeSetPackageResolutionSummary" in patch) currentLocalOutcomeSetPackageResolutionSummary = patch.currentLocalOutcomeSetPackageResolutionSummary;
  if ("currentLocalOutcomeSetPackage" in patch) currentLocalOutcomeSetPackage = patch.currentLocalOutcomeSetPackage;
  if ("currentLocalOutcomeSetPackagePreviewResult" in patch) currentLocalOutcomeSetPackagePreviewResult = patch.currentLocalOutcomeSetPackagePreviewResult;
  if ("currentLocalOutcomeSetPackageImportDecisions" in patch) currentLocalOutcomeSetPackageImportDecisions = patch.currentLocalOutcomeSetPackageImportDecisions;
  if ("currentLocalOutcomeSetPackageResult" in patch) currentLocalOutcomeSetPackageResult = patch.currentLocalOutcomeSetPackageResult;
  if ("currentPortableLocalOutcomeThreeWayMergeResult" in patch) currentPortableLocalOutcomeThreeWayMergeResult = patch.currentPortableLocalOutcomeThreeWayMergeResult;
  if ("currentPortableLocalOutcomeMergeDecisions" in patch) currentPortableLocalOutcomeMergeDecisions = patch.currentPortableLocalOutcomeMergeDecisions;
  if ("currentPortableLocalOutcomeMergeResolutionSummary" in patch) currentPortableLocalOutcomeMergeResolutionSummary = patch.currentPortableLocalOutcomeMergeResolutionSummary;
  if ("currentPortableLocalOutcomeMergeResolutionResult" in patch) currentPortableLocalOutcomeMergeResolutionResult = patch.currentPortableLocalOutcomeMergeResolutionResult;
  if ("currentPortableLocalOutcomeMergeCommitResult" in patch) currentPortableLocalOutcomeMergeCommitResult = patch.currentPortableLocalOutcomeMergeCommitResult;
  if ("selectedPortableLocalOutcomeMergeItemId" in patch) selectedPortableLocalOutcomeMergeItemId = patch.selectedPortableLocalOutcomeMergeItemId;
  if ("currentCompareResult" in patch) currentCompareResult = patch.currentCompareResult;
  if ("currentMergeResult" in patch) currentMergeResult = patch.currentMergeResult;
  if ("currentResolvedMergeResult" in patch) currentResolvedMergeResult = patch.currentResolvedMergeResult;
  if ("currentConflictDecisions" in patch) currentConflictDecisions = patch.currentConflictDecisions;
  if ("currentMergeCommitResult" in patch) currentMergeCommitResult = patch.currentMergeCommitResult;
  if ("currentBranchCherryPickResult" in patch) currentBranchCherryPickResult = patch.currentBranchCherryPickResult;
  if ("currentBranchSquashResult" in patch) currentBranchSquashResult = patch.currentBranchSquashResult;
}

function getProjectLifecycleWorkflowController() {
  if (!projectLifecycleWorkflowController) {
    const factory = window.ProjectLifecycleWorkflow?.createProjectLifecycleController;
    if (!factory) {
      throw new Error("Project lifecycle workflow module is not loaded");
    }
    projectLifecycleWorkflowController = factory({
      els,
      getState: getProjectLifecycleWorkflowState,
      setState: setProjectLifecycleWorkflowState,
      pretty,
      parseCsvList,
      postJson,
      renderResult,
      setStatus,
      refreshProjectHydratedPanels,
      downloadBlob,
    });
  }
  return projectLifecycleWorkflowController;
}

function getGraphSessionWorkspaceState() {
  return {
    currentResult,
    previewMode,
    graphDoc,
    selectedEntityId,
    dragState,
    currentSession,
    currentProject,
  };
}

function setGraphSessionWorkspaceState(patch) {
  if ("currentResult" in patch) currentResult = patch.currentResult;
  if ("previewMode" in patch) previewMode = patch.previewMode;
  if ("graphDoc" in patch) graphDoc = patch.graphDoc;
  if ("selectedEntityId" in patch) selectedEntityId = patch.selectedEntityId;
  if ("dragState" in patch) dragState = patch.dragState;
  if ("currentSession" in patch) currentSession = patch.currentSession;
  if ("currentProject" in patch) currentProject = patch.currentProject;
}

function getGraphSessionWorkspaceController() {
  if (!graphSessionWorkspaceController) {
    const factory = window.GraphSessionWorkspace?.createGraphSessionWorkspaceController;
    if (!factory) {
      throw new Error("Graph session workspace module is not loaded");
    }
    graphSessionWorkspaceController = factory({
      els,
      getState: getGraphSessionWorkspaceState,
      setState: setGraphSessionWorkspaceState,
      pretty,
      parseInitialState,
      entityLabel,
      postJson,
      renderResult,
      setStatus,
      downloadBlob,
      renderProjectSessions: () => getInspectorPanelController().renderProjectSessions(),
    });
  }
  return graphSessionWorkspaceController;
}

function getInspectorPanelController() {
  if (!inspectorPanelController) {
    const factory = window.InspectorPanelWorkflow?.createInspectorPanelController;
    if (!factory) {
      throw new Error("Inspector panel workflow module is not loaded");
    }
    inspectorPanelController = factory({
      els,
      getCurrentBranchSummary: () => currentBranchSummary,
      getProjectOperationsController: getProjectOperationsWorkflowController,
      getProjectWorkspaceController: getProjectWorkspaceWorkflowController,
      getProjectLifecycleController: getProjectLifecycleWorkflowController,
      getSnapshotReconcileController: getSnapshotReconcileWorkflowController,
      getReconcileCommitPackageController: getReconcileCommitPackageWorkflowController,
      getLocalOutcomeSetPackageController: getLocalOutcomeSetPackageWorkflowController,
      getPortableLocalOutcomeMergeController: getPortableLocalOutcomeMergeController,
    });
  }
  return inspectorPanelController;
}

function getInspectorActionController() {
  if (!inspectorActionController) {
    const factory = window.InspectorActionWorkflow?.createInspectorActionController;
    if (!factory) {
      throw new Error("Inspector action workflow module is not loaded");
    }
    inspectorActionController = factory({
      getGraphSessionWorkspaceController,
      getProjectLifecycleController: getProjectLifecycleWorkflowController,
      getProjectOperationsController: getProjectOperationsWorkflowController,
      getSnapshotReconcileController: getSnapshotReconcileWorkflowController,
      getReconcileCommitPackageController: getReconcileCommitPackageWorkflowController,
      getLocalOutcomeSetPackageController: getLocalOutcomeSetPackageWorkflowController,
      getPortableLocalOutcomeMergeController,
      getInspectorPanelController,
    });
  }
  return inspectorActionController;
}

function getInspectorBootstrapController() {
  if (!inspectorBootstrapController) {
    const factory = window.InspectorBootstrapWorkflow?.createInspectorBootstrapController;
    if (!factory) {
      throw new Error("Inspector bootstrap workflow module is not loaded");
    }
    const actionController = getInspectorActionController();
    inspectorBootstrapController = factory({
      els,
      getPreviewMode: () => previewMode,
      setPreviewMode: (value) => { previewMode = value; },
      renderSvg,
      actions: actionController,
      initializers: actionController,
    });
  }
  return inspectorBootstrapController;
}
function downloadBlob(text, filename) {
  const blob = new Blob([text], {type: "application/json"});
  const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
}
function parseCsvList(raw) {
  return (raw || "")
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
}
getInspectorBootstrapController().bindEventHandlers();
getInspectorBootstrapController().initialize();
```


## FILE: inspector/inspector-core-workflow.js

Size: 7458 bytes

```file
(function () {
  function createInspectorCoreController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      hydrateProjectResult,
      renderSvg,
      renderGraph,
      renderers,
      updaters,
    } = config;

    function state() {
      return getState();
    }

    function patch(nextState) {
      setState(nextState);
    }

    function syncActiveSession(activeSession) {
      if (!activeSession) return;

      patch({ currentSession: activeSession });
      if (typeof activeSession.project?.source_text === "string" && els.inputText) {
        els.inputText.value = activeSession.project.source_text;
      }
      if (els.initialState) {
        els.initialState.value = activeSession.project?.initial_state !== undefined
          ? pretty(activeSession.project.initial_state)
          : "";
      }
      if (activeSession.project?.profile && els.profile) {
        els.profile.value = activeSession.project.profile;
      }
      if (els.sessionJson) {
        els.sessionJson.value = pretty(activeSession);
      }
    }

    function refreshProjectUiForSnapshotReconcileWorkflow() {
      renderers.renderProjectSessions();
      renderers.renderProjectMap();
      renderers.renderProjectTimeline();
      renderers.renderBranchList();
      renderers.renderTagPointList();
      renderers.renderSnapshotList();
      renderers.renderSnapshotReconcileList();
      renderers.renderSnapshotReconcileCommitList();
      renderers.renderLineageGraph();
      updaters.updateTagTargetSessions();
      updaters.updateSnapshotSelectors();
      updaters.updateResetSelectors();
      updaters.updateRebaseSelectors();
      updaters.updateCherryPickSelectors();
      updaters.updateSquashSelectors();
      updaters.updatePartialImportSelectors();
      updaters.updateSnapshotReconcileSelectors();
      updaters.updateCompareSelectors();
      updaters.updateMergeSelectors();
    }

    function renderSupplementaryPanelsForSnapshotReconcileWorkflow() {
      renderers.renderTagPointResult();
      renderers.renderSnapshotResult();
      renderers.renderSnapshotRestorePreview();
      renderers.renderSnapshotRestoreResult();
      renderers.renderPartialImportResult();
      renderers.renderCompareResult();
      renderers.renderMergeResult();
    }

    function refreshProjectUiForReconcileCommitPackageWorkflow() {
      renderers.renderProjectSessions();
      renderers.renderProjectMap();
      renderers.renderProjectTimeline();
      renderers.renderBranchList();
      renderers.renderTagPointList();
      renderers.renderLineageGraph();
    }

    function renderLocalOutcomeSetPackagePanels() {
      renderers.renderLocalOutcomeSetPackageList();
      renderers.renderLocalOutcomeSetPackagePreviewResult();
      renderers.renderLocalOutcomeSetPackageDecisionList();
      renderers.renderLocalOutcomeSetPackageResult();
    }

    function refreshProjectHydratedPanels() {
      renderers.renderProjectSessions();
      renderers.renderProjectMap();
      renderers.renderProjectTimeline();
      renderers.renderBranchList();
      renderers.renderTagPointList();
      renderers.renderSnapshotList();
      renderers.renderSnapshotReconcileList();
      renderers.renderSnapshotReconcileCommitList();
      renderers.renderReconcileCommitPackageList();
      renderers.renderReconcileCommitPackagePreview();
      renderers.renderReconcileCommitPackageDecisionList();
      renderers.renderReconcileCommitPackageResult();
      renderers.renderSnapshotReconcileCommitCompareResult();
      renderers.renderLineageGraph();
      updaters.updateTagTargetSessions();
      updaters.updatePartialImportSelectors();
      updaters.updateSnapshotSelectors();
      updaters.updateResetSelectors();
      updaters.updateRebaseSelectors();
      updaters.updateCherryPickSelectors();
      updaters.updateSquashSelectors();
      updaters.updateCompareSelectors();
      updaters.updateMergeSelectors();
      updaters.updateReconcileCommitPackageSelectors();
      updaters.updateLocalOutcomeSetPackageSelectors();
      updaters.updatePortableLocalOutcomeMergeSelectors();
      renderers.renderTagPointResult();
      renderers.renderSnapshotResult();
      renderers.renderSnapshotRestorePreview();
      renderers.renderSnapshotRestoreResult();
      renderers.renderPartialImportResult();
      renderers.renderSnapshotReconcileResult();
      renderers.renderSnapshotReconcileCommitResult();
      renderers.renderCompareResult();
      renderers.renderMergeResult();
      renderers.renderResolvedMergeResult();
      renderers.renderMergeCommitResult();
      renderers.renderBranchResetResult();
      renderers.renderBranchRebaseResult();
      renderers.renderBranchCherryPickResult();
      renderers.renderBranchSquashResult();
      renderLocalOutcomeSetPackagePanels();
      renderers.renderPortableLocalOutcomeThreeWayMergeResult();
      renderers.renderPortableLocalOutcomeMergeDecisionList();
      renderers.renderPortableLocalOutcomeMergeResolutionResult();
      renderers.renderPortableLocalOutcomeMergeCommitResult();
      renderers.renderPortableLocalOutcomeWorkstation();
    }

    function renderResult(result) {
      patch({ currentResult: result });

      if (result.session_name && els.sessionName) {
        els.sessionName.value = result.session_name;
      }
      if (typeof result.source_text === "string" && els.inputText) {
        els.inputText.value = result.source_text;
      }
      if (result.profile && els.profile) {
        els.profile.value = result.profile;
      }

      if (hydrateProjectResult(result)) {
        const activeSession = result.project_index?.sessions?.find(
          (item) => item.session_id === result.project_index.active_session_id,
        )?.session || null;
        syncActiveSession(activeSession);
        refreshProjectHydratedPanels();
      }

      if (result.ui_state?.preview_mode) {
        patch({ previewMode: result.ui_state.preview_mode });
      }

      if (els.normalizedText) {
        els.normalizedText.textContent = [
          `normalized_text:\n${result.normalized_text || ""}`,
          "",
          `slinear:\n${result.slinear || ""}`,
          result.decomposed_slinear ? `\ndecomposed_slinear:\n${result.decomposed_slinear}` : "",
        ].join("\n");
      }
      if (els.validationText) {
        els.validationText.textContent = pretty(result.validation);
      }
      if (els.astText) {
        els.astText.textContent = pretty(result.ast_document);
      }
      if (els.runtimeText) {
        els.runtimeText.textContent = pretty(result.runtime_report);
      }
      if (els.stateText) {
        els.stateText.textContent = pretty(result.state_report);
      }

      if (result.graph_document) {
        const graphDocument = structuredClone(result.graph_document);
        patch({
          graphDoc: graphDocument,
          selectedEntityId: result.ui_state?.selected_entity_id || graphDocument.root_entity_id || null,
        });
        renderGraph();
      }

      renderSvg();
    }

    return {
      refreshProjectUiForSnapshotReconcileWorkflow,
      renderSupplementaryPanelsForSnapshotReconcileWorkflow,
      refreshProjectUiForReconcileCommitPackageWorkflow,
      renderLocalOutcomeSetPackagePanels,
      refreshProjectHydratedPanels,
      renderResult,
    };
  }

  window.InspectorCoreWorkflow = {
    createInspectorCoreController,
  };
})();
```


## FILE: inspector/project-workspace-workflow.js

Size: 16273 bytes

```file
(function () {
  function createProjectWorkspaceController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      postJson,
      renderResult,
      setStatus,
    } = config;

    function state() {
      return getState();
    }

    function hydrateProjectResult(result) {
      if (!result.project_index?.project_name) return false;

      if (els.projectName) {
        els.projectName.value = result.project_index.project_name;
      }

      setState({
        currentProject: result.project_index,
        currentProjectMap: result.workspace_dependency_map || null,
        currentProjectTimeline: result.workspace_timeline || null,
        currentBranchSummary: result.branch_summary || null,
        currentLineageGraph: result.workspace_lineage_graph || null,
        currentBranchRebaseResult: result.branch_rebase_result || state().currentBranchRebaseResult,
        currentBranchResetResult: result.branch_reset_result || state().currentBranchResetResult,
        currentTagSummary: result.tag_point_summary || state().currentTagSummary,
        currentTagPointResult: result.tag_release_result || state().currentTagPointResult,
        currentSnapshotSummary: result.snapshot_export_summary || state().currentSnapshotSummary,
        currentSnapshotResult: result.snapshot_export_result || state().currentSnapshotResult,
        currentSnapshotPackage: result.snapshot_export_package || state().currentSnapshotPackage,
        currentSnapshotRestoreSummary: result.snapshot_restore_summary || state().currentSnapshotRestoreSummary,
        currentSnapshotRestoreResult: result.snapshot_restore_result || state().currentSnapshotRestoreResult,
        currentPartialSnapshotImportSummary: result.partial_snapshot_import_summary || state().currentPartialSnapshotImportSummary,
        currentPartialSnapshotImportResult: result.partial_snapshot_import_result || state().currentPartialSnapshotImportResult,
        currentSnapshotReconcileSummary: result.snapshot_reconcile_summary || state().currentSnapshotReconcileSummary,
        currentSnapshotReconcilePreview: result.snapshot_reconcile_preview || state().currentSnapshotReconcilePreview,
        currentSnapshotReconcileResult: result.snapshot_reconcile_result || state().currentSnapshotReconcileResult,
        currentSnapshotReconcileCommitSummary: result.snapshot_reconcile_commit_summary || state().currentSnapshotReconcileCommitSummary,
        currentSnapshotReconcileCommitResult: result.snapshot_reconcile_commit_result || state().currentSnapshotReconcileCommitResult,
        currentSnapshotReconcileCommitCompareResult: result.snapshot_reconcile_commit_compare_result || state().currentSnapshotReconcileCommitCompareResult,
        currentSnapshotReconcileCommitPackageSummary: result.snapshot_reconcile_commit_package_summary || state().currentSnapshotReconcileCommitPackageSummary,
        currentSnapshotReconcileCommitPackageImportSummary: result.snapshot_reconcile_commit_package_import_summary || state().currentSnapshotReconcileCommitPackageImportSummary,
        currentSnapshotReconcileCommitPackagePreview: result.snapshot_reconcile_commit_package_preview || state().currentSnapshotReconcileCommitPackagePreview,
        currentSnapshotReconcileCommitPackageResolutionSummary: result.snapshot_reconcile_commit_package_resolution_summary || state().currentSnapshotReconcileCommitPackageResolutionSummary,
        currentSnapshotReconcileCommitPackageCommitSummary: result.snapshot_reconcile_commit_package_commit_summary || state().currentSnapshotReconcileCommitPackageCommitSummary,
        currentSnapshotReconcileCommitPackageResult:
          result.snapshot_reconcile_commit_package_result
          || result.snapshot_reconcile_commit_package_import_result
          || result.snapshot_reconcile_commit_package_resolution_result
          || result.snapshot_reconcile_commit_package_commit_result
          || state().currentSnapshotReconcileCommitPackageResult,
        currentSnapshotReconcileCommitPackage: result.snapshot_reconcile_commit_package || state().currentSnapshotReconcileCommitPackage,
        currentLocalOutcomeSetPackageSummary: result.local_outcome_set_package_summary || state().currentLocalOutcomeSetPackageSummary,
        currentLocalOutcomeSetPackageImportSummary: result.local_outcome_set_package_import_summary || state().currentLocalOutcomeSetPackageImportSummary,
        currentLocalOutcomeSetPackageResolutionSummary: result.local_outcome_set_package_resolution_summary || state().currentLocalOutcomeSetPackageResolutionSummary,
        currentLocalOutcomeSetPackage: result.local_outcome_set_package || state().currentLocalOutcomeSetPackage,
        currentLocalOutcomeSetPackagePreviewResult: result.local_outcome_set_package_preview_result || state().currentLocalOutcomeSetPackagePreviewResult,
        currentLocalOutcomeSetPackageResult:
          result.local_outcome_set_package_result
          || result.local_outcome_set_package_import_result
          || result.local_outcome_set_package_resolution_result
          || result.local_outcome_set_package_commit_result
          || state().currentLocalOutcomeSetPackageResult,
        currentPortableLocalOutcomeMergeResolutionSummary:
          result.portable_local_outcome_package_merge_resolution_summary || state().currentPortableLocalOutcomeMergeResolutionSummary,
        currentPortableLocalOutcomeMergeResolutionResult:
          result.portable_local_outcome_package_merge_resolution_result || state().currentPortableLocalOutcomeMergeResolutionResult,
        currentPortableLocalOutcomeMergeCommitResult:
          result.portable_local_outcome_package_merge_commit_result || state().currentPortableLocalOutcomeMergeCommitResult,
        currentBranchCherryPickResult: result.branch_cherry_pick_result || state().currentBranchCherryPickResult,
        currentBranchSquashResult: result.branch_squash_result || state().currentBranchSquashResult,
      });

      if (els.projectJson && result.project_index) {
        els.projectJson.value = pretty(result.project_index);
      }

      return true;
    }

    async function activateProjectSession(sessionId, successMessage, failurePrefix) {
      const currentProject = state().currentProject;
      if (!currentProject || !sessionId) return;

      try {
        const data = await postJson("/api/switch-project-session", {
          project_index: currentProject,
          session_id: sessionId,
        });
        renderResult(data);
        setStatus(successMessage);
      } catch (err) {
        setStatus(`${failurePrefix}: ${err.message}`);
      }
    }

    function renderProjectTimeline() {
      if (!els.projectTimeline) return;
      const timeline = state().currentProjectTimeline;
      if (!timeline || !Array.isArray(timeline.events) || !timeline.events.length) {
        els.projectTimeline.innerHTML = '<div class="project-map-empty">No timeline available</div>';
        return;
      }

      const list = document.createElement("div");
      list.className = "timeline-list";
      for (const event of timeline.events) {
        const item = document.createElement("div");
        item.className = "timeline-item" + (event.is_active_session_event ? " active" : "");
        item.innerHTML = `<strong>#${event.seq} · ${event.title}</strong><div class="meta">${event.event_type}${event.session_id ? " · " + event.session_id : ""}</div>`;
        if (event.session_id && state().currentProject) {
          const btn = document.createElement("button");
          btn.textContent = "Activate from event";
          btn.addEventListener("click", async () => {
            await activateProjectSession(event.session_id, `Activated ${event.session_id}`, "Timeline switch failed");
          });
          item.appendChild(btn);
        }
        list.appendChild(item);
      }
      els.projectTimeline.innerHTML = "";
      els.projectTimeline.appendChild(list);
    }

    function renderProjectMap() {
      if (!els.projectDependencyMap) return;
      const projectMap = state().currentProjectMap;
      if (!projectMap || !Array.isArray(projectMap.nodes) || !projectMap.nodes.length) {
        els.projectDependencyMap.innerHTML = '<div class="project-map-empty">No dependency map available</div>';
        return;
      }

      let maxX = 0;
      let maxY = 0;
      for (const node of projectMap.nodes) {
        maxX = Math.max(maxX, node.x || 0);
        maxY = Math.max(maxY, node.y || 0);
      }
      const width = Math.max(760, maxX + 180);
      const height = Math.max(260, maxY + 120);

      const linkParts = [];
      const nodeIndex = new Map(projectMap.nodes.map((node) => [node.session_id, node]));
      for (const link of projectMap.links || []) {
        const from = nodeIndex.get(link.from_session_id);
        const to = nodeIndex.get(link.to_session_id);
        if (!from || !to) continue;
        const x1 = (from.x || 60) + 70;
        const y1 = (from.y || 60) + 24;
        const x2 = (to.x || 60) + 70;
        const y2 = (to.y || 60) + 24;
        const stroke = link.relation === "flow" ? "#2563eb" : "#9ca3af";
        const dash = link.relation === "shared" ? ' stroke-dasharray="5,4"' : "";
        const mx = (x1 + x2) / 2;
        const my = (y1 + y2) / 2 - 8;
        const label = `${link.relation}:${(link.tokens || []).slice(0, 2).join(",")}`;
        linkParts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" stroke-width="1.6"${dash}/>`);
        linkParts.push(`<text class="project-map-meta" x="${mx}" y="${my}" text-anchor="middle">${label}</text>`);
      }

      const nodeParts = [];
      for (const node of projectMap.nodes) {
        const x = node.x || 60;
        const y = node.y || 60;
        const stroke = node.is_active ? "#10b981" : "#111827";
        const fill = node.is_active ? "#ecfdf5" : "#ffffff";
        const tokens = (node.outputs || []).slice(0, 3).join(", ");
        nodeParts.push(`
          <g class="project-map-node" data-session-id="${node.session_id}">
            <rect x="${x}" y="${y}" width="150" height="54" rx="14" ry="14" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
            <text class="project-map-label" x="${x + 75}" y="${y + 20}" text-anchor="middle">${node.session_name}</text>
            <text class="project-map-meta" x="${x + 75}" y="${y + 36}" text-anchor="middle">${node.profile || "-"} · out:${tokens || "-"}</text>
          </g>
        `);
      }

      els.projectDependencyMap.innerHTML = `<svg viewBox="0 0 ${width} ${height}">${linkParts.join("\n")}${nodeParts.join("\n")}</svg>`;
      els.projectDependencyMap.querySelectorAll(".project-map-node").forEach((el) => {
        el.addEventListener("click", async () => {
          const sessionId = el.getAttribute("data-session-id");
          await activateProjectSession(sessionId, `Activated ${sessionId}`, "Switch failed");
        });
      });
    }

    function renderBranchList() {
      if (!els.branchList) return;
      els.branchList.innerHTML = "";
      const branches = state().currentBranchSummary || [];
      for (const branch of branches) {
        const wrap = document.createElement("div");
        wrap.className = "branch-item" + (branch.is_active_branch ? " active" : "");
        wrap.innerHTML = `<strong>${branch.branch_name}</strong><div class="meta">root: ${branch.root_session_id || "-"} · head: ${branch.head_session_id || "-"} · sessions: ${branch.session_count}</div>`;
        const btn = document.createElement("button");
        btn.textContent = "Activate head";
        btn.addEventListener("click", async () => {
          if (!branch.head_session_id) return;
          await activateProjectSession(branch.head_session_id, `Activated head of ${branch.branch_name}`, "Branch head switch failed");
        });
        wrap.appendChild(btn);
        els.branchList.appendChild(wrap);
      }
    }

    function renderLineageGraph() {
      if (!els.projectLineageGraph) return;
      const lineageGraph = state().currentLineageGraph;
      if (!lineageGraph || !Array.isArray(lineageGraph.nodes) || !lineageGraph.nodes.length) {
        els.projectLineageGraph.innerHTML = '<div class="project-map-empty">No lineage graph available</div>';
        return;
      }

      let maxX = 0;
      let maxY = 0;
      for (const node of lineageGraph.nodes) {
        maxX = Math.max(maxX, node.x || 0);
        maxY = Math.max(maxY, node.y || 0);
      }
      const width = Math.max(760, maxX + 180);
      const height = Math.max(260, maxY + 120);

      const nodeIndex = new Map(lineageGraph.nodes.map((node) => [node.session_id, node]));
      const edgeParts = [];
      for (const edge of lineageGraph.edges || []) {
        const from = nodeIndex.get(edge.from_session_id);
        const to = nodeIndex.get(edge.to_session_id);
        if (!from || !to) continue;
        const x1 = (from.x || 60) + 72;
        const y1 = (from.y || 60) + 24;
        const x2 = (to.x || 60) + 72;
        const y2 = (to.y || 60) + 24;
        const dash = edge.relation === "merge_parent" ? ' stroke-dasharray="5,4"' : "";
        edgeParts.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#111827" stroke-width="1.4"${dash}/>`);
      }

      const nodeParts = [];
      for (const node of lineageGraph.nodes) {
        const x = node.x || 60;
        const y = node.y || 60;
        const fill = node.is_active ? "#ecfdf5" : "#ffffff";
        const stroke = node.is_active ? "#10b981" : "#111827";
        nodeParts.push(`
          <g class="project-map-node" data-session-id="${node.session_id}">
            <rect x="${x}" y="${y}" width="150" height="68" rx="14" ry="14" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
            <text class="project-map-label" x="${x + 75}" y="${y + 18}" text-anchor="middle">${node.session_name}</text>
            <text class="project-map-meta" x="${x + 75}" y="${y + 35}" text-anchor="middle">${node.branch_name} · ${node.lineage_kind}</text>
            <text class="project-map-meta" x="${x + 75}" y="${y + 50}" text-anchor="middle">${(node.attached_points && node.attached_points.length) ? node.attached_points.map((point) => point.tag_name).slice(0, 2).join(", ") : ""}</text>
          </g>
        `);
      }

      els.projectLineageGraph.innerHTML = `<svg viewBox="0 0 ${width} ${height}">${edgeParts.join("\n")}${nodeParts.join("\n")}</svg>`;
      els.projectLineageGraph.querySelectorAll(".project-map-node").forEach((el) => {
        el.addEventListener("click", async () => {
          const sessionId = el.getAttribute("data-session-id");
          await activateProjectSession(sessionId, `Activated ${sessionId}`, "Lineage switch failed");
        });
      });
    }

    function renderProjectSessions() {
      if (!els.projectSessionsList) return;
      els.projectSessionsList.innerHTML = "";
      const currentProject = state().currentProject;
      if (!currentProject || !Array.isArray(currentProject.sessions)) return;

      for (const item of currentProject.sessions) {
        const wrap = document.createElement("div");
        wrap.className = "project-session-item" + (item.session_id === currentProject.active_session_id ? " active" : "");
        wrap.innerHTML = `<strong>${item.session_name}</strong><div class="meta">${item.session_id} · ${item.profile || "-"} · ${item.source_mode || "-"}</div><div class="meta">${(item.tags || []).join(", ")}</div>`;
        const buttons = document.createElement("div");
        buttons.className = "buttons";
        const activate = document.createElement("button");
        activate.textContent = "Activate";
        activate.addEventListener("click", async () => {
          await activateProjectSession(item.session_id, `Activated ${item.session_id}`, "Switch failed");
        });
        buttons.appendChild(activate);
        wrap.appendChild(buttons);
        els.projectSessionsList.appendChild(wrap);
      }
    }

    return {
      hydrateProjectResult,
      renderProjectTimeline,
      renderProjectMap,
      renderBranchList,
      renderLineageGraph,
      renderProjectSessions,
    };
  }

  window.ProjectWorkspaceWorkflow = {
    createProjectWorkspaceController,
  };
})();
```


## FILE: inspector/reconcile-commit-package-workflow.js

Size: 24510 bytes

```file
(function () {
  function createReconcileCommitPackageController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      postJson,
      renderResult,
      setStatus,
      refreshProjectUi,
      updateLocalOutcomeSetPackageSelectors,
      renderLocalOutcomeSetPackagePanels,
    } = config;

    function state() {
      return getState();
    }

    function packageGuidance() {
      return window.InspectorPackageGuidance || null;
    }

    function analyzePackageInput() {
      const guidance = packageGuidance();
      if (!guidance) {
        return {
          state: !els.importReconcileCommitPackageJson?.value.trim() ? "empty" : "valid",
          data: null,
          summary: null,
          message: "Package guidance helper is unavailable",
        };
      }
      return guidance.analyzeText(els.importReconcileCommitPackageJson?.value || "", "reconcile_commit_package");
    }

    function applySuggestedInputValue(element, nextValue) {
      if (!element || !nextValue) return;
      const normalized = String(nextValue).trim();
      if (!normalized) return;
      const current = (element.value || "").trim();
      const previous = element.dataset.autofillValue || "";
      if (!current || current === previous) {
        element.value = normalized;
        element.dataset.autofillValue = normalized;
      }
    }

    function applySuggestedSelectValue(element, nextValue) {
      if (!element || !nextValue) return;
      const normalized = String(nextValue).trim();
      if (!normalized) return;
      const options = Array.from(element.options || []);
      if (!options.some((item) => item.value === normalized)) return;
      const current = element.value || "";
      const previous = element.dataset.autofillValue || "";
      if (!current || current === previous || !options.some((item) => item.value === current)) {
        element.value = normalized;
        element.dataset.autofillValue = normalized;
      }
    }

    function syncPackageAutofill(analysis) {
      if (analysis.state !== "valid" || !analysis.data) return;
      const packageName = analysis.data.package_name || "standalone_package";
      const branchName = analysis.data.exported_commit?.target_branch_name || "";
      applySuggestedInputValue(els.importReconcileCommitPackageName, `${packageName}_import`);
      applySuggestedSelectValue(els.importReconcileCommitTargetBranch, branchName);
    }

    function syncExportAutofill() {
      const commitName = els.exportReconcileCommitName?.value?.trim() || "";
      if (!commitName) return;
      applySuggestedInputValue(els.exportReconcileCommitPackageName, `${commitName}_package`);
    }

    function syncCommitAutofill() {
      const currentResult = state().currentSnapshotReconcileCommitPackageResult;
      const resolutionName = currentResult?.resolution_name || "";
      if (!resolutionName) return;
      applySuggestedInputValue(els.reconcileCommitPackageCommitName, `${resolutionName}_commit`);
      applySuggestedInputValue(els.reconcileCommitPackagePromotePointName, `${resolutionName}_release`);
    }

    function renderCurrentPackageSummary() {
      if (!els.reconcileCommitPackageCurrentSummary) return;
      const guidance = packageGuidance();
      if (guidance?.renderPayloadSummary) {
        guidance.renderPayloadSummary(
          els.reconcileCommitPackageCurrentSummary,
          state().currentSnapshotReconcileCommitPackage,
          "reconcile_commit_package",
          {
            headline: "Current standalone package payload",
            emptyMessage: "Export a standalone package or load one in this flow to see a structured package summary here.",
            note: "Current standalone package payload. Use current exported package to load it into the import textarea.",
          },
        );
        return;
      }
      els.reconcileCommitPackageCurrentSummary.textContent = state().currentSnapshotReconcileCommitPackage
        ? pretty(state().currentSnapshotReconcileCommitPackage)
        : "No current standalone package payload.";
    }

    function syncPackageGuidance() {
      const guidance = packageGuidance();
      const analysis = analyzePackageInput();
      if (guidance) {
        guidance.renderHint(els.reconcileCommitPackageHint, analysis);
      } else if (els.reconcileCommitPackageHint) {
        els.reconcileCommitPackageHint.textContent = analysis.message || "";
      }
      syncPackageAutofill(analysis);
      return analysis;
    }

    function parsePackageInput() {
      const analysis = syncPackageGuidance();
      if (analysis.state === "empty") {
        setStatus("Standalone package JSON is empty. Paste a standalone promoted outcome package before previewing or importing.");
        return null;
      }
      if (analysis.state === "invalid" || analysis.state === "mismatch" || analysis.state === "unknown") {
        setStatus(analysis.message);
        return null;
      }
      return analysis.data;
    }

    function updateProjectState(data, patch = {}) {
      setState({
        currentProject: data.project_index,
        currentProjectMap: data.workspace_dependency_map || null,
        currentProjectTimeline: data.workspace_timeline || null,
        currentBranchSummary: data.branch_summary || null,
        currentLineageGraph: data.workspace_lineage_graph || null,
        currentTagSummary: data.tag_point_summary || null,
        ...patch,
      });
      if (els.projectJson && data.project_index) {
        els.projectJson.value = pretty(data.project_index);
      }
    }

    function updateSelectors() {
      if (els.exportReconcileCommitName) {
        els.exportReconcileCommitName.innerHTML = "";
        for (const item of (state().currentSnapshotReconcileCommitSummary || [])) {
          const opt = document.createElement("option");
          opt.value = item.commit_name;
          opt.textContent = `${item.commit_name} · ${item.snapshot_name}`;
          els.exportReconcileCommitName.appendChild(opt);
        }
      }
      if (els.importReconcileCommitTargetBranch) {
        els.importReconcileCommitTargetBranch.innerHTML = "";
        for (const item of (state().currentBranchSummary || [])) {
          const opt = document.createElement("option");
          opt.value = item.branch_name;
          opt.textContent = item.branch_name;
          if (item.is_active_branch) opt.selected = true;
          els.importReconcileCommitTargetBranch.appendChild(opt);
        }
      }
      syncExportAutofill();
    }

    function renderDecisionList() {
      if (!els.reconcileCommitPackageDecisionList) return;
      const preview = state().currentSnapshotReconcileCommitPackagePreview;
      if (!preview?.preview_items?.length) {
        els.reconcileCommitPackageDecisionList.innerHTML = '<div class="project-map-empty">No package import decisions</div>';
        return;
      }
      els.reconcileCommitPackageDecisionList.innerHTML = "";
      for (const item of preview.preview_items) {
        const wrap = document.createElement("div");
        wrap.className = "conflict-item";
        const decision = state().currentSnapshotReconcileCommitPackageImportDecisions[item.original_session_id] || { choice: "use_package" };
        wrap.innerHTML = `<strong>${item.original_session_id} · ${item.session_name || ""}</strong><div class="meta">status: ${item.status} · compare: ${item.compare_session_id || "-"} · target: ${item.target_branch_name}</div>`;

        const row = document.createElement("div");
        row.className = "row";
        const select = document.createElement("select");
        for (const choice of ["use_package", "use_current", "skip", "custom_text"]) {
          const opt = document.createElement("option");
          opt.value = choice;
          opt.textContent = choice;
          if (decision.choice === choice) opt.selected = true;
          select.appendChild(opt);
        }

        const customInput = document.createElement("textarea");
        customInput.className = "small";
        customInput.placeholder = "Custom source_text";
        customInput.value = decision.choice === "custom_text" ? (decision.custom_text || "") : "";
        customInput.style.display = decision.choice === "custom_text" ? "block" : "none";

        select.addEventListener("change", () => {
          const decisions = { ...state().currentSnapshotReconcileCommitPackageImportDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = select.value;
          if (select.value !== "custom_text") delete decisions[item.original_session_id].custom_text;
          setState({ currentSnapshotReconcileCommitPackageImportDecisions: decisions });
          customInput.style.display = select.value === "custom_text" ? "block" : "none";
        });

        customInput.addEventListener("input", () => {
          const decisions = { ...state().currentSnapshotReconcileCommitPackageImportDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = "custom_text";
          decisions[item.original_session_id].custom_text = customInput.value;
          setState({ currentSnapshotReconcileCommitPackageImportDecisions: decisions });
        });

        row.appendChild(select);
        row.appendChild(customInput);
        wrap.appendChild(row);
        els.reconcileCommitPackageDecisionList.appendChild(wrap);
      }
    }

    function setDecisionForAll(choice, conflictsOnly = false) {
      const preview = state().currentSnapshotReconcileCommitPackagePreview;
      if (!preview?.preview_items?.length) return;
      const decisions = { ...state().currentSnapshotReconcileCommitPackageImportDecisions };
      for (const item of preview.preview_items) {
        if (conflictsOnly && !item.conflict_like) continue;
        decisions[item.original_session_id] = { choice };
      }
      setState({ currentSnapshotReconcileCommitPackageImportDecisions: decisions });
      renderDecisionList();
    }

    async function applyDecisions() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/resolve-snapshot-reconcile-commit-package-import", {
          current_project_index: currentProject,
          package: pkg,
          decisions: state().currentSnapshotReconcileCommitPackageImportDecisions,
          resolution_name: els.importReconcileCommitPackageName?.value.trim() || undefined,
          target_branch_name: els.importReconcileCommitTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedReconcileCommit?.checked,
        });
        updateProjectState(data, {
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitPackageSummary: data.snapshot_reconcile_commit_package_summary || null,
          currentSnapshotReconcileCommitPackageImportSummary: data.snapshot_reconcile_commit_package_import_summary || null,
          currentSnapshotReconcileCommitPackageResolutionSummary: data.snapshot_reconcile_commit_package_resolution_summary || null,
          currentSnapshotReconcileCommitPackagePreview: null,
          currentSnapshotReconcileCommitPackageResult: data.snapshot_reconcile_commit_package_resolution_result || null,
          currentSnapshotReconcileCommitPackage: pkg,
        });
        refreshProjectUi();
        renderList();
        renderPreview();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        setStatus(`Resolved standalone package import ${data.snapshot_reconcile_commit_package_resolution_result?.resolution_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package resolution failed: ${err.message}`);
      }
    }

    function renderPreview() {
      if (!els.reconcileCommitPackagePreviewText) return;
      const preview = state().currentSnapshotReconcileCommitPackagePreview;
      els.reconcileCommitPackagePreviewText.textContent = preview ? pretty(preview) : "";
      renderDecisionList();
    }

    async function commitResolution() {
      const currentProject = state().currentProject;
      const currentResult = state().currentSnapshotReconcileCommitPackageResult;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      if (!currentResult?.resolved_session_ids) {
        setStatus("No resolved package import result to commit");
        return;
      }

      try {
        const data = await postJson("/api/commit-snapshot-reconcile-commit-package-resolution", {
          project_index: currentProject,
          snapshot_reconcile_commit_package_resolution_result: currentResult,
          commit_name: els.reconcileCommitPackageCommitName?.value.trim() || undefined,
          promote_point_name: els.reconcileCommitPackagePromotePointName?.value.trim() || undefined,
          promote_point_kind: els.reconcileCommitPackagePromotePointKind?.value || "release",
          note: els.reconcileCommitPackageCommitNote?.value.trim() || undefined,
        });
        updateProjectState(data, {
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitPackageSummary: data.snapshot_reconcile_commit_package_summary || null,
          currentSnapshotReconcileCommitPackageImportSummary: data.snapshot_reconcile_commit_package_import_summary || null,
          currentSnapshotReconcileCommitPackageResolutionSummary: data.snapshot_reconcile_commit_package_resolution_summary || null,
          currentSnapshotReconcileCommitPackageCommitSummary: data.snapshot_reconcile_commit_package_commit_summary || null,
          currentSnapshotReconcileCommitPackageResult: data.snapshot_reconcile_commit_package_commit_result || null,
        });
        refreshProjectUi();
        renderList();
        renderPreview();
        renderDecisionList();
        renderResultPanel();
        renderResult(data);
        setStatus(`Committed imported package resolution ${state().currentSnapshotReconcileCommitPackageResult?.commit_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package commit failed: ${err.message}`);
      }
    }

    function renderList() {
      if (!els.reconcileCommitPackageList) return;
      els.reconcileCommitPackageList.innerHTML = "";
      const commitItems = (state().currentSnapshotReconcileCommitPackageCommitSummary?.length
        ? state().currentSnapshotReconcileCommitPackageCommitSummary
        : Object.values(state().currentProject?.snapshot_reconcile_commit_package_commits || {}));
      for (const item of (state().currentSnapshotReconcileCommitPackageSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.package_name}</strong><div class="meta">${item.commit_name} · ${item.snapshot_name} · resolved:${item.resolved_session_count}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.reconcileCommitPackageList.appendChild(wrap);
      }
      for (const item of (state().currentSnapshotReconcileCommitPackageImportSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.import_name}</strong><div class="meta">package:${item.package_name} · imported commit:${item.imported_commit_name} · branch:${item.target_branch_name} · imported:${item.imported_session_count}</div>`;
        els.reconcileCommitPackageList.appendChild(wrap);
      }
      for (const item of (state().currentSnapshotReconcileCommitPackageResolutionSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.resolution_name}</strong><div class="meta">package:${item.package_name} · source commit:${item.source_commit_name} · branch:${item.target_branch_name} · resolved:${item.resolved_session_count} · skipped:${item.skipped_session_count}</div>`;
        els.reconcileCommitPackageList.appendChild(wrap);
      }
      for (const item of commitItems) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.commit_name}</strong><div class="meta">resolution:${item.resolution_name} · package:${item.package_name} · branch:${item.target_branch_name} · resolved:${item.resolved_session_count}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.reconcileCommitPackageList.appendChild(wrap);
      }
      updateLocalOutcomeSetPackageSelectors();
    }

    function renderResultPanel() {
      if (!els.reconcileCommitPackageResultText) return;
      const currentPackage = state().currentSnapshotReconcileCommitPackage;
      const currentResult = state().currentSnapshotReconcileCommitPackageResult;
      if (currentPackage) {
        els.reconcileCommitPackageResultText.textContent = pretty(currentPackage);
      } else if (currentResult) {
        els.reconcileCommitPackageResultText.textContent = pretty(currentResult);
      } else {
        els.reconcileCommitPackageResultText.textContent = "";
      }
      renderCurrentPackageSummary();
      syncCommitAutofill();
    }

    async function exportPackage() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const commitName = els.exportReconcileCommitName?.value;
      if (!commitName) {
        setStatus("No reconcile commit selected");
        return;
      }

      try {
        const data = await postJson("/api/export-snapshot-reconcile-commit-package", {
          project_index: currentProject,
          commit_name: commitName,
          package_name: els.exportReconcileCommitPackageName?.value.trim() || undefined,
          note: "standalone promoted outcome package",
        });
        updateProjectState(data, {
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitPackageSummary: data.snapshot_reconcile_commit_package_summary || null,
          currentSnapshotReconcileCommitPackageImportSummary: data.snapshot_reconcile_commit_package_import_summary || null,
          currentSnapshotReconcileCommitPackageResolutionSummary: data.snapshot_reconcile_commit_package_resolution_summary || null,
          currentSnapshotReconcileCommitPackageImportDecisions: {},
          currentSnapshotReconcileCommitPackagePreview: null,
          currentSnapshotReconcileCommitPackageResult: data.snapshot_reconcile_commit_package_result || null,
          currentSnapshotReconcileCommitPackage: data.snapshot_reconcile_commit_package || null,
        });
        renderList();
        renderPreview();
        renderResultPanel();
        updateSelectors();
        setStatus(`Exported standalone package ${state().currentSnapshotReconcileCommitPackageResult?.package_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package export failed: ${err.message}`);
      }
    }

    function useCurrentPackage() {
      if (!els.importReconcileCommitPackageJson) return;
      const currentPackage = state().currentSnapshotReconcileCommitPackage;
      els.importReconcileCommitPackageJson.value = currentPackage ? pretty(currentPackage) : "";
      syncPackageGuidance();
      setStatus(currentPackage ? "Loaded current standalone package" : "No exported standalone package");
    }

    function clearInput() {
      if (els.importReconcileCommitPackageJson) els.importReconcileCommitPackageJson.value = "";
      if (els.importReconcileCommitPackageName) els.importReconcileCommitPackageName.value = "";
      setState({
        currentSnapshotReconcileCommitPackagePreview: null,
        currentSnapshotReconcileCommitPackageResult: null,
        currentSnapshotReconcileCommitPackage: null,
        currentLocalOutcomeSetPackageSummary: null,
        currentLocalOutcomeSetPackageImportSummary: null,
        currentLocalOutcomeSetPackageResolutionSummary: null,
        currentLocalOutcomeSetPackage: null,
        currentLocalOutcomeSetPackagePreviewResult: null,
        currentLocalOutcomeSetPackageImportDecisions: {},
        currentLocalOutcomeSetPackageResult: null,
      });
      renderPreview();
      renderResultPanel();
      renderLocalOutcomeSetPackagePanels();
      syncPackageGuidance();
      setStatus("Cleared standalone package input");
    }

    async function previewImport() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/preview-snapshot-reconcile-commit-package-import", {
          current_project_index: currentProject,
          package: pkg,
          import_name: els.importReconcileCommitPackageName?.value.trim() || undefined,
          target_branch_name: els.importReconcileCommitTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedReconcileCommit?.checked,
        });
        setState({
          currentSnapshotReconcileCommitPackageImportDecisions: {},
          currentSnapshotReconcileCommitPackagePreview: data,
        });
        renderPreview();
        setStatus(`Previewed standalone package compatibility ${data.package_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package preview failed: ${err.message}`);
      }
    }

    async function importPackage() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/import-snapshot-reconcile-commit-package", {
          current_project_index: currentProject,
          package: pkg,
          import_name: els.importReconcileCommitPackageName?.value.trim() || undefined,
          target_branch_name: els.importReconcileCommitTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedReconcileCommit?.checked,
        });
        updateProjectState(data, {
          currentSnapshotReconcileCommitSummary: data.snapshot_reconcile_commit_summary || null,
          currentSnapshotReconcileCommitPackageSummary: data.snapshot_reconcile_commit_package_summary || null,
          currentSnapshotReconcileCommitPackageImportSummary: data.snapshot_reconcile_commit_package_import_summary || null,
          currentSnapshotReconcileCommitPackageResolutionSummary: data.snapshot_reconcile_commit_package_resolution_summary || null,
          currentSnapshotReconcileCommitPackageImportDecisions: {},
          currentSnapshotReconcileCommitPackagePreview: null,
          currentSnapshotReconcileCommitPackageResult: data.snapshot_reconcile_commit_package_import_result || null,
          currentSnapshotReconcileCommitPackage: pkg,
        });
        refreshProjectUi();
        renderList();
        renderPreview();
        renderResultPanel();
        updateSelectors();
        setStatus(`Imported standalone package ${data.snapshot_reconcile_commit_package_import_result?.import_name || ""}`);
      } catch (err) {
        setStatus(`Reconcile package import failed: ${err.message}`);
      }
    }

    return {
      updateSelectors,
      renderDecisionList,
      setDecisionForAll,
      applyDecisions,
      renderPreview,
      commitResolution,
      renderList,
      renderResultPanel,
      exportPackage,
      useCurrentPackage,
      clearInput,
      previewImport,
      importPackage,
      syncPackageGuidance,
      syncExportAutofill,
      syncCommitAutofill,
      renderCurrentPackageSummary,
    };
  }

  window.ReconcileCommitPackageWorkflow = {
    createReconcileCommitPackageController,
  };
})();
```


## FILE: inspector/local-outcome-set-package-workflow.js

Size: 21456 bytes

```file
(function () {
  function createLocalOutcomeSetPackageController(config) {
    const {
      els,
      getState,
      setState,
      pretty,
      postJson,
      renderResult,
      setStatus,
      updatePortableLocalOutcomeMergeSelectors,
    } = config;

    function state() {
      return getState();
    }

    function packageGuidance() {
      return window.InspectorPackageGuidance || null;
    }

    function analyzePackageInput() {
      const guidance = packageGuidance();
      if (!guidance) {
        return {
          state: !els.importLocalOutcomeSetPackageJson?.value.trim() ? "empty" : "valid",
          data: null,
          summary: null,
          message: "Package guidance helper is unavailable",
        };
      }
      return guidance.analyzeText(els.importLocalOutcomeSetPackageJson?.value || "", "local_outcome_set_package");
    }

    function applySuggestedInputValue(element, nextValue) {
      if (!element || !nextValue) return;
      const normalized = String(nextValue).trim();
      if (!normalized) return;
      const current = (element.value || "").trim();
      const previous = element.dataset.autofillValue || "";
      if (!current || current === previous) {
        element.value = normalized;
        element.dataset.autofillValue = normalized;
      }
    }

    function applySuggestedSelectValue(element, nextValue) {
      if (!element || !nextValue) return;
      const normalized = String(nextValue).trim();
      if (!normalized) return;
      const options = Array.from(element.options || []);
      if (!options.some((item) => item.value === normalized)) return;
      const current = element.value || "";
      const previous = element.dataset.autofillValue || "";
      if (!current || current === previous || !options.some((item) => item.value === current)) {
        element.value = normalized;
        element.dataset.autofillValue = normalized;
      }
    }

    function syncPackageAutofill(analysis) {
      if (analysis.state !== "valid" || !analysis.data) return;
      const packageName = analysis.data.package_name || "local_outcome_package";
      const branchName = analysis.data.exported_local_outcome_commit?.target_branch_name || "";
      applySuggestedInputValue(els.importLocalOutcomeSetPackageNameInput, `${packageName}_import`);
      applySuggestedSelectValue(els.importLocalOutcomeSetTargetBranch, branchName);
    }

    function syncExportAutofill() {
      const commitName = els.exportLocalOutcomeSetCommit?.value?.trim() || "";
      if (!commitName) return;
      applySuggestedInputValue(els.localOutcomeSetPackageName, `${commitName}_package`);
    }

    function syncPackageGuidance() {
      const guidance = packageGuidance();
      const analysis = analyzePackageInput();
      if (guidance) {
        guidance.renderHint(els.localOutcomeSetPackageHint, analysis);
      } else if (els.localOutcomeSetPackageHint) {
        els.localOutcomeSetPackageHint.textContent = analysis.message || "";
      }
      syncPackageAutofill(analysis);
      return analysis;
    }

    function syncCommitAutofill() {
      const result = state().currentLocalOutcomeSetPackageResult;
      const resolutionName = result?.resolution_name || "";
      if (!resolutionName) return;
      applySuggestedInputValue(els.localOutcomeSetPackageCommitName, `${resolutionName}_commit`);
      applySuggestedInputValue(els.localOutcomeSetPackagePromotePointName, `${resolutionName}_release`);
    }

    function renderCurrentPackageSummary() {
      if (!els.localOutcomeSetPackageCurrentSummary) return;
      const guidance = packageGuidance();
      if (guidance?.renderPayloadSummary) {
        guidance.renderPayloadSummary(
          els.localOutcomeSetPackageCurrentSummary,
          state().currentLocalOutcomeSetPackage,
          "local_outcome_set_package",
          {
            headline: "Current local outcome package payload",
            emptyMessage: "Export a local outcome package or load one in this flow to see a structured package summary here.",
            note: "Current local outcome package payload. Use current local package to load it into the import textarea.",
          },
        );
        return;
      }
      els.localOutcomeSetPackageCurrentSummary.textContent = state().currentLocalOutcomeSetPackage
        ? pretty(state().currentLocalOutcomeSetPackage)
        : "No current local outcome package payload.";
    }

    function parsePackageInput() {
      const analysis = syncPackageGuidance();
      if (analysis.state === "empty") {
        setStatus("Local outcome package JSON is empty. Paste a portable local outcome package before previewing or importing.");
        return null;
      }
      if (analysis.state === "invalid" || analysis.state === "mismatch" || analysis.state === "unknown") {
        setStatus(analysis.message);
        return null;
      }
      return analysis.data;
    }

    function updateSelectors() {
      if (!els.exportLocalOutcomeSetCommit || !els.importLocalOutcomeSetTargetBranch) return;

      const commitItems = (state().currentSnapshotReconcileCommitPackageCommitSummary?.length
        ? state().currentSnapshotReconcileCommitPackageCommitSummary
        : Object.values(state().currentProject?.snapshot_reconcile_commit_package_commits || {}));

      els.exportLocalOutcomeSetCommit.innerHTML = "";
      for (const item of commitItems) {
        const opt = document.createElement("option");
        opt.value = item.commit_name;
        opt.textContent = item.commit_name;
        els.exportLocalOutcomeSetCommit.appendChild(opt);
      }
      if (els.exportLocalOutcomeSetCommit.options.length && !els.exportLocalOutcomeSetCommit.value) {
        els.exportLocalOutcomeSetCommit.value = els.exportLocalOutcomeSetCommit.options[0].value;
      }

      els.importLocalOutcomeSetTargetBranch.innerHTML = "";
      for (const item of (state().currentBranchSummary || [])) {
        const opt = document.createElement("option");
        opt.value = item.branch_name;
        opt.textContent = item.branch_name;
        if (item.is_active_branch) opt.selected = true;
        els.importLocalOutcomeSetTargetBranch.appendChild(opt);
      }
      syncExportAutofill();
    }

    function renderList() {
      if (!els.localOutcomeSetPackageList) return;
      els.localOutcomeSetPackageList.innerHTML = "";

      for (const item of (state().currentLocalOutcomeSetPackageSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.package_name}</strong><div class="meta">${item.commit_name} · ${item.package_kind} · resolved:${item.resolved_session_count}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.localOutcomeSetPackageList.appendChild(wrap);
      }

      for (const item of (state().currentLocalOutcomeSetPackageImportSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.import_name}</strong><div class="meta">package:${item.package_name} · imported commit:${item.imported_commit_name} · branch:${item.target_branch_name} · imported:${item.imported_session_count}</div>`;
        els.localOutcomeSetPackageList.appendChild(wrap);
      }

      for (const item of (state().currentLocalOutcomeSetPackageResolutionSummary || [])) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.resolution_name}</strong><div class="meta">package:${item.package_name} · source:${item.source_commit_name} · branch:${item.target_branch_name} · resolved:${item.resolved_session_count} · skipped:${item.skipped_session_count}</div>`;
        els.localOutcomeSetPackageList.appendChild(wrap);
      }

      for (const item of Object.values(state().currentProject?.local_outcome_set_package_commits || {})) {
        const wrap = document.createElement("div");
        wrap.className = "snapshot-item";
        wrap.innerHTML = `<strong>${item.commit_name}</strong><div class="meta">resolution:${item.resolution_name} · package:${item.package_name} · branch:${item.target_branch_name} · resolved:${(item.resolved_session_ids || []).length}${item.promoted_point_name ? ` · promoted:${item.promoted_point_kind}:${item.promoted_point_name}` : ""}</div>`;
        els.localOutcomeSetPackageList.appendChild(wrap);
      }
    }

    function renderPreviewResult() {
      if (!els.localOutcomeSetPackagePreviewResultText) return;
      els.localOutcomeSetPackagePreviewResultText.textContent = state().currentLocalOutcomeSetPackagePreviewResult ? pretty(state().currentLocalOutcomeSetPackagePreviewResult) : "";
    }

    function renderDecisionList() {
      if (!els.localOutcomeSetPackageDecisionList) return;
      const preview = state().currentLocalOutcomeSetPackagePreviewResult;
      if (!preview?.preview_items?.length) {
        els.localOutcomeSetPackageDecisionList.innerHTML = '<div class="project-map-empty">No local outcome package preview decisions</div>';
        return;
      }

      els.localOutcomeSetPackageDecisionList.innerHTML = "";
      for (const item of preview.preview_items) {
        const wrap = document.createElement("div");
        wrap.className = "conflict-item";
        const decision = state().currentLocalOutcomeSetPackageImportDecisions[item.original_session_id] || { choice: "use_package" };
        wrap.innerHTML = `<strong>${item.original_session_id}</strong><div class="meta">status: ${item.status} · current head: ${item.current_head_session_id || "-"}</div>`;

        const row = document.createElement("div");
        row.className = "row";
        const select = document.createElement("select");
        for (const choice of ["use_package", "use_current", "skip", "custom_text"]) {
          const opt = document.createElement("option");
          opt.value = choice;
          opt.textContent = choice;
          if (decision.choice === choice) opt.selected = true;
          select.appendChild(opt);
        }

        const customInput = document.createElement("textarea");
        customInput.className = "small";
        customInput.placeholder = "Custom source_text";
        customInput.value = decision.choice === "custom_text" ? (decision.custom_text || "") : "";
        customInput.style.display = decision.choice === "custom_text" ? "block" : "none";

        select.addEventListener("change", () => {
          const decisions = { ...state().currentLocalOutcomeSetPackageImportDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = select.value;
          if (select.value !== "custom_text") delete decisions[item.original_session_id].custom_text;
          setState({ currentLocalOutcomeSetPackageImportDecisions: decisions });
          customInput.style.display = select.value === "custom_text" ? "block" : "none";
        });

        customInput.addEventListener("input", () => {
          const decisions = { ...state().currentLocalOutcomeSetPackageImportDecisions };
          decisions[item.original_session_id] = decisions[item.original_session_id] || {};
          decisions[item.original_session_id].choice = "custom_text";
          decisions[item.original_session_id].custom_text = customInput.value;
          setState({ currentLocalOutcomeSetPackageImportDecisions: decisions });
        });

        row.appendChild(select);
        row.appendChild(customInput);
        wrap.appendChild(row);
        els.localOutcomeSetPackageDecisionList.appendChild(wrap);
      }
    }

    async function previewImport() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/preview-local-outcome-set-package-import", {
          current_project_index: currentProject,
          package_data: pkg,
          import_name: els.importLocalOutcomeSetPackageNameInput?.value.trim() || undefined,
          target_branch_name: els.importLocalOutcomeSetTargetBranch?.value || undefined,
        });
        setState({
          currentLocalOutcomeSetPackagePreviewResult: data,
          currentLocalOutcomeSetPackageImportDecisions: {},
        });
        renderPreviewResult();
        renderDecisionList();
        setStatus(`Previewed local outcome package ${data.package_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package preview failed: ${err.message}`);
      }
    }

    function setDecisionForAll(choice, conflictsOnly = false) {
      const preview = state().currentLocalOutcomeSetPackagePreviewResult;
      if (!preview?.preview_items?.length) return;

      const decisions = { ...state().currentLocalOutcomeSetPackageImportDecisions };
      for (const item of preview.preview_items) {
        if (conflictsOnly && !item.conflict_like) continue;
        decisions[item.original_session_id] = { choice };
      }
      setState({ currentLocalOutcomeSetPackageImportDecisions: decisions });
      renderDecisionList();
    }

    async function applyDecisions() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/resolve-local-outcome-set-package-import-conflicts", {
          current_project_index: currentProject,
          package_data: pkg,
          decisions: state().currentLocalOutcomeSetPackageImportDecisions,
          resolution_name: els.importLocalOutcomeSetPackageNameInput?.value.trim() || undefined,
          target_branch_name: els.importLocalOutcomeSetTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedLocalOutcomeSet?.checked,
        });
        renderResult(data);
        setState({
          currentLocalOutcomeSetPackagePreviewResult: null,
          currentLocalOutcomeSetPackageImportDecisions: {},
          currentLocalOutcomeSetPackageResult: data.local_outcome_set_package_resolution_result || null,
        });
        renderList();
        renderPreviewResult();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        updatePortableLocalOutcomeMergeSelectors();
        syncCommitAutofill();
        setStatus(`Resolved local outcome package import ${data.local_outcome_set_package_resolution_result?.resolution_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package resolution failed: ${err.message}`);
      }
    }

    function renderResultPanel() {
      if (!els.localOutcomeSetPackageResultText) return;
      if (state().currentLocalOutcomeSetPackage) {
        els.localOutcomeSetPackageResultText.textContent = pretty(state().currentLocalOutcomeSetPackage);
      } else if (state().currentLocalOutcomeSetPackageResult) {
        els.localOutcomeSetPackageResultText.textContent = pretty(state().currentLocalOutcomeSetPackageResult);
      } else {
        els.localOutcomeSetPackageResultText.textContent = "";
      }
      renderCurrentPackageSummary();
      syncCommitAutofill();
    }

    async function exportPackage() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const commitName = els.exportLocalOutcomeSetCommit?.value;
      if (!commitName) {
        setStatus("No local outcome set selected");
        return;
      }

      try {
        const data = await postJson("/api/export-local-outcome-set-package", {
          project_index: currentProject,
          commit_name: commitName,
          package_name: els.localOutcomeSetPackageName?.value.trim() || undefined,
          note: els.localOutcomeSetPackageNote?.value.trim() || undefined,
        });
        renderResult(data);
        renderList();
        renderPreviewResult();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        updatePortableLocalOutcomeMergeSelectors();
        setStatus(`Exported local outcome package ${data.local_outcome_set_package_result?.package_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package export failed: ${err.message}`);
      }
    }

    async function commitResolution() {
      const currentProject = state().currentProject;
      const currentResult = state().currentLocalOutcomeSetPackageResult;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      if (!currentResult?.resolved_session_ids) {
        setStatus("No resolved local outcome package result to commit");
        return;
      }

      try {
        const data = await postJson("/api/commit-local-outcome-set-package-resolution", {
          project_index: currentProject,
          local_outcome_set_package_resolution_result: currentResult,
          commit_name: els.localOutcomeSetPackageCommitName?.value.trim() || undefined,
          promote_point_name: els.localOutcomeSetPackagePromotePointName?.value.trim() || undefined,
          promote_point_kind: els.localOutcomeSetPackagePromotePointKind?.value || "release",
          note: els.localOutcomeSetPackageCommitNote?.value.trim() || undefined,
        });
        renderResult(data);
        setState({
          currentLocalOutcomeSetPackageResult: data.local_outcome_set_package_commit_result || null,
        });
        renderList();
        renderPreviewResult();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        updatePortableLocalOutcomeMergeSelectors();
        setStatus(`Committed local outcome package resolution ${data.local_outcome_set_package_commit_result?.commit_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package commit failed: ${err.message}`);
      }
    }

    function useCurrentPackage() {
      if (!els.importLocalOutcomeSetPackageJson) return;
      const currentPackage = state().currentLocalOutcomeSetPackage;
      els.importLocalOutcomeSetPackageJson.value = currentPackage ? pretty(currentPackage) : "";
      syncPackageGuidance();
      setStatus(currentPackage ? "Loaded current local outcome package" : "No current local outcome package");
    }

    function clearInput() {
      if (els.importLocalOutcomeSetPackageJson) els.importLocalOutcomeSetPackageJson.value = "";
      if (els.importLocalOutcomeSetPackageNameInput) els.importLocalOutcomeSetPackageNameInput.value = "";
      if (els.localOutcomeSetPackageCommitName) els.localOutcomeSetPackageCommitName.value = "";
      if (els.localOutcomeSetPackagePromotePointName) els.localOutcomeSetPackagePromotePointName.value = "";
      if (els.localOutcomeSetPackageCommitNote) els.localOutcomeSetPackageCommitNote.value = "";
      setState({
        currentLocalOutcomeSetPackagePreviewResult: null,
        currentLocalOutcomeSetPackageImportDecisions: {},
        currentLocalOutcomeSetPackageResult: null,
      });
      renderPreviewResult();
      renderDecisionList();
      renderResultPanel();
      syncPackageGuidance();
      setStatus("Cleared local outcome package input");
    }

    async function importPackage() {
      const currentProject = state().currentProject;
      if (!currentProject) {
        setStatus("No project loaded");
        return;
      }
      const pkg = parsePackageInput();
      if (!pkg) return;

      try {
        const data = await postJson("/api/import-local-outcome-set-package", {
          current_project_index: currentProject,
          package: pkg,
          import_name: els.importLocalOutcomeSetPackageNameInput?.value.trim() || undefined,
          target_branch_name: els.importLocalOutcomeSetTargetBranch?.value || undefined,
          activate_last_imported: !!els.activateImportedLocalOutcomeSet?.checked,
        });
        renderResult(data);
        setState({
          currentLocalOutcomeSetPackagePreviewResult: null,
          currentLocalOutcomeSetPackageImportDecisions: {},
          currentLocalOutcomeSetPackageResult: data.local_outcome_set_package_import_result || null,
        });
        renderList();
        renderPreviewResult();
        renderDecisionList();
        renderResultPanel();
        updateSelectors();
        updatePortableLocalOutcomeMergeSelectors();
        setStatus(`Imported local outcome package ${data.local_outcome_set_package_import_result?.import_name || ""}`);
      } catch (err) {
        setStatus(`Local outcome package import failed: ${err.message}`);
      }
    }

    return {
      updateSelectors,
      renderList,
      renderPreviewResult,
      renderDecisionList,
      previewImport,
      setDecisionForAll,
      applyDecisions,
      renderResultPanel,
      exportPackage,
      useCurrentPackage,
      clearInput,
      importPackage,
      commitResolution,
      syncPackageGuidance,
      syncExportAutofill,
      syncCommitAutofill,
      renderCurrentPackageSummary,
    };
  }

  window.LocalOutcomeSetPackageWorkflow = {
    createLocalOutcomeSetPackageController,
  };
})();
```
