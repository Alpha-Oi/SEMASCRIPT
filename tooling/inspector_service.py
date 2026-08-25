
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
