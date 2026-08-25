
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Set

from workspace_navigation import summarize_session_entry


def _entry_by_id(project_index: dict, session_id: str) -> dict:
    for entry in project_index.get("sessions", []):
        if entry["session_id"] == session_id:
            return entry
    raise ValueError(f"Unknown session_id: {session_id}")


def _session_metrics(entry: dict) -> dict:
    session = entry["session"]
    nav = summarize_session_entry(entry)
    runtime = session.get("reports", {}).get("runtime_report", {}) or {}
    state = session.get("reports", {}).get("state_report", {}) or {}
    final_state = state.get("final_state", {}) or {}
    history = state.get("runtime_report", {}).get("history", []) if isinstance(state.get("runtime_report"), dict) else []

    runtime_ops = [step.get("op_name") for step in runtime.get("plan", []) if step.get("op_name")]
    return {
        "session_id": entry["session_id"],
        "session_name": entry.get("session_name"),
        "profile": entry.get("profile"),
        "source_mode": entry.get("source_mode"),
        "slinear": session.get("project", {}).get("slinear"),
        "decomposed_slinear": session.get("project", {}).get("decomposed_slinear"),
        "entities": nav["entities"],
        "inputs": nav["inputs"],
        "outputs": nav["outputs"],
        "state_nodes": nav["state_nodes"],
        "runtime_accepted": bool(runtime.get("accepted")),
        "state_accepted": bool(state.get("accepted")),
        "runtime_ops": runtime_ops,
        "dependency_count": len(final_state.get("dependencies", []) or []),
        "expansion_count": len(final_state.get("expansions", []) or []),
        "action_count": len(final_state.get("actions", []) or []),
        "observation_count": len(final_state.get("observations", []) or []),
        "history_len": len(final_state.get("history", []) or []),
    }


def _set_diff(left: list[str], right: list[str]) -> dict:
    left_set = set(left)
    right_set = set(right)
    return {
        "shared": sorted(left_set & right_set),
        "left_only": sorted(left_set - right_set),
        "right_only": sorted(right_set - left_set),
    }


def _scalar_diff(left_value, right_value) -> dict:
    return {
        "left": left_value,
        "right": right_value,
        "changed": left_value != right_value,
    }


def compare_sessions(project_index: dict, left_session_id: str, right_session_id: str) -> dict:
    left_entry = _entry_by_id(project_index, left_session_id)
    right_entry = _entry_by_id(project_index, right_session_id)

    left = _session_metrics(left_entry)
    right = _session_metrics(right_entry)

    diff = {
        "compare_version": "SEMASCRIPT_CROSS_SESSION_DIFF_v0.1",
        "project_name": project_index.get("project_name"),
        "left_session_id": left_session_id,
        "right_session_id": right_session_id,
        "left_session_name": left.get("session_name"),
        "right_session_name": right.get("session_name"),
        "identity": {
            "profile": _scalar_diff(left["profile"], right["profile"]),
            "source_mode": _scalar_diff(left["source_mode"], right["source_mode"]),
        },
        "structure": {
            "slinear": _scalar_diff(left["slinear"], right["slinear"]),
            "decomposed_slinear": _scalar_diff(left["decomposed_slinear"], right["decomposed_slinear"]),
            "entities": _set_diff(left["entities"], right["entities"]),
            "inputs": _set_diff(left["inputs"], right["inputs"]),
            "outputs": _set_diff(left["outputs"], right["outputs"]),
            "state_nodes": _set_diff(left["state_nodes"], right["state_nodes"]),
        },
        "execution": {
            "runtime_accepted": _scalar_diff(left["runtime_accepted"], right["runtime_accepted"]),
            "state_accepted": _scalar_diff(left["state_accepted"], right["state_accepted"]),
            "runtime_ops": _set_diff(left["runtime_ops"], right["runtime_ops"]),
            "dependency_count": _scalar_diff(left["dependency_count"], right["dependency_count"]),
            "expansion_count": _scalar_diff(left["expansion_count"], right["expansion_count"]),
            "action_count": _scalar_diff(left["action_count"], right["action_count"]),
            "observation_count": _scalar_diff(left["observation_count"], right["observation_count"]),
            "history_len": _scalar_diff(left["history_len"], right["history_len"]),
        },
        "summary": {
            "same_profile": left["profile"] == right["profile"],
            "same_source_mode": left["source_mode"] == right["source_mode"],
            "shared_entities_count": len(set(left["entities"]) & set(right["entities"])),
            "left_only_entities_count": len(set(left["entities"]) - set(right["entities"])),
            "right_only_entities_count": len(set(right["entities"]) - set(left["entities"])),
            "runtime_ops_overlap_count": len(set(left["runtime_ops"]) & set(right["runtime_ops"])),
        },
    }
    return diff
