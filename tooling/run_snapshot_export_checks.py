
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace, create_tag_release_in_project, create_snapshot_export_in_project


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

    project = create_workspace(project_name="Snapshot Project")
    project = add_session_to_workspace(project, base, session_id="base_s", tags=["base"])
    project = add_session_to_workspace(project, feature, session_id="feature_s", tags=["feature"])
    project, tag_result = create_tag_release_in_project(project, tag_name="v0_tag", target_session_id="feature_s", point_kind="tag", note="checkpoint")

    snap_project, snap_result, snap_package = create_snapshot_export_in_project(
        project,
        source_point_name="v0_tag",
        snapshot_name="snapshot_v0",
        note="frozen export",
    )
    ok1 = snap_result["snapshot_name"] == "snapshot_v0" and snap_package["immutability"]["frozen"] is True
    if ok1:
        passed += 1
    else:
        print("FAILED: snapshot result", snap_result, snap_package)

    ok2 = "snapshot_exports" in snap_project and "snapshot_v0" in snap_project["snapshot_exports"] and "snapshot_exports" not in snap_package["export_state"]["project_index_frozen"]
    if ok2:
        passed += 1
    else:
        print("FAILED: frozen project export", snap_project, snap_package)

    ok3 = any(ev["event_type"] == "snapshot_exported" and ev["payload"]["source_point_name"] == "v0_tag" for ev in snap_project["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: snapshot history", snap_project["history"])

    print(f"snapshot_immutable_workspace_export: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
