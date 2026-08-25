
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, create_branch_from_session, commit_merged_session_to_workspace, save_project_index
from session_merge import merge_sessions_three_way
from session_conflict_resolution import resolve_merge_result_conflicts
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

base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Branch Base")
feature = create_session_from_text("gen(template -> instance_a)", profile="human", decompose=True, initial_state=empty_state, session_name="Feature A")
main2 = create_session_from_text("gen(template -> instance_b)", profile="human", decompose=True, initial_state=empty_state, session_name="Main B")

save_session(base, "corpus/sample_branch_base_session.json")
save_session(feature, "corpus/sample_branch_feature_session.json")
save_session(main2, "corpus/sample_branch_main_session.json")

project = create_workspace(project_name="Sample Branch Lineage Project")
project = add_session_to_workspace(project, base, session_id="base_s", file_name="sample_branch_base_session.json", tags=["branching"], branch_name="main")
project = create_branch_from_session(project, "base_s", "feature_a")
project = add_session_to_workspace(project, feature, session_id="feature_s", file_name="sample_branch_feature_session.json", tags=["branching"], branch_name="feature_a")
project = add_session_to_workspace(project, main2, session_id="main_s", file_name="sample_branch_main_session.json", tags=["branching"], branch_name="main")

merge_result = merge_sessions_three_way(project, "base_s", "feature_s", "main_s")
resolved = resolve_merge_result_conflicts(merge_result, {"source_text": {"choice": "left"}})
project = commit_merged_session_to_workspace(project, resolved, session_id="merge_s", session_name="Merged Branch Session", activate=True, branch_name="main")
save_project_index(project, "corpus/sample_branching_project_index.json")

lineage = build_named_merge_lineage_graph(project)
Path("corpus/sample_named_merge_lineage_graph.json").write_text(json.dumps(lineage, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
