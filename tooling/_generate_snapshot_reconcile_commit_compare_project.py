
from session_model import create_session_from_text, save_session
from project_model import (
    create_workspace,
    add_session_to_workspace,
    create_tag_release_in_project,
    create_snapshot_export_in_project,
    create_snapshot_reconcile_resolution_in_project,
    create_snapshot_reconcile_commit_in_project,
    compare_snapshot_reconcile_commit_sets,
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

source_base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Compare Source Base")
source_feature = create_session_from_text("spr(seed -> source_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Compare Source Feature")
current_head = create_session_from_text("spr(seed -> current_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Compare Current Head")

save_session(source_base, "corpus/sample_compare_source_base_session.json")
save_session(source_feature, "corpus/sample_compare_source_feature_session.json")
save_session(current_head, "corpus/sample_compare_current_head_session.json")

source = create_workspace(project_name="Sample Reconcile Compare Source")
source = add_session_to_workspace(source, source_base, session_id="compare_base", file_name="sample_compare_source_base_session.json", tags=["compare"])
source = add_session_to_workspace(source, source_feature, session_id="compare_feature", file_name="sample_compare_source_feature_session.json", tags=["compare"])
source, _ = create_tag_release_in_project(source, "compare_release", "compare_feature", point_kind="release", note="compare anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "compare_release", snapshot_name="snapshot_compare_v1", note="compare snapshot")

current = create_workspace(project_name="Sample Reconcile Compare Current")
current = add_session_to_workspace(current, current_head, session_id="compare_current", file_name="sample_compare_current_head_session.json", tags=["compare"])
resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"compare_feature": {"choice": "use_snapshot"}},
    resolution_name="compare_resolution_v1",
    selected_session_ids=["compare_feature"],
    target_branch_name="main",
    activate_last_resolved=True,
)
committed1, commit_result1 = create_snapshot_reconcile_commit_in_project(
    project_index=resolved,
    snapshot_reconcile_resolution_result=resolution_result,
    commit_name="compare_commit_left",
    promote_point_name="compare_release_left",
    promote_point_kind="release",
    note="left compare commit",
)
committed2, commit_result2 = create_snapshot_reconcile_commit_in_project(
    project_index=committed1,
    snapshot_reconcile_resolution_result=resolution_result,
    commit_name="compare_commit_right",
    promote_point_name="compare_tag_right",
    promote_point_kind="tag",
    note="right compare commit",
)
compare_result = compare_snapshot_reconcile_commit_sets(committed2, "compare_commit_left", "compare_commit_right")

save_project_index(committed2, "corpus/sample_snapshot_reconcile_commit_compare_project_index.json")
Path("corpus/sample_snapshot_reconcile_commit_left_result.json").write_text(json.dumps(commit_result1, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_right_result.json").write_text(json.dumps(commit_result2, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_compare_result.json").write_text(json.dumps(compare_result, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
