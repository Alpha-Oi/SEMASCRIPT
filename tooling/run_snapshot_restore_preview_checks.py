
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_restore_preview,
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
    extra = create_session_from_text("spr(seed -> extra)", profile="human", decompose=True, initial_state=empty_state(), session_name="Extra")

    project = create_workspace(project_name="Preview Project")
    project = add_session_to_workspace(project, base, session_id="base_s")
    project = add_session_to_workspace(project, feature, session_id="feature_s")
    project, _ = create_tag_release_in_project(project, tag_name="release_anchor", target_session_id="feature_s", point_kind="release", note="release")
    project, _, snapshot_package = create_snapshot_export_in_project(project, "release_anchor", snapshot_name="preview_snapshot")

    current = add_session_to_workspace(project, extra, session_id="extra_s")
    preview = create_snapshot_restore_preview(
        current_project_index=current,
        snapshot_package=snapshot_package,
        restored_project_name="Preview Restored",
        activate_anchor=True,
    )

    ok1 = preview["snapshot_name"] == "preview_snapshot" and preview["restore_target"]["would_activate_session_id"] == "feature_s"
    if ok1:
        passed += 1
    else:
        print("FAILED: preview identity", preview)

    ok2 = "extra_s" in preview["collections"]["sessions"]["current_only"] and preview["summary"]["changed"] is True
    if ok2:
        passed += 1
    else:
        print("FAILED: session diff", preview)

    ok3 = preview["restore_target"]["restored_project_name"] == "Preview Restored" and preview["summary"]["project_name_changed"] is True
    if ok3:
        passed += 1
    else:
        print("FAILED: restore target name diff", preview)

    print(f"snapshot_diff_restore_preview: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
