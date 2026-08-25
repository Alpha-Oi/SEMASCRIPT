
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_preview,
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
    source_feature = create_session_from_text("spr(seed -> form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Source Feature")
    current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Head")

    source = create_workspace(project_name="Source Reconcile Preview Project")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "reconcile_release", "feature_s", point_kind="release", note="reconcile anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "reconcile_release", snapshot_name="reconcile_preview_snapshot")

    current = create_workspace(project_name="Current Reconcile Preview Project")
    current = add_session_to_workspace(current, current_head, session_id="current_s")

    preview = create_snapshot_reconcile_preview(
        current_project_index=current,
        snapshot_package=snapshot_package,
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        reconcile_name="reconcile_preview_v1",
    )

    ok1 = preview["reconcile_name"] == "reconcile_preview_v1" and preview["summary"]["selected_session_count"] == 1
    if ok1:
        passed += 1
    else:
        print("FAILED: preview identity", preview)

    item = preview["preview_items"][0]
    ok2 = item["current_head_session_id"] == "current_s" and item["conflict_like"] is True and item["status"] == "conflict_like"
    if ok2:
        passed += 1
    else:
        print("FAILED: preview conflict detection", preview)

    ok3 = preview["summary"]["conflict_like_count"] == 1 and preview["summary"]["has_conflicts"] is True
    if ok3:
        passed += 1
    else:
        print("FAILED: preview summary", preview)

    print(f"snapshot_conflict_detection_reconcile_preview: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
