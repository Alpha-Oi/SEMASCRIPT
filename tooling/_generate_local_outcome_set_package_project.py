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
    create_local_outcome_set_package_import_in_project,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Current Head")

save_session(source_base, "corpus/sample_local_package_source_base_session.json")
save_session(source_feature, "corpus/sample_local_package_source_feature_session.json")
save_session(current_head, "corpus/sample_local_package_current_head_session.json")

source = create_workspace(project_name="Sample Local Package Source")
source = add_session_to_workspace(source, source_base, session_id="lp_base", file_name="sample_local_package_source_base_session.json", tags=["local-package"])
source = add_session_to_workspace(source, source_feature, session_id="lp_feature", file_name="sample_local_package_source_feature_session.json", tags=["local-package"])
source, _ = create_tag_release_in_project(source, "lp_release", "lp_feature", point_kind="release", note="local package anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "lp_release", snapshot_name="lp_snapshot_v1", note="local package snapshot")

current = create_workspace(project_name="Sample Local Package Current")
current = add_session_to_workspace(current, current_head, session_id="lp_current", file_name="sample_local_package_current_head_session.json", tags=["local-package"])

resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"lp_feature": {"choice": "use_snapshot"}},
    resolution_name="lp_resolution",
    selected_session_ids=["lp_feature"],
    target_branch_name="main",
    activate_last_resolved=True,
)
committed, commit_result = create_snapshot_reconcile_commit_in_project(
    project_index=resolved,
    snapshot_reconcile_resolution_result=resolution_result,
    commit_name="lp_source_commit",
    promote_point_name="lp_source_release",
    promote_point_kind="release",
    note="local package source commit",
)
committed, pkg_result, pkg = create_snapshot_reconcile_commit_package_export_in_project(
    committed,
    "lp_source_commit",
    package_name="lp_intermediate_pkg",
    note="intermediate",
)
resolved_pkg, pkg_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index=committed,
    package=pkg,
    decisions={"lp_feature_reconcile_resolved": {"choice": "use_package"}},
    resolution_name="lp_pkg_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
local_committed, local_commit_result = create_snapshot_reconcile_commit_package_import_commit_in_project(
    resolved_pkg,
    pkg_resolution_result,
    commit_name="lp_local_outcome",
    promote_point_name="lp_local_release",
    promote_point_kind="release",
    note="local outcome",
)
local_packaged, local_package_result, local_package = create_local_outcome_set_package_export_in_project(
    local_committed,
    "lp_local_outcome",
    package_name="lp_local_portable",
    note="portable local outcome",
)

import_target = create_workspace(project_name="Sample Local Package Import Target")
import_target = add_session_to_workspace(import_target, current_head, session_id="lp_import_current", tags=["local-package"])
imported, import_result = create_local_outcome_set_package_import_in_project(
    current_project_index=import_target,
    package=local_package,
    import_name="lp_local_portable_import",
    target_branch_name="main",
    activate_last_imported=True,
)

save_project_index(imported, "corpus/sample_local_outcome_set_package_imported_project_index.json")
Path("corpus/sample_local_outcome_set_package_export_result.json").write_text(json.dumps(local_package_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_local_outcome_set_package_import_result.json").write_text(json.dumps(import_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_local_outcome_set_package.json").write_text(json.dumps(local_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
