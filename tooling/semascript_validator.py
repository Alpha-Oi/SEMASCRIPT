
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Union

from semascript_parser import Node, parse

Value = Union[Node, List["Value"], str]

CORE_CLASSES: Set[str] = {"ENT", "PRC", "STA", "REL", "MOD", "FRM", "IDX"}
EXT_CLASSES: Set[str] = {"PAT", "TIME", "LAW", "VAL"}
EXEC_CLASSES: Set[str] = {"EXEC"}

ALL_CLASSES: Set[str] = CORE_CLASSES | EXT_CLASSES | EXEC_CLASSES

CORE_ROLES: Set[str] = {
    "agt", "obj", "src", "dst", "ctx", "res", "cau", "dep", "mod",
    "ins", "loc", "tim", "scp", "axis", "scope", "code", "core",
    "law", "mode", "qty", "time", "invariant", "left", "right"
}

EXEC_REQUIRED: Dict[str, Set[str]] = {
    "TRANSFER": {"src", "dst", "obj"},
    "CREATE": {"dst", "obj"},
    "DESTROY": {"obj"},
    "ACT": {"agt"},
    "OBSERVE": {"agt", "obj"},
    "CHANGE": {"obj"},
}


@dataclass
class ValidationResult:
    valid: bool
    errors: List[Tuple[str, str]] = field(default_factory=list)

    def add(self, code: str, message: str) -> None:
        self.errors.append((code, message))

    def finish(self) -> "ValidationResult":
        self.valid = not self.errors
        return self


def validate_core_text(text: str) -> ValidationResult:
    try:
        node = parse(text)
    except Exception as exc:
        return ValidationResult(valid=False, errors=[("P000", f"Parse error: {exc}")])
    return validate_core_node(node)


def validate_exec_text(text: str) -> ValidationResult:
    try:
        node = parse(text)
    except Exception as exc:
        return ValidationResult(valid=False, errors=[("P000", f"Parse error: {exc}")])
    return validate_exec_node(node)


def validate_core_node(node: Node) -> ValidationResult:
    result = ValidationResult(valid=True)
    _validate_node_recursive(node, result, is_top=True)

    if node.class_name == "MOD":
        result.add("C005", "Standalone MOD node is not a valid complete construction")
    if node.class_name == "FRM" and node.root in {"INV", "TIME", "CND"} and "scp" not in node.roles:
        result.add("C004", f"Frame {node.root} requires scp role")
    if node.class_name == "FRM" and node.root == "INV" and "law" not in node.roles:
        result.add("C004", "FRM:INV requires law role")
    if node.class_name == "FRM" and node.root == "TIME" and "mode" not in node.roles:
        result.add("C004", "FRM:TIME requires mode role")
    if node.class_name == "PAT":
        _validate_pattern(node, result)

    return result.finish()


def validate_exec_node(node: Node) -> ValidationResult:
    result = ValidationResult(valid=True)
    _validate_node_recursive(node, result, is_top=True)

    if node.class_name != "EXEC":
        result.add("X001", "Exec validation requires top-level EXEC node")
        return result.finish()

    required = EXEC_REQUIRED.get(node.root)
    if required is None:
        result.add("X001", f"Unsupported EXEC operation: {node.root}")
        return result.finish()

    for role in sorted(required):
        if role not in node.roles:
            result.add("X002", f"Missing required role for EXEC:{node.root}: {role}")

    for role, value in node.roles.items():
        _validate_exec_value(role, value, result)

    return result.finish()


def _validate_exec_value(role: str, value: Value, result: ValidationResult) -> None:
    if isinstance(value, list):
        result.add("X010", f"List value is not supported in exec role {role}")
        return

    if isinstance(value, Node):
        if role == "time":
            if value.class_name != "TIME":
                result.add("X008", "time role must be [TIME:...]")
        elif role == "invariant":
            if value.class_name != "LAW":
                result.add("X007", "invariant role must be [LAW:...]")
        elif value.class_name == "PAT":
            result.add("X006", "Pattern macros cannot be executed directly")
        elif value.class_name == "EXEC":
            result.add("X010", "Nested EXEC blocks are not supported in MVP")
        return

    # raw string
    if role in {"time", "invariant"}:
        result.add("X010", f"{role} must be typed, not raw token")
    else:
        result.add("X003", f"Untyped executable operand for role {role}: {value}")


def _validate_node_recursive(node: Node, result: ValidationResult, is_top: bool = False) -> None:
    if node.class_name not in ALL_CLASSES:
        result.add("C002", f"Unknown class: {node.class_name}")

    if not node.root:
        result.add("C002", "Missing root")

    if node.class_name in CORE_CLASSES | {"PAT"}:
        for role in node.roles:
            if role not in CORE_ROLES:
                result.add("C003", f"Unknown or unsupported role: {role}")

    for role, value in node.roles.items():
        _validate_value_recursive(role, value, result)

    if is_top and node.class_name == "MOD":
        result.add("C005", "Top-level modifier has no target")

    if node.class_name == "STA" and node.root == "ZSUM":
        result.add("E206", "ZSUM is invariant logic, not a state")

    if node.class_name == "FRM":
        if node.root == "INV":
            if "scp" not in node.roles:
                result.add("C004", "FRM:INV missing scp")
            if "law" not in node.roles:
                result.add("C004", "FRM:INV missing law")
        if node.root == "TIME":
            if "scp" not in node.roles:
                result.add("E203", "FRM:TIME missing scp")
            if "mode" not in node.roles:
                result.add("C004", "FRM:TIME missing mode")

    if node.class_name == "PAT":
        _validate_pattern(node, result)


def _validate_value_recursive(role: str, value: Value, result: ValidationResult) -> None:
    if isinstance(value, Node):
        _validate_node_recursive(value, result, is_top=False)
        return

    if isinstance(value, list):
        if role in {"scp", "scope"} and len(value) == 0:
            result.add("C004", f"Empty scope list in role {role}")
        for item in value:
            _validate_value_recursive(role, item, result)
        return

    if role in {"scp", "scope"} and not value:
        result.add("C004", f"Empty scope in role {role}")


def _validate_pattern(node: Node, result: ValidationResult) -> None:
    if node.root == "SPR":
        if "core" not in node.roles or "res" not in node.roles:
            result.add("E201", "PAT:SPR requires core and res roles")
    elif node.root == "GEN":
        if "code" not in node.roles or "dst" not in node.roles:
            result.add("E201", "PAT:GEN requires code and dst roles")
    elif node.root == "PAL":
        if "axis" not in node.roles or not ("scope" in node.roles or "scp" in node.roles):
            result.add("E201", "PAT:PAL requires axis and scope/scp roles")
    else:
        result.add("E202", f"Unsupported pattern macro: {node.root}")
