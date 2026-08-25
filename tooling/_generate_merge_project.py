
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace
from session_merge import merge_sessions_three_way
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
    session_name="Merge Base",
)
left = create_session_from_text(
    text="gen(template -> instance_a)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Merge Left",
)
right = create_session_from_text(
    text="gen(template -> instance_b)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Merge Right",
)

save_session(base, "corpus/sample_merge_base_session.json")
save_session(left, "corpus/sample_merge_left_session.json")
save_session(right, "corpus/sample_merge_right_session.json")

project = create_workspace(project_name="Sample Merge Project")
project = add_session_to_workspace(project, base, session_id="merge_base", file_name="sample_merge_base_session.json", tags=["merge"])
project = add_session_to_workspace(project, left, session_id="merge_left", file_name="sample_merge_left_session.json", tags=["merge"])
project = add_session_to_workspace(project, right, session_id="merge_right", file_name="sample_merge_right_session.json", tags=["merge"])

merge_result = merge_sessions_three_way(project, "merge_base", "merge_left", "merge_right")
Path("corpus/sample_three_way_merge_result.json").write_text(json.dumps(merge_result, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
