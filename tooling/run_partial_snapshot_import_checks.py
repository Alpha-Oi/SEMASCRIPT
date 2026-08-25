
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_partial_snapshot_import_in_project,
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

    base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Base")
    feature = create_session_from_text("spr(seed -> form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Feature")
    current_extra = create_session_from_text("spr(seed -> current_extra)", profile="human", decompose=True, initial_state=empty_state(), session_name="Current Extra")

    source = create_workspace(project_name="Source Project")
    source = add_session_to_workspace(source, base, session_id="base_s", tags=["base"])
    source = add_session_to_workspace(source, feature, session_id="feature_s", tags=["feature"])
    source, _ = create_tag_release_in_project(source, tag_name="release_anchor", target_session_id="feature_s", point_kind="release", note="release")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "release_anchor", snapshot_name="partial_source_snapshot")

    current = create_workspace(project_name="Current Project")
    current = add_session_to_workspace(current, current_extra, session_id="current_s", tags=["current"])

    updated, result = create_partial_snapshot_import_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        import_name="partial_import_v1",
        selected_session_ids=["feature_s"],
        selected_tag_point_names=["release_anchor"],
        selected_snapshot_export_names=[],
        target_branch_name="main",
        activate_last_imported=True,
    )

    ok1 = result["import_name"] == "partial_import_v1" and result["summary"]["imported_session_count"] == 1
    if ok1:
        passed += 1
    else:
        print("FAILED: partial import result", result)

    imported_id = result["imported_session_ids"][0]
    ok2 = imported_id != "feature_s" and any(item["session_id"] == imported_id for item in updated["sessions"]) and updated["active_session_id"] == imported_id
    if ok2:
        passed += 1
    else:
        print("FAILED: imported session insertion", updated)

    ok3 = any(ev["event_type"] == "snapshot_partial_imported" for ev in updated["history"]["events"]) and result["imported_tag_point_names"] and "partial_import_v1" in updated["partial_snapshot_imports"]
    if ok3:
        passed += 1
    else:
        print("FAILED: partial import history/registry", updated)

    print(f"partial_snapshot_restore_selective_workspace_import: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
