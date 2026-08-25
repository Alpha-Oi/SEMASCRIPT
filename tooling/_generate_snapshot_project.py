
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, create_tag_release_in_project, create_snapshot_export_in_project, save_project_index
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

base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Tag Base")
feature = create_session_from_text("spr(seed -> release_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Tag Feature")

save_session(base, "corpus/sample_tag_base_session.json")
save_session(feature, "corpus/sample_tag_feature_session.json")

project = create_workspace(project_name="Sample Tag Release Project")
project = add_session_to_workspace(project, base, session_id="tag_base", file_name="sample_tag_base_session.json", tags=["snapshot"])
project = add_session_to_workspace(project, feature, session_id="tag_feature", file_name="sample_tag_feature_session.json", tags=["snapshot"])
project, tag_result = create_tag_release_in_project(project, "release_v1", "tag_feature", point_kind="release", note="release anchor")
project, snapshot_result, snapshot_package = create_snapshot_export_in_project(project, "release_v1", snapshot_name="snapshot_release_v1", note="immutable export")

save_project_index(project, "corpus/sample_tag_release_project_index.json")
Path("corpus/sample_tag_release_result.json").write_text(json.dumps(tag_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_export_result.json").write_text(json.dumps(snapshot_result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_snapshot_export_package.json").write_text(json.dumps(snapshot_package, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_tag_release_lineage_graph.json").write_text(json.dumps(snapshot_package["export_state"]["lineage_graph"], ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
