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
    create_snapshot_reconcile_commit_package_import_commit_in_project,
    create_local_outcome_set_package_export_in_project,
    create_local_outcome_set_package_import_resolution_in_project,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Resolution Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Resolution Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Resolution Current Head")

save_session(source_base, "corpus/sample_local_package_resolution_source_base_session.json")
save_session(source_feature, "corpus/sample_local_package_resolution_source_feature_session.json")
save_session(current_head, "corpus/sample_local_package_resolution_current_head_session.json")

source = create_workspace(project_name="Sample Local Package Resolution Source")
source = add_session_to_workspace(source, source_base, session_id="resolve_base", file_name="sample_local_package_resolution_source_base_session.json", tags=["local-package-resolution"])
source = add_session_to_workspace(source, source_feature, session_id="resolve_feature", file_name="sample_local_package_resolution_source_feature_session.json", tags=["local-package-resolution"])
source, _ = create_tag_release_in_project(source, "resolve_release", "resolve_feature", point_kind="release", note="resolve anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "resolve_release", snapshot_name="resolve_snapshot_v1", note="resolve snapshot")

current = create_workspace(project_name="Sample Local Package Resolution Current")
current = add_session_to_workspace(current, current_head, session_id="resolve_current", file_name="sample_local_package_resolution_current_head_session.json", tags=["local-package-resolution"])

resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"resolve_feature": {"choice": "use_snapshot"}},
    resolution_name="source_resolution",
    selected_session_ids=["resolve_feature"],
    target_branch_name="main",
    activate_last_resolved=True,
)
committed, _ = create_snapshot_reconcile_commit_in_project(
    project_index=resolved,
    snapshot_reconcile_resolution_result=resolution_result,
    commit_name="source_commit",
    promote_point_name="source_release",
    promote_point_kind="release",
    note="source commit",
)
committed, _, intermediate_pkg = create_snapshot_reconcile_commit_package_export_in_project(
    committed,
    "source_commit",
    package_name="resolve_intermediate_pkg",
    note="intermediate",
)
resolved_pkg, pkg_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index=committed,
    package=intermediate_pkg,
    decisions={"resolve_feature_reconcile_resolved": {"choice": "use_package"}},
    resolution_name="pkg_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
local_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
    resolved_pkg,
    pkg_resolution_result,
    commit_name="local_outcome_commit",
    promote_point_name="local_release",
    promote_point_kind="release",
    note="local outcome",
)
local_committed, _, local_package = create_local_outcome_set_package_export_in_project(
    local_committed,
    "local_outcome_commit",
    package_name="local_outcome_pkg_v1",
    note="portable local outcome package",
)
resolution_target = add_session_to_workspace(create_workspace(project_name="Local Package Resolution Target"), current_head, session_id="target_current", tags=["local-package-resolution"])

resolution_project, resolution_result = create_local_outcome_set_package_import_resolution_in_project(
    current_project_index=resolution_target,
    package_data=local_package,
    decisions={local_package["resolved_sessions"][0]["session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> resolved_form)"}},
    resolution_name="local_pkg_resolution_v1",
    target_branch_name="main",
    activate_last_imported=True,
)

save_project_index(resolution_project, "corpus/sample_local_outcome_set_package_resolution_project_index.json")
Path("corpus/sample_local_outcome_set_package_resolution_result.json").write_text(json.dumps(resolution_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_local_outcome_set_package_resolution_package.json").write_text(json.dumps(local_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
