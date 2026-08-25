
from session_model import create_session_from_text, save_session
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_resolution_in_project,
    create_snapshot_reconcile_commit_package_import_commit_in_project,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Package Commit Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Package Commit Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Package Commit Current Head")

save_session(source_base, "corpus/sample_package_commit_source_base_session.json")
save_session(source_feature, "corpus/sample_package_commit_source_feature_session.json")
save_session(current_head, "corpus/sample_package_commit_current_head_session.json")

commit_source = create_workspace(project_name="Package Commit Source")
commit_source = add_session_to_workspace(commit_source, source_feature, session_id="pkg_src_feature", file_name="sample_package_commit_source_feature_session.json", tags=["package-commit"])
synthetic_resolution = {
    "resolution_name": "pkg_src_resolution",
    "snapshot_name": "pkg_snapshot",
    "source_point_name": "pkg_release",
    "target_branch_name": "main",
    "resolved_session_ids": ["pkg_src_feature"],
    "skipped_session_ids": [],
    "resolution_pairs": [],
}
commit_source, commit_result = create_snapshot_reconcile_commit_in_project(
    project_index=commit_source,
    snapshot_reconcile_resolution_result=synthetic_resolution,
    commit_name="pkg_src_commit",
    promote_point_name="pkg_src_release",
    promote_point_kind="release",
    note="portable source",
)
commit_source, export_result, package = create_snapshot_reconcile_commit_package_export_in_project(
    commit_source,
    commit_name="pkg_src_commit",
    package_name="pkg_src_commit_package",
    note="portable package",
)

target = create_workspace(project_name="Package Commit Target")
target = add_session_to_workspace(target, current_head, session_id="pkg_target_current", file_name="sample_package_commit_current_head_session.json", tags=["package-commit"])
target, resolution_result = create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index=target,
    package=package,
    decisions={"pkg_src_feature": {"choice": "use_package"}},
    resolution_name="pkg_import_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
target, commit_pkg_result = create_snapshot_reconcile_commit_package_import_commit_in_project(
    project_index=target,
    snapshot_reconcile_commit_package_resolution_result=resolution_result,
    commit_name="pkg_import_commit",
    promote_point_name="pkg_import_release",
    promote_point_kind="release",
    note="local promote",
)

save_project_index(target, "corpus/sample_snapshot_reconcile_commit_package_commit_project_index.json")
Path("corpus/sample_snapshot_reconcile_commit_package_commit_result.json").write_text(json.dumps(commit_pkg_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_package_commit_package.json").write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
