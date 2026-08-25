
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_restore_in_project,
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

    project = create_workspace(project_name="Restore Source Project")
    project = add_session_to_workspace(project, base, session_id="base_s", tags=["base"])
    project = add_session_to_workspace(project, feature, session_id="feature_s", tags=["feature"])
    project, _ = create_tag_release_in_project(project, tag_name="release_anchor", target_session_id="feature_s", point_kind="release", note="release")
    project, snapshot_result, snapshot_package = create_snapshot_export_in_project(project, "release_anchor", snapshot_name="snapshot_restore_source")

    restored, restore_result = create_snapshot_restore_in_project(
        snapshot_package=snapshot_package,
        restored_project_name="Restored Project",
        restore_name="restore_v1",
        activate_anchor=True,
    )
    ok1 = restore_result["restore_name"] == "restore_v1" and restored["project_name"] == "Restored Project"
    if ok1:
        passed += 1
    else:
        print("FAILED: restore result", restore_result, restored)

    ok2 = restored["active_session_id"] == "feature_s" and "snapshot_restores" in restored and "restore_v1" in restored["snapshot_restores"]
    if ok2:
        passed += 1
    else:
        print("FAILED: restored state", restored)

    ok3 = any(ev["event_type"] == "snapshot_restored" and ev["payload"]["snapshot_name"] == "snapshot_restore_source" for ev in restored["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: restore history", restored["history"])

    print(f"snapshot_import_workspace_restore: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
