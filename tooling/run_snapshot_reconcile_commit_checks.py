
from __future__ import annotations

from session_model import create_session_from_text
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
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

    source = create_workspace(project_name="Source Commit Project")
    source = add_session_to_workspace(source, source_base, session_id="base_s")
    source = add_session_to_workspace(source, source_feature, session_id="feature_s")
    source, _ = create_tag_release_in_project(source, "commit_release", "feature_s", point_kind="release", note="commit anchor")
    source, _, snapshot_package = create_snapshot_export_in_project(source, "commit_release", snapshot_name="commit_snapshot")

    current = create_workspace(project_name="Current Commit Project")
    current = add_session_to_workspace(current, current_head, session_id="current_s")

    resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
        current_project_index=current,
        snapshot_package=snapshot_package,
        decisions={"feature_s": {"choice": "use_snapshot"}},
        resolution_name="resolution_v1",
        selected_session_ids=["feature_s"],
        target_branch_name="main",
        activate_last_resolved=True,
    )
    committed, commit_result = create_snapshot_reconcile_commit_in_project(
        project_index=resolved,
        snapshot_reconcile_resolution_result=resolution_result,
        commit_name="resolution_set_v1",
        promote_point_name="release_resolution_v1",
        promote_point_kind="release",
        note="promoted release",
    )

    ok1 = commit_result["commit_name"] == "resolution_set_v1" and "resolution_set_v1" in committed["snapshot_reconcile_commits"]
    if ok1:
        passed += 1
    else:
        print("FAILED: reconcile commit set", commit_result, committed)

    ok2 = commit_result["summary"]["promoted"] is True and "release_resolution_v1" in committed["tag_points"]
    if ok2:
        passed += 1
    else:
        print("FAILED: promoted point", commit_result, committed.get("tag_points"))

    ok3 = any(ev["event_type"] == "snapshot_reconcile_committed" and ev["payload"]["commit_name"] == "resolution_set_v1" for ev in committed["history"]["events"])
    if ok3:
        passed += 1
    else:
        print("FAILED: commit history", committed["history"])

    print(f"snapshot_reconcile_commit_promote_resolution_set: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
