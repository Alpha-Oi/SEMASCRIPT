
from pathlib import Path
import json
from graph_model import load_graph_document
from session_model import create_session_from_graph, save_session

graph = load_graph_document(Path("corpus") / "sample_graph_document.json")
session = create_session_from_graph(
    graph_document=graph,
    profile="exec",
    decompose=True,
    initial_state={
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {"A": {"RES": 2}, "B": {"RES": 0}},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    },
    session_name="Sample Graph Session",
    ui_state={
        "selected_entity_id": graph["root_entity_id"],
        "preview_mode": "raw",
        "decompose": True,
        "viewport": {"scroll_x": 0, "scroll_y": 0, "zoom": 1.0},
        "panels": {"svg": True, "ast": True, "runtime": True, "state": True, "graph_json": True},
    },
)
save_session(session, "corpus/sample_graph_session.json")
print("ok")
