
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, set_active_session, save_project_index
from session_diff import compare_sessions
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

left = create_session_from_text(
    text="gen(template -> instance)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Compare Left",
)
right = create_session_from_text(
    text="spr(seed -> form)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Compare Right",
)

save_session(left, "corpus/sample_compare_left_session.json")
save_session(right, "corpus/sample_compare_right_session.json")

project = create_workspace(project_name="Sample Compare Project")
project = add_session_to_workspace(project, left, session_id="compare_left", file_name="sample_compare_left_session.json", tags=["compare"])
project = add_session_to_workspace(project, right, session_id="compare_right", file_name="sample_compare_right_session.json", tags=["compare"])
project = set_active_session(project, "compare_right")
save_project_index(project, "corpus/sample_compare_project_index.json")

diff = compare_sessions(project, "compare_left", "compare_right")
Path("corpus/sample_cross_session_diff.json").write_text(json.dumps(diff, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
