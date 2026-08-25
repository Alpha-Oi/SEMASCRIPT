
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_in_project,
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

    source = create_workspace(project_name="Source Reconcile Project")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "reconcile_release", "feature_s", point_kind="release", note="reconcile anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "reconcile_release", snapshot_name="reconcile_snapshot")

    current = create_workspace(project_name="Current Reconcile Project")
    current = add_session_to_workspace(current, current_head, session_id="current_s")

    updated, result = create_snapshot_reconcile_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        reconcile_name="reconcile_v1",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_reconciled=True,
    )

    ok1 = result["reconcile_name"] == "reconcile_v1" and result["summary"]["reconciled_session_count"] == 1
    if ok1:
        passed += 1
    else:
        print("FAILED: reconcile result", result)

    reconciled_id = result["reconciled_session_ids"][0]
    entry = next(item for item in updated["sessions"] if item["session_id"] == reconciled_id)
    ok2 = entry["entry_metadata"]["commit_kind"] == "snapshot_reconcile" and entry["entry_metadata"]["snapshot_reconcile"]["reconciled_with_head_session_id"] == "current_s"
    if ok2:
        passed += 1
    else:
        print("FAILED: reconcile metadata", entry)

    ok3 = any(ev["event_type"] == "snapshot_reconciled" and ev["payload"]["reconciled_session_count"] == 1 for ev in updated["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: reconcile history", updated["history"])

    print(f"snapshot_merge_reconcile_imported_state: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
