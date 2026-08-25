
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from workspace_timeline import append_history_event


class ProjectTagReleaseError(Exception):
    """Raised when tag/release point operation is invalid."""


def ensure_tag_point_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("tag_points", {})
    return out


def tag_point_summary(project_index: dict) -> list[dict]:
    project_index = ensure_tag_point_state(ensure_branching_state(project_index))
    out = []
    for tag_name, point in (project_index.get("tag_points") or {}).items():
        out.append({
            "tag_name": tag_name,
            "point_kind": point.get("point_kind", "tag"),
            "target_session_id": point.get("target_session_id"),
            "target_session_name": point.get("target_session_name"),
            "branch_name": point.get("branch_name"),
            "note": point.get("note"),
            "is_release": point.get("point_kind") == "release",
        })
    out.sort(key=lambda x: (x["point_kind"], x["tag_name"]))
    return out


def create_tag_release_point(
    project_index: dict,
    tag_name: str,
    target_session_id: str,
    point_kind: str = "tag",
    note: str | None = None,
) -> tuple[dict, dict]:
    tag_name = (tag_name or "").strip()
    if not tag_name:
        raise ProjectTagReleaseError("tag_name is required")
    if point_kind not in {"tag", "release"}:
        raise ProjectTagReleaseError("point_kind must be 'tag' or 'release'")

    project_index = ensure_tag_point_state(ensure_branching_state(project_index))
    if tag_name in project_index.get("tag_points", {}):
        raise ProjectTagReleaseError(f"Tag/release already exists: {tag_name}")

    target_entry = next((item for item in project_index.get("sessions", []) if item["session_id"] == target_session_id), None)
    if not target_entry:
        raise ProjectTagReleaseError(f"Unknown target_session_id: {target_session_id}")

    branch_name = target_entry.get("entry_metadata", {}).get("branching", {}).get("branch_name", project_index.get("active_branch_name", "main"))
    branch_head = project_index.get("branches", {}).get(branch_name, {}).get("head_session_id")
    point = {
        "tag_name": tag_name,
        "point_kind": point_kind,
        "target_session_id": target_session_id,
        "target_session_name": target_entry.get("session_name"),
        "branch_name": branch_name,
        "note": note.strip() if isinstance(note, str) and note.strip() else None,
        "lineage_state": {
            "branch_name": branch_name,
            "branch_head_session_id": branch_head,
            "active_session_id": project_index.get("active_session_id"),
            "active_branch_name": project_index.get("active_branch_name"),
            "is_branch_head_target": branch_head == target_session_id,
        },
    }

    out = deepcopy(project_index)
    out.setdefault("tag_points", {})[tag_name] = point
    title_prefix = "Release point created" if point_kind == "release" else "Tag created"
    out = append_history_event(
        out,
        "tag_release_created",
        f"{title_prefix}: {tag_name}",
        session_id=target_session_id,
        session_name=target_entry.get("session_name"),
        payload={
            "tag_name": tag_name,
            "point_kind": point_kind,
            "branch_name": branch_name,
        },
    )
    result = {
        "tag_release_version": "SEMASCRIPT_TAG_RELEASE_POINTS_v0.1",
        "project_name": out.get("project_name"),
        "tag_name": tag_name,
        "point_kind": point_kind,
        "target_session_id": target_session_id,
        "branch_name": branch_name,
        "summary": {
            "created": True,
            "is_release": point_kind == "release",
        },
    }
    return ensure_tag_point_state(ensure_branching_state(out)), result
