
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union, Optional

from semascript_parser import Node, parse


ASTValue = Dict[str, Any]


def _value_to_ast(value: Any) -> ASTValue:
    if isinstance(value, Node):
        return node_to_ast(value)
    if isinstance(value, list):
        return {
            "kind": "list",
            "items": [_value_to_ast(v) for v in value],
        }
    return {
        "kind": "raw_token",
        "value": str(value),
    }


def node_to_ast(node: Node, source_profile: Optional[str] = None) -> Dict[str, Any]:
    ast_node: Dict[str, Any] = {
        "kind": "node",
        "class_name": node.class_name,
        "root": node.root,
        "modifiers": list(node.modifiers),
        "roles": [
            {
                "name": role,
                "value": _value_to_ast(value),
            }
            for role, value in node.roles.items()
        ],
    }
    if source_profile:
        ast_node["source_profile"] = source_profile
    return ast_node


def text_to_ast_document(text: str, source_profile: str = "core", source_text: Optional[str] = None) -> Dict[str, Any]:
    node = parse(text)
    return {
        "schema_version": "SEMASCRIPT_AST_SCHEMA_v0.1",
        "source_profile": source_profile,
        "source_text": source_text if source_text is not None else text,
        "ast": node_to_ast(node, source_profile=source_profile),
        "validation_annotations": [],
        "metadata": {},
    }


def _ast_value_to_runtime(value: Dict[str, Any]) -> Any:
    kind = value["kind"]
    if kind == "node":
        return ast_to_node(value)
    if kind == "list":
        return [_ast_value_to_runtime(v) for v in value["items"]]
    if kind == "typed_literal":
        from semascript_parser import Node as ParserNode
        return ParserNode(class_name=value["class_name"], root=value["root"], modifiers=[], roles={})
    if kind == "raw_token":
        return value["value"]
    raise ValueError(f"Unsupported AST value kind: {kind}")


def ast_to_node(ast_node: Dict[str, Any]) -> Node:
    if ast_node.get("kind") != "node":
        raise ValueError("ast_to_node expects a node dict")
    roles = {}
    for role in ast_node.get("roles", []):
        roles[role["name"]] = _ast_value_to_runtime(role["value"])
    return Node(
        class_name=ast_node["class_name"],
        root=ast_node["root"],
        modifiers=list(ast_node.get("modifiers", [])),
        roles=roles,
    )


def _ast_value_to_slinear(value: Dict[str, Any]) -> str:
    kind = value["kind"]
    if kind == "node":
        return ast_to_slinear(value)
    if kind == "list":
        return "[" + "; ".join(_ast_value_to_slinear(v) for v in value["items"]) + "]"
    if kind == "typed_literal":
        if "value" in value and value["value"] is not None:
            return f"[{value['class_name']}:{value['root']}={value['value']}]"
        return f"[{value['class_name']}:{value['root']}]"
    if kind == "raw_token":
        return value["value"]
    raise ValueError(f"Unsupported AST value kind: {kind}")


def ast_to_slinear(ast_node: Dict[str, Any]) -> str:
    if ast_node.get("kind") != "node":
        raise ValueError("ast_to_slinear expects a node dict")
    header = f"[{ast_node['class_name']}:{ast_node['root']}"
    mods = ast_node.get("modifiers", [])
    if mods:
        header += " {" + " ".join(mods) + "}"
    roles = ast_node.get("roles", [])
    if roles:
        role_str = "; ".join(f"{role['name']}={_ast_value_to_slinear(role['value'])}" for role in roles)
        header += f" <{role_str}>"
    header += "]"
    return header


def load_ast_document(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_ast_document(doc: Dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
