
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
from workspace_timeline import ensure_workspace_history


class ProjectSnapshotReconcileCommitPackagePreviewError(Exception):
    """Raised when standalone promoted outcome package preview is invalid."""


def _normalize(project_index: dict) -> dict:
    return ensure_snapshot_reconcile_commit_package_state(
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


def _set_diff(current_items: list[str], package_items: list[str]) -> dict:
    current_set = set(current_items)
    package_set = set(package_items)
    return {
        "shared": sorted(current_set & package_set),
        "current_only": sorted(current_set - package_set),
        "package_only": sorted(package_set - current_set),
    }


def preview_standalone_reconcile_outcome_package_import(
    current_project_index: dict,
    package: dict,
    import_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_imported: bool = True,
) -> dict:
    current = _normalize(current_project_index)
    if not isinstance(package, dict):
        raise ProjectSnapshotReconcileCommitPackagePreviewError("package must be an object")
    if package.get("resolution_set_package_version") != "SEMASCRIPT_PROMOTED_RECONCILE_OUTCOME_PACKAGE_v0.1":
        raise ProjectSnapshotReconcileCommitPackagePreviewError("Unsupported or missing resolution_set_package_version")

    exported_commit = deepcopy(package.get("exported_commit") or {})
    resolved_sessions = list(package.get("resolved_sessions") or [])
    if not exported_commit or not resolved_sessions:
        raise ProjectSnapshotReconcileCommitPackagePreviewError("Package is missing exported_commit or resolved_sessions")

    resolved_import_name = (import_name or f"{package.get('package_name', 'package')}_import").strip()
    if not resolved_import_name:
        raise ProjectSnapshotReconcileCommitPackagePreviewError("import_name is required")

    target_branch = (target_branch_name or exported_commit.get("target_branch_name") or current.get("active_branch_name") or "main").strip()
    branch_exists = target_branch in (current.get("branches") or {})
    current_head_session_id = (current.get("branches", {}).get(target_branch) or {}).get("head_session_id") if branch_exists else None

    current_head_entry = None
    if current_head_session_id:
        current_head_entry = next((item for item in current.get("sessions", []) if item["session_id"] == current_head_session_id), None)

    would_import_commit_name = f"{package.get('commit_name', 'reconcile_commit')}_import"
    import_name_available = resolved_import_name not in (current.get("snapshot_reconcile_commit_package_imports") or {})
    promoted_point = deepcopy(package.get("promoted_point") or {})
    promoted_point_name = promoted_point.get("tag_name") or exported_commit.get("promoted_point_name")
    promoted_point_collision = bool(promoted_point_name and promoted_point_name in (current.get("tag_points") or {}))

    preview_items = []
    compare_entry = current_head_entry
    exact_match_count = 0
    conflict_like_count = 0
    source_mode_mismatch_count = 0
    profile_mismatch_count = 0

    for idx, packaged in enumerate(resolved_sessions, start=1):
        session = packaged.get("session", {}) or {}
        project = session.get("project", {}) or {}
        package_text = project.get("source_text")
        package_profile = packaged.get("profile")
        package_source_mode = packaged.get("source_mode")
        compare_sid = compare_entry.get("session_id") if compare_entry else None
        compare_profile = compare_entry.get("profile") if compare_entry else None
        compare_source_mode = compare_entry.get("source_mode") if compare_entry else None
        compare_text = (compare_entry.get("session", {}) or {}).get("project", {}).get("source_text") if compare_entry else None

        same_profile = bool(compare_profile is not None and package_profile == compare_profile)
        same_source_mode = bool(compare_source_mode is not None and package_source_mode == compare_source_mode)
        same_source_text = bool(compare_text is not None and package_text is not None and package_text == compare_text)
        exact_match = bool(same_profile and same_source_mode and same_source_text)
        conflict_like = bool(compare_entry is not None and package_text is not None and compare_text is not None and package_text != compare_text)

        if exact_match:
            exact_match_count += 1
        if conflict_like:
            conflict_like_count += 1
        if compare_entry is not None and not same_source_mode:
            source_mode_mismatch_count += 1
        if compare_entry is not None and not same_profile:
            profile_mismatch_count += 1

        status = "exact_match" if exact_match else ("conflict_like" if conflict_like else ("compatible" if compare_entry else "new_branch_import"))

        preview_items.append({
            "original_session_id": packaged.get("session_id"),
            "session_name": packaged.get("session_name"),
            "package_index": idx,
            "target_branch_name": target_branch,
            "compare_session_id": compare_sid,
            "same_profile_as_compare": same_profile,
            "same_source_mode_as_compare": same_source_mode,
            "same_source_text_as_compare": same_source_text,
            "exact_match": exact_match,
            "conflict_like": conflict_like,
            "status": status,
        })
        compare_entry = packaged

    current_session_ids = [item["session_id"] for item in current.get("sessions", [])]
    package_session_ids = [item.get("session_id") for item in resolved_sessions]
    current_branch_names = sorted((current.get("branches") or {}).keys())
    current_tag_names = sorted((current.get("tag_points") or {}).keys())
    package_point_names = [promoted_point_name] if promoted_point_name else []

    compatibility = {
        "version_supported": True,
        "import_name_available": import_name_available,
        "target_branch_exists": branch_exists,
        "would_create_target_branch": not branch_exists,
        "promoted_point_name_collision": promoted_point_collision,
        "portable": bool((package.get("immutability") or {}).get("portable")),
        "standalone": bool((package.get("immutability") or {}).get("standalone")),
    }

    summary = {
        "resolved_session_count": len(resolved_sessions),
        "exact_match_count": exact_match_count,
        "conflict_like_count": conflict_like_count,
        "source_mode_mismatch_count": source_mode_mismatch_count,
        "profile_mismatch_count": profile_mismatch_count,
        "compatible_for_import": compatibility["version_supported"] and compatibility["import_name_available"],
    }

    return {
        "snapshot_reconcile_commit_package_preview_version": "SEMASCRIPT_STANDALONE_OUTCOME_PACKAGE_DIFF_COMPATIBILITY_v0.1",
        "package_name": package.get("package_name"),
        "commit_name": package.get("commit_name"),
        "import_target": {
            "import_name": resolved_import_name,
            "target_branch_name": target_branch,
            "activate_last_imported": activate_last_imported,
            "would_import_commit_name": would_import_commit_name,
            "current_head_session_id": current_head_session_id,
        },
        "metadata": {
            "exported_from_project_name": package.get("exported_from_project_name"),
            "snapshot_name": exported_commit.get("snapshot_name"),
            "resolution_name": exported_commit.get("resolution_name"),
            "promoted_point_name": promoted_point_name,
            "promoted_point_kind": exported_commit.get("promoted_point_kind"),
            "note": package.get("note"),
        },
        "collections": {
            "sessions": _set_diff(current_session_ids, package_session_ids),
            "branches": _set_diff(current_branch_names, [target_branch]),
            "tag_points": _set_diff(current_tag_names, package_point_names),
        },
        "compatibility": compatibility,
        "preview_items": preview_items,
        "summary": summary,
    }
