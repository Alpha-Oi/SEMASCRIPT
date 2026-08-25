
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_preview,
    create_snapshot_reconcile_resolution_in_project,
)


def empty_state():
    return {
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    }


def main() -> None:
    total = 3
    passed = 0

    source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Base")
    source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Source Resolution Project")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "resolve_release", "feature_s", point_kind="release", note="resolve anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "resolve_release", snapshot_name="resolve_snapshot")

    current = create_workspace(project_name="Current Resolution Project")
    current = add_session_to_workspace(current, current_head, session_id="current_s")

    preview = create_snapshot_reconcile_preview(
        current_project_index=current,
        snapshot_package=snapshot_package,
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        reconcile_name="resolve_preview_v1",
    )
    ok1 = preview["summary"]["has_conflicts"] is True and preview["preview_items"][0]["status"] == "conflict_like"
    if ok1:
        passed += 1
    else:
        print("FAILED: preview conflict", preview)

    resolved, result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        decisions={"feature_s": {"choice": "custom_text", "custom_text": "spr(seed -> resolved_form)"}},
        resolution_name="resolve_v1",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    resolved_id = result["resolved_session_ids"][0]
    resolved_entry = next(item for item in resolved["sessions"] if item["session_id"] == resolved_id)
    ok2 = result["summary"]["resolved_session_count"] == 1 and resolved_entry["session"]["project"]["source_text"] == "spr(seed -> resolved_form)"
    if ok2:
        passed += 1
    else:
        print("FAILED: custom resolution", result, resolved_entry)

    ok3 = (
        resolved_entry["entry_metadata"]["commit_kind"] == "snapshot_reconcile_resolution"
        and resolved_entry["entry_metadata"]["snapshot_reconcile_resolution"]["decision_choice"] == "custom_text"
        and any(ev["event_type"] == "snapshot_reconcile_resolved" for ev in resolved["history"]["events"])
    )
    if ok3:
        passed += 1
    else:
        print("FAILED: resolution provenance/history", resolved_entry, resolved["history"])

    print(f"snapshot_conflict_resolution_manual_reconcile_decisions: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
