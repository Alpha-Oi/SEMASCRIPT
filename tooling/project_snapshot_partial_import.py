
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectSnapshotPartialImportError(Exception):
    """Raised when partial snapshot restore / selective workspace import is invalid."""


def ensure_partial_snapshot_import_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("partial_snapshot_imports", {})
    return out


def partial_snapshot_import_summary(project_index: dict) -> list[dict]:
    project_index = ensure_partial_snapshot_import_state(
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
    out = []
    for import_name, entry in (project_index.get("partial_snapshot_imports") or {}).items():
        out.append({
            "import_name": import_name,
            "snapshot_name": entry.get("snapshot_name"),
            "source_point_name": entry.get("source_point_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "imported_session_count": len(entry.get("imported_session_ids") or []),
            "imported_tag_point_count": len(entry.get("imported_tag_point_names") or []),
            "imported_snapshot_export_count": len(entry.get("imported_snapshot_export_names") or []),
        })
    out.sort(key=lambda x: x["import_name"])
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_partial_snapshot_import_state(
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
    raise ProjectSnapshotPartialImportError(f"Unknown snapshot session_id: {session_id}")


def import_selective_snapshot_state(
    current_project_index: dict,
    snapshot_package: dict,
    import_name: str | None = None,
    selected_session_ids: list[str] | None = None,
    selected_tag_point_names: list[str] | None = None,
    selected_snapshot_export_names: list[str] | None = None,
    target_branch_name: str | None = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    if not isinstance(snapshot_package, dict):
        raise ProjectSnapshotPartialImportError("snapshot_package must be an object")
    if snapshot_package.get("snapshot_version") != "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1":
        raise ProjectSnapshotPartialImportError("Unsupported or missing snapshot_version")

    export_state = snapshot_package.get("export_state") or {}
    frozen_project = export_state.get("project_index_frozen")
    if not isinstance(frozen_project, dict):
        raise ProjectSnapshotPartialImportError("snapshot export_state.project_index_frozen is missing")

    current = _normalize(current_project_index)
    snapshot_project = _normalize(frozen_project)
    anchor = deepcopy(snapshot_package.get("anchor") or {})

    session_ids = [item.strip() for item in (selected_session_ids or []) if str(item).strip()]
    tag_names = [item.strip() for item in (selected_tag_point_names or []) if str(item).strip()]
    snapshot_names = [item.strip() for item in (selected_snapshot_export_names or []) if str(item).strip()]

    if not session_ids and not tag_names and not snapshot_names:
        raise ProjectSnapshotPartialImportError("At least one selective import set must be provided")

    resolved_import_name = (import_name or f"{snapshot_package.get('snapshot_name', 'snapshot')}_partial_import").strip()
    if not resolved_import_name:
        raise ProjectSnapshotPartialImportError("import_name is required")
    if resolved_import_name in current.get("partial_snapshot_imports", {}):
        raise ProjectSnapshotPartialImportError(f"Partial snapshot import already exists: {resolved_import_name}")

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
    existing_tag_names = set((out.get("tag_points") or {}).keys())
    existing_snapshot_names = set((out.get("snapshot_exports") or {}).keys())

    session_id_map: dict[str, str] = {}
    imported_session_ids: list[str] = []
    imported_tag_point_names: list[str] = []
    imported_snapshot_export_names: list[str] = []
    skipped_tag_point_names: list[str] = []

    previous_parent = out["branches"].get(target_branch, {}).get("head_session_id")

    for idx, original_session_id in enumerate(session_ids, start=1):
        source_entry = _session_entry_by_id(snapshot_project, original_session_id)
        new_session_id = _derive_unique_name(existing_session_ids, original_session_id, "_import")
        source_branch_name = source_entry.get("entry_metadata", {}).get("branching", {}).get("branch_name")

        session_copy = deepcopy(source_entry["session"])
        entry_metadata = deepcopy(source_entry.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "snapshot_partial_import"
        entry_metadata["snapshot_partial_import"] = {
            "import_name": resolved_import_name,
            "source_snapshot_name": snapshot_package.get("snapshot_name"),
            "source_point_name": snapshot_package.get("source_point_name"),
            "original_session_id": original_session_id,
            "source_branch_name": source_branch_name,
            "target_branch_name": target_branch,
            "import_index": idx,
        }
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "snapshot_partial_import",
        }

        entry = {
            "session_id": new_session_id,
            "session_name": source_entry.get("session_name"),
            "profile": source_entry.get("profile"),
            "source_mode": source_entry.get("source_mode"),
            "file_name": None,
            "tags": list(dict.fromkeys(list(source_entry.get("tags", [])) + ["snapshot-partial-import"])),
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
        session_id_map[original_session_id] = new_session_id
        imported_session_ids.append(new_session_id)

    current_valid_session_ids = {item["session_id"] for item in out.get("sessions", [])}

    for tag_name in tag_names:
        point = deepcopy((snapshot_project.get("tag_points") or {}).get(tag_name))
        if not point:
            skipped_tag_point_names.append(tag_name)
            continue

        original_target_id = point.get("target_session_id")
        remapped_target_id = session_id_map.get(original_target_id, original_target_id)
        if remapped_target_id not in current_valid_session_ids:
            skipped_tag_point_names.append(tag_name)
            continue

        target_entry = next(item for item in out["sessions"] if item["session_id"] == remapped_target_id)
        new_tag_name = _derive_unique_name(existing_tag_names, tag_name, "_import")
        point["tag_name"] = new_tag_name
        point["target_session_id"] = remapped_target_id
        point["target_session_name"] = target_entry.get("session_name")
        point["branch_name"] = target_entry.get("entry_metadata", {}).get("branching", {}).get("branch_name", target_branch)
        point["lineage_state"] = {
            "branch_name": point["branch_name"],
            "branch_head_session_id": out.get("branches", {}).get(point["branch_name"], {}).get("head_session_id"),
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
            "is_branch_head_target": out.get("branches", {}).get(point["branch_name"], {}).get("head_session_id") == remapped_target_id,
        }
        out.setdefault("tag_points", {})[new_tag_name] = point
        imported_tag_point_names.append(new_tag_name)

    for snap_name in snapshot_names:
        package = deepcopy((snapshot_project.get("snapshot_exports") or {}).get(snap_name))
        if not package:
            continue
        new_snapshot_name = _derive_unique_name(existing_snapshot_names, snap_name, "_import")
        package["snapshot_name"] = new_snapshot_name
        out.setdefault("snapshot_exports", {})[new_snapshot_name] = package
        imported_snapshot_export_names.append(new_snapshot_name)

    if activate_last_imported and imported_session_ids:
        out["active_session_id"] = imported_session_ids[-1]
        out["active_branch_name"] = target_branch

    out.setdefault("partial_snapshot_imports", {})[resolved_import_name] = {
        "import_name": resolved_import_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "source_point_kind": snapshot_package.get("source_point_kind"),
        "target_branch_name": target_branch,
        "imported_session_ids": imported_session_ids,
        "imported_tag_point_names": imported_tag_point_names,
        "imported_snapshot_export_names": imported_snapshot_export_names,
        "skipped_tag_point_names": skipped_tag_point_names,
        "session_id_map": session_id_map,
    }

    history_session_id = imported_session_ids[-1] if imported_session_ids else anchor.get("target_session_id")
    history_session_name = None
    if history_session_id:
        match = next((item for item in out.get("sessions", []) if item["session_id"] == history_session_id), None)
        history_session_name = match.get("session_name") if match else None

    out = append_history_event(
        out,
        "snapshot_partial_imported",
        f"Snapshot partial import: {resolved_import_name}",
        session_id=history_session_id,
        session_name=history_session_name,
        payload={
            "snapshot_name": snapshot_package.get("snapshot_name"),
            "source_point_name": snapshot_package.get("source_point_name"),
            "target_branch_name": target_branch,
            "imported_session_count": len(imported_session_ids),
            "imported_tag_point_count": len(imported_tag_point_names),
            "imported_snapshot_export_count": len(imported_snapshot_export_names),
        },
    )

    result = {
        "snapshot_partial_import_version": "SEMASCRIPT_PARTIAL_SNAPSHOT_RESTORE_v0.1",
        "import_name": resolved_import_name,
        "snapshot_name": snapshot_package.get("snapshot_name"),
        "source_point_name": snapshot_package.get("source_point_name"),
        "target_branch_name": target_branch,
        "imported_session_ids": imported_session_ids,
        "imported_tag_point_names": imported_tag_point_names,
        "imported_snapshot_export_names": imported_snapshot_export_names,
        "skipped_tag_point_names": skipped_tag_point_names,
        "summary": {
            "imported_session_count": len(imported_session_ids),
            "imported_tag_point_count": len(imported_tag_point_names),
            "imported_snapshot_export_count": len(imported_snapshot_export_names),
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
