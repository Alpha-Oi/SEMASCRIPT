
from session_model import create_session_from_text, save_session
from project_model import create_workspace, add_session_to_workspace, set_active_session, save_project_index

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

a = create_session_from_text(
    text="gen(template -> instance)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Session A",
)
b = create_session_from_text(
    text="spr(seed -> form)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Session B",
)

save_session(a, "corpus/sample_timeline_session_a.json")
save_session(b, "corpus/sample_timeline_session_b.json")

project = create_workspace(project_name="Sample Timeline Project")
project = add_session_to_workspace(project, a, session_id="session_a", file_name="sample_timeline_session_a.json", tags=["timeline"])
project = add_session_to_workspace(project, b, session_id="session_b", file_name="sample_timeline_session_b.json", tags=["timeline"])
project = set_active_session(project, "session_b")
save_project_index(project, "corpus/sample_timeline_project_index.json")
print("ok")
