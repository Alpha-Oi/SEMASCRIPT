
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


class ProjectPortableLocalOutcomePackageCommitCompareError(Exception):
    """Raised when portable local outcome package commit compare is invalid."""


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


def compare_portable_local_outcome_package_commits(
    project_index: dict,
    left_commit_name: str,
    right_commit_name: str,
) -> dict:
    project_index = _normalize(project_index)
    registry = project_index.get("local_outcome_set_package_commits") or {}
    left = deepcopy(registry.get(left_commit_name))
    right = deepcopy(registry.get(right_commit_name))
    if not left:
        raise ProjectPortableLocalOutcomePackageCommitCompareError(f"Unknown left_commit_name: {left_commit_name}")
    if not right:
        raise ProjectPortableLocalOutcomePackageCommitCompareError(f"Unknown right_commit_name: {right_commit_name}")

    sessions = _index_sessions(project_index)
    left_ids = list(left.get("resolved_session_ids") or [])
    right_ids = list(right.get("resolved_session_ids") or [])

    left_texts = {sid: (sessions.get(sid) or {}).get("session", {}).get("project", {}).get("source_text") for sid in left_ids}
    right_texts = {sid: (sessions.get(sid) or {}).get("session", {}).get("project", {}).get("source_text") for sid in right_ids}

    left_pairs = list(left.get("resolution_pairs") or [])
    right_pairs = list(right.get("resolution_pairs") or [])

    result = {
        "portable_local_outcome_package_commit_compare_version": "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_COMMIT_COMPARE_v0.1",
        "left_commit_name": left_commit_name,
        "right_commit_name": right_commit_name,
        "identity": {
            "same_commit_name": left_commit_name == right_commit_name,
            "same_resolution_name": left.get("resolution_name") == right.get("resolution_name"),
            "same_package_name": left.get("package_name") == right.get("package_name"),
            "same_source_commit_name": left.get("source_commit_name") == right.get("source_commit_name"),
        },
        "metadata": {
            "resolution_name": {"left": left.get("resolution_name"), "right": right.get("resolution_name"), "same": left.get("resolution_name") == right.get("resolution_name")},
            "package_name": {"left": left.get("package_name"), "right": right.get("package_name"), "same": left.get("package_name") == right.get("package_name")},
            "source_commit_name": {"left": left.get("source_commit_name"), "right": right.get("source_commit_name"), "same": left.get("source_commit_name") == right.get("source_commit_name")},
            "target_branch_name": {"left": left.get("target_branch_name"), "right": right.get("target_branch_name"), "same": left.get("target_branch_name") == right.get("target_branch_name")},
            "promoted_point_name": {"left": left.get("promoted_point_name"), "right": right.get("promoted_point_name"), "same": left.get("promoted_point_name") == right.get("promoted_point_name")},
            "promoted_point_kind": {"left": left.get("promoted_point_kind"), "right": right.get("promoted_point_kind"), "same": left.get("promoted_point_kind") == right.get("promoted_point_kind")},
            "note": {"left": left.get("note"), "right": right.get("note"), "same": left.get("note") == right.get("note")},
        },
        "resolved_sessions": {
            "left": left_ids,
            "right": right_ids,
            "shared": sorted(set(left_ids) & set(right_ids)),
            "left_only": sorted(set(left_ids) - set(right_ids)),
            "right_only": sorted(set(right_ids) - set(left_ids)),
        },
        "resolution_pairs": {
            "left_count": len(left_pairs),
            "right_count": len(right_pairs),
            "same_count": len(left_pairs) == len(right_pairs),
            "left": left_pairs,
            "right": right_pairs,
        },
        "resolved_session_texts": {
            "left": left_texts,
            "right": right_texts,
            "shared_equal_count": sum(1 for sid in set(left_texts) & set(right_texts) if left_texts.get(sid) == right_texts.get(sid)),
        },
    }
    result["summary"] = {
        "resolved_session_count_differs": len(left_ids) != len(right_ids),
        "promoted_point_differs": (
            left.get("promoted_point_name") != right.get("promoted_point_name")
            or left.get("promoted_point_kind") != right.get("promoted_point_kind")
        ),
        "text_differs": result["resolved_session_texts"]["shared_equal_count"] != len(set(left_texts) & set(right_texts)),
        "has_any_diff": True,
    }
    return result
