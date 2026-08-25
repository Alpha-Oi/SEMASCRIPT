
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
