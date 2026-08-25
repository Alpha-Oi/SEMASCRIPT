
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from workspace_timeline import ensure_workspace_history


class ProjectSnapshotReconcilePreviewError(Exception):
    """Raised when snapshot reconcile preview / conflict detection is invalid."""


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


def _session_entry_by_id(project_index: dict, session_id: str) -> dict:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    raise ProjectSnapshotReconcilePreviewError(f"Unknown snapshot session_id: {session_id}")


def preview_snapshot_reconcile_before_apply(
    current_project_index: dict,
    snapshot_package: dict,
    selected_session_ids: list[str] | None = None,
    target_branch_name: str | None = None,
    reconcile_name: str | None = None,
) -> dict:
    if not isinstance(snapshot_package, dict):
        raise ProjectSnapshotReconcilePreviewError("snapshot_package must be an object")
    if snapshot_package.get("snapshot_version") != "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1":
        raise ProjectSnapshotReconcilePreviewError("Unsupported or missing snapshot_version")

    export_state = snapshot_package.get("export_state") or {}
    frozen_project = export_state.get("project_index_frozen")
    if not isinstance(frozen_project, dict):
        raise ProjectSnapshotReconcilePreviewError("snapshot export_state.project_index_frozen is missing")

    current = _normalize(current_project_index)
    snapshot_project = _normalize(frozen_project)
    anchor = deepcopy(snapshot_package.get("anchor") or {})

    session_ids = [item.strip() for item in (selected_session_ids or []) if str(item).strip()]
    if not session_ids:
        raise ProjectSnapshotReconcilePreviewError("At least one selected_session_id is required")

    resolved_reconcile_name = (reconcile_name or f"{snapshot_package.get('snapshot_name', 'snapshot')}_reconcile").strip()
    if not resolved_reconcile_name:
        raise ProjectSnapshotReconcilePreviewError("reconcile_name is required")

    target_branch = (target_branch_name or anchor.get("branch_name") or current.get("active_branch_name") or "main").strip()
    current_head_session_id = current.get("branches", {}).get(target_branch, {}).get("head_session_id")
    would_parent = current_head_session_id

    previews = []
    conflict_count = 0
    exact_match_count = 0
    for idx, original_session_id in enumerate(session_ids, start=1):
        source_entry = _session_entry_by_id(snapshot_project, original_session_id)
        current_head_entry = next((item for item in current.get("sessions", []) if item["session_id"] == would_parent), None)

        source_branch_name = source_entry.get("entry_metadata", {}).get("branching", {}).get("branch_name")
        source_text = source_entry.get("session", {}).get("project", {}).get("source_text")
        head_text = current_head_entry.get("session", {}).get("project", {}).get("source_text") if current_head_entry else None
        source_profile = source_entry.get("profile")
        head_profile = current_head_entry.get("profile") if current_head_entry else None

        same_source_as_head = bool(source_text is not None and head_text is not None and source_text == head_text)
        same_profile_as_head = bool(source_profile is not None and head_profile is not None and source_profile == head_profile)
        exact_match = same_source_as_head and same_profile_as_head
        conflict_like = current_head_entry is not None and not same_source_as_head
        if conflict_like:
            conflict_count += 1
        if exact_match:
            exact_match_count += 1

        status = "exact_match" if exact_match else ("conflict_like" if conflict_like else ("compatible" if current_head_entry is not None else "no_current_head"))

        previews.append({
            "preview_index": idx,
            "original_session_id": original_session_id,
            "session_name": source_entry.get("session_name"),
            "source_branch_name": source_branch_name,
            "target_branch_name": target_branch,
            "current_head_session_id": would_parent,
            "current_head_session_name": current_head_entry.get("session_name") if current_head_entry else None,
            "source_profile": source_profile,
            "current_head_profile": head_profile,
            "same_source_as_head": same_source_as_head,
            "same_profile_as_head": same_profile_as_head,
            "exact_match": exact_match,
            "conflict_like": conflict_like,
            "status": status,
        })

        would_parent = f"{original_session_id}_reconcile"

    return {
        "snapshot_reconcile_preview_version": "SEMASCRIPT_SNAPSHOT_CONFLICT_DETECTION_RECONCILE_PREVIEW_v0.1",
        "reconcile_name": resolved_reconcile_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "source_point_kind": snapshot_package.get("source_point_kind"),
        "target_branch_name": target_branch,
        "current_head_session_id": current_head_session_id,
        "selected_session_ids": session_ids,
        "preview_items": previews,
        "summary": {
            "selected_session_count": len(session_ids),
            "conflict_like_count": conflict_count,
            "exact_match_count": exact_match_count,
            "has_conflicts": conflict_count > 0,
        },
    }
