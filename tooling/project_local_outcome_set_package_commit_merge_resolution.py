
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
from project_local_outcome_set_package_resolution import (
    ensure_local_outcome_set_package_resolution_state,
    _unique_name,
    _build_custom_text_session,
)
from project_local_outcome_set_package_commit import ensure_local_outcome_set_package_commit_state
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(Exception):
    """Raised when portable local outcome package three-way merge resolution is invalid."""


def ensure_portable_local_outcome_package_merge_resolution_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("portable_local_outcome_set_package_merge_resolutions", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_portable_local_outcome_package_merge_resolution_state(
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


def portable_local_outcome_package_merge_resolution_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for resolution_name, entry in (project_index.get("portable_local_outcome_set_package_merge_resolutions") or {}).items():
        out.append({
            "resolution_name": resolution_name,
            "base_commit_name": entry.get("base_commit_name"),
            "left_commit_name": entry.get("left_commit_name"),
            "right_commit_name": entry.get("right_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "conflict_count": entry.get("conflict_count", 0),
            "decision_counts": deepcopy(entry.get("decision_counts") or {}),
        })
    out.sort(key=lambda x: x["resolution_name"])
    return out


def _session_index(project_index: dict) -> dict[str, dict]:
    return {item["session_id"]: item for item in project_index.get("sessions", [])}


def _role_entry(item: dict, sessions: dict[str, dict]) -> dict | None:
    sid = (item or {}).get("resolved_session_id")
    return deepcopy(sessions.get(sid)) if sid else None


def resolve_portable_local_outcome_package_three_way_conflicts_with_decisions(
    project_index: dict,
    merge_result: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_resolved: bool = True,
) -> tuple[dict, dict]:
    project_index = _normalize(project_index)
    if not isinstance(merge_result, dict):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError("merge_result must be an object")
    if merge_result.get("portable_local_outcome_package_baseline_three_way_merge_version") != "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_BASELINE_THREE_WAY_MERGE_v0.1":
        raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError("Unsupported or missing merge preview version")

    resolved_name = (resolution_name or f"{merge_result.get('left_commit_name', 'portable_local_merge')}_merge_resolution").strip()
    if not resolved_name:
        raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError("resolution_name is required")
    if resolved_name in (project_index.get("portable_local_outcome_set_package_merge_resolutions") or {}):
        raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"Portable local outcome merge resolution already exists: {resolved_name}")

    out = deepcopy(project_index)
    target_branch = (
        (target_branch_name or "").strip()
        or (merge_result.get("metadata", {}).get("left", {}) or {}).get("target_branch_name")
        or out.get("active_branch_name")
        or "main"
    )
    if target_branch not in out.get("branches", {}):
        out["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(out.get("branches", {})),
        }

    existing_ids = {item["session_id"] for item in out.get("sessions", [])}
    previous_parent = out["branches"][target_branch].get("head_session_id")
    sessions = _session_index(out)
    decisions = deepcopy(decisions or {})

    resolved_session_ids = []
    skipped_session_ids = []
    merge_pairs = []
    decision_counts = {"use_auto": 0, "use_base": 0, "use_left": 0, "use_right": 0, "skip": 0, "custom_text": 0}
    conflict_count = 0
    conflict_resolved_count = 0

    for idx, item in enumerate(merge_result.get("merge_items") or [], start=1):
        original_id = item["original_session_id"]
        decision = decisions.get(original_id, {}) or {}
        choice = (decision.get("choice") or ("use_auto" if not item.get("conflict") else "")).strip()

        if item.get("conflict"):
            conflict_count += 1
            if not choice:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(
                    f"Conflict requires a decision for original_session_id: {original_id}"
                )

        if choice not in {"use_auto", "use_base", "use_left", "use_right", "skip", "custom_text"}:
            raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"Unsupported merge decision choice: {choice or '<empty>'}")

        base_entry = _role_entry(item.get("base"), sessions)
        left_entry = _role_entry(item.get("left"), sessions)
        right_entry = _role_entry(item.get("right"), sessions)

        if choice == "skip":
            skipped_session_ids.append(original_id)
            decision_counts["skip"] += 1
            merge_pairs.append({
                "original_session_id": original_id,
                "resolved_session_id": None,
                "resolved_with_head_session_id": previous_parent,
                "decision_choice": "skip",
                "merge_status": item.get("status"),
                "conflict": item.get("conflict", False),
            })
            continue

        if choice == "use_auto":
            status = item.get("status")
            if status == "unchanged":
                selected_entry = base_entry or left_entry or right_entry
            elif status in {"same_change", "left_only_change"}:
                selected_entry = left_entry or right_entry or base_entry
            elif status == "right_only_change":
                selected_entry = right_entry or left_entry or base_entry
            else:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(
                    f"use_auto is not allowed for conflict item: {original_id}"
                )
            session_copy = deepcopy((selected_entry or {}).get("session", {}))
            profile = (selected_entry or {}).get("profile")
            source_mode = (selected_entry or {}).get("source_mode")
            session_name = (selected_entry or {}).get("session_name") or original_id
            decision_counts["use_auto"] += 1
        elif choice == "use_base":
            if not base_entry:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"use_base requires base entry for {original_id}")
            session_copy = deepcopy(base_entry.get("session", {}))
            profile = base_entry.get("profile")
            source_mode = base_entry.get("source_mode")
            session_name = base_entry.get("session_name")
            decision_counts["use_base"] += 1
        elif choice == "use_left":
            if not left_entry:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"use_left requires left entry for {original_id}")
            session_copy = deepcopy(left_entry.get("session", {}))
            profile = left_entry.get("profile")
            source_mode = left_entry.get("source_mode")
            session_name = left_entry.get("session_name")
            decision_counts["use_left"] += 1
        elif choice == "use_right":
            if not right_entry:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"use_right requires right entry for {original_id}")
            session_copy = deepcopy(right_entry.get("session", {}))
            profile = right_entry.get("profile")
            source_mode = right_entry.get("source_mode")
            session_name = right_entry.get("session_name")
            decision_counts["use_right"] += 1
        else:
            custom_text = (decision.get("custom_text") or "").strip()
            if not custom_text:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(
                    f"custom_text decision requires custom_text for {original_id}"
                )
            template_entry = left_entry or right_entry or base_entry
            if not template_entry:
                raise ProjectPortableLocalOutcomePackageThreeWayMergeResolutionError(f"No template entry for custom_text on {original_id}")
            session_copy, profile, source_mode, session_name = _build_custom_text_session(template_entry, custom_text)
            decision_counts["custom_text"] += 1

        if item.get("conflict"):
            conflict_resolved_count += 1

        new_session_id = _unique_name(existing_ids, original_id, "_localpkg_merge_resolved")
        entry_metadata = deepcopy((left_entry or right_entry or base_entry or {}).get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "portable_local_outcome_package_three_way_merge_resolution"
        entry_metadata["portable_local_outcome_package_three_way_merge_resolution"] = {
            "resolution_name": resolved_name,
            "base_commit_name": merge_result.get("base_commit_name"),
            "left_commit_name": merge_result.get("left_commit_name"),
            "right_commit_name": merge_result.get("right_commit_name"),
            "original_session_id": original_id,
            "target_branch_name": target_branch,
            "resolved_with_head_session_id": previous_parent,
            "resolution_index": idx,
            "decision_choice": choice,
            "merge_status": item.get("status"),
            "conflict": item.get("conflict", False),
        }
        if choice == "custom_text":
            entry_metadata["portable_local_outcome_package_three_way_merge_resolution"]["custom_text"] = (decision.get("custom_text") or "").strip()
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "portable_local_outcome_package_three_way_merge_resolution",
        }
        entry = {
            "session_id": new_session_id,
            "session_name": session_name,
            "profile": profile,
            "source_mode": source_mode,
            "file_name": None,
            "tags": list(dict.fromkeys(list((left_entry or right_entry or base_entry or {}).get("tags", [])) + ["portable-local-outcome-package-merge-resolution"])),
            "entry_metadata": entry_metadata,
            "session": session_copy,
        }
        out.setdefault("sessions", []).append(entry)
        if out["branches"][target_branch].get("root_session_id") is None:
            out["branches"][target_branch]["root_session_id"] = new_session_id
        out["branches"][target_branch]["head_session_id"] = new_session_id
        out["branches"][target_branch]["manual_head_session_id"] = new_session_id
        out["active_branch_name"] = target_branch
        previous_parent = new_session_id
        resolved_session_ids.append(new_session_id)
        merge_pairs.append({
            "original_session_id": original_id,
            "resolved_session_id": new_session_id,
            "resolved_with_head_session_id": entry_metadata["portable_local_outcome_package_three_way_merge_resolution"]["resolved_with_head_session_id"],
            "decision_choice": choice,
            "merge_status": item.get("status"),
            "conflict": item.get("conflict", False),
        })

    if activate_last_resolved and resolved_session_ids:
        out["active_session_id"] = resolved_session_ids[-1]

    out.setdefault("portable_local_outcome_set_package_merge_resolutions", {})[resolved_name] = {
        "resolution_name": resolved_name,
        "base_commit_name": merge_result.get("base_commit_name"),
        "left_commit_name": merge_result.get("left_commit_name"),
        "right_commit_name": merge_result.get("right_commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "merge_pairs": merge_pairs,
        "decision_counts": deepcopy(decision_counts),
        "conflict_count": conflict_count,
        "conflict_resolved_count": conflict_resolved_count,
    }

    if resolved_session_ids:
        last = next(item for item in out["sessions"] if item["session_id"] == resolved_session_ids[-1])
        out = append_history_event(
            out,
            "portable_local_outcome_package_three_way_merge_resolved",
            f"Portable local outcome package three-way merge resolved: {resolved_name}",
            session_id=last["session_id"],
            session_name=last["session_name"],
            payload={
                "resolution_name": resolved_name,
                "base_commit_name": merge_result.get("base_commit_name"),
                "left_commit_name": merge_result.get("left_commit_name"),
                "right_commit_name": merge_result.get("right_commit_name"),
                "target_branch_name": target_branch,
                "conflict_count": conflict_count,
                "conflict_resolved_count": conflict_resolved_count,
            },
        )

    result = {
        "portable_local_outcome_package_three_way_merge_resolution_version": "SEMASCRIPT_PORTABLE_LOCAL_OUTCOME_PACKAGE_THREE_WAY_MERGE_RESOLUTION_v0.1",
        "resolution_name": resolved_name,
        "base_commit_name": merge_result.get("base_commit_name"),
        "left_commit_name": merge_result.get("left_commit_name"),
        "right_commit_name": merge_result.get("right_commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "merge_pairs": merge_pairs,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
            "conflict_count": conflict_count,
            "conflict_resolved_count": conflict_resolved_count,
            "decision_counts": deepcopy(decision_counts),
        },
    }
    return _normalize(out), result
