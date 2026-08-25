from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state, create_tag_release_point
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
from project_local_outcome_set_package_commit_merge_resolution import (
    ensure_portable_local_outcome_package_merge_resolution_state,
)
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectPortableLocalOutcomePackageThreeWayMergeCommitError(Exception):
    """Raised when portable local outcome package three-way merge commit/promote is invalid."""


def ensure_portable_local_outcome_package_merge_commit_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("portable_local_outcome_set_package_merge_commits", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_portable_local_outcome_package_merge_commit_state(
        ensure_portable_local_outcome_package_merge_resolution_state(
            ensure_local_outcome_set_package_commit_state(
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
        )
    )


def portable_local_outcome_package_merge_commit_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for commit_name, entry in (project_index.get("portable_local_outcome_set_package_merge_commits") or {}).items():
        out.append({
            "commit_name": commit_name,
            "resolution_name": entry.get("resolution_name"),
            "base_commit_name": entry.get("base_commit_name"),
            "left_commit_name": entry.get("left_commit_name"),
            "right_commit_name": entry.get("right_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "promoted_point_name": entry.get("promoted_point_name"),
            "promoted_point_kind": entry.get("promoted_point_kind"),
            "note": entry.get("note"),
        })
    out.sort(key=lambda x: x["commit_name"])
    return out


def _derive_shared_metadata(project_index: dict, resolution_result: dict) -> tuple[str | None, str | None]:
    registry = project_index.get("local_outcome_set_package_commits") or {}
    commit_names = [
        resolution_result.get("base_commit_name"),
        resolution_result.get("left_commit_name"),
        resolution_result.get("right_commit_name"),
    ]
    entries = [deepcopy(registry.get(name)) for name in commit_names if name and registry.get(name)]
    if not entries:
        return None, None

    package_names = {entry.get("package_name") for entry in entries}
    source_commit_names = {entry.get("source_commit_name") for entry in entries}
    package_name = package_names.pop() if len(package_names) == 1 else None
    source_commit_name = source_commit_names.pop() if len(source_commit_names) == 1 else None
    return package_name, source_commit_name


def _resolution_pairs_from_merge_pairs(merge_pairs: list[dict]) -> list[dict]:
    out = []
    for item in merge_pairs or []:
        out.append({
            "original_session_id": item.get("original_session_id"),
            "resolved_session_id": item.get("resolved_session_id"),
            "decision_choice": item.get("decision_choice"),
            "conflict_like": item.get("conflict", False),
            "merge_status": item.get("merge_status"),
        })
    return out


def commit_portable_local_outcome_package_three_way_merge_resolution(
    project_index: dict,
    merge_resolution_result: dict,
    commit_name: str | None = None,
    promote_point_name: str | None = None,
    promote_point_kind: str = "release",
    note: str | None = None,
) -> tuple[dict, dict]:
    project_index = _normalize(project_index)

    if not isinstance(merge_resolution_result, dict):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError("merge_resolution_result must be an object")
    if merge_resolution_result.get("portable_local_outcome_package_three_way_merge_resolution_version") != "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_RESOLUTION_v0.1":
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError("Unsupported or missing portable local outcome merge resolution version")

    resolved_session_ids = list(merge_resolution_result.get("resolved_session_ids") or [])
    if not resolved_session_ids:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError("No resolved_session_ids to commit")

    resolved_commit_name = (
        commit_name or f"{merge_resolution_result.get('resolution_name', 'portable_local_merge_resolution')}_commit"
    ).strip()
    if not resolved_commit_name:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError("commit_name is required")
    if resolved_commit_name in (project_index.get("portable_local_outcome_set_package_merge_commits") or {}):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError(
            f"Portable local outcome package merge commit already exists: {resolved_commit_name}"
        )
    if resolved_commit_name in (project_index.get("local_outcome_set_package_commits") or {}):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError(
            f"Local outcome set package commit already exists: {resolved_commit_name}"
        )

    out = deepcopy(project_index)
    last_resolved_session_id = resolved_session_ids[-1]
    last_entry = next((item for item in out.get("sessions", []) if item["session_id"] == last_resolved_session_id), None)
    if not last_entry:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeCommitError(
            f"Resolved merged session not found in project: {last_resolved_session_id}"
        )

    promoted_point_result = None
    promoted_point_name_resolved = None
    promoted_point_kind_resolved = None
    if promote_point_name and promote_point_name.strip():
        promoted_point_name_resolved = promote_point_name.strip()
        promoted_point_kind_resolved = (promote_point_kind or "release").strip() or "release"
        out, promoted_point_result = create_tag_release_point(
            out,
            tag_name=promoted_point_name_resolved,
            target_session_id=last_resolved_session_id,
            point_kind=promoted_point_kind_resolved,
            note=note,
        )

    package_name, source_commit_name = _derive_shared_metadata(project_index, merge_resolution_result)
    commit_entry = {
        "commit_name": resolved_commit_name,
        "resolution_name": merge_resolution_result.get("resolution_name"),
        "package_name": package_name,
        "source_commit_name": source_commit_name,
        "base_commit_name": merge_resolution_result.get("base_commit_name"),
        "left_commit_name": merge_resolution_result.get("left_commit_name"),
        "right_commit_name": merge_resolution_result.get("right_commit_name"),
        "target_branch_name": merge_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": list(merge_resolution_result.get("skipped_session_ids") or []),
        "merge_pairs": deepcopy(merge_resolution_result.get("merge_pairs") or []),
        "resolution_pairs": _resolution_pairs_from_merge_pairs(merge_resolution_result.get("merge_pairs") or []),
        "decision_counts": deepcopy((merge_resolution_result.get("summary") or {}).get("decision_counts") or {}),
        "promoted_point_name": promoted_point_name_resolved,
        "promoted_point_kind": promoted_point_kind_resolved,
        "note": note,
        "commit_kind": "portable_local_outcome_package_three_way_merge_commit",
    }

    out.setdefault("portable_local_outcome_set_package_merge_commits", {})[resolved_commit_name] = deepcopy(commit_entry)
    out.setdefault("local_outcome_set_package_commits", {})[resolved_commit_name] = deepcopy(commit_entry)

    out = append_history_event(
        out,
        "portable_local_outcome_package_three_way_merge_committed",
        f"Portable local outcome package three-way merge committed: {resolved_commit_name}",
        session_id=last_resolved_session_id,
        session_name=last_entry.get("session_name"),
        payload={
            "commit_name": resolved_commit_name,
            "resolution_name": merge_resolution_result.get("resolution_name"),
            "base_commit_name": merge_resolution_result.get("base_commit_name"),
            "left_commit_name": merge_resolution_result.get("left_commit_name"),
            "right_commit_name": merge_resolution_result.get("right_commit_name"),
            "target_branch_name": merge_resolution_result.get("target_branch_name"),
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
        },
    )

    result = {
        "portable_local_outcome_package_three_way_merge_commit_version": "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_COMMIT_PROMOTE_v0.1",
        "commit_name": resolved_commit_name,
        "resolution_name": merge_resolution_result.get("resolution_name"),
        "base_commit_name": merge_resolution_result.get("base_commit_name"),
        "left_commit_name": merge_resolution_result.get("left_commit_name"),
        "right_commit_name": merge_resolution_result.get("right_commit_name"),
        "target_branch_name": merge_resolution_result.get("target_branch_name"),
        "resolved_session_ids": resolved_session_ids,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(merge_resolution_result.get("skipped_session_ids") or []),
            "promoted": promoted_point_result is not None,
            "promoted_point_name": promoted_point_name_resolved,
            "promoted_point_kind": promoted_point_kind_resolved,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
