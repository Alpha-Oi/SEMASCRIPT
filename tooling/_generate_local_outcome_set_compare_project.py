
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
    compare_local_outcome_sets_in_project,
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

source = create_workspace(project_name="Sample Local Outcome Compare Source")
source = add_session_to_workspace(source, source_base, session_id="compare_base", file_name="sample_compare_source_base_session.json", tags=["local-outcome-compare"])
source = add_session_to_workspace(source, source_feature, session_id="compare_feature", file_name="sample_compare_source_feature_session.json", tags=["local-outcome-compare"])
source, _ = create_tag_release_in_project(source, "compare_release", "compare_feature", point_kind="release", note="compare anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "compare_release", snapshot_name="compare_snapshot_v1", note="compare snapshot")

current = create_workspace(project_name="Sample Local Outcome Compare Current")
current = add_session_to_workspace(current, current_head, session_id="compare_current", file_name="sample_compare_current_head_session.json", tags=["local-outcome-compare"])

resolved, resolution_result = create_snapshot_reconcile_resolution_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    decisions={"compare_feature": {"choice": "use_snapshot"}},
    resolution_name="source_resolution",
    selected_session_ids=["compare_feature"],
    target_branch_name="main",
    activate_last_resolved=True,
)
committed, commit_result = create_snapshot_reconcile_commit_in_project(
    project_index=resolved,
    snapshot_reconcile_resolution_result=resolution_result,
    commit_name="source_commit",
    promote_point_name="source_release",
    promote_point_kind="release",
    note="source commit",
)
committed, package_export_result, package_data = create_snapshot_reconcile_commit_package_export_in_project(
    committed,
    "source_commit",
    package_name="compare_package_v1",
    note="portable compare package",
)

left_imported, left_resolution = create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index=committed,
    package=package_data,
    decisions={"compare_feature_reconcile_resolved": {"choice": "use_package"}},
    resolution_name="left_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
left_committed, left_commit_result = create_snapshot_reconcile_commit_package_import_commit_in_project(
    left_imported,
    left_resolution,
    commit_name="left_local_outcome",
    promote_point_name="left_local_release",
    promote_point_kind="release",
    note="left",
)

right_imported, right_resolution = create_snapshot_reconcile_commit_package_import_resolution_in_project(
    current_project_index=left_committed,
    package=package_data,
    decisions={"compare_feature_reconcile_resolved": {"choice": "custom_text", "custom_text": "spr(seed -> alt_form)"}},
    resolution_name="right_resolution",
    target_branch_name="main",
    activate_last_imported=True,
)
right_committed, right_commit_result = create_snapshot_reconcile_commit_package_import_commit_in_project(
    right_imported,
    right_resolution,
    commit_name="right_local_outcome",
    promote_point_name="right_local_release",
    promote_point_kind="release",
    note="right",
)

compare_result = compare_local_outcome_sets_in_project(
    right_committed,
    "left_local_outcome",
    "right_local_outcome",
)

save_project_index(right_committed, "corpus/sample_snapshot_reconcile_commit_local_outcome_compare_project_index.json")
Path("corpus/sample_snapshot_reconcile_commit_left_result.json").write_text(json.dumps(left_commit_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_right_result.json").write_text(json.dumps(right_commit_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_reconcile_commit_compare_result.json").write_text(json.dumps(compare_result, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
