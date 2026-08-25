
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, create_tag_release_in_project, save_project_index
from project_branching import build_named_merge_lineage_graph
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
feature = create_session_from_text("spr(seed -> feature_form)", profile="human", decompose=True, initial_state=empty_state, session_name="Tag Feature")

save_session(base, "corpus/sample_tag_base_session.json")
save_session(feature, "corpus/sample_tag_feature_session.json")

project = create_workspace(project_name="Sample Tag Release Project")
project = add_session_to_workspace(project, base, session_id="base_s", branch_name="main", file_name="sample_tag_base_session.json", tags=["tag"])
project = add_session_to_workspace(project, feature, session_id="feature_s", branch_name="main", file_name="sample_tag_feature_session.json", tags=["tag"])

project, result = create_tag_release_in_project(project, "v0.2.0", "feature_s", point_kind="release", note="Sample release point")
save_project_index(project, "corpus/sample_tag_release_project_index.json")
Path("corpus/sample_tag_release_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_tag_release_lineage_graph.json").write_text(json.dumps(build_named_merge_lineage_graph(project), ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
