
from __future__ import annotations

from copy import deepcopy

from session_model import create_session_from_text
from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_preview import preview_snapshot_reconcile_before_apply
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectSnapshotReconcileResolutionError(Exception):
    """Raised when snapshot conflict resolution / manual reconcile decisions are invalid."""


def ensure_snapshot_reconcile_resolution_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_reconcile_resolutions", {})
    return out


def snapshot_reconcile_resolution_summary(project_index: dict) -> list[dict]:
    project_index = ensure_snapshot_reconcile_resolution_state(
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
    out = []
    for resolution_name, entry in (project_index.get("snapshot_reconcile_resolutions") or {}).items():
        out.append({
            "resolution_name": resolution_name,
            "snapshot_name": entry.get("snapshot_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "skipped_session_count": len(entry.get("skipped_session_ids") or []),
            "conflict_like_count": entry.get("conflict_like_count", 0),
            "decision_counts": deepcopy(entry.get("decision_counts") or {}),
        })
    out.sort(key=lambda x: x["resolution_name"])
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_snapshot_reconcile_resolution_state(
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
    raise ProjectSnapshotReconcileResolutionError(f"Unknown session_id: {session_id}")


def _build_custom_text_session(source_entry: dict, current_head_entry: dict | None, custom_text: str) -> tuple[dict, str, str]:
    base_entry = source_entry or current_head_entry
    if not base_entry:
        raise ProjectSnapshotReconcileResolutionError("custom_text decision requires a source or current entry")
    profile = base_entry.get("profile") or "core"
    source_mode = base_entry.get("source_mode") or base_entry.get("session", {}).get("project", {}).get("source_mode")
    if source_mode != "text":
        raise ProjectSnapshotReconcileResolutionError("custom_text is supported only for text sessions in v0.1")
    initial_state = deepcopy(base_entry.get("session", {}).get("project", {}).get("initial_state"))
    session_name = base_entry.get("session_name")
    session = create_session_from_text(
        text=custom_text,
        profile=profile,
        decompose=True,
        initial_state=initial_state,
        session_name=session_name,
    )
    return session, profile, "text"


def resolve_snapshot_reconcile_conflicts_with_decisions(
    current_project_index: dict,
    snapshot_package: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: str | None = None,
    selected_session_ids: list[str] | None = None,
    target_branch_name: str | None = None,
    activate_last_resolved: bool = True,
) -> tuple[dict, dict]:
    if not isinstance(snapshot_package, dict):
        raise ProjectSnapshotReconcileResolutionError("snapshot_package must be an object")
    if snapshot_package.get("snapshot_version") != "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1":
        raise ProjectSnapshotReconcileResolutionError("Unsupported or missing snapshot_version")

    export_state = snapshot_package.get("export_state") or {}
    frozen_project = export_state.get("project_index_frozen")
    if not isinstance(frozen_project, dict):
        raise ProjectSnapshotReconcileResolutionError("snapshot export_state.project_index_frozen is missing")

    current = _normalize(current_project_index)
    snapshot_project = _normalize(frozen_project)
    preview = preview_snapshot_reconcile_before_apply(
        current_project_index=current,
        snapshot_package=snapshot_package,
        selected_session_ids=selected_session_ids,
        target_branch_name=target_branch_name,
        reconcile_name=resolution_name or None,
    )
    anchor = deepcopy(snapshot_package.get("anchor") or {})
    session_ids = list(preview.get("selected_session_ids") or [])
    if not session_ids:
        raise ProjectSnapshotReconcileResolutionError("At least one selected_session_id is required")

    resolved_name = (resolution_name or f"{snapshot_package.get('snapshot_name', 'snapshot')}_reconcile_resolution").strip()
    if not resolved_name:
        raise ProjectSnapshotReconcileResolutionError("resolution_name is required")
    if resolved_name in current.get("snapshot_reconcile_resolutions", {}):
        raise ProjectSnapshotReconcileResolutionError(f"Snapshot reconcile resolution already exists: {resolved_name}")

    decisions = deepcopy(decisions or {})
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

    resolved_session_ids: list[str] = []
    skipped_session_ids: list[str] = []
    resolution_pairs: list[dict] = []
    decision_counts = {"use_snapshot": 0, "use_current": 0, "skip": 0, "custom_text": 0}
    conflict_like_count = 0
    conflict_resolved_count = 0

    for idx, preview_item in enumerate(preview.get("preview_items") or [], start=1):
        original_session_id = preview_item["original_session_id"]
        source_entry = _session_entry_by_id(snapshot_project, original_session_id)
        current_head_entry = next((item for item in out.get("sessions", []) if item["session_id"] == previous_parent), None)

        decision = decisions.get(original_session_id, {}) or {}
        choice = (decision.get("choice") or "use_snapshot").strip()
        if choice not in {"use_snapshot", "use_current", "skip", "custom_text"}:
            raise ProjectSnapshotReconcileResolutionError(f"Unsupported decision choice: {choice}")

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

        if choice == "use_snapshot":
            session_copy = deepcopy(source_entry["session"])
            profile = source_entry.get("profile")
            source_mode = source_entry.get("source_mode")
            session_name = source_entry.get("session_name")
            decision_counts["use_snapshot"] += 1
        elif choice == "use_current":
            if not current_head_entry:
                raise ProjectSnapshotReconcileResolutionError(
                    f"use_current requires a current head for session {original_session_id}"
                )
            session_copy = deepcopy(current_head_entry["session"])
            profile = current_head_entry.get("profile")
            source_mode = current_head_entry.get("source_mode")
            session_name = current_head_entry.get("session_name")
            decision_counts["use_current"] += 1
        else:  # custom_text
            custom_text = (decision.get("custom_text") or "").strip()
            if not custom_text:
                raise ProjectSnapshotReconcileResolutionError(f"custom_text decision requires custom_text for session {original_session_id}")
            session_copy, profile, source_mode = _build_custom_text_session(source_entry, current_head_entry, custom_text)
            session_name = session_copy.get("session_name") or source_entry.get("session_name")
            decision_counts["custom_text"] += 1

        if preview_item.get("conflict_like"):
            conflict_resolved_count += 1

        new_session_id = _derive_unique_name(existing_session_ids, original_session_id, "_reconcile_resolved")

        entry_metadata = deepcopy(source_entry.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "snapshot_reconcile_resolution"
        entry_metadata["snapshot_reconcile_resolution"] = {
            "resolution_name": resolved_name,
            "source_snapshot_name": snapshot_package.get("snapshot_name"),
            "source_point_name": snapshot_package.get("source_point_name"),
            "original_session_id": original_session_id,
            "source_branch_name": source_entry.get("entry_metadata", {}).get("branching", {}).get("branch_name"),
            "target_branch_name": target_branch,
            "resolved_with_head_session_id": previous_parent,
            "resolution_index": idx,
            "decision_choice": choice,
            "preview_status": preview_item.get("status"),
            "conflict_like": preview_item.get("conflict_like", False),
            "same_source_as_head": preview_item.get("same_source_as_head", False),
            "same_profile_as_head": preview_item.get("same_profile_as_head", False),
        }
        if choice == "custom_text":
            entry_metadata["snapshot_reconcile_resolution"]["custom_text"] = (decision.get("custom_text") or "").strip()
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "snapshot_reconcile_resolution",
        }

        entry = {
            "session_id": new_session_id,
            "session_name": session_name,
            "profile": profile,
            "source_mode": source_mode,
            "file_name": None,
            "tags": list(dict.fromkeys(list(source_entry.get("tags", [])) + ["snapshot-reconcile-resolution"])),
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

    if activate_last_resolved and resolved_session_ids:
        out["active_session_id"] = resolved_session_ids[-1]
        out["active_branch_name"] = target_branch

    out.setdefault("snapshot_reconcile_resolutions", {})[resolved_name] = {
        "resolution_name": resolved_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "source_point_kind": snapshot_package.get("source_point_kind"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "resolution_pairs": resolution_pairs,
        "decision_counts": decision_counts,
        "conflict_like_count": conflict_like_count,
        "conflict_resolved_count": conflict_resolved_count,
    }

    history_session_id = resolved_session_ids[-1] if resolved_session_ids else anchor.get("target_session_id")
    history_session_name = None
    if history_session_id:
        match = next((item for item in out.get("sessions", []) if item["session_id"] == history_session_id), None)
        history_session_name = match.get("session_name") if match else None

    out = append_history_event(
        out,
        "snapshot_reconcile_resolved",
        f"Snapshot reconcile resolved: {resolved_name}",
        session_id=history_session_id,
        session_name=history_session_name,
        payload={
            "snapshot_name": snapshot_package.get("snapshot_name"),
            "source_point_name": snapshot_package.get("source_point_name"),
            "target_branch_name": target_branch,
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
            "conflict_like_count": conflict_like_count,
        },
    )

    result = {
        "snapshot_reconcile_resolution_version": "SEMASCRIPT_SNAPSHOT_CONFLICT_RESOLUTION_v0.1",
        "resolution_name": resolved_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
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
