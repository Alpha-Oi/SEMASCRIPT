
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, create_branch_from_session, save_project_index
from project_rebase import replay_branch_onto_target_lineage
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

save_session(base, "corpus/sample_rebase_base_session.json")
save_session(feature1, "corpus/sample_rebase_feature1_session.json")
save_session(feature2, "corpus/sample_rebase_feature2_session.json")
save_session(main2, "corpus/sample_rebase_main2_session.json")

project = create_workspace(project_name="Sample Branch Rebase Project")
project = add_session_to_workspace(project, base, session_id="base_s", branch_name="main", file_name="sample_rebase_base_session.json", tags=["rebase"])
project = create_branch_from_session(project, "base_s", "feature_rebase")
project = add_session_to_workspace(project, feature1, session_id="feature_1", branch_name="feature_rebase", file_name="sample_rebase_feature1_session.json", tags=["rebase"])
project = add_session_to_workspace(project, feature2, session_id="feature_2", branch_name="feature_rebase", file_name="sample_rebase_feature2_session.json", tags=["rebase"])
project = add_session_to_workspace(project, main2, session_id="main_2", branch_name="main", file_name="sample_rebase_main2_session.json", tags=["rebase"])

rebased, result = replay_branch_onto_target_lineage(project, "feature_rebase", "main", activate_head=True)
save_project_index(rebased, "corpus/sample_branch_rebased_project_index.json")
Path("corpus/sample_branch_rebase_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
Path("corpus/sample_branch_rebase_lineage_graph.json").write_text(json.dumps(build_named_merge_lineage_graph(rebased), ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
