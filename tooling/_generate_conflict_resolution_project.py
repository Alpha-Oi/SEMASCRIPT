
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace
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

base = create_session_from_text(
    text="gen(template -> instance)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Resolve Base",
)
left = create_session_from_text(
    text="gen(template -> instance_a)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Resolve Left",
)
right = create_session_from_text(
    text="gen(template -> instance_b)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Resolve Right",
)

save_session(base, "corpus/sample_resolve_base_session.json")
save_session(left, "corpus/sample_resolve_left_session.json")
save_session(right, "corpus/sample_resolve_right_session.json")

project = create_workspace(project_name="Sample Resolve Project")
project = add_session_to_workspace(project, base, session_id="resolve_base", file_name="sample_resolve_base_session.json", tags=["resolve"])
project = add_session_to_workspace(project, left, session_id="resolve_left", file_name="sample_resolve_left_session.json", tags=["resolve"])
project = add_session_to_workspace(project, right, session_id="resolve_right", file_name="sample_resolve_right_session.json", tags=["resolve"])

merge_result = merge_sessions_three_way(project, "resolve_base", "resolve_left", "resolve_right")
Path("corpus/sample_conflicted_merge_result.json").write_text(json.dumps(merge_result, ensure_ascii=False, indent=2), encoding="utf-8")

resolved = resolve_merge_result_conflicts(merge_result, {"source_text": {"choice": "left"}})
Path("corpus/sample_resolved_merge_result.json").write_text(json.dumps(resolved, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
