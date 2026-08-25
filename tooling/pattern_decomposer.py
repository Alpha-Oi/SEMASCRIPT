
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Tuple

from semascript_ast import load_ast_document, save_ast_document, ast_to_slinear

ASTNode = Dict[str, Any]
ASTValue = Dict[str, Any]


class PatternDecompositionError(Exception):
    """Raised when a pattern cannot be decomposed."""


def _role_map(node: ASTNode) -> Dict[str, ASTValue]:
    return {entry["name"]: entry["value"] for entry in node.get("roles", [])}


def _make_node(class_name: str, root: str, roles: List[Tuple[str, ASTValue]], notes: List[str] | None = None) -> ASTNode:
    node: ASTNode = {
        "kind": "node",
        "class_name": class_name,
        "root": root,
        "modifiers": [],
        "roles": [{"name": name, "value": value} for name, value in roles],
    }
    if notes:
        node["notes"] = notes
    return node


def _decompose_value(value: ASTValue) -> tuple[ASTValue, int]:
    kind = value["kind"]

    if kind == "node":
        return _decompose_node(value)
    if kind == "list":
        total = 0
        items = []
        for item in value["items"]:
            new_item, count = _decompose_value(item)
            items.append(new_item)
            total += count
        return {"kind": "list", "items": items}, total

    return deepcopy(value), 0


def _decompose_node(node: ASTNode) -> tuple[ASTNode, int]:
    roles = []
    nested_count = 0
    for entry in node.get("roles", []):
        new_value, count = _decompose_value(entry["value"])
        roles.append({"name": entry["name"], "value": new_value})
        nested_count += count

    current = deepcopy(node)
    current["roles"] = roles

    if current["class_name"] != "PAT":
        return current, nested_count

    root = current["root"]
    roles_map = _role_map(current)

    if root == "SPR":
        if "core" not in roles_map or "res" not in roles_map:
            raise PatternDecompositionError("PAT:SPR requires core and res")
        decomposed = _make_node(
            "PRC",
            "EXP",
            [
                ("src", roles_map["core"]),
                ("res", roles_map["res"]),
            ],
            notes=["decomposed_from:PAT:SPR"],
        )
        return decomposed, nested_count + 1

    if root == "GEN":
        if "code" not in roles_map or "dst" not in roles_map:
            raise PatternDecompositionError("PAT:GEN requires code and dst")
        decomposed = _make_node(
            "REL",
            "DEP",
            [
                ("dst", roles_map["dst"]),
                ("src", roles_map["code"]),
            ],
            notes=["decomposed_from:PAT:GEN"],
        )
        return decomposed, nested_count + 1

    if root == "PAL":
        scope_value = roles_map.get("scope", roles_map.get("scp"))
        if "axis" not in roles_map or scope_value is None:
            raise PatternDecompositionError("PAT:PAL requires axis and scope/scp")
        decomposed = _make_node(
            "FRM",
            "SCN",
            [
                ("axis", roles_map["axis"]),
                ("scp", scope_value),
            ],
            notes=["decomposed_from:PAT:PAL"],
        )
        return decomposed, nested_count + 1

    raise PatternDecompositionError(f"Unsupported pattern macro: {root}")


def decompose_ast_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    new_doc = deepcopy(doc)
    new_ast, count = _decompose_node(new_doc["ast"])
    new_doc["ast"] = new_ast
    metadata = dict(new_doc.get("metadata", {}))
    metadata["pattern_decomposition_applied"] = True
    metadata["pattern_decomposition_count"] = count
    new_doc["metadata"] = metadata
    return new_doc


def decompose_file(input_path: str, output_path: str) -> None:
    doc = load_ast_document(input_path)
    out = decompose_ast_document(doc)
    save_ast_document(out, output_path)


def ast_document_to_slinear(doc: Dict[str, Any]) -> str:
    return ast_to_slinear(doc["ast"])
