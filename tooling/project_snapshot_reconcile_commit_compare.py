
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit import ensure_snapshot_reconcile_commit_state
from workspace_timeline import ensure_workspace_history


class ProjectSnapshotReconcileCommitCompareError(Exception):
    """Raised when resolution set diff / compare is invalid."""


def _normalize(project_index: dict) -> dict:
    return ensure_snapshot_reconcile_commit_state(
        ensure_snapshot_reconcile_resolution_state(
            ensure_snapshot_reconcile_state(
                ensure_partial_snapshot_import_state(
                    ensure_snapshot_restore_state(
                        ensure_snapshot_state(
                            ensure_tag_point_state(
                                ensure_branching_state(
                                    ensure_workspace_history(deepcopy(project_index))
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def _commit_entry(project_index: dict, commit_name: str) -> dict:
    entry = (project_index.get("snapshot_reconcile_commits") or {}).get(commit_name)
    if not entry:
        raise ProjectSnapshotReconcileCommitCompareError(f"Unknown snapshot reconcile commit: {commit_name}")
    return entry


def _session_entry(project_index: dict, session_id: str) -> dict | None:
    for item in project_index.get("sessions", []):
        if item["session_id"] == session_id:
            return item
    return None


def _set_diff(left_items: list[str], right_items: list[str]) -> dict:
    left = set(left_items)
    right = set(right_items)
    return {
        "shared": sorted(left & right),
        "left_only": sorted(left - right),
        "right_only": sorted(right - left),
    }


def _pair_index(pairs: list[dict]) -> dict[str, dict]:
    out = {}
    for pair in pairs or []:
        key = pair.get("original_session_id") or pair.get("resolved_session_id")
        if key:
            out[key] = pair
    return out


def compare_promoted_reconcile_outcomes(
    project_index: dict,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    project_index = _normalize(project_index)

    left = _commit_entry(project_index, left_commit_name)
    right = _commit_entry(project_index, right_commit_name)

    left_pairs = _pair_index(left.get("resolution_pairs") or [])
    right_pairs = _pair_index(right.get("resolution_pairs") or [])
    pair_keys = sorted(set(left_pairs.keys()) | set(right_pairs.keys()))

    pair_diffs = []
    for key in pair_keys:
        lp = left_pairs.get(key)
        rp = right_pairs.get(key)
        changed = lp != rp
        pair_diffs.append({
            "original_session_id": key,
            "left": deepcopy(lp),
            "right": deepcopy(rp),
            "changed": changed,
        })

    left_resolved_ids = list(left.get("resolved_session_ids") or [])
    right_resolved_ids = list(right.get("resolved_session_ids") or [])

    def session_texts(session_ids):
        out = {}
        for sid in session_ids:
            entry = _session_entry(project_index, sid)
            if entry:
                out[sid] = entry.get("session", {}).get("project", {}).get("source_text")
        return out

    left_texts = session_texts(left_resolved_ids)
    right_texts = session_texts(right_resolved_ids)

    identity = {
        "left_commit_name": left_commit_name,
        "right_commit_name": right_commit_name,
        "same_snapshot_name": left.get("snapshot_name") == right.get("snapshot_name"),
        "same_target_branch_name": left.get("target_branch_name") == right.get("target_branch_name"),
        "same_promoted_point_kind": left.get("promoted_point_kind") == right.get("promoted_point_kind"),
        "same_promoted_point_name": left.get("promoted_point_name") == right.get("promoted_point_name"),
        "same_resolution_name": left.get("resolution_name") == right.get("resolution_name"),
    }

    metadata = {
        "snapshot_name": {"left": left.get("snapshot_name"), "right": right.get("snapshot_name"), "changed": left.get("snapshot_name") != right.get("snapshot_name")},
        "resolution_name": {"left": left.get("resolution_name"), "right": right.get("resolution_name"), "changed": left.get("resolution_name") != right.get("resolution_name")},
        "target_branch_name": {"left": left.get("target_branch_name"), "right": right.get("target_branch_name"), "changed": left.get("target_branch_name") != right.get("target_branch_name")},
        "promoted_point_name": {"left": left.get("promoted_point_name"), "right": right.get("promoted_point_name"), "changed": left.get("promoted_point_name") != right.get("promoted_point_name")},
        "promoted_point_kind": {"left": left.get("promoted_point_kind"), "right": right.get("promoted_point_kind"), "changed": left.get("promoted_point_kind") != right.get("promoted_point_kind")},
        "note": {"left": left.get("note"), "right": right.get("note"), "changed": left.get("note") != right.get("note")},
    }

    text_diffs = []
    text_keys = sorted(set(left_texts.keys()) | set(right_texts.keys()))
    for sid in text_keys:
        lt = left_texts.get(sid)
        rt = right_texts.get(sid)
        text_diffs.append({
            "resolved_session_id": sid,
            "left_source_text": lt,
            "right_source_text": rt,
            "changed": lt != rt,
        })

    summary = {
        "resolved_session_count_left": len(left_resolved_ids),
        "resolved_session_count_right": len(right_resolved_ids),
        "shared_resolved_session_count": len(set(left_resolved_ids) & set(right_resolved_ids)),
        "pair_diff_count": sum(1 for item in pair_diffs if item["changed"]),
        "text_diff_count": sum(1 for item in text_diffs if item["changed"]),
        "metadata_diff_count": sum(1 for item in metadata.values() if item["changed"]),
    }
    summary["changed"] = any([
        summary["pair_diff_count"] > 0,
        summary["text_diff_count"] > 0,
        summary["metadata_diff_count"] > 0,
    ])

    return {
        "snapshot_reconcile_commit_compare_version": "SEMASCRIPT_RESOLUTION_SET_DIFF_COMPARE_v0.1",
        "left_commit_name": left_commit_name,
        "right_commit_name": right_commit_name,
        "identity": identity,
        "metadata": metadata,
        "resolved_sessions": _set_diff(left_resolved_ids, right_resolved_ids),
        "resolution_pairs": pair_diffs,
        "resolved_session_texts": text_diffs,
        "summary": summary,
    }
