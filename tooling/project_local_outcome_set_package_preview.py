
from __future__ import annotations

from copy import deepcopy

from project_branching import ensure_branching_state
from project_tags import ensure_tag_point_state
from project_snapshot import ensure_snapshot_state
from project_snapshot_restore import ensure_snapshot_restore_state
from project_snapshot_partial_import import ensure_partial_snapshot_import_state
from project_snapshot_reconcile import ensure_snapshot_reconcile_state
from project_snapshot_reconcile_resolution import ensure_snapshot_reconcile_resolution_state
from project_snapshot_reconcile_commit_package_commit import ensure_snapshot_reconcile_commit_package_commit_state
from project_local_outcome_set_package import ensure_local_outcome_set_package_state
from workspace_timeline import ensure_workspace_history


class ProjectLocalOutcomeSetPackagePreviewError(Exception):
    """Raised when local outcome set package preview is invalid."""


def _normalize(project_index: dict) -> dict:
    return ensure_local_outcome_set_package_state(
        ensure_snapshot_reconcile_commit_package_commit_state(
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


def preview_portable_local_outcome_package_before_import(
    current_project_index: dict,
    package_data: dict,
    import_name: str | None = None,
    target_branch_name: str | None = None,
) -> dict:
    if not isinstance(package_data, dict):
        raise ProjectLocalOutcomeSetPackagePreviewError("package_data must be an object")
    if package_data.get("local_outcome_set_package_version") != "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1":
        raise ProjectLocalOutcomeSetPackagePreviewError("Unsupported or missing local_outcome_set_package_version")

    current = _normalize(current_project_index)
    registry = current.get("snapshot_reconcile_commit_package_commits") or {}
    local_pkg_imports = current.get("local_outcome_set_package_imports") or {}
    branches = current.get("branches") or {}

    resolved_import_name = (import_name or f"{package_data.get('package_name', 'package')}_import").strip()
    if not resolved_import_name:
        raise ProjectLocalOutcomeSetPackagePreviewError("import_name is required")

    resolved_ids = [
        item.get("session_id")
        for item in (package_data.get("resolved_sessions") or [])
        if item.get("session_id")
    ]
    current_session_ids = {item["session_id"] for item in current.get("sessions", [])}
    current_head = None
    target_branch = (target_branch_name or package_data.get("exported_local_outcome_commit", {}).get("target_branch_name") or current.get("active_branch_name") or "main").strip()
    if target_branch in branches:
        current_head = branches[target_branch].get("head_session_id")

    compare_entry = None
    if current_head:
        compare_entry = next((item for item in current.get("sessions", []) if item["session_id"] == current_head), None)

    preview_items = []
    compatible_count = 0
    conflict_like_count = 0
    for item in (package_data.get("resolved_sessions") or []):
        source_text = item.get("session", {}).get("project", {}).get("source_text")
        source_mode = item.get("source_mode")
        profile = item.get("profile")
        compare_text = compare_entry.get("session", {}).get("project", {}).get("source_text") if compare_entry else None
        compare_mode = compare_entry.get("source_mode") if compare_entry else None
        compare_profile = compare_entry.get("profile") if compare_entry else None
        same_profile = compare_entry is not None and profile == compare_profile
        same_mode = compare_entry is not None and source_mode == compare_mode
        same_text = compare_entry is not None and source_text == compare_text
        exact_match = bool(compare_entry is not None and same_profile and same_mode and same_text)
        conflict_like = bool(compare_entry is not None and source_text is not None and compare_text is not None and source_text != compare_text)
        if exact_match or (compare_entry is None):
            compatible_count += 1
        if conflict_like:
            conflict_like_count += 1
        preview_items.append({
            "original_session_id": item.get("session_id"),
            "current_head_session_id": current_head,
            "same_profile_as_compare": same_profile,
            "same_source_mode_as_compare": same_mode,
            "same_source_text_as_compare": same_text,
            "exact_match": exact_match,
            "conflict_like": conflict_like,
            "status": "conflict_like" if conflict_like else ("exact_match" if exact_match else ("compatible_no_compare" if compare_entry is None else "compatible_variant")),
        })

    promoted_point = package_data.get("promoted_point") or {}
    promoted_name = promoted_point.get("point_name")
    promoted_name_conflict = bool(promoted_name and promoted_name in (current.get("tag_points") or {}))

    result = {
        "portable_local_outcome_package_preview_version": "SEMASCRIPT_LOCAL_OUTCOME_SET_PORTABLE_PACKAGE_PREVIEW_v0.1",
        "package_name": package_data.get("package_name"),
        "import_target": {
            "import_name": resolved_import_name,
            "target_branch_name": target_branch,
            "target_branch_exists": target_branch in branches,
            "would_create_branch": target_branch not in branches,
        },
        "metadata": {
            "source_commit_name": package_data.get("exported_local_outcome_commit", {}).get("commit_name"),
            "resolution_name": package_data.get("exported_local_outcome_commit", {}).get("resolution_name"),
            "promoted_point_name": promoted_name,
            "promoted_point_kind": promoted_point.get("point_kind"),
            "has_promoted_point": bool(promoted_name),
        },
        "collections": {
            "resolved_sessions": {
                "package_count": len(resolved_ids),
                "current_conflicting_ids": sorted(set(resolved_ids) & current_session_ids),
            },
            "local_outcome_commits": {
                "existing_count": len(registry),
            },
            "local_package_imports": {
                "existing_count": len(local_pkg_imports),
                "import_name_conflict": resolved_import_name in local_pkg_imports,
            },
        },
        "compatibility": {
            "version_ok": True,
            "import_name_available": resolved_import_name not in local_pkg_imports,
            "promoted_point_name_conflict": promoted_name_conflict,
            "resolved_sessions_have_content": len(resolved_ids) > 0,
        },
        "preview_items": preview_items,
    }
    result["summary"] = {
        "selected_session_count": len(preview_items),
        "compatible_count": compatible_count,
        "conflict_like_count": conflict_like_count,
        "has_conflicts": conflict_like_count > 0 or promoted_name_conflict or (resolved_import_name in local_pkg_imports),
    }
    return result
