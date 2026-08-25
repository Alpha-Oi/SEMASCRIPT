
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
