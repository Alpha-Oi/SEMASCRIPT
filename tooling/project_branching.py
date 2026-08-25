
from __future__ import annotations

from copy import deepcopy


def _find_entry(project_index: dict, session_id: str) -> dict | None:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    return None


def _branch_session_ids(project_index: dict, branch_name: str) -> list[str]:
    return [
        item["session_id"]
        for item in project_index.get("sessions", [])
        if item.get("entry_metadata", {}).get("branching", {}).get("branch_name") == branch_name
    ]


def ensure_branching_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("branches", {})
    out.setdefault("active_branch_name", "main")
    sessions = out.setdefault("sessions", [])

    if not out["branches"]:
        out["branches"]["main"] = {
            "branch_name": "main",
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": 0,
        }

    last_in_branch = {}
    for item in sessions:
        meta = item.setdefault("entry_metadata", {})
        branching = meta.setdefault("branching", {})

        branch_name = branching.get("branch_name") or out.get("active_branch_name") or "main"
        if branch_name not in out["branches"]:
            out["branches"][branch_name] = {
                "branch_name": branch_name,
                "root_session_id": None,
                "head_session_id": None,
                "manual_head_session_id": None,
                "color_index": len(out["branches"]),
            }
        branch = out["branches"][branch_name]

        parents = branching.get("parent_session_ids")
        if parents is None:
            merge_info = meta.get("merge_commit", {}) or {}
            derived = [sid for sid in [merge_info.get("base_session_id"), merge_info.get("left_session_id"), merge_info.get("right_session_id")] if sid]
            if not derived:
                prev = last_in_branch.get(branch_name)
                derived = [prev] if prev else []
            parents = list(dict.fromkeys(derived))
        branching["parent_session_ids"] = parents
        branching["branch_name"] = branch_name

        if not branching.get("lineage_kind"):
            commit_kind = meta.get("commit_kind")
            if commit_kind == "merge_commit" or len(parents) > 1:
                branching["lineage_kind"] = "merge_commit"
            elif commit_kind == "rebase_replay":
                branching["lineage_kind"] = "rebase_replay"
            elif commit_kind == "cherry_pick":
                branching["lineage_kind"] = "cherry_pick"
            elif commit_kind == "squash_fold":
                branching["lineage_kind"] = "squash_fold"
            elif commit_kind == "snapshot_partial_import":
                branching["lineage_kind"] = "snapshot_partial_import"
            elif commit_kind == "snapshot_reconcile":
                branching["lineage_kind"] = "snapshot_reconcile"
            elif commit_kind == "snapshot_reconcile_resolution":
                branching["lineage_kind"] = "snapshot_reconcile_resolution"
            elif commit_kind == "local_outcome_set_package_import":
                branching["lineage_kind"] = "local_outcome_set_package_import"
            elif commit_kind == "local_outcome_set_package_import_resolution":
                branching["lineage_kind"] = "local_outcome_set_package_import_resolution"
            elif not parents:
                branching["lineage_kind"] = "root"
            else:
                branching["lineage_kind"] = "commit"

        branching["branch_order"] = branch["color_index"]

        if branch["root_session_id"] is None:
            branch["root_session_id"] = item["session_id"]
        branch["head_session_id"] = item["session_id"]
        last_in_branch[branch_name] = item["session_id"]

    # Respect manual head overrides when valid for the branch.
    for branch_name, branch in out.get("branches", {}).items():
        valid_session_ids = set(_branch_session_ids(out, branch_name))
        manual_head = branch.get("manual_head_session_id")
        if manual_head and manual_head in valid_session_ids:
            branch["head_session_id"] = manual_head
        elif manual_head and manual_head not in valid_session_ids:
            branch["manual_head_session_id"] = None

    active = _find_entry(out, out.get("active_session_id"))
    if active:
        out["active_branch_name"] = active.get("entry_metadata", {}).get("branching", {}).get("branch_name", out.get("active_branch_name", "main"))

    return out


def branch_summary(project_index: dict) -> list[dict]:
    project_index = ensure_branching_state(project_index)
    out = []
    for branch_name, branch in project_index.get("branches", {}).items():
        count = 0
        for item in project_index.get("sessions", []):
            if item.get("entry_metadata", {}).get("branching", {}).get("branch_name") == branch_name:
                count += 1
        out.append({
            "branch_name": branch_name,
            "root_session_id": branch.get("root_session_id"),
            "head_session_id": branch.get("head_session_id"),
            "manual_head_session_id": branch.get("manual_head_session_id"),
            "is_active_branch": branch_name == project_index.get("active_branch_name"),
            "session_count": count,
            "color_index": branch.get("color_index", 0),
        })
    out.sort(key=lambda x: (x["color_index"], x["branch_name"]))
    return out


def create_named_branch(project_index: dict, source_session_id: str, branch_name: str) -> dict:
    if not branch_name or not branch_name.strip():
        raise ValueError("branch_name is required")
    project_index = ensure_branching_state(project_index)
    if branch_name in project_index.get("branches", {}):
        raise ValueError(f"Branch already exists: {branch_name}")
    source_entry = _find_entry(project_index, source_session_id)
    if not source_entry:
        raise ValueError(f"Unknown source_session_id: {source_session_id}")

    out = deepcopy(project_index)
    out["branches"][branch_name] = {
        "branch_name": branch_name,
        "root_session_id": source_session_id,
        "head_session_id": source_session_id,
        "manual_head_session_id": source_session_id,
        "color_index": len(out["branches"]),
    }
    out["active_branch_name"] = branch_name
    return out


def build_named_merge_lineage_graph(project_index: dict) -> dict:
    project_index = ensure_branching_state(project_index)
    summary = branch_summary(project_index)
    branch_order = {item["branch_name"]: idx for idx, item in enumerate(summary)}
    head_by_branch = {item["branch_name"]: item["head_session_id"] for item in summary}
    branch_rows = {}

    nodes = []
    for item in project_index.get("sessions", []):
        meta = item.get("entry_metadata", {})
        branching = meta.get("branching", {})
        branch_name = branching.get("branch_name", "main")
        row = branch_rows.get(branch_name, 0)
        branch_rows[branch_name] = row + 1

        x = 120 + branch_order.get(branch_name, 0) * 240
        y = 70 + row * 115

        attached_points = []
        for point_name, point in (project_index.get("tag_points") or {}).items():
            if point.get("target_session_id") == item["session_id"]:
                attached_points.append({"tag_name": point_name, "point_kind": point.get("point_kind", "tag")})

        nodes.append({
            "session_id": item["session_id"],
            "session_name": item["session_name"],
            "branch_name": branch_name,
            "lineage_kind": branching.get("lineage_kind", "commit"),
            "tags": item.get("tags", []),
            "is_active": item["session_id"] == project_index.get("active_session_id"),
            "is_branch_head": item["session_id"] == head_by_branch.get(branch_name),
            "attached_points": attached_points,
            "x": x,
            "y": y,
        })

    edges = []
    for item in project_index.get("sessions", []):
        meta = item.get("entry_metadata", {})
        branching = meta.get("branching", {})
        parents = branching.get("parent_session_ids", []) or []
        relation = "merge_parent" if len(parents) > 1 or branching.get("lineage_kind") == "merge_commit" else "parent"
        for parent_id in parents:
            edges.append({
                "from_session_id": parent_id,
                "to_session_id": item["session_id"],
                "relation": relation,
                "branch_name": branching.get("branch_name", "main"),
            })

        squash_info = meta.get("squash_fold", {}) or {}
        for source_session_id in squash_info.get("source_session_ids", []) or []:
            edges.append({
                "from_session_id": source_session_id,
                "to_session_id": item["session_id"],
                "relation": "squash_origin",
                "branch_name": branching.get("branch_name", "main"),
            })

    return {
        "lineage_graph_version": "SEMASCRIPT_NAMED_MERGE_LINEAGE_GRAPH_v0.1",
        "project_name": project_index.get("project_name"),
        "active_session_id": project_index.get("active_session_id"),
        "active_branch_name": project_index.get("active_branch_name"),
        "branches": summary,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "branch_count": len(summary),
            "session_count": len(nodes),
            "edge_count": len(edges),
        },
    }
