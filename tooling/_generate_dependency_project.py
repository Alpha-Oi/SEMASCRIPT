
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

producer = create_session_from_text(
    text="gen(template -> instance)",
    profile="human",
    decompose=True,
    initial_state=empty_state,
    session_name="Producer Session",
)
consumer = create_session_from_text(
    text="[EXEC:TRANSFER <src=[ENT:INSTANCE]; dst=[ENT:STORE]; obj=[ENT:RESOURCE]>]",
    profile="exec",
    decompose=True,
    initial_state={
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {"INSTANCE": {"RESOURCE": 2}, "STORE": {"RESOURCE": 0}},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    },
    session_name="Consumer Session",
)

save_session(producer, "corpus/sample_navigation_producer_session.json")
save_session(consumer, "corpus/sample_navigation_consumer_session.json")

project = create_workspace(project_name="Sample Dependency Project")
project = add_session_to_workspace(project, producer, session_id="producer_session", file_name="sample_navigation_producer_session.json", tags=["producer"])
project = add_session_to_workspace(project, consumer, session_id="consumer_session", file_name="sample_navigation_consumer_session.json", tags=["consumer"])
project = set_active_session(project, "consumer_session")
save_project_index(project, "corpus/sample_dependency_project_index.json")
print("ok")
