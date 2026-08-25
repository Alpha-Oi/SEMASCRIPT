
from session_model import create_session_from_text, save_session
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Commit Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Commit Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Commit Current Head")

save_session(source_base, "corpus/sample_commit_source_base_session.json")
save_session(source_feature, "corpus/sample_commit_source_feature_session.json")
save_session(current_head, "corpus/sample_commit_current_head_session.json")

source = create_workspace(project_name="Sample Reconcile Commit Source")
source = add_session_to_workspace(source, source_base, session_id="commit_base", file_name="sample_commit_source_base_session.json", tags=["reconcile-commit"])
source = add_session_to_workspace(source, source_feature, session_id="commit_feature", file_name="sample_commit_source_feature_session.json", tags=["reconcile-commit"])
source, _ = create_tag_release_in_project(source, "commit_release", "commit_feature", point_kind="release", note="commit anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "commit_release", snapshot_name="snapshot_commit_v1", note="frozen commit source")

current = create_workspace(project_name="Sample Reconcile Commit Current")
current = add_session_to_workspace(current, current_head, session_id="commit_current", file_name="sample_commit_current_head_session.json", tags=["reconcile-commit"])
resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"commit_feature": {"choice": "use_snapshot"}},
    resolution_name="resolution_v1",
    selected_session_ids=["commit_feature"],
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

save_project_index(committed, "corpus/sample_snapshot_reconcile_commit_project_index.json")
Path("corpus/sample_snapshot_reconcile_commit_result.json").write_text(json.dumps(commit_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_package.json").write_text(json.dumps(snapshot_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
