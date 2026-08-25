
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, create_branch_from_session, save_project_index
from project_squash import squash_sessions_into_lineage_commit
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

base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Base")
feature1 = create_session_from_text("spr(seed -> feature_form_1)", profile="human", decompose=True, initial_state=empty_state, session_name="Feature 1")
feature2 = create_session_from_text("spr(seed -> feature_form_2)", profile="human", decompose=True, initial_state=empty_state, session_name="Feature 2")
main2 = create_session_from_text("gen(template -> instance_main)", profile="human", decompose=True, initial_state=empty_state, session_name="Main 2")

save_session(base, "corpus/sample_squash_base_session.json")
save_session(feature1, "corpus/sample_squash_feature1_session.json")
save_session(feature2, "corpus/sample_squash_feature2_session.json")
save_session(main2, "corpus/sample_squash_main2_session.json")

project = create_workspace(project_name="Sample Squash Project")
project = add_session_to_workspace(project, base, session_id="base_s", branch_name="main", file_name="sample_squash_base_session.json", tags=["squash"])
project = create_branch_from_session(project, "base_s", "feature_squash")
project = add_session_to_workspace(project, feature1, session_id="feature_1", branch_name="feature_squash", file_name="sample_squash_feature1_session.json", tags=["squash"])
project = add_session_to_workspace(project, feature2, session_id="feature_2", branch_name="feature_squash", file_name="sample_squash_feature2_session.json", tags=["squash"])
project = add_session_to_workspace(project, main2, session_id="main_2", branch_name="main", file_name="sample_squash_main2_session.json", tags=["squash"])

squashed, result = squash_sessions_into_lineage_commit(project, ["feature_1", "feature_2"], "main", session_id="squash_s", session_name="Squashed Feature Session", activate_head=True)
save_project_index(squashed, "corpus/sample_squashed_project_index.json")
Path("corpus/sample_squash_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_squash_lineage_graph.json").write_text(json.dumps(build_named_merge_lineage_graph(squashed), ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
