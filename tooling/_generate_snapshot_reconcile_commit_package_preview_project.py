
from pathlib import Path
import json
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_preview_in_project,
)
from session_model import create_session_from_text, save_session

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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Package Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Package Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Package Current Head")

save_session(source_base, "corpus/sample_package_preview_source_base_session.json")
save_session(source_feature, "corpus/sample_package_preview_source_feature_session.json")
save_session(current_head, "corpus/sample_package_preview_current_head_session.json")

source = create_workspace(project_name="Sample Package Preview Source")
source = add_session_to_workspace(source, source_base, session_id="pkg_base", file_name="sample_package_preview_source_base_session.json", tags=["package-preview"])
source = add_session_to_workspace(source, source_feature, session_id="pkg_feature", file_name="sample_package_preview_source_feature_session.json", tags=["package-preview"])
source, _ = create_tag_release_in_project(source, "pkg_release", "pkg_feature", point_kind="release", note="pkg anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "pkg_release", snapshot_name="pkg_snapshot")

resolved_workspace, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=create_workspace(project_name="Resolve Current"),
    snapshot_package=snapshot_package,
    decisions={"pkg_feature": {"choice": "use_snapshot"}},
    resolution_name="pkg_resolution",
    selected_session_ids=["pkg_feature"],
    target_branch_name="main",
    activate_last_resolved=True,
)
resolved_workspace, _ = create_snapshot_reconcile_commit_in_project(
    resolved_workspace,
    resolution_result,
    commit_name="pkg_commit",
    promote_point_name="pkg_promoted",
    promote_point_kind="release",
    note="promoted",
)
resolved_workspace, _, outcome_package = create_snapshot_reconcile_commit_package_export_in_project(
    resolved_workspace,
    commit_name="pkg_commit",
    package_name="pkg_outcome",
    note="portable",
)

current = create_workspace(project_name="Sample Package Preview Current")
current = add_session_to_workspace(current, current_head, session_id="pkg_current", file_name="sample_package_preview_current_head_session.json", tags=["package-preview"])
preview = create_snapshot_reconcile_commit_package_import_preview_in_project(
    current_project_index=current,
    package=outcome_package,
    import_name="pkg_import_preview",
    target_branch_name="main",
    activate_last_imported=True,
)

Path("corpus/sample_snapshot_reconcile_commit_package_preview_result.json").write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_package_preview_package.json").write_text(json.dumps(outcome_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
