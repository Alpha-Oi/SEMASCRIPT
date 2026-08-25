
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from workspace_timeline import append_history_event
from project_model import set_active_session


class ProjectBranchResetError(Exception):
    """Raised when branch head reset/restore cannot proceed safely."""


def reset_branch_head_to_historical_session(
    project_index: dict,
    branch_name: str,
    target_session_id: str,
    activate_head: bool = True,
) -> tuple[dict, dict]:
    project_index = ensure_branching_state(project_index)

    if branch_name not in project_index.get("branches", {}):
        raise ProjectBranchResetError(f"Unknown branch: {branch_name}")

    branch_entries = [
        item for item in project_index.get("sessions", [])
        if item.get("entry_metadata", {}).get("branching", {}).get("branch_name") == branch_name
    ]
    valid_session_ids = {item["session_id"] for item in branch_entries}
    if target_session_id not in valid_session_ids:
        raise ProjectBranchResetError(
            f"target_session_id {target_session_id!r} is not in branch {branch_name!r}"
        )

    out = deepcopy(project_index)
    previous_head = out["branches"][branch_name].get("head_session_id")
    out["branches"][branch_name]["manual_head_session_id"] = target_session_id
    out["branches"][branch_name]["head_session_id"] = target_session_id
    out["active_branch_name"] = branch_name

    target_entry = next(item for item in out["sessions"] if item["session_id"] == target_session_id)
    out = append_history_event(
        out,
        "branch_reset",
        f"Branch head reset: {branch_name} -> {target_entry['session_name']}",
        session_id=target_session_id,
        session_name=target_entry["session_name"],
        payload={
            "branch_name": branch_name,
            "previous_head_session_id": previous_head,
            "target_session_id": target_session_id,
        },
    )
    if activate_head:
        out = set_active_session(out, target_session_id)

    result = {
        "branch_reset_version": "SEMASCRIPT_BRANCH_RESET_RESTORE_v0.1",
        "project_name": out.get("project_name"),
        "branch_name": branch_name,
        "previous_head_session_id": previous_head,
        "target_session_id": target_session_id,
        "summary": {
            "head_changed": previous_head != target_session_id,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return ensure_branching_state(out), result
