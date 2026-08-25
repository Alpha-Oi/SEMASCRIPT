
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, commit_merged_session_to_workspace, save_project_index
from session_merge import merge_sessions_three_way
from session_conflict_resolution import resolve_merge_result_conflicts
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

base = create_session_from_text("gen(template -> instance)", profile="human", decompose=True, initial_state=empty_state, session_name="Commit Base")
left = create_session_from_text("gen(template -> instance_a)", profile="human", decompose=True, initial_state=empty_state, session_name="Commit Left")
right = create_session_from_text("gen(template -> instance_b)", profile="human", decompose=True, initial_state=empty_state, session_name="Commit Right")

save_session(base, "corpus/sample_commit_base_session.json")
save_session(left, "corpus/sample_commit_left_session.json")
save_session(right, "corpus/sample_commit_right_session.json")

project = create_workspace(project_name="Sample Commit Project")
project = add_session_to_workspace(project, base, session_id="commit_base", file_name="sample_commit_base_session.json", tags=["commit"])
project = add_session_to_workspace(project, left, session_id="commit_left", file_name="sample_commit_left_session.json", tags=["commit"])
project = add_session_to_workspace(project, right, session_id="commit_right", file_name="sample_commit_right_session.json", tags=["commit"])

merge_result = merge_sessions_three_way(project, "commit_base", "commit_left", "commit_right")
resolved = resolve_merge_result_conflicts(merge_result, {"source_text": {"choice": "left"}})
committed = commit_merged_session_to_workspace(project, resolved, session_id="commit_merged", session_name="Commit Merged Session", activate=True, tags=["merge-commit"])
save_project_index(committed, "corpus/sample_merge_commit_project_index.json")
Path("corpus/sample_merge_commit_result.json").write_text(json.dumps(committed, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
