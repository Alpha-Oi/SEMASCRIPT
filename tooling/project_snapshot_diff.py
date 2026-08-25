
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from workspace_timeline import ensure_workspace_history


class ProjectSnapshotDiffError(Exception):
    """Raised when snapshot diff / restore preview is invalid."""


def _normalize_project(project_index: dict) -> dict:
    return ensure_snapshot_restore_state(
        ensure_snapshot_state(
            ensure_tag_point_state(
                ensure_branching_state(
                    ensure_workspace_history(deepcopy(project_index))
                )
            )
        )
    )


def _set_diff(current_items: list[str], snapshot_items: list[str]) -> dict:
    current_set = set(current_items)
    snapshot_set = set(snapshot_items)
    return {
        "shared": sorted(current_set & snapshot_set),
        "current_only": sorted(current_set - snapshot_set),
        "snapshot_only": sorted(snapshot_set - current_set),
    }


def preview_snapshot_restore_before_apply(
    current_project_index: dict,
    snapshot_package: dict,
    restored_project_name: str | None = None,
    activate_anchor: bool = True,
) -> dict:
    if not isinstance(snapshot_package, dict):
        raise ProjectSnapshotDiffError("snapshot_package must be an object")
    if snapshot_package.get("snapshot_version") != "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1":
        raise ProjectSnapshotDiffError("Unsupported or missing snapshot_version")

    export_state = snapshot_package.get("export_state") or {}
    frozen_project = export_state.get("project_index_frozen")
    if not isinstance(frozen_project, dict):
        raise ProjectSnapshotDiffError("snapshot export_state.project_index_frozen is missing")

    current = _normalize_project(current_project_index)
    snapshot_project = _normalize_project(frozen_project)
    anchor = deepcopy(snapshot_package.get("anchor") or {})

    current_session_ids = [item["session_id"] for item in current.get("sessions", [])]
    snapshot_session_ids = [item["session_id"] for item in snapshot_project.get("sessions", [])]

    current_branch_names = sorted((current.get("branches") or {}).keys())
    snapshot_branch_names = sorted((snapshot_project.get("branches") or {}).keys())

    current_tag_names = sorted((current.get("tag_points") or {}).keys())
    snapshot_tag_names = sorted((snapshot_project.get("tag_points") or {}).keys())

    current_snapshot_names = sorted((current.get("snapshot_exports") or {}).keys())
    snapshot_snapshot_names = sorted((snapshot_project.get("snapshot_exports") or {}).keys())

    current_restore_names = sorted((current.get("snapshot_restores") or {}).keys())
    snapshot_restore_names = sorted((snapshot_project.get("snapshot_restores") or {}).keys())

    would_activate_session_id = anchor.get("target_session_id") if activate_anchor else snapshot_project.get("active_session_id")
    would_activate_branch_name = anchor.get("branch_name") if activate_anchor else snapshot_project.get("active_branch_name")

    summary = {
        "current_session_count": len(current_session_ids),
        "snapshot_session_count": len(snapshot_session_ids),
        "current_branch_count": len(current_branch_names),
        "snapshot_branch_count": len(snapshot_branch_names),
        "project_name_changed": current.get("project_name") != (restored_project_name.strip() if isinstance(restored_project_name, str) and restored_project_name.strip() else snapshot_project.get("project_name")),
        "active_session_changed": current.get("active_session_id") != would_activate_session_id,
        "active_branch_changed": current.get("active_branch_name") != would_activate_branch_name,
    }
    summary["changed"] = any(summary.values())

    return {
        "snapshot_restore_preview_version": "SEMASCRIPT_SNAPSHOT_DIFF_RESTORE_PREVIEW_v0.1",
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "source_point_kind": snapshot_package.get("source_point_kind"),
        "anchor": anchor,
        "restore_target": {
            "restored_project_name": restored_project_name.strip() if isinstance(restored_project_name, str) and restored_project_name.strip() else snapshot_project.get("project_name"),
            "would_activate_session_id": would_activate_session_id,
            "would_activate_branch_name": would_activate_branch_name,
            "activate_anchor": activate_anchor,
        },
        "scalar_diff": {
            "current_project_name": current.get("project_name"),
            "snapshot_project_name": snapshot_project.get("project_name"),
            "current_active_session_id": current.get("active_session_id"),
            "snapshot_active_session_id": snapshot_project.get("active_session_id"),
            "current_active_branch_name": current.get("active_branch_name"),
            "snapshot_active_branch_name": snapshot_project.get("active_branch_name"),
        },
        "collections": {
            "sessions": _set_diff(current_session_ids, snapshot_session_ids),
            "branches": _set_diff(current_branch_names, snapshot_branch_names),
            "tag_points": _set_diff(current_tag_names, snapshot_tag_names),
            "snapshot_exports": _set_diff(current_snapshot_names, snapshot_snapshot_names),
            "snapshot_restores": _set_diff(current_restore_names, snapshot_restore_names),
        },
        "summary": summary,
    }
