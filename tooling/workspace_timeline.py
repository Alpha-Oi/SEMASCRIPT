
from __future__ import annotations

from copy import deepcopy
from typing import Optional


def _history_container(project_index: dict) -> dict:
    history = project_index.setdefault("history", {})
    history.setdefault("events", [])
    history.setdefault("next_seq", 1)
    return history


def _make_event(seq: int, event_type: str, title: str, session_id: Optional[str] = None, session_name: Optional[str] = None, payload: Optional[dict] = None) -> dict:
    return {
        "seq": seq,
        "event_type": event_type,
        "title": title,
        "session_id": session_id,
        "session_name": session_name,
        "payload": deepcopy(payload or {}),
    }


def append_history_event(
    project_index: dict,
    event_type: str,
    title: str,
    session_id: Optional[str] = None,
    session_name: Optional[str] = None,
    payload: Optional[dict] = None,
) -> dict:
    out = deepcopy(project_index)
    history = _history_container(out)
    seq = history["next_seq"]
    history["events"].append(_make_event(seq, event_type, title, session_id=session_id, session_name=session_name, payload=payload))
    history["next_seq"] = seq + 1
    return out


def ensure_workspace_history(project_index: dict) -> dict:
    out = deepcopy(project_index)
    history = _history_container(out)
    if history["events"]:
        return out

    out = append_history_event(
        out,
        "workspace_created",
        f"Workspace created: {out.get('project_name', 'Untitled SEMASCRIPT Project')}",
        payload={"project_name": out.get("project_name")},
    )
    for item in out.get("sessions", []):
        out = append_history_event(
            out,
            "session_added",
            f"Session added: {item.get('session_name', item['session_id'])}",
            session_id=item["session_id"],
            session_name=item.get("session_name"),
            payload={"profile": item.get("profile"), "source_mode": item.get("source_mode")},
        )
    active_id = out.get("active_session_id")
    if active_id:
        active = next((item for item in out.get("sessions", []) if item["session_id"] == active_id), None)
        out = append_history_event(
            out,
            "active_session_set",
            f"Active session set: {active.get('session_name', active_id) if active else active_id}",
            session_id=active_id,
            session_name=active.get("session_name") if active else active_id,
        )
    return out


def build_workspace_timeline(project_index: dict) -> dict:
    project_index = ensure_workspace_history(project_index)
    events = deepcopy(project_index.get("history", {}).get("events", []))
    for idx, event in enumerate(events):
        event["x"] = 80 + idx * 170
        event["y"] = 44 if idx % 2 == 0 else 112
        event["is_active_session_event"] = event.get("session_id") == project_index.get("active_session_id")
    return {
        "timeline_version": "SEMASCRIPT_WORKSPACE_TIMELINE_v0.1",
        "project_name": project_index.get("project_name"),
        "active_session_id": project_index.get("active_session_id"),
        "events": events,
        "summary": {
            "event_count": len(events),
            "session_event_count": sum(1 for e in events if e.get("session_id")),
        },
    }
