
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, create_tag_release_in_project, create_snapshot_export_in_project, create_snapshot_restore_in_project, save_project_index
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

base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Restore Base")
feature = create_session_from_text("spr(seed -> restore_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Restore Feature")

save_session(base, "corpus/sample_restore_base_session.json")
save_session(feature, "corpus/sample_restore_feature_session.json")

project = create_workspace(project_name="Sample Snapshot Restore Source")
project = add_session_to_workspace(project, base, session_id="restore_base", file_name="sample_restore_base_session.json", tags=["restore"])
project = add_session_to_workspace(project, feature, session_id="restore_feature", file_name="sample_restore_feature_session.json", tags=["restore"])
project, tag_result = create_tag_release_in_project(project, "restore_release", "restore_feature", point_kind="release", note="restore anchor")
project, snapshot_result, snapshot_package = create_snapshot_export_in_project(project, "restore_release", snapshot_name="snapshot_restore_v1", note="frozen restore source")

restored, restore_result = create_snapshot_restore_in_project(snapshot_package, restored_project_name="Sample Restored Project", restore_name="restore_v1", activate_anchor=True)

save_project_index(restored, "corpus/sample_snapshot_restored_project_index.json")
Path("corpus/sample_snapshot_restore_result.json").write_text(json.dumps(restore_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_restore_package.json").write_text(json.dumps(snapshot_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
