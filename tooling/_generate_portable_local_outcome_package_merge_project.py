
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
    create_local_outcome_set_package_import_commit_in_project,
    compare_baseline_or_three_way_portable_local_outcomes_in_project,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Merge Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Merge Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Merge Current Head")

save_session(source_base, "corpus/sample_local_merge_source_base_session.json")
save_session(source_feature, "corpus/sample_local_merge_source_feature_session.json")
save_session(current_head, "corpus/sample_local_merge_current_head_session.json")

source = create_workspace(project_name="Sample Portable Local Merge Source")
source = add_session_to_workspace(source, source_base, session_id="merge_base", file_name="sample_local_merge_source_base_session.json", tags=["portable-local-merge"])
source = add_session_to_workspace(source, source_feature, session_id="merge_feature", file_name="sample_local_merge_source_feature_session.json", tags=["portable-local-merge"])
source, _ = create_tag_release_in_project(source, "merge_release", "merge_feature", point_kind="release", note="merge anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "merge_release", snapshot_name="merge_snapshot_v1", note="merge snapshot")

current = create_workspace(project_name="Sample Portable Local Merge Current")
current = add_session_to_workspace(current, current_head, session_id="merge_current", file_name="sample_local_merge_current_head_session.json", tags=["portable-local-merge"])

resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"merge_feature": {"choice": "use_snapshot"}},
    resolution_name="source_resolution",
    selected_session_ids=["merge_feature"],
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
    package_name="intermediate_pkg",
    note="intermediate",
)
resolved_pkg, pkg_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index=committed,
    package=intermediate_pkg,
    decisions={"merge_feature_reconcile_resolved": {"choice": "use_package"}},
    resolution_name="pkg_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
local_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
    resolved_pkg,
    pkg_resolution_result,
    commit_name="local_outcome_commit",
    promote_point_name="local_outcome_release",
    promote_point_kind="release",
    note="local outcome",
)
local_committed, _, portable_pkg = create_local_outcome_set_package_export_in_project(
    local_committed,
    "local_outcome_commit",
    package_name="portable_local_pkg",
    note="portable local",
)

base_project, base_res = create_local_outcome_set_package_import_resolution_in_project(
    current_project_index=local_committed,
    package_data=portable_pkg,
    decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "use_package"}},
    resolution_name="base_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
base_project, base_commit_result = create_local_outcome_set_package_import_commit_in_project(
    project_index=base_project,
    local_outcome_set_package_resolution_result=base_res,
    commit_name="base_commit",
    promote_point_name="base_release",
    promote_point_kind="release",
    note="base",
)

left_project, left_res = create_local_outcome_set_package_import_resolution_in_project(
    current_project_index=base_project,
    package_data=portable_pkg,
    decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> left_form)"}},
    resolution_name="left_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
left_project, left_commit_result = create_local_outcome_set_package_import_commit_in_project(
    project_index=left_project,
    local_outcome_set_package_resolution_result=left_res,
    commit_name="left_commit",
    promote_point_name="left_release",
    promote_point_kind="release",
    note="left",
)

right_project, right_res = create_local_outcome_set_package_import_resolution_in_project(
    current_project_index=left_project,
    package_data=portable_pkg,
    decisions={portable_pkg["resolved_sessions"][0]["session_id"]: {"choice": "custom_text", "custom_text": "spr(seed -> right_form)"}},
    resolution_name="right_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
right_project, right_commit_result = create_local_outcome_set_package_import_commit_in_project(
    project_index=right_project,
    local_outcome_set_package_resolution_result=right_res,
    commit_name="right_commit",
    promote_point_name="right_release",
    promote_point_kind="release",
    note="right",
)

merge_result = compare_baseline_or_three_way_portable_local_outcomes_in_project(
    right_project,
    "base_commit",
    "left_commit",
    "right_commit",
)

save_project_index(right_project, "corpus/sample_portable_local_outcome_package_merge_project_index.json")
Path("corpus/sample_portable_local_outcome_package_base_commit_result.json").write_text(json.dumps(base_commit_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_portable_local_outcome_package_left_commit_result.json").write_text(json.dumps(left_commit_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_portable_local_outcome_package_right_commit_result.json").write_text(json.dumps(right_commit_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_portable_local_outcome_package_merge_result.json").write_text(json.dumps(merge_result, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
