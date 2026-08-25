
from __future__ import annotations

from copy import deepcopy

from session_model import create_session_from_text
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
from project_local_outcome_set_package_preview import preview_portable_local_outcome_package_before_import
from workspace_timeline import ensure_workspace_history, append_history_event


class ProjectLocalOutcomeSetPackageResolutionError(Exception):
    """Raised when portable local outcome package manual import resolution is invalid."""


def ensure_local_outcome_set_package_resolution_state(project_index: dict) -> dict:
    out = deepcopy(project_index)
    out.setdefault("local_outcome_set_package_resolutions", {})
    return out


def _normalize(project_index: dict) -> dict:
    return ensure_local_outcome_set_package_resolution_state(
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


def local_outcome_set_package_resolution_summary(project_index: dict) -> list[dict]:
    project_index = _normalize(project_index)
    out = []
    for resolution_name, entry in (project_index.get("local_outcome_set_package_resolutions") or {}).items():
        out.append({
            "resolution_name": resolution_name,
            "package_name": entry.get("package_name"),
            "source_commit_name": entry.get("source_commit_name"),
            "target_branch_name": entry.get("target_branch_name"),
            "resolved_session_count": len(entry.get("resolved_session_ids") or []),
            "skipped_session_count": len(entry.get("skipped_session_ids") or []),
            "conflict_like_count": entry.get("conflict_like_count", 0),
            "decision_counts": deepcopy(entry.get("decision_counts") or {}),
        })
    out.sort(key=lambda x: x["resolution_name"])
    return out


def _unique_name(existing: set[str], base: str, suffix: str) -> str:
    candidate = f"{base}{suffix}"
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    n = 2
    while f"{candidate}_{n}" in existing:
        n += 1
    resolved = f"{candidate}_{n}"
    existing.add(resolved)
    return resolved


def _build_custom_text_session(base_entry: dict, custom_text: str) -> tuple[dict, str, str, str]:
    profile = base_entry.get("profile") or "core"
    source_mode = base_entry.get("source_mode") or base_entry.get("session", {}).get("project", {}).get("source_mode") or "text"
    if source_mode != "text":
        raise ProjectLocalOutcomeSetPackageResolutionError("custom_text is supported only for text sessions in v0.1")
    initial_state = deepcopy(base_entry.get("session", {}).get("project", {}).get("initial_state"))
    session_name = base_entry.get("session_name") or "Resolved Package Session"
    session = create_session_from_text(
        text=custom_text,
        profile=profile,
        decompose=True,
        initial_state=initial_state,
        session_name=session_name,
    )
    return session, profile, "text", session_name


def resolve_portable_local_outcome_package_import_with_decisions(
    current_project_index: dict,
    package_data: dict,
    decisions: dict[str, dict] | None = None,
    resolution_name: str | None = None,
    target_branch_name: str | None = None,
    activate_last_imported: bool = True,
) -> tuple[dict, dict]:
    current_project_index = _normalize(current_project_index)
    if not isinstance(package_data, dict):
        raise ProjectLocalOutcomeSetPackageResolutionError("package_data must be an object")
    if package_data.get("local_outcome_set_package_version") != "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_v0.1":
        raise ProjectLocalOutcomeSetPackageResolutionError("Unsupported or missing local_outcome_set_package_version")

    preview = preview_portable_local_outcome_package_before_import(
        current_project_index=current_project_index,
        package_data=package_data,
        import_name=resolution_name or None,
        target_branch_name=target_branch_name,
    )
    exported_commit = deepcopy(package_data.get("exported_local_outcome_commit") or {})
    resolved_sessions = list(package_data.get("resolved_sessions") or [])
    if not exported_commit or not resolved_sessions:
        raise ProjectLocalOutcomeSetPackageResolutionError("Package is missing exported_local_outcome_commit or resolved_sessions")

    target_branch = preview["import_target"]["target_branch_name"]
    resolved_resolution_name = (resolution_name or f"{package_data.get('package_name', 'local_package')}_resolution").strip()
    if not resolved_resolution_name:
        raise ProjectLocalOutcomeSetPackageResolutionError("resolution_name is required")
    if resolved_resolution_name in (current_project_index.get("local_outcome_set_package_resolutions") or {}):
        raise ProjectLocalOutcomeSetPackageResolutionError(f"Local outcome package resolution already exists: {resolved_resolution_name}")

    decisions = deepcopy(decisions or {})
    out = deepcopy(current_project_index)
    if target_branch not in out.get("branches", {}):
        out["branches"][target_branch] = {
            "branch_name": target_branch,
            "root_session_id": None,
            "head_session_id": None,
            "manual_head_session_id": None,
            "color_index": len(out.get("branches", {})),
        }

    existing_session_ids = {item["session_id"] for item in out.get("sessions", [])}
    previous_parent = out["branches"].get(target_branch, {}).get("head_session_id")

    resolved_session_ids = []
    skipped_session_ids = []
    resolution_pairs = []
    decision_counts = {"use_package": 0, "use_current": 0, "skip": 0, "custom_text": 0}
    conflict_like_count = 0
    conflict_resolved_count = 0

    packaged_by_id = {item.get("session_id"): item for item in resolved_sessions}

    for idx, preview_item in enumerate(preview.get("preview_items") or [], start=1):
        original_session_id = preview_item["original_session_id"]
        packaged = deepcopy(packaged_by_id.get(original_session_id) or {})
        if not packaged:
            raise ProjectLocalOutcomeSetPackageResolutionError(f"Packaged session not found: {original_session_id}")

        current_head_entry = next((item for item in out.get("sessions", []) if item["session_id"] == previous_parent), None)
        decision = decisions.get(original_session_id, {}) or {}
        choice = (decision.get("choice") or "use_package").strip()
        if choice not in {"use_package", "use_current", "skip", "custom_text"}:
            raise ProjectLocalOutcomeSetPackageResolutionError(f"Unsupported decision choice: {choice}")

        if preview_item.get("conflict_like"):
            conflict_like_count += 1

        if choice == "skip":
            skipped_session_ids.append(original_session_id)
            decision_counts["skip"] += 1
            resolution_pairs.append({
                "original_session_id": original_session_id,
                "resolved_session_id": None,
                "resolved_with_head_session_id": previous_parent,
                "decision_choice": "skip",
                "preview_status": preview_item.get("status"),
                "conflict_like": preview_item.get("conflict_like", False),
            })
            continue

        if choice == "use_package":
            session_copy = deepcopy(packaged.get("session", {}))
            profile = packaged.get("profile")
            source_mode = packaged.get("source_mode")
            session_name = packaged.get("session_name")
            decision_counts["use_package"] += 1
        elif choice == "use_current":
            if not current_head_entry:
                raise ProjectLocalOutcomeSetPackageResolutionError(
                    f"use_current requires a current head for packaged session {original_session_id}"
                )
            session_copy = deepcopy(current_head_entry.get("session", {}))
            profile = current_head_entry.get("profile")
            source_mode = current_head_entry.get("source_mode")
            session_name = current_head_entry.get("session_name")
            decision_counts["use_current"] += 1
        else:
            custom_text = (decision.get("custom_text") or "").strip()
            if not custom_text:
                raise ProjectLocalOutcomeSetPackageResolutionError(
                    f"custom_text decision requires custom_text for packaged session {original_session_id}"
                )
            base_entry = current_head_entry if current_head_entry else packaged
            session_copy, profile, source_mode, session_name = _build_custom_text_session(base_entry, custom_text)
            decision_counts["custom_text"] += 1

        if preview_item.get("conflict_like"):
            conflict_resolved_count += 1

        new_session_id = _unique_name(existing_session_ids, original_session_id, "_localpkg_resolved")
        entry_metadata = deepcopy(packaged.get("entry_metadata", {}))
        entry_metadata["commit_kind"] = "local_outcome_set_package_import_resolution"
        entry_metadata["local_outcome_set_package_import_resolution"] = {
            "resolution_name": resolved_resolution_name,
            "package_name": package_data.get("package_name"),
            "source_commit_name": package_data.get("commit_name"),
            "original_session_id": original_session_id,
            "target_branch_name": target_branch,
            "resolved_with_head_session_id": previous_parent,
            "resolution_index": idx,
            "decision_choice": choice,
            "preview_status": preview_item.get("status"),
            "conflict_like": preview_item.get("conflict_like", False),
            "same_profile_as_compare": preview_item.get("same_profile_as_compare", False),
            "same_source_mode_as_compare": preview_item.get("same_source_mode_as_compare", False),
            "same_source_text_as_compare": preview_item.get("same_source_text_as_compare", False),
        }
        if choice == "custom_text":
            entry_metadata["local_outcome_set_package_import_resolution"]["custom_text"] = (decision.get("custom_text") or "").strip()
        entry_metadata["branching"] = {
            "branch_name": target_branch,
            "parent_session_ids": [previous_parent] if previous_parent else [],
            "lineage_kind": "local_outcome_set_package_import_resolution",
        }
        entry = {
            "session_id": new_session_id,
            "session_name": session_name,
            "profile": profile,
            "source_mode": source_mode,
            "file_name": None,
            "tags": list(dict.fromkeys(list(packaged.get("tags", [])) + ["local-outcome-set-package-resolution"])),
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
        resolution_pairs.append({
            "original_session_id": original_session_id,
            "resolved_session_id": new_session_id,
            "resolved_with_head_session_id": entry_metadata["local_outcome_set_package_import_resolution"]["resolved_with_head_session_id"],
            "decision_choice": choice,
            "preview_status": preview_item.get("status"),
            "conflict_like": preview_item.get("conflict_like", False),
        })

    if activate_last_imported and resolved_session_ids:
        out["active_session_id"] = resolved_session_ids[-1]
        out["active_branch_name"] = target_branch

    out.setdefault("local_outcome_set_package_resolutions", {})[resolved_resolution_name] = {
        "resolution_name": resolved_resolution_name,
        "package_name": package_data.get("package_name"),
        "source_commit_name": package_data.get("commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "resolution_pairs": resolution_pairs,
        "decision_counts": decision_counts,
        "conflict_like_count": conflict_like_count,
        "conflict_resolved_count": conflict_resolved_count,
    }

    history_session_id = resolved_session_ids[-1] if resolved_session_ids else previous_parent
    history_session_name = next((item.get("session_name") for item in out.get("sessions", []) if item["session_id"] == history_session_id), None)
    out = append_history_event(
        out,
        "local_outcome_set_package_import_resolved",
        f"Local outcome set package import resolved: {resolved_resolution_name}",
        session_id=history_session_id,
        session_name=history_session_name,
        payload={
            "resolution_name": resolved_resolution_name,
            "package_name": package_data.get("package_name"),
            "source_commit_name": package_data.get("commit_name"),
            "target_branch_name": target_branch,
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
        },
    )

    result = {
        "local_outcome_set_package_resolution_version": "SEMASCRIPT_LOCAL_PROMOTED_RESOLUTION_PACKAGE_IMPORT_RESOLUTION_v0.1",
        "resolution_name": resolved_resolution_name,
        "package_name": package_data.get("package_name"),
        "source_commit_name": package_data.get("commit_name"),
        "target_branch_name": target_branch,
        "resolved_session_ids": resolved_session_ids,
        "skipped_session_ids": skipped_session_ids,
        "resolution_pairs": resolution_pairs,
        "summary": {
            "resolved_session_count": len(resolved_session_ids),
            "skipped_session_count": len(skipped_session_ids),
            "conflict_like_count": conflict_like_count,
            "conflict_resolved_count": conflict_resolved_count,
            "decision_counts": decision_counts,
            "active_session_id": out.get("active_session_id"),
            "active_branch_name": out.get("active_branch_name"),
        },
    }
    return _normalize(out), result
