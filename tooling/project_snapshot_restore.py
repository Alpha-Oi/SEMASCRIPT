
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectSnapshotRestoreError(Exception):
    """Raised when immutable snapshot restore is invalid."""


def ensure_snapshot_restore_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_restores", {})
    return out


def snapshot_restore_summary(project_index: dict) -> list[dict]:
    project_index = ensure_snapshot_restore_state(ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index)))))
    out = []
    for restore_name, entry in (project_index.get("snapshot_restores") or {}).items():
        out.append({
            "restore_name": restore_name,
            "snapshot_name": entry.get("snapshot_name"),
            "source_point_name": entry.get("source_point_name"),
            "source_point_kind": entry.get("source_point_kind"),
            "target_session_id": entry.get("target_session_id"),
            "branch_name": entry.get("branch_name"),
            "note": entry.get("note"),
        })
    out.sort(key=lambda x: x["restore_name"])
    return out


def restore_workspace_from_snapshot_export(
    snapshot_package: dict,
    restored_project_name: str | None = None,
    restore_name: str | None = None,
    activate_anchor: bool = True,
) -> tuple[dict, dict]:
    if not isinstance(snapshot_package, dict):
        raise ProjectSnapshotRestoreError("snapshot_package must be an object")
    if snapshot_package.get("snapshot_version") != "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1":
        raise ProjectSnapshotRestoreError("Unsupported or missing snapshot_version")

    export_state = snapshot_package.get("export_state") or {}
    frozen_project = export_state.get("project_index_frozen")
    if not isinstance(frozen_project, dict):
        raise ProjectSnapshotRestoreError("snapshot export_state.project_index_frozen is missing")

    restored = deepcopy(frozen_project)
    if restored_project_name and restored_project_name.strip():
        restored["project_name"] = restored_project_name.strip()

    restored = ensure_snapshot_restore_state(
        ensure_snapshot_state(
            ensure_tag_point_state(
                ensure_branching_state(
                    ensure_workspace_history(restored)
                )
            )
        )
    )

    resolved_restore_name = (restore_name or f"{snapshot_package.get('snapshot_name', 'snapshot')}_restore").strip()
    if not resolved_restore_name:
        raise ProjectSnapshotRestoreError("restore_name is required")
    if resolved_restore_name in restored.get("snapshot_restores", {}):
        raise ProjectSnapshotRestoreError(f"Restore already exists: {resolved_restore_name}")

    anchor = deepcopy(snapshot_package.get("anchor") or {})
    target_session_id = anchor.get("target_session_id")
    branch_name = anchor.get("branch_name")

    if activate_anchor and target_session_id:
        valid_ids = {item["session_id"] for item in restored.get("sessions", [])}
        if target_session_id in valid_ids:
            restored["active_session_id"] = target_session_id
        if branch_name:
            restored["active_branch_name"] = branch_name

    restored.setdefault("snapshot_restores", {})[resolved_restore_name] = {
        "restore_name": resolved_restore_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "source_point_kind": snapshot_package.get("source_point_kind"),
        "target_session_id": target_session_id,
        "branch_name": branch_name,
        "note": snapshot_package.get("note"),
        "immutability": deepcopy(snapshot_package.get("immutability") or {}),
    }

    restored = append_history_event(
        restored,
        "snapshot_restored",
        f"Snapshot restored: {snapshot_package.get('snapshot_name')}",
        session_id=target_session_id,
        session_name=anchor.get("target_session_name"),
        payload={
            "restore_name": resolved_restore_name,
            "snapshot_name": snapshot_package.get("snapshot_name"),
            "source_point_name": snapshot_package.get("source_point_name"),
            "source_point_kind": snapshot_package.get("source_point_kind"),
            "branch_name": branch_name,
        },
    )

    result = {
        "snapshot_restore_version": "SEMASCRIPT_SNAPSHOT_IMPORT_RESTORE_v0.1",
        "project_name": restored.get("project_name"),
        "restore_name": resolved_restore_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "source_point_kind": snapshot_package.get("source_point_kind"),
        "target_session_id": target_session_id,
        "summary": {
            "restored": True,
            "immutable_source": bool((snapshot_package.get("immutability") or {}).get("frozen")),
            "active_session_id": restored.get("active_session_id"),
            "active_branch_name": restored.get("active_branch_name"),
        },
    }
    return restored, result
