
from __future__ import annotations

from pathlib import Path

from session_model import (
    create_session_from_text,
    create_session_from_graph,
    session_to_inspector_payload,
    save_session,
    load_session,
)
from inspector_service import graph_from_input


def empty_state():
    return {
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


def main() -> None:
    total = 3
    passed = 0

    session1 = create_session_from_text(
        text="gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Text Session",
    )
    ok1 = session1["session_version"] == "SEMASCRIPT_PROJECT_SESSION_v0.1" and session1["documents"]["graph_document"]["root_entity_id"]
    if ok1:
        passed += 1
    else:
        print("FAILED: text session")

    graph_doc = graph_from_input("[EXEC:TRANSFER <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]", profile="exec")["graph_document"]
    session2 = create_session_from_graph(
        graph_document=graph_doc,
        profile="exec",
        decompose=True,
        initial_state=empty_state(),
        session_name="Graph Session",
        ui_state={"selected_entity_id": graph_doc["root_entity_id"], "preview_mode": "raw", "decompose": True, "viewport": {"scroll_x": 0, "scroll_y": 0, "zoom": 1.0}, "panels": {}},
    )
    tmp = Path("corpus") / "session_roundtrip_test.json"
    save_session(session2, tmp)
    loaded = load_session(tmp)
    restored = session_to_inspector_payload(loaded)
    ok2 = restored["session_name"] == "Graph Session" and restored["graph_document"]["root_entity_id"] == graph_doc["root_entity_id"]
    if ok2:
        passed += 1
    else:
        print("FAILED: graph session roundtrip")

    ok3 = loaded["project"]["profile"] == "exec" and "runtime_report" in loaded["reports"] and "svg_raw" in loaded["render"]
    if ok3:
        passed += 1
    else:
        print("FAILED: report/render persistence")

    print(f"persisted_project_session: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
