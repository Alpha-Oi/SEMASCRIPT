
from pathlib import Path
from session_model import load_session
from project_model import create_workspace, add_session_to_workspace, set_active_session, save_project_index

base = Path("corpus")
text_session = load_session(base / "sample_text_session.json")
graph_session = load_session(base / "sample_graph_session.json")

project = create_workspace(project_name="Sample Multi-session Project")
project = add_session_to_workspace(project, text_session, session_id="text_session", file_name="sample_text_session.json", tags=["text", "human"])
project = add_session_to_workspace(project, graph_session, session_id="graph_session", file_name="sample_graph_session.json", tags=["graph", "exec"])
project = set_active_session(project, "graph_session")
save_project_index(project, base / "sample_project_index.json")
print("ok")
