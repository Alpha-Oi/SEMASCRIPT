
from pathlib import Path
import json

from session_model import create_session_from_text, save_session
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    create_snapshot_reconcile_commit_package_export_in_project,
    create_snapshot_reconcile_commit_package_import_in_project,
    save_project_index,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state(), session_name="Compare Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Compare Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state(), session_name="Compare Current Head")

save_session(source_base, "corpus/sample_package_source_base_session.json")
save_session(source_feature, "corpus/sample_package_source_feature_session.json")
save_session(current_head, "corpus/sample_package_current_head_session.json")

source = create_workspace(project_name="Sample Package Source")
source = add_session_to_workspace(source, source_base, session_id="pkg_base", file_name="sample_package_source_base_session.json", tags=["package"])
source = add_session_to_workspace(source, source_feature, session_id="pkg_feature", file_name="sample_package_source_feature_session.json", tags=["package"])
source, _ = create_tag_release_in_project(source, "pkg_release", "pkg_feature", point_kind="release", note="package anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "pkg_release", snapshot_name="snapshot_pkg_v1", note="frozen package source")

current = create_workspace(project_name="Sample Package Current")
current = add_session_to_workspace(current, current_head, session_id="pkg_current", file_name="sample_package_current_head_session.json", tags=["package"])
resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"pkg_feature": {"choice": "use_snapshot"}},
    resolution_name="pkg_resolution_v1",
    selected_session_ids=["pkg_feature"],
    target_branch_name="main",
    activate_last_resolved=True,
)
committed, commit_result = create_snapshot_reconcile_commit_in_project(
    project_index=resolved,
    snapshot_reconcile_resolution_result=resolution_result,
    commit_name="pkg_commit_v1",
    promote_point_name="pkg_commit_release",
    promote_point_kind="release",
    note="portable package",
)
packaged, package_export_result, standalone_package = create_snapshot_reconcile_commit_package_export_in_project(
    committed,
    commit_name="pkg_commit_v1",
    package_name="pkg_commit_v1_package",
    note="standalone portable outcome",
)

import_target = create_workspace(project_name="Sample Package Import Target")
import_target = add_session_to_workspace(import_target, current_head, session_id="pkg_import_current", tags=["package"])
imported, package_import_result = create_snapshot_reconcile_commit_package_import_in_project(
    current_project_index=import_target,
    package=standalone_package,
    import_name="pkg_commit_v1_import",
    target_branch_name="main",
    activate_last_imported=True,
)

save_project_index(packaged, "corpus/sample_snapshot_reconcile_commit_package_project_index.json")
save_project_index(imported, "corpus/sample_snapshot_reconcile_commit_package_imported_project_index.json")
Path("corpus/sample_snapshot_reconcile_commit_package_export_result.json").write_text(json.dumps(package_export_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_package_import_result.json").write_text(json.dumps(package_import_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_package.json").write_text(json.dumps(standalone_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
