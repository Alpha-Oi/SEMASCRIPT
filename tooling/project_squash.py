
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from workspace_timeline import append_history_event
from project_model import add_session_to_workspace, set_active_session


class ProjectSquashError(Exception):
    """Raised when squash / fold cannot proceed safely."""


def _find_entry(project_index: dict, session_id: str) -> dict | None:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    return None


def _unique_squash_session_id(project_index: dict, last_source_session_id: str) -> str:
    existing = {item["session_id"] for item in project_index.get("sessions", [])}
    base = f"{last_source_session_id}_sq"
    if base not in existing:
        return base
    n = 2
    while f"{base}_{n}" in existing:
        n += 1
    return f"{base}_{n}"


def squash_sessions_into_lineage_commit(
    project_index: dict,
    source_session_ids: list[str],
    target_branch_name: str,
    session_id: str | None = None,
    session_name: str | None = None,
    activate_head: bool = True,
) -> tuple[dict, dict]:
    project_index = ensure_branching_state(project_index)

    if not source_session_ids:
        raise ProjectSquashError("source_session_ids is empty")
    if target_branch_name not in project_index.get("branches", {}):
        raise ProjectSquashError(f"Unknown target branch: {target_branch_name}")

    source_entries = []
    for sid in source_session_ids:
        entry = _find_entry(project_index, sid)
        if not entry:
            raise ProjectSquashError(f"Unknown source session: {sid}")
        source_entries.append(entry)

    target_head_before = project_index["branches"][target_branch_name].get("head_session_id")
    materialized_entry = source_entries[-1]
    materialized_session = deepcopy(materialized_entry["session"])
    if session_name:
        materialized_session["session_name"] = session_name

    source_branch_names = [
        entry.get("entry_metadata", {}).get("branching", {}).get("branch_name")
        for entry in source_entries
    ]

    tags = list(materialized_entry.get("tags", []))
    if "squash-fold" not in tags:
        tags.append("squash-fold")

    new_session_id = session_id or _unique_squash_session_id(project_index, source_session_ids[-1])
    entry_metadata = deepcopy(materialized_entry.get("entry_metadata", {}))
    entry_metadata["commit_kind"] = "squash_fold"
    entry_metadata["squash_fold"] = {
        "source_session_ids": list(source_session_ids),
        "source_branch_names": list(source_branch_names),
        "target_branch_name": target_branch_name,
        "target_head_before_squash": target_head_before,
        "materialized_from_session_id": source_session_ids[-1],
        "folded_count": len(source_session_ids),
    }
    entry_metadata["branching"] = {
        "branch_name": target_branch_name,
        "parent_session_ids": [target_head_before] if target_head_before else [],
        "lineage_kind": "squash_commit",
    }

    updated = add_session_to_workspace(
        project_index=project_index,
        session=materialized_session,
        session_id=new_session_id,
        file_name=None,
        tags=tags,
        entry_metadata=entry_metadata,
        branch_name=target_branch_name,
    )
    committed_entry = updated["sessions"][-1]

    updated = append_history_event(
        updated,
        "branch_squashed",
        f"Branch squashed: {committed_entry['session_name']}",
        session_id=committed_entry["session_id"],
        session_name=committed_entry["session_name"],
        payload={
            "source_session_ids": list(source_session_ids),
            "target_branch_name": target_branch_name,
            "folded_count": len(source_session_ids),
        },
    )

    if activate_head:
        updated = set_active_session(updated, committed_entry["session_id"])

    result = {
        "squash_version": "SEMASCRIPT_SQUASH_FOLD_LINEAGE_COMMIT_v0.1",
        "project_name": updated.get("project_name"),
        "source_session_ids": list(source_session_ids),
        "target_branch_name": target_branch_name,
        "materialized_from_session_id": source_session_ids[-1],
        "squashed_session_id": committed_entry["session_id"],
        "squashed_session_name": committed_entry["session_name"],
        "summary": {
            "folded_count": len(source_session_ids),
            "target_head_before": target_head_before,
            "active_session_id": updated.get("active_session_id"),
        },
    }
    return ensure_branching_state(updated), result
