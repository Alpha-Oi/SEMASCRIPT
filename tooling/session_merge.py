
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from session_model import create_session_from_text, create_session_from_graph


class SessionMergeConflict(Exception):
    """Raised when merge cannot be finalized."""


def _entry_by_id(project_index: dict, session_id: str) -> dict:
    for entry in project_index.get("sessions", []):
        if entry["session_id"] == session_id:
            return entry
    raise ValueError(f"Unknown session_id: {session_id}")


def _changed(base: Any, other: Any) -> bool:
    return base != other


def _three_way_merge_value(base: Any, left: Any, right: Any, path: str, conflicts: List[dict]) -> Any:
    if left == right:
        return deepcopy(left)
    if left == base:
        return deepcopy(right)
    if right == base:
        return deepcopy(left)

    if isinstance(base, dict) and isinstance(left, dict) and isinstance(right, dict):
        out = {}
        keys = set(base.keys()) | set(left.keys()) | set(right.keys())
        for key in sorted(keys):
            out[key] = _three_way_merge_value(
                base.get(key),
                left.get(key),
                right.get(key),
                f"{path}.{key}" if path else key,
                conflicts,
            )
        return out

    if isinstance(base, list) and isinstance(left, list) and isinstance(right, list):
        # Conservative policy for lists in v0.1:
        # identical or one-sided changes are allowed; concurrent divergent list edits conflict.
        conflicts.append({
            "path": path,
            "base": deepcopy(base),
            "left": deepcopy(left),
            "right": deepcopy(right),
            "reason": "concurrent_list_change",
        })
        return deepcopy(left)

    conflicts.append({
        "path": path,
        "base": deepcopy(base),
        "left": deepcopy(left),
        "right": deepcopy(right),
        "reason": "concurrent_scalar_change",
    })
    return deepcopy(left)



def _merged_session_name(base_session: dict, left_session: dict, right_session: dict) -> str:
    base_name = base_session.get("session_name")
    left_name = left_session.get("session_name")
    right_name = right_session.get("session_name")

    if left_name == right_name:
        return left_name or right_name or "Merged Session"
    if left_name == base_name:
        return right_name or left_name or "Merged Session"
    if right_name == base_name:
        return left_name or right_name or "Merged Session"
    return f"Merged: {left_name or 'left'} + {right_name or 'right'}"

def _source_payload(session: dict) -> dict:
    project = session.get("project", {}) or {}
    documents = session.get("documents", {}) or {}
    source_mode = project.get("source_mode")
    payload = {
        "profile": project.get("profile"),
        "source_mode": source_mode,
        "source_text": project.get("source_text"),
        "initial_state": project.get("initial_state"),
        "ui_state": session.get("ui_state"),
    }
    if source_mode == "graph":
        payload["graph_document"] = documents.get("graph_document")
    return payload


def finalize_merged_source(merged_source: dict) -> dict:
    return _finalize_merged_session(merged_source)


def _finalize_merged_session(merged_source: dict) -> dict:
    source_mode = merged_source.get("source_mode")
    profile = merged_source.get("profile") or "core"
    session_name = merged_source.get("session_name") or "Merged Session"
    initial_state = merged_source.get("initial_state")
    ui_state = merged_source.get("ui_state")

    if source_mode == "text":
        text = merged_source.get("source_text")
        if not text:
            raise SessionMergeConflict("Merged text session has no source_text")
        return create_session_from_text(
            text=text,
            profile=profile,
            decompose=bool(ui_state.get("decompose", True)) if isinstance(ui_state, dict) else True,
            initial_state=initial_state,
            session_name=session_name,
        )

    if source_mode == "graph":
        graph_document = merged_source.get("graph_document")
        if not graph_document:
            raise SessionMergeConflict("Merged graph session has no graph_document")
        return create_session_from_graph(
            graph_document=graph_document,
            profile=profile,
            decompose=bool(ui_state.get("decompose", True)) if isinstance(ui_state, dict) else True,
            initial_state=initial_state,
            session_name=session_name,
            ui_state=ui_state,
        )

    raise SessionMergeConflict(f"Unsupported source_mode for merge: {source_mode!r}")


def merge_sessions_three_way(
    project_index: dict,
    base_session_id: str,
    left_session_id: str,
    right_session_id: str,
) -> dict:
    base_entry = _entry_by_id(project_index, base_session_id)
    left_entry = _entry_by_id(project_index, left_session_id)
    right_entry = _entry_by_id(project_index, right_session_id)

    base_source = _source_payload(base_entry["session"])
    left_source = _source_payload(left_entry["session"])
    right_source = _source_payload(right_entry["session"])

    conflicts: List[dict] = []
    merged_source = _three_way_merge_value(base_source, left_source, right_source, "", conflicts)
    merged_source["session_name"] = _merged_session_name(base_entry["session"], left_entry["session"], right_entry["session"])

    result = {
        "merge_version": "SEMASCRIPT_THREE_WAY_SESSION_MERGE_v0.1",
        "project_name": project_index.get("project_name"),
        "base_session_id": base_session_id,
        "left_session_id": left_session_id,
        "right_session_id": right_session_id,
        "base_session_name": base_entry.get("session_name"),
        "left_session_name": left_entry.get("session_name"),
        "right_session_name": right_entry.get("session_name"),
        "conflicts": conflicts,
        "summary": {
            "conflict_count": len(conflicts),
            "auto_merged": len(conflicts) == 0,
        },
        "merged_source": merged_source,
    }

    if not conflicts:
        merged_session = _finalize_merged_session(merged_source)
        result["merged_session"] = merged_session

    return result
