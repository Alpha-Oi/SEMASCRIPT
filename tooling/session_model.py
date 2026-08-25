
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json
from copy import deepcopy



class SessionModelError(Exception):
    """Raised when session model cannot be created or restored."""


def empty_ui_state() -> dict:
    return {
        "selected_entity_id": None,
        "preview_mode": "raw",
        "decompose": True,
        "viewport": {"scroll_x": 0, "scroll_y": 0, "zoom": 1.0},
        "panels": {
            "svg": True,
            "ast": True,
            "runtime": True,
            "state": True,
            "graph_json": True,
        },
    }


def create_session_from_text(
    text: str,
    profile: str = "core",
    decompose: bool = True,
    initial_state: Optional[dict] = None,
    session_name: Optional[str] = None,
) -> dict:
    from inspector_service import analyze_input
    analysis = analyze_input(
        text=text,
        profile=profile,
        decompose=decompose,
        initial_state=initial_state,
    )
    return {
        "session_version": "SEMASCRIPT_PROJECT_SESSION_v0.1",
        "session_name": session_name or "Untitled SEMASCRIPT Session",
        "project": {
            "profile": profile,
            "source_mode": "text",
            "source_text": analysis["source_text"],
            "normalized_text": analysis["normalized_text"],
            "slinear": analysis["slinear"],
            "decomposed_slinear": analysis.get("decomposed_slinear"),
            "initial_state": deepcopy(initial_state),
        },
        "documents": {
            "ast_document": analysis["ast_document"],
            "decomposed_ast_document": analysis.get("decomposed_ast_document"),
            "graph_document": analysis.get("graph_document"),
            "decomposed_graph_document": analysis.get("decomposed_graph_document"),
        },
        "reports": {
            "validation": analysis["validation"],
            "runtime_report": analysis["runtime_report"],
            "state_report": analysis["state_report"],
        },
        "render": {
            "svg_raw": analysis["svg_raw"],
            "svg_decomposed": analysis.get("svg_decomposed"),
        },
        "ui_state": empty_ui_state(),
        "metadata": {
            "generated_from": "text_input",
        },
    }


def create_session_from_graph(
    graph_document: dict,
    profile: str = "core",
    decompose: bool = True,
    initial_state: Optional[dict] = None,
    session_name: Optional[str] = None,
    ui_state: Optional[dict] = None,
) -> dict:
    from inspector_service import analyze_graph
    analysis = analyze_graph(
        graph_document=graph_document,
        profile=profile,
        decompose=decompose,
        initial_state=initial_state,
    )
    session = {
        "session_version": "SEMASCRIPT_PROJECT_SESSION_v0.1",
        "session_name": session_name or "Untitled SEMASCRIPT Graph Session",
        "project": {
            "profile": profile,
            "source_mode": "graph",
            "source_text": analysis["source_text"],
            "normalized_text": analysis["normalized_text"],
            "slinear": analysis["slinear"],
            "decomposed_slinear": analysis.get("decomposed_slinear"),
            "initial_state": deepcopy(initial_state),
        },
        "documents": {
            "ast_document": analysis["ast_document"],
            "decomposed_ast_document": analysis.get("decomposed_ast_document"),
            "graph_document": analysis.get("graph_document"),
            "decomposed_graph_document": analysis.get("decomposed_graph_document"),
        },
        "reports": {
            "validation": analysis["validation"],
            "runtime_report": analysis["runtime_report"],
            "state_report": analysis["state_report"],
        },
        "render": {
            "svg_raw": analysis["svg_raw"],
            "svg_decomposed": analysis.get("svg_decomposed"),
        },
        "ui_state": deepcopy(ui_state) if ui_state is not None else empty_ui_state(),
        "metadata": {
            "generated_from": "graph_input",
        },
    }
    return session


def save_session(session: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


def load_session(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def session_to_inspector_payload(session: dict) -> dict:
    if session.get("session_version") != "SEMASCRIPT_PROJECT_SESSION_v0.1":
        raise SessionModelError("Unsupported session_version")

    project = session["project"]
    documents = session["documents"]
    reports = session["reports"]
    render = session["render"]

    payload = {
        "source_text": project["source_text"],
        "profile": project["profile"],
        "normalized_text": project["normalized_text"],
        "slinear": project["slinear"],
        "decomposed_slinear": project.get("decomposed_slinear"),
        "ast_document": documents["ast_document"],
        "decomposed_ast_document": documents.get("decomposed_ast_document"),
        "graph_document": documents.get("graph_document"),
        "decomposed_graph_document": documents.get("decomposed_graph_document"),
        "validation": reports["validation"],
        "runtime_report": reports["runtime_report"],
        "state_report": reports["state_report"],
        "svg_raw": render["svg_raw"],
        "svg_decomposed": render.get("svg_decomposed"),
        "session_name": session.get("session_name"),
        "ui_state": session.get("ui_state", empty_ui_state()),
    }
    return payload


def create_project_index(session_files: list[dict]) -> dict:
    return {
        "project_index_version": "SEMASCRIPT_PROJECT_INDEX_v0.1",
        "sessions": session_files,
    }
