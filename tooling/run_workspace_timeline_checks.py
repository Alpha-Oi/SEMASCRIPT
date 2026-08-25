
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace, set_active_session
from workspace_timeline import build_workspace_timeline


def empty_state():
    return {
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


def main() -> None:
    total = 2
    passed = 0

    s1 = create_session_from_text(
        text="gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="S1",
    )
    s2 = create_session_from_text(
        text="spr(seed -> form)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="S2",
    )

    project = create_workspace(project_name="Timeline Project")
    project = add_session_to_workspace(project, s1, session_id="s1")
    project = add_session_to_workspace(project, s2, session_id="s2")
    project = set_active_session(project, "s2")

    timeline = build_workspace_timeline(project)
    ok1 = timeline["summary"]["event_count"] >= 4 and timeline["active_session_id"] == "s2"
    if ok1:
        passed += 1
    else:
        print("FAILED: timeline summary", timeline)

    events = timeline["events"]
    ok2 = any(e["event_type"] == "session_added" and e["session_id"] == "s1" for e in events) and any(e["event_type"] == "active_session_switched" and e["session_id"] == "s2" for e in events)
    if ok2:
        passed += 1
    else:
        print("FAILED: timeline event detection", timeline)

    print(f"workspace_timeline_session_history: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
