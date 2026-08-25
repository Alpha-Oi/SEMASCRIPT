
from inspector_service import analyze_input
import json
from pathlib import Path

result = analyze_input(
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
        "metadata": {"applied_steps": 0, "last_schedule": None}
    },
)
Path("corpus/inspector_sample_analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
