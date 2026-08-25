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
