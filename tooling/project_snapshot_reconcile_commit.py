
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
