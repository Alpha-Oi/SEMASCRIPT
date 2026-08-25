
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
from project_snapshot_reconcile_commit_package import ensure_snapshot_reconcile_commit_package_state
from project_snapshot_reconcile_commit_package_resolution import ensure_snapshot_reconcile_commit_package_resolution_state
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state
from project_local_outcome_set_package import ensure_local_outcome_set_package_state
from project_local_outcome_set_package_resolution import ensure_local_outcome_set_package_resolution_state
from project_local_outcome_set_package_commit import ensure_local_outcome_set_package_commit_state
from workspace_timeline import ensure_workspace_history


class ProjectPortableLocalOutcomePackageThreeWayMergeError(Exception):
    """Raised when portable local outcome package three-way merge is invalid."""


def _normalize(project_index: dict) -> dict:
    return ensure_local_outcome_set_package_commit_state(
        ensure_local_outcome_set_package_resolution_state(
            ensure_local_outcome_set_package_state(
                ensure_snapshot_reconcile_commit_package_commit_state(
                    ensure_snapshot_reconcile_commit_package_resolution_state(
                        ensure_snapshot_reconcile_commit_package_state(
                            ensure_snapshot_reconcile_commit_state(
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
                        )
                    )
                )
            )
        )
    )


def _index_sessions(project_index: dict) -> dict[str, dict]:
    return {item["session_id"]: item for item in project_index.get("sessions", [])}


def _commit_entry(project_index: dict, commit_name: str) -> dict:
    registry = project_index.get("local_outcome_set_package_commits") or {}
    entry = deepcopy(registry.get(commit_name))
    if not entry:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeError(f"Unknown commit_name: {commit_name}")
    return entry


def _original_id_map(commit_entry: dict, sessions: dict[str, dict]) -> dict[str, dict]:
    out = {}
    for pair in (commit_entry.get("resolution_pairs") or []):
        original_id = pair.get("original_session_id")
        resolved_id = pair.get("resolved_session_id")
        if not original_id:
            continue
        entry = sessions.get(resolved_id or "")
        out[original_id] = {
            "original_session_id": original_id,
            "resolved_session_id": resolved_id,
            "decision_choice": pair.get("decision_choice"),
            "conflict_like": pair.get("conflict_like", False),
            "source_text": (entry or {}).get("session", {}).get("project", {}).get("source_text"),
            "session_name": (entry or {}).get("session_name"),
            "profile": (entry or {}).get("profile"),
            "source_mode": (entry or {}).get("source_mode"),
        }
    return out


def compare_baseline_or_three_way_merge_portable_local_outcome_package_commits(
    project_index: dict,
    base_commit_name: str,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    project_index = _normalize(project_index)
    sessions = _index_sessions(project_index)

    base_entry = _commit_entry(project_index, base_commit_name)
    left_entry = _commit_entry(project_index, left_commit_name)
    right_entry = _commit_entry(project_index, right_commit_name)

    base_map = _original_id_map(base_entry, sessions)
    left_map = _original_id_map(left_entry, sessions)
    right_map = _original_id_map(right_entry, sessions)

    original_ids = sorted(set(base_map) | set(left_map) | set(right_map))
    merge_items = []
    auto_merged = []
    conflict_count = 0

    for original_id in original_ids:
        base_text = (base_map.get(original_id) or {}).get("source_text")
        left_text = (left_map.get(original_id) or {}).get("source_text")
        right_text = (right_map.get(original_id) or {}).get("source_text")

        if left_text == base_text and right_text == base_text:
            status = "unchanged"
            merged_text = base_text
            conflict = False
        elif left_text == right_text and left_text != base_text:
            status = "same_change"
            merged_text = left_text
            conflict = False
        elif left_text != base_text and right_text == base_text:
            status = "left_only_change"
            merged_text = left_text
            conflict = False
        elif right_text != base_text and left_text == base_text:
            status = "right_only_change"
            merged_text = right_text
            conflict = False
        else:
            status = "conflict"
            merged_text = None
            conflict = True
            conflict_count += 1

        item = {
            "original_session_id": original_id,
            "base": deepcopy(base_map.get(original_id) or {"source_text": None}),
            "left": deepcopy(left_map.get(original_id) or {"source_text": None}),
            "right": deepcopy(right_map.get(original_id) or {"source_text": None}),
            "status": status,
            "conflict": conflict,
            "merged_source_text": merged_text,
        }
        merge_items.append(item)
        if not conflict and merged_text is not None:
            auto_merged.append({
                "original_session_id": original_id,
                "status": status,
                "merged_source_text": merged_text,
            })

    result = {
        "portable_local_outcome_package_baseline_three_way_merge_version": "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_BASELINE_THREE_WAY_MERGE_v0.1",
        "base_commit_name": base_commit_name,
        "left_commit_name": left_commit_name,
        "right_commit_name": right_commit_name,
        "identity": {
            "same_package_triplet": (
                base_entry.get("package_name") == left_entry.get("package_name") == right_entry.get("package_name")
            ),
            "same_source_commit_triplet": (
                base_entry.get("source_commit_name") == left_entry.get("source_commit_name") == right_entry.get("source_commit_name")
            ),
        },
        "metadata": {
            "base": {
                "resolution_name": base_entry.get("resolution_name"),
                "package_name": base_entry.get("package_name"),
                "source_commit_name": base_entry.get("source_commit_name"),
                "target_branch_name": base_entry.get("target_branch_name"),
                "promoted_point_name": base_entry.get("promoted_point_name"),
                "promoted_point_kind": base_entry.get("promoted_point_kind"),
            },
            "left": {
                "resolution_name": left_entry.get("resolution_name"),
                "package_name": left_entry.get("package_name"),
                "source_commit_name": left_entry.get("source_commit_name"),
                "target_branch_name": left_entry.get("target_branch_name"),
                "promoted_point_name": left_entry.get("promoted_point_name"),
                "promoted_point_kind": left_entry.get("promoted_point_kind"),
            },
            "right": {
                "resolution_name": right_entry.get("resolution_name"),
                "package_name": right_entry.get("package_name"),
                "source_commit_name": right_entry.get("source_commit_name"),
                "target_branch_name": right_entry.get("target_branch_name"),
                "promoted_point_name": right_entry.get("promoted_point_name"),
                "promoted_point_kind": right_entry.get("promoted_point_kind"),
            },
        },
        "merge_items": merge_items,
        "auto_merged_items": auto_merged,
        "summary": {
            "original_session_count": len(original_ids),
            "auto_merged_count": len(auto_merged),
            "conflict_count": conflict_count,
            "has_conflicts": conflict_count > 0,
        },
    }
    return result
