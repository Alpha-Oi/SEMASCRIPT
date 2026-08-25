
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Set, Tuple
import re

ENT_RE = re.compile(r"\[ENT:([A-Z0-9_]+)\]")
STATE_RE = re.compile(r"\[STA:([A-Z0-9_]+)")

PRODUCER_ROLES = {"dst", "res", "right"}
CONSUMER_ROLES = {"src", "code", "cau", "left", "obj", "ctx", "agt"}
STATE_ROLES = {"ctx"}


def _parse_label_tokens(label: str | None) -> Set[str]:
    if not label:
        return set()
    return set(ENT_RE.findall(label))


def _parse_state_tokens(label: str | None) -> Set[str]:
    if not label:
        return set()
    return set(STATE_RE.findall(label))


def _collect_from_value(value: dict, role_name: str | None, signals: dict) -> None:
    kind = value["kind"]
    if kind == "node":
        class_name = value["class_name"]
        root = value["root"]
        if class_name == "ENT":
            signals["entities"].add(root)
            if role_name in PRODUCER_ROLES:
                signals["outputs"].add(root)
            if role_name in CONSUMER_ROLES:
                signals["inputs"].add(root)
        elif class_name == "STA":
            signals["state_nodes"].add(root)
        for role in value.get("roles", []):
            _collect_from_value(role["value"], role["name"], signals)
    elif kind == "list":
        for item in value.get("items", []):
            _collect_from_value(item, role_name, signals)
    elif kind == "typed_literal":
        if value.get("class_name") == "STA":
            signals["state_nodes"].add(value["root"])


def summarize_session_entry(entry: dict) -> dict:
    session = entry["session"]
    doc = session.get("documents", {}).get("decomposed_ast_document") or session.get("documents", {}).get("ast_document")
    signals = {
        "entities": set(),
        "inputs": set(),
        "outputs": set(),
        "state_nodes": set(),
    }
    if doc and doc.get("ast"):
        _collect_from_value(doc["ast"], None, signals)

    final_state = session.get("reports", {}).get("state_report", {}).get("final_state", {}) or {}
    for dep in final_state.get("dependencies", []):
        signals["outputs"].update(_parse_label_tokens(dep.get("dst")))
        signals["inputs"].update(_parse_label_tokens(dep.get("src")))
        signals["entities"].update(_parse_label_tokens(dep.get("dst")))
        signals["entities"].update(_parse_label_tokens(dep.get("src")))

    for exp in final_state.get("expansions", []):
        signals["inputs"].update(_parse_label_tokens(exp.get("src")))
        signals["outputs"].update(_parse_label_tokens(exp.get("res")))
        signals["entities"].update(_parse_label_tokens(exp.get("src")))
        signals["entities"].update(_parse_label_tokens(exp.get("res")))

    for action in final_state.get("actions", []):
        signals["inputs"].update(_parse_label_tokens(action.get("agt")))
        signals["entities"].update(_parse_label_tokens(action.get("agt")))
        signals["entities"].update(_parse_label_tokens(action.get("obj")))

    for obs in final_state.get("observations", []):
        signals["inputs"].update(_parse_label_tokens(obs.get("agt")))
        signals["entities"].update(_parse_label_tokens(obs.get("agt")))
        signals["entities"].update(_parse_label_tokens(obs.get("obj")))

    states = final_state.get("states", {}) or {}
    for entity_name, state_list in states.items():
        signals["entities"].add(entity_name)
        for st in state_list:
            signals["state_nodes"].add(st)

    return {
        "session_id": entry["session_id"],
        "session_name": entry["session_name"],
        "profile": entry.get("profile"),
        "source_mode": entry.get("source_mode"),
        "tags": list(entry.get("tags", [])),
        "entities": sorted(signals["entities"]),
        "inputs": sorted(signals["inputs"]),
        "outputs": sorted(signals["outputs"]),
        "state_nodes": sorted(signals["state_nodes"]),
    }


def _grid_position(index: int, cols: int = 3) -> tuple[int, int]:
    col = index % cols
    row = index // cols
    return 120 + col * 240, 80 + row * 170


def build_workspace_dependency_map(project_index: dict) -> dict:
    summaries = [summarize_session_entry(entry) for entry in project_index.get("sessions", [])]
    nodes = []
    for idx, summary in enumerate(summaries):
        x, y = _grid_position(idx)
        nodes.append({
            "session_id": summary["session_id"],
            "session_name": summary["session_name"],
            "profile": summary.get("profile"),
            "tags": summary.get("tags", []),
            "entities": summary["entities"],
            "inputs": summary["inputs"],
            "outputs": summary["outputs"],
            "state_nodes": summary["state_nodes"],
            "x": x,
            "y": y,
            "is_active": summary["session_id"] == project_index.get("active_session_id"),
        })

    links = []
    seen_shared = set()
    for i, a in enumerate(summaries):
        for j, b in enumerate(summaries):
            if i == j:
                continue
            flow_tokens = sorted(set(a["outputs"]) & set(b["inputs"]))
            if flow_tokens:
                links.append({
                    "from_session_id": a["session_id"],
                    "to_session_id": b["session_id"],
                    "relation": "flow",
                    "tokens": flow_tokens,
                    "weight": len(flow_tokens),
                })

        for j in range(i + 1, len(summaries)):
            b = summaries[j]
            shared_tokens = sorted((set(a["entities"]) & set(b["entities"])) - (set(a["outputs"]) & set(b["inputs"])) - (set(b["outputs"]) & set(a["inputs"])))
            if shared_tokens:
                key = (a["session_id"], b["session_id"])
                if key not in seen_shared:
                    seen_shared.add(key)
                    links.append({
                        "from_session_id": a["session_id"],
                        "to_session_id": b["session_id"],
                        "relation": "shared",
                        "tokens": shared_tokens,
                        "weight": len(shared_tokens),
                    })

    return {
        "dependency_map_version": "SEMASCRIPT_WORKSPACE_NAVIGATION_MAP_v0.1",
        "project_name": project_index.get("project_name"),
        "active_session_id": project_index.get("active_session_id"),
        "nodes": nodes,
        "links": links,
        "summary": {
            "session_count": len(nodes),
            "flow_link_count": sum(1 for link in links if link["relation"] == "flow"),
            "shared_link_count": sum(1 for link in links if link["relation"] == "shared"),
        },
    }
