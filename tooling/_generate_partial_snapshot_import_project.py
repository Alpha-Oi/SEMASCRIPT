
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, create_tag_release_in_project, create_snapshot_export_in_project, create_partial_snapshot_import_in_project, save_project_index
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

base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Partial Base")
feature = create_session_from_text("spr(seed -> partial_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Partial Feature")
current_extra = create_session_from_text("spr(seed -> current_extra)", profile="human", decompose=True, initial_state=empty_state, session_name="Current Extra")

save_session(base, "corpus/sample_partial_base_session.json")
save_session(feature, "corpus/sample_partial_feature_session.json")
save_session(current_extra, "corpus/sample_partial_current_session.json")

source = create_workspace(project_name="Sample Partial Source")
source = add_session_to_workspace(source, base, session_id="partial_base", file_name="sample_partial_base_session.json", tags=["partial"])
source = add_session_to_workspace(source, feature, session_id="partial_feature", file_name="sample_partial_feature_session.json", tags=["partial"])
source, _ = create_tag_release_in_project(source, "partial_release", "partial_feature", point_kind="release", note="partial anchor")
source, _, snapshot_package = create_snapshot_export_in_project(source, "partial_release", snapshot_name="partial_snapshot_v1", note="frozen partial source")

current = create_workspace(project_name="Sample Partial Current")
current = add_session_to_workspace(current, current_extra, session_id="partial_current", file_name="sample_partial_current_session.json", tags=["partial"])

updated, result = create_partial_snapshot_import_in_project(
    current_project_index=current,
    snapshot_package=snapshot_package,
    import_name="partial_import_v1",
    selected_session_ids=["partial_feature"],
    selected_tag_point_names=["partial_release"],
    selected_snapshot_export_names=[],
    target_branch_name="main",
    activate_last_imported=True,
)

save_project_index(updated, "corpus/sample_partial_import_project_index.json")
Path("corpus/sample_partial_import_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_partial_import_snapshot_package.json").write_text(json.dumps(snapshot_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
