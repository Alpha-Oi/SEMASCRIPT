
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, create_tag_release_in_project, create_snapshot_export_in_project, create_snapshot_restore_preview
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

base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Preview Base")
feature = create_session_from_text("spr(seed -> preview_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Preview Feature")
extra = create_session_from_text("spr(seed -> preview_extra)", profile="human", decompose=True, initial_state=empty_state, session_name="Preview Extra")

save_session(base, "corpus/sample_preview_base_session.json")
save_session(feature, "corpus/sample_preview_feature_session.json")
save_session(extra, "corpus/sample_preview_extra_session.json")

project = create_workspace(project_name="Sample Snapshot Preview Source")
project = add_session_to_workspace(project, base, session_id="preview_base", file_name="sample_preview_base_session.json", tags=["preview"])
project = add_session_to_workspace(project, feature, session_id="preview_feature", file_name="sample_preview_feature_session.json", tags=["preview"])
project, _ = create_tag_release_in_project(project, "preview_release", "preview_feature", point_kind="release", note="preview anchor")
project, _, snapshot_package = create_snapshot_export_in_project(project, "preview_release", snapshot_name="snapshot_preview_v1", note="preview frozen")

current = add_session_to_workspace(project, extra, session_id="preview_extra", file_name="sample_preview_extra_session.json", tags=["preview"])
preview = create_snapshot_restore_preview(current, snapshot_package, restored_project_name="Sample Preview Restored", activate_anchor=True)

Path("corpus/sample_snapshot_restore_preview_result.json").write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_restore_preview_package.json").write_text(json.dumps(snapshot_package, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
