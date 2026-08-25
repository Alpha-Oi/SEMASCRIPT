
from session_model import create_session_from_text, save_session

session = create_session_from_text(
    text="gen(template -> instance)",
    profile="human",
    decompose=True,
    initial_state={
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    },
    session_name="Sample Text Session",
)
save_session(session, "corpus/sample_text_session.json")
print("ok")
