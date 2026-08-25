
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from session_merge import finalize_merged_source


class ConflictResolutionError(Exception):
    """Raised when manual conflict resolution is invalid."""


def _set_path_value(obj: dict, path: str, value: Any) -> dict:
    out = deepcopy(obj)
    if not path:
        return deepcopy(value)
    parts = path.split(".")
    cursor = out
    for part in parts[:-1]:
        if part not in cursor or not isinstance(cursor[part], dict):
            cursor[part] = {}
        cursor = cursor[part]
    cursor[parts[-1]] = deepcopy(value)
    return out


def _decision_value(conflict: dict, decision: dict) -> Any:
    choice = decision.get("choice")
    if choice not in {"base", "left", "right", "custom"}:
        raise ConflictResolutionError(f"Unsupported decision choice: {choice!r}")
    if choice == "custom":
        if "value" not in decision:
            raise ConflictResolutionError("Custom decision requires 'value'")
        return deepcopy(decision["value"])
    return deepcopy(conflict[choice])


def resolve_merge_result_conflicts(merge_result: dict, decisions: dict[str, dict]) -> dict:
    out = {
        "resolution_version": "SEMASCRIPT_INTERACTIVE_CONFLICT_RESOLUTION_v0.1",
        "merge_version": merge_result.get("merge_version"),
        "base_session_id": merge_result.get("base_session_id"),
        "left_session_id": merge_result.get("left_session_id"),
        "right_session_id": merge_result.get("right_session_id"),
        "summary": {},
        "applied_decisions": [],
        "unresolved_conflicts": [],
        "resolved_source": deepcopy(merge_result.get("merged_source")),
    }

    conflicts = merge_result.get("conflicts", []) or []
    if not conflicts:
        out["summary"] = {
            "conflict_count": 0,
            "resolved_count": 0,
            "unresolved_count": 0,
            "finalized": "merged_session" in merge_result,
        }
        if "merged_session" in merge_result:
            out["merged_session"] = deepcopy(merge_result["merged_session"])
        return out

    resolved_source = deepcopy(merge_result.get("merged_source"))
    applied = []
    unresolved = []

    for conflict in conflicts:
        path = conflict["path"]
        decision = decisions.get(path)
        if not decision:
            unresolved.append(deepcopy(conflict))
            continue
        value = _decision_value(conflict, decision)
        resolved_source = _set_path_value(resolved_source, path, value)
        applied.append({
            "path": path,
            "choice": decision.get("choice"),
            "value": deepcopy(value),
        })

    out["applied_decisions"] = applied
    out["unresolved_conflicts"] = unresolved
    out["resolved_source"] = resolved_source
    out["summary"] = {
        "conflict_count": len(conflicts),
        "resolved_count": len(applied),
        "unresolved_count": len(unresolved),
        "finalized": len(unresolved) == 0,
    }

    if not unresolved:
        out["merged_session"] = finalize_merged_source(resolved_source)

    return out
