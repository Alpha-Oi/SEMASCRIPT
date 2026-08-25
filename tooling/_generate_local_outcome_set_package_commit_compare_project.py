
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
    compare_portable_local_outcome_package_commits_in_project,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Compare Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Compare Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Compare Current Head")

save_session(source_base, "corpus/sample_local_package_compare_source_base_session.json")
save_session(source_feature, "corpus/sample_local_package_compare_source_feature_session.json")
save_session(current_head, "corpus/sample_local_package_compare_current_head_session.json")

source = create_workspace(project_name="Sample Local Package Compare Source")
source = add_session_to_workspace(source, source_base, session_id="compare_base", file_name="sample_local_package_compare_source_base_session.json", tags=["local-package-compare"])
source = add_session_to_workspace(source, source_feature, session_id="compare_feature", file_name="sample_local_package_compare_source_feature_session.json", tags=["local-package-compare"])
source, _ = create_tag_release_in_project(source, "compare_release", "compare_feature", point_kind="release", note="compare anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "compare_release", snapshot_name="compare_snapshot_v1", note="compare snapshot")

current = create_workspace(project_name="Sample Local Package Compare Current")
current = add_session_to_workspace(current, current_head, session_id="compare_current", file_name="sample_local_package_compare_current_head_session.json", tags=["local-package-compare"])

resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"compare_feature": {"choice": "use_snapshot"}},
    resolution_name="source_resolution",
    selected_session_ids=["compare_feature"],
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
    decisions={"compare_feature_reconcile_resolved": {"choice": "use_package"}},
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
local_committed, _, local_package = create_local_outcome_set_package_export_in_project(
    local_committed,
    "local_outcome_commit",
    package_name="local_outcome_portable_pkg",
    note="portable local outcome",
)
resolved_local_pkg, local_pkg_resolution_result = create_local_outcome_set_package_import_resolution_in_project(
    current_project_index=local_committed,
    package_data=local_package,
    decisions={"compare_feature_reconcile_resolved_pkg_import": {"choice": "use_package"}},
    resolution_name="portable_local_pkg_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
committed_local_pkg, left_commit_result = create_local_outcome_set_package_import_commit_in_project(
    project_index=resolved_local_pkg,
    local_outcome_set_package_resolution_result=local_pkg_resolution_result,
    commit_name="portable_local_pkg_commit",
    promote_point_name="portable_local_pkg_release",
    promote_point_kind="release",
    note="portable local package commit",
)
committed_local_pkg_2, right_commit_result = create_local_outcome_set_package_import_commit_in_project(
    project_index=committed_local_pkg,
    local_outcome_set_package_resolution_result=local_pkg_resolution_result,
    commit_name="portable_local_pkg_commit_2",
    promote_point_name="portable_local_pkg_release_2",
    promote_point_kind="release",
    note="portable local package commit 2",
)
compare_result = compare_portable_local_outcome_package_commits_in_project(
    committed_local_pkg_2,
    "portable_local_pkg_commit",
    "portable_local_pkg_commit_2",
)

save_project_index(committed_local_pkg_2, "corpus/sample_local_outcome_set_package_commit_compare_project_index.json")
Path("corpus/sample_local_outcome_set_package_left_commit_result.json").write_text(json.dumps(left_commit_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_local_outcome_set_package_right_commit_result.json").write_text(json.dumps(right_commit_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_local_outcome_set_package_commit_compare_result.json").write_text(json.dumps(compare_result, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
