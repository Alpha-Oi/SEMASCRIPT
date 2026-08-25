
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from workspace_timeline import append_history_event
from project_model import add_session_to_workspace, set_active_session


class ProjectRebaseError(Exception):
    """Raised when branch rebase/replay cannot proceed safely."""


def _branch_entries(project_index: dict, branch_name: str) -> list[dict]:
    return [
        item for item in project_index.get("sessions", [])
        if item.get("entry_metadata", {}).get("branching", {}).get("branch_name") == branch_name
    ]


def _unique_replay_session_id(project_index: dict, original_session_id: str) -> str:
    existing = {item["session_id"] for item in project_index.get("sessions", [])}
    base = f"{original_session_id}_replay"
    if base not in existing:
        return base
    n = 2
    while f"{base}_{n}" in existing:
        n += 1
    return f"{base}_{n}"


def replay_branch_onto_target_lineage(
    project_index: dict,
    source_branch_name: str,
    target_branch_name: str,
    activate_head: bool = True,
) -> tuple[dict, dict]:
    project_index = ensure_branching_state(project_index)

    if source_branch_name == target_branch_name:
        raise ProjectRebaseError("source_branch_name and target_branch_name must differ")

    if source_branch_name not in project_index.get("branches", {}):
        raise ProjectRebaseError(f"Unknown source branch: {source_branch_name}")
    if target_branch_name not in project_index.get("branches", {}):
        raise ProjectRebaseError(f"Unknown target branch: {target_branch_name}")

    source_branch = project_index["branches"][source_branch_name]
    target_branch = project_index["branches"][target_branch_name]

    source_root = source_branch.get("root_session_id")
    source_head_before = source_branch.get("head_session_id")
    target_head_before = target_branch.get("head_session_id")

    source_entries = _branch_entries(project_index, source_branch_name)
    replay_candidates = [entry for entry in source_entries if entry["session_id"] != source_root]

    updated = deepcopy(project_index)
    replayed = []
    previous_parent = target_head_before

    for idx, entry in enumerate(replay_candidates, start=1):
        original_session_id = entry["session_id"]
        original_session = deepcopy(entry["session"])
        original_tags = list(entry.get("tags", []))
        if "rebase-replay" not in original_tags:
            original_tags.append("rebase-replay")

        source_entry_meta = deepcopy(entry.get("entry_metadata", {}))
        branching_meta = {
            "branch_name": source_branch_name,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "rebase_replay",
        }
        entry_metadata = {
            **source_entry_meta,
            "commit_kind": "rebase_replay",
            "rebase_replay": {
                "source_branch_name": source_branch_name,
                "target_branch_name": target_branch_name,
                "source_root_session_id": source_root,
                "target_head_before_rebase": target_head_before,
                "original_session_id": original_session_id,
                "replay_index": idx,
            },
            "branching": branching_meta,
        }

        new_session_id = _unique_replay_session_id(updated, original_session_id)
        updated = add_session_to_workspace(
            project_index=updated,
            session=original_session,
            session_id=new_session_id,
            file_name=None,
            tags=original_tags,
            entry_metadata=entry_metadata,
            branch_name=source_branch_name,
        )
        previous_parent = updated["sessions"][-1]["session_id"]
        replayed.append({
            "original_session_id": original_session_id,
            "replayed_session_id": previous_parent,
            "replay_index": idx,
        })

    if replayed:
        updated = append_history_event(
            updated,
            "branch_rebased",
            f"Branch rebased: {source_branch_name} onto {target_branch_name}",
            session_id=replayed[-1]["replayed_session_id"],
            session_name=updated["sessions"][-1]["session_name"],
            payload={
                "source_branch_name": source_branch_name,
                "target_branch_name": target_branch_name,
                "source_head_before": source_head_before,
                "target_head_before": target_head_before,
                "replayed_count": len(replayed),
            },
        )
        if activate_head:
            updated = set_active_session(updated, replayed[-1]["replayed_session_id"])

    result = {
        "rebase_version": "SEMASCRIPT_BRANCH_REBASE_REPLAY_v0.1",
        "project_name": updated.get("project_name"),
        "source_branch_name": source_branch_name,
        "target_branch_name": target_branch_name,
        "source_root_session_id": source_root,
        "source_head_before": source_head_before,
        "target_head_before": target_head_before,
        "replayed_sessions": replayed,
        "summary": {
            "replayed_count": len(replayed),
            "source_head_after": updated.get("branches", {}).get(source_branch_name, {}).get("head_session_id"),
            "active_session_id": updated.get("active_session_id"),
        },
    }
    return ensure_branching_state(updated), result
