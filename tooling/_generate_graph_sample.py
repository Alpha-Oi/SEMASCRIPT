
from pathlib import Path
import json
from graph_model import load_graph_document
from inspector_service import analyze_graph

graph = load_graph_document(Path("corpus") / "sample_graph_document.json")
result = analyze_graph(
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
    }
)
Path("corpus/inspector_graph_sample_analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
