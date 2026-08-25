
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state, branch_summary, build_named_merge_lineage_graph
from project_tags import ensure_tag_point_state, tag_point_summary
from workspace_navigation import build_workspace_dependency_map
from workspace_timeline import ensure_workspace_history, append_history_event, build_workspace_timeline


class ProjectSnapshotError(Exception):
    """Raised when immutable workspace snapshot export is invalid."""


def ensure_snapshot_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("snapshot_exports", {})
    return out


def snapshot_export_summary(project_index: dict) -> list[dict]:
    project_index = ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index))))
    out = []
    for snapshot_name, package in (project_index.get("snapshot_exports") or {}).items():
        out.append({
            "snapshot_name": snapshot_name,
            "source_point_name": package.get("source_point_name"),
            "source_point_kind": package.get("source_point_kind"),
            "target_session_id": package.get("target_session_id"),
            "branch_name": package.get("anchor", {}).get("branch_name"),
            "is_release": package.get("source_point_kind") == "release",
            "note": package.get("note"),
        })
    out.sort(key=lambda x: (x["source_point_kind"], x["snapshot_name"]))
    return out


def _workspace_summary_min(project_index: dict) -> list[dict]:
    return [
        {
            "session_id": item["session_id"],
            "session_name": item["session_name"],
            "profile": item.get("profile"),
            "source_mode": item.get("source_mode"),
            "branch_name": item.get("entry_metadata", {}).get("branching", {}).get("branch_name"),
            "tags": item.get("tags", []),
            "is_active": item["session_id"] == project_index.get("active_session_id"),
        }
        for item in project_index.get("sessions", [])
    ]


def _frozen_project_index(project_index: dict) -> dict:
    frozen = deepcopy(project_index)
    frozen.pop("snapshot_exports", None)
    return frozen


def create_immutable_snapshot_export(
    project_index: dict,
    source_point_name: str,
    snapshot_name: str | None = None,
    note: str | None = None,
) -> tuple[dict, dict, dict]:
    project_index = ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(ensure_workspace_history(project_index))))

    point = (project_index.get("tag_points") or {}).get(source_point_name)
    if not point:
        raise ProjectSnapshotError(f"Unknown source_point_name: {source_point_name}")

    resolved_snapshot_name = (snapshot_name or f"{source_point_name}_snapshot").strip()
    if not resolved_snapshot_name:
        raise ProjectSnapshotError("snapshot_name is required")
    if resolved_snapshot_name in project_index.get("snapshot_exports", {}):
        raise ProjectSnapshotError(f"Snapshot export already exists: {resolved_snapshot_name}")

    frozen_project = _frozen_project_index(project_index)
    package = {
        "snapshot_version": "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1",
        "snapshot_name": resolved_snapshot_name,
        "project_name": project_index.get("project_name"),
        "source_point_name": source_point_name,
        "source_point_kind": point.get("point_kind", "tag"),
        "target_session_id": point.get("target_session_id"),
        "target_session_name": point.get("target_session_name"),
        "note": note.strip() if isinstance(note, str) and note.strip() else point.get("note"),
        "immutability": {
            "frozen": True,
            "mutable": False,
            "source": "tag_release_point",
        },
        "anchor": deepcopy(point),
        "export_state": {
            "active_session_id": project_index.get("active_session_id"),
            "active_branch_name": project_index.get("active_branch_name"),
            "workspace_summary": _workspace_summary_min(project_index),
            "branch_summary": branch_summary(project_index),
            "lineage_graph": build_named_merge_lineage_graph(project_index),
            "dependency_map": build_workspace_dependency_map(project_index),
            "timeline": build_workspace_timeline(project_index),
            "tag_point_summary": tag_point_summary(project_index),
            "project_index_frozen": frozen_project,
        },
    }

    out = deepcopy(project_index)
    out.setdefault("snapshot_exports", {})[resolved_snapshot_name] = package
    out = append_history_event(
        out,
        "snapshot_exported",
        f"Snapshot exported: {resolved_snapshot_name}",
        session_id=point.get("target_session_id"),
        session_name=point.get("target_session_name"),
        payload={
            "snapshot_name": resolved_snapshot_name,
            "source_point_name": source_point_name,
            "source_point_kind": point.get("point_kind", "tag"),
            "branch_name": point.get("branch_name"),
        },
    )

    result = {
        "snapshot_export_version": "SEMASCRIPT_IMMUTABLE_WORKSPACE_SNAPSHOT_v0.1",
        "project_name": out.get("project_name"),
        "snapshot_name": resolved_snapshot_name,
        "source_point_name": source_point_name,
        "source_point_kind": point.get("point_kind", "tag"),
        "target_session_id": point.get("target_session_id"),
        "summary": {
            "created": True,
            "immutable": True,
            "is_release_source": point.get("point_kind") == "release",
        },
    }
    return ensure_snapshot_state(ensure_tag_point_state(ensure_branching_state(out))), result, package
