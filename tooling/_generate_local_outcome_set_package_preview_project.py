
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
    preview_local_outcome_set_package_before_import_in_project,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Preview Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Preview Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Local Package Preview Current Head")

save_session(source_base, "corpus/sample_local_package_preview_source_base_session.json")
save_session(source_feature, "corpus/sample_local_package_preview_source_feature_session.json")
save_session(current_head, "corpus/sample_local_package_preview_current_head_session.json")

source = create_workspace(project_name="Sample Local Package Preview Source")
source = add_session_to_workspace(source, source_base, session_id="preview_base", file_name="sample_local_package_preview_source_base_session.json", tags=["local-package-preview"])
source = add_session_to_workspace(source, source_feature, session_id="preview_feature", file_name="sample_local_package_preview_source_feature_session.json", tags=["local-package-preview"])
source, _ = create_tag_release_in_project(source, "preview_release", "preview_feature", point_kind="release", note="preview anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "preview_release", snapshot_name="preview_snapshot_v1", note="preview snapshot")

current = create_workspace(project_name="Sample Local Package Preview Current")
current = add_session_to_workspace(current, current_head, session_id="preview_current", file_name="sample_local_package_preview_current_head_session.json", tags=["local-package-preview"])

resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"preview_feature": {"choice": "use_snapshot"}},
    resolution_name="preview_resolution",
    selected_session_ids=["preview_feature"],
    target_branch_name="main",
    activate_last_resolved=True,
)
committed, _ = create_snapshot_reconcile_commit_in_project(
    project_index=resolved,
    snapshot_reconcile_resolution_result=resolution_result,
    commit_name="preview_source_commit",
    promote_point_name="preview_source_release",
    promote_point_kind="release",
    note="preview source commit",
)
committed, _, intermediate_pkg = create_snapshot_reconcile_commit_package_export_in_project(
    committed,
    "preview_source_commit",
    package_name="preview_intermediate_pkg",
    note="preview intermediate",
)
resolved_pkg, pkg_resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index=committed,
    package=intermediate_pkg,
    decisions={"preview_feature_reconcile_resolved": {"choice": "use_package"}},
    resolution_name="preview_pkg_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
local_committed, _ = create_snapshot_reconcile_commit_package_import_commit_in_project(
    resolved_pkg,
    pkg_resolution_result,
    commit_name="preview_local_outcome_commit",
    promote_point_name="preview_local_release",
    promote_point_kind="release",
    note="preview local outcome",
)
local_committed, package_export_result, package_data = create_local_outcome_set_package_export_in_project(
    local_committed,
    "preview_local_outcome_commit",
    package_name="preview_local_outcome_pkg",
    note="preview portable local package",
)

preview = preview_local_outcome_set_package_before_import_in_project(
    current_project_index=local_committed,
    package_data=package_data,
    import_name="preview_local_outcome_import",
    target_branch_name="main",
)

save_project_index(local_committed, "corpus/sample_local_outcome_set_package_preview_project_index.json")
Path("corpus/sample_local_outcome_set_package_preview_result.json").write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_local_outcome_set_package_preview_package.json").write_text(json.dumps(package_data, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
