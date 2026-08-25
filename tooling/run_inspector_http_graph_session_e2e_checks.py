from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from inspector_server import InspectorHandler


def post_json(base_url: str, path: str, payload: dict) -> tuple[int, dict]:
    request = Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def empty_state() -> dict:
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
    total = 7
    passed = 0

    server = ThreadingHTTPServer(("127.0.0.1", 0), InspectorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        text_input = "gen(template -> instance)"
        exec_input = "[EXEC:TRANSFER <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RES]>]"

        _, analyze_result = post_json(base_url, "/api/analyze", {
            "text": text_input,
            "profile": "human",
            "decompose": True,
            "initial_state": empty_state(),
        })
        ok1 = (
            analyze_result["validation"]["valid"] is True
            and analyze_result["normalized_text"]
            and analyze_result["graph_document"]["root_entity_id"]
            and analyze_result["runtime_report"]["accepted"] is True
        )
        if ok1:
            passed += 1
        else:
            print("FAILED: analyze text editor route", analyze_result)

        _, graph_import = post_json(base_url, "/api/graph-from-input", {
            "text": exec_input,
            "profile": "exec",
        })
        graph_document = graph_import["graph_document"]
        ok2 = (
            graph_import["ast_document"]["source_text"] == exec_input
            and graph_document["root_entity_id"]
            and len(graph_document.get("entities", [])) >= 4
        )
        if ok2:
            passed += 1
        else:
            print("FAILED: graph-from-input editor route", graph_import)

        _, analyze_graph_result = post_json(base_url, "/api/analyze-graph", {
            "graph_document": graph_document,
            "profile": "exec",
            "decompose": True,
            "initial_state": empty_state(),
        })
        ok3 = (
            analyze_graph_result["validation"]["valid"] is True
            and analyze_graph_result["runtime_report"]["accepted"] is True
            and analyze_graph_result["state_report"]["accepted"] is True
            and analyze_graph_result["source_text"] == exec_input
        )
        if ok3:
            passed += 1
        else:
            print("FAILED: analyze-graph editor route", analyze_graph_result)

        ui_state = {
            "selected_entity_id": graph_document["root_entity_id"],
            "preview_mode": "raw",
            "decompose": True,
            "viewport": {"scroll_x": 0, "scroll_y": 0, "zoom": 1.0},
            "panels": {},
        }
        _, graph_session = post_json(base_url, "/api/export-session-graph", {
            "graph_document": graph_document,
            "profile": "exec",
            "decompose": True,
            "initial_state": empty_state(),
            "session_name": "HTTP Graph Session",
            "ui_state": ui_state,
        })
        ok4 = (
            graph_session["session_version"] == "SEMASCRIPT_PROJECT_SESSION_v0.1"
            and graph_session["session_name"] == "HTTP Graph Session"
            and graph_session["ui_state"]["selected_entity_id"] == graph_document["root_entity_id"]
            and graph_session["documents"]["graph_document"]["root_entity_id"] == graph_document["root_entity_id"]
        )
        if ok4:
            passed += 1
        else:
            print("FAILED: export-session-graph route", graph_session)

        _, imported_graph_session = post_json(base_url, "/api/import-session", {
            "session": graph_session,
        })
        ok5 = (
            imported_graph_session["session_name"] == "HTTP Graph Session"
            and imported_graph_session["graph_document"]["root_entity_id"] == graph_document["root_entity_id"]
            and imported_graph_session["ui_state"]["selected_entity_id"] == graph_document["root_entity_id"]
            and imported_graph_session["runtime_report"]["accepted"] is True
        )
        if ok5:
            passed += 1
        else:
            print("FAILED: import-session graph route", imported_graph_session)

        _, text_session = post_json(base_url, "/api/export-session-text", {
            "text": text_input,
            "profile": "human",
            "decompose": True,
            "initial_state": empty_state(),
            "session_name": "HTTP Text Session",
        })
        ok6 = (
            text_session["session_name"] == "HTTP Text Session"
            and text_session["project"]["source_text"] == text_input
            and text_session["reports"]["validation"]["valid"] is True
            and text_session["documents"]["graph_document"]["root_entity_id"]
        )
        if ok6:
            passed += 1
        else:
            print("FAILED: export-session-text route", text_session)

        _, project_index = post_json(base_url, "/api/export-project-index", {
            "sessions": [
                {"session_id": "text_s", "session": text_session, "tags": ["text"]},
                {"session_id": "graph_s", "session": graph_session, "tags": ["graph"]},
            ],
            "project_name": "HTTP Graph Session Project",
            "active_session_id": "graph_s",
        })
        ok7 = (
            project_index["active_session_id"] == "graph_s"
            and len(project_index["sessions"]) == 2
            and project_index["sessions"][1]["session_name"] == "HTTP Graph Session"
        )
        if ok7:
            passed += 1
        else:
            print("FAILED: graph/text session project export route", project_index)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    print(f"inspector_http_graph_session_e2e: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
