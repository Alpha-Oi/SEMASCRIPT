
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import json


GraphEntity = Dict[str, Any]
GraphEdge = Dict[str, Any]
GraphDoc = Dict[str, Any]
ASTValue = Dict[str, Any]


class GraphModelError(Exception):
    """Raised when graph model cannot be converted."""


def _entity_kind_label(entity: GraphEntity) -> str:
    kind = entity["kind"]
    if kind == "node":
        return f"{entity['class_name']}:{entity['root']}"
    if kind == "list":
        return "LIST"
    if kind == "raw_token":
        return entity["value"]
    if kind == "typed_literal":
        if entity.get("value") is not None:
            return f"{entity['class_name']}:{entity['root']}={entity['value']}"
        return f"{entity['class_name']}:{entity['root']}"
    return entity["id"]


def _new_entity_id(counter: List[int]) -> str:
    counter[0] += 1
    return f"e{counter[0]}"


def _value_to_graph(value: ASTValue, entities: List[GraphEntity], edges: List[GraphEdge], counter: List[int], x: float, y: float) -> str:
    kind = value["kind"]
    eid = _new_entity_id(counter)

    if kind == "node":
        entity = {
            "id": eid,
            "kind": "node",
            "class_name": value["class_name"],
            "root": value["root"],
            "modifiers": list(value.get("modifiers", [])),
            "x": x,
            "y": y,
        }
        entities.append(entity)
        child_y = y + 120
        for index, role in enumerate(value.get("roles", [])):
            child_id = _value_to_graph(role["value"], entities, edges, counter, x + (index - 1) * 180, child_y + index * 24)
            edges.append({
                "id": f"edge_{eid}_{child_id}_{index}",
                "from_id": eid,
                "to_id": child_id,
                "role": role["name"],
                "order": index,
            })
        return eid

    if kind == "list":
        entity = {
            "id": eid,
            "kind": "list",
            "label": "LIST",
            "x": x,
            "y": y,
        }
        entities.append(entity)
        child_y = y + 110
        for index, item in enumerate(value.get("items", [])):
            child_id = _value_to_graph(item, entities, edges, counter, x + (index - 1) * 180, child_y + index * 24)
            edges.append({
                "id": f"edge_{eid}_{child_id}_{index}",
                "from_id": eid,
                "to_id": child_id,
                "role": f"item_{index}",
                "order": index,
            })
        return eid

    if kind == "raw_token":
        entities.append({
            "id": eid,
            "kind": "raw_token",
            "value": value["value"],
            "x": x,
            "y": y,
        })
        return eid

    if kind == "typed_literal":
        entities.append({
            "id": eid,
            "kind": "typed_literal",
            "class_name": value["class_name"],
            "root": value["root"],
            "value": value.get("value"),
            "x": x,
            "y": y,
        })
        return eid

    raise GraphModelError(f"Unsupported AST value kind: {kind}")


def ast_document_to_graph_document(ast_doc: Dict[str, Any]) -> GraphDoc:
    entities: List[GraphEntity] = []
    edges: List[GraphEdge] = []
    counter = [0]
    root_id = _value_to_graph(ast_doc["ast"], entities, edges, counter, 320, 80)
    return {
        "graph_version": "SEMASCRIPT_GRAPH_MODEL_v0.1",
        "profile": ast_doc.get("source_profile", "core"),
        "source_text": ast_doc.get("source_text"),
        "root_entity_id": root_id,
        "entities": entities,
        "edges": edges,
        "metadata": {
            "generated_from_ast": True,
        },
    }


def _entity_index(graph_doc: GraphDoc) -> Dict[str, GraphEntity]:
    return {entity["id"]: entity for entity in graph_doc.get("entities", [])}


def _outgoing_edges(graph_doc: GraphDoc, entity_id: str) -> List[GraphEdge]:
    edges = [edge for edge in graph_doc.get("edges", []) if edge["from_id"] == entity_id]
    edges.sort(key=lambda e: (e.get("order", 0), e["role"], e["to_id"]))
    return edges


def _entity_to_ast(entity_id: str, graph_doc: GraphDoc, index: Dict[str, GraphEntity]) -> ASTValue:
    if entity_id not in index:
        raise GraphModelError(f"Missing entity: {entity_id}")

    entity = index[entity_id]
    kind = entity["kind"]

    if kind == "node":
        roles = []
        for edge in _outgoing_edges(graph_doc, entity_id):
            roles.append({
                "name": edge["role"],
                "value": _entity_to_ast(edge["to_id"], graph_doc, index),
            })
        return {
            "kind": "node",
            "class_name": entity["class_name"],
            "root": entity["root"],
            "modifiers": list(entity.get("modifiers", [])),
            "roles": roles,
        }

    if kind == "list":
        items = []
        for edge in _outgoing_edges(graph_doc, entity_id):
            items.append(_entity_to_ast(edge["to_id"], graph_doc, index))
        return {
            "kind": "list",
            "items": items,
        }

    if kind == "raw_token":
        return {
            "kind": "raw_token",
            "value": entity["value"],
        }

    if kind == "typed_literal":
        return {
            "kind": "typed_literal",
            "class_name": entity["class_name"],
            "root": entity["root"],
            "value": entity.get("value"),
        }

    raise GraphModelError(f"Unsupported graph entity kind: {kind}")


def graph_document_to_ast_document(graph_doc: GraphDoc) -> Dict[str, Any]:
    root_id = graph_doc.get("root_entity_id")
    if not root_id:
        raise GraphModelError("Graph document has no root_entity_id")

    index = _entity_index(graph_doc)
    root_value = _entity_to_ast(root_id, graph_doc, index)
    if root_value["kind"] != "node":
        raise GraphModelError("Graph root must resolve to AST node")

    return {
        "schema_version": "SEMASCRIPT_AST_SCHEMA_v0.1",
        "source_profile": graph_doc.get("profile", "core"),
        "source_text": graph_doc.get("source_text"),
        "ast": root_value,
        "validation_annotations": [],
        "metadata": {
            "generated_from_graph": True,
        },
    }


def save_graph_document(graph_doc: GraphDoc, path: str | Path) -> None:
    Path(path).write_text(json.dumps(graph_doc, ensure_ascii=False, indent=2), encoding="utf-8")


def load_graph_document(path: str | Path) -> GraphDoc:
    return json.loads(Path(path).read_text(encoding="utf-8"))
