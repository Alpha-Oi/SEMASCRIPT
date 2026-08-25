
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from workspace_timeline import append_history_event
from project_model import add_session_to_workspace, set_active_session


class ProjectCherryPickError(Exception):
    """Raised when selective session replay cannot proceed safely."""


def _find_entry(project_index: dict, session_id: str) -> dict | None:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    return None


def _unique_cherry_pick_session_id(project_index: dict, original_session_id: str) -> str:
    existing = {item["session_id"] for item in project_index.get("sessions", [])}
    base = f"{original_session_id}_cp"
    if base not in existing:
        return base
    n = 2
    while f"{base}_{n}" in existing:
        n += 1
    return f"{base}_{n}"


def cherry_pick_sessions_onto_branch(
    project_index: dict,
    source_session_ids: list[str],
    target_branch_name: str,
    activate_head: bool = True,
) -> tuple[dict, dict]:
    project_index = ensure_branching_state(project_index)

    if not source_session_ids:
        raise ProjectCherryPickError("source_session_ids is empty")
    if target_branch_name not in project_index.get("branches", {}):
        raise ProjectCherryPickError(f"Unknown target branch: {target_branch_name}")

    target_head_before = project_index["branches"][target_branch_name].get("head_session_id")
    updated = deepcopy(project_index)
    replayed = []
    previous_parent = target_head_before

    for idx, source_session_id in enumerate(source_session_ids, start=1):
        source_entry = _find_entry(updated, source_session_id)
        if not source_entry:
            raise ProjectCherryPickError(f"Unknown source session: {source_session_id}")

        original_session = deepcopy(source_entry["session"])
        original_tags = list(source_entry.get("tags", []))
        if "cherry-pick" not in original_tags:
            original_tags.append("cherry-pick")

        source_branch_name = source_entry.get("entry_metadata", {}).get("branching", {}).get("branch_name")
        entry_metadata = deepcopy(source_entry.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "cherry_pick"
        entry_metadata["cherry_pick"] = {
            "source_session_id": source_session_id,
            "source_branch_name": source_branch_name,
            "target_branch_name": target_branch_name,
            "target_head_before_cherry_pick": target_head_before,
            "cherry_pick_index": idx,
        }
        entry_metadata["branching"] = {
            "branch_name": target_branch_name,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "cherry_pick",
        }

        new_session_id = _unique_cherry_pick_session_id(updated, source_session_id)
        updated = add_session_to_workspace(
            project_index=updated,
            session=original_session,
            session_id=new_session_id,
            file_name=None,
            tags=original_tags,
            entry_metadata=entry_metadata,
            branch_name=target_branch_name,
        )
        previous_parent = updated["sessions"][-1]["session_id"]
        replayed.append({
            "source_session_id": source_session_id,
            "replayed_session_id": previous_parent,
            "source_branch_name": source_branch_name,
            "target_branch_name": target_branch_name,
            "cherry_pick_index": idx,
        })

    updated = append_history_event(
        updated,
        "branch_cherry_picked",
        f"Cherry-picked into {target_branch_name}",
        session_id=replayed[-1]["replayed_session_id"],
        session_name=updated["sessions"][-1]["session_name"],
        payload={
            "target_branch_name": target_branch_name,
            "source_session_ids": list(source_session_ids),
            "picked_count": len(replayed),
        },
    )
    if activate_head:
        updated = set_active_session(updated, replayed[-1]["replayed_session_id"])

    result = {
        "cherry_pick_version": "SEMASCRIPT_CHERRY_PICK_REPLAY_v0.1",
        "project_name": updated.get("project_name"),
        "source_session_ids": list(source_session_ids),
        "target_branch_name": target_branch_name,
        "target_head_before": target_head_before,
        "replayed_sessions": replayed,
        "summary": {
            "picked_count": len(replayed),
            "target_head_after": updated.get("branches", {}).get(target_branch_name, {}).get("head_session_id"),
            "active_session_id": updated.get("active_session_id"),
        },
    }
    return ensure_branching_state(updated), result
