
from session_model import create_session_from_text, save_session
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_resolution_in_project,
    save_project_index,
)
from pathlib import Path
import json

empty_state = {
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Package Resolution Source Base")
source_feature = create_session_from_text("spr(seed -> package_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Package Resolution Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Package Resolution Current Head")

save_session(source_base, "corpus/sample_package_resolution_source_base_session.json")
save_session(source_feature, "corpus/sample_package_resolution_source_feature_session.json")
save_session(current_head, "corpus/sample_package_resolution_current_head_session.json")

source = create_workspace(project_name="Sample Package Resolution Source")
source = add_session_to_workspace(source, source_base, session_id="pkg_base", file_name="sample_package_resolution_source_base_session.json", tags=["package-resolution"])
source = add_session_to_workspace(source, source_feature, session_id="pkg_feature", file_name="sample_package_resolution_source_feature_session.json", tags=["package-resolution"])
source, _ = create_tag_release_in_project(source, "pkg_release", "pkg_feature", point_kind="release", note="package resolution anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "pkg_release", snapshot_name="pkg_snapshot_v1", note="snapshot")
current = create_workspace(project_name="Sample Package Resolution Current")
current = add_session_to_workspace(current, current_head, session_id="pkg_current", file_name="sample_package_resolution_current_head_session.json", tags=["package-resolution"])

resolved, reconcile_resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"pkg_feature": {"choice": "use_snapshot"}},
    resolution_name="pkg_reconcile_resolution_v1",
    selected_session_ids=["pkg_feature"],
    target_branch_name="main",
    activate_last_resolved=True,
)
committed, _ = create_snapshot_reconcile_commit_in_project(
    project_index=resolved,
    snapshot_reconcile_resolution_result=reconcile_resolution_result,
    commit_name="pkg_reconcile_commit_v1",
    promote_point_name="pkg_reconcile_release_v1",
    promote_point_kind="release",
    note="commit",
)
committed, _, package = create_snapshot_reconcile_commit_package_export_in_project(
    committed,
    commit_name="pkg_reconcile_commit_v1",
    package_name="pkg_reconcile_commit_v1_pkg",
    note="portable",
)

import_target = create_workspace(project_name="Sample Package Resolution Import Target")
import_target = add_session_to_workspace(import_target, current_head, session_id="import_current", tags=["package-resolution"])
resolved_import, resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index=import_target,
    package=package,
    decisions={"pkg_feature_reconcile_resolution": {"choice": "custom_text", "custom_text": "spr(seed -> package_import_resolved_form)"}},
    resolution_name="pkg_import_resolution_v1",
    target_branch_name="main",
    activate_last_imported=True,
)

save_project_index(resolved_import, "corpus/sample_snapshot_reconcile_commit_package_resolution_project_index.json")
Path("corpus/sample_snapshot_reconcile_commit_package_resolution_result.json").write_text(json.dumps(resolution_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_package_resolution_package.json").write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
