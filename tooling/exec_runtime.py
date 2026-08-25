
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from human_normalizer import normalize
from semascript_ast import (
    ast_to_slinear,
    load_ast_document,
    save_ast_document,
    text_to_ast_document,
)
from pattern_decomposer import decompose_ast_document, PatternDecompositionError


ASTNode = Dict[str, Any]
ASTValue = Dict[str, Any]


class ExecRuntimeError(Exception):
    """Raised when runtime execution cannot proceed."""


def _role_map(node: ASTNode) -> Dict[str, ASTValue]:
    return {entry["name"]: entry["value"] for entry in node.get("roles", [])}


def _value_label(value: ASTValue) -> str:
    kind = value["kind"]
    if kind == "node":
        return ast_to_slinear(value)
    if kind == "list":
        return "[" + "; ".join(_value_label(v) for v in value["items"]) + "]"
    if kind == "typed_literal":
        if value.get("value") is not None:
            return f"[{value['class_name']}:{value['root']}={value['value']}]"
        return f"[{value['class_name']}:{value['root']}]"
    if kind == "raw_token":
        return value["value"]
    return "<UNKNOWN>"


def _value_token(value: Optional[ASTValue]) -> Optional[str]:
    if value is None:
        return None
    kind = value["kind"]
    if kind == "raw_token":
        return value["value"]
    if kind == "typed_literal":
        return value["root"]
    if kind == "node":
        return value["root"]
    return None


def _normalize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(context)
    out.setdefault("time_mode", None)
    out.setdefault("invariant_law", None)
    out.setdefault("schedule", None)
    out.setdefault("notes", [])
    return out


def _make_step(op_family: str, op_name: str, roles: Dict[str, str], context: Dict[str, Any], reversible: bool, effect_class: str) -> Dict[str, Any]:
    return {
        "op_family": op_family,
        "op_name": op_name,
        "roles": roles,
        "constraints": {
            "time_mode": context.get("time_mode"),
            "invariant_law": context.get("invariant_law"),
            "schedule": context.get("schedule"),
        },
        "reversible": reversible,
        "effect_class": effect_class,
    }


def _combine_results(results: List[Dict[str, Any]], context: Dict[str, Any], entry_kind: str) -> Dict[str, Any]:
    plan = []
    errors = []
    notes = []
    accepted = True
    decomposition_count = 0

    for result in results:
        plan.extend(result.get("plan", []))
        errors.extend(result.get("errors", []))
        notes.extend(result.get("notes", []))
        decomposition_count += result.get("decomposition_count", 0)
        if not result.get("accepted", False):
            accepted = False

    return {
        "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
        "accepted": accepted and not errors,
        "entry_kind": entry_kind,
        "context": {
            "time_mode": context.get("time_mode"),
            "invariant_law": context.get("invariant_law"),
            "schedule": context.get("schedule"),
        },
        "plan": plan,
        "errors": errors,
        "notes": notes,
        "decomposition_count": decomposition_count,
    }


def _runtime_error(code: str, message: str, context: Dict[str, Any], entry_kind: str) -> Dict[str, Any]:
    return {
        "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
        "accepted": False,
        "entry_kind": entry_kind,
        "context": {
            "time_mode": context.get("time_mode"),
            "invariant_law": context.get("invariant_law"),
            "schedule": context.get("schedule"),
        },
        "plan": [],
        "errors": [{"code": code, "message": message}],
        "notes": [],
        "decomposition_count": 0,
    }


def _execute_scope(value: ASTValue, context: Dict[str, Any]) -> Dict[str, Any]:
    kind = value["kind"]
    if kind == "list":
        items = value["items"]
        results = []
        ctx = dict(context)

        if ctx.get("time_mode") == "LIN":
            ctx["schedule"] = "sequential"
        elif ctx.get("time_mode") == "CYC":
            ctx["schedule"] = "cyclical"
        elif ctx.get("time_mode") == "BRN":
            ctx["schedule"] = "branch_set"
        elif ctx.get("time_mode") == "REC":
            ctx["schedule"] = "recursive"
        elif ctx.get("time_mode") == "REV":
            ctx["schedule"] = "reversible_sequence"
        elif ctx.get("time_mode") == "ATM":
            ctx["schedule"] = "atemporal_set"
        else:
            ctx["schedule"] = "sequential" if len(items) > 1 else None

        if ctx.get("time_mode") == "BRN":
            # branch set is representable but not automatically selected
            notes = ["branch_set_deferred_selection"]
            base = _combine_results([_execute_node(item, ctx) for item in items], ctx, "branch_scope")
            base["notes"].extend(notes)
            return base

        results = [_execute_node(item, ctx) for item in items]
        return _combine_results(results, ctx, "list_scope")

    if kind == "node":
        return _execute_node(value, context)

    return _runtime_error("R_SCOPE", f"Unsupported scope value kind: {kind}", context, "scope")


def _exec_operation(node: ASTNode, context: Dict[str, Any]) -> Dict[str, Any]:
    roles = _role_map(node)
    op = node["root"]

    required = {
        "TRANSFER": {"src", "dst", "obj"},
        "CREATE": {"dst", "obj"},
        "DESTROY": {"obj"},
        "ACT": {"agt"},
        "OBSERVE": {"agt", "obj"},
        "CHANGE": {"obj"},
    }.get(op)

    if required is None:
        return _runtime_error("R_EXEC_OP", f"Unsupported runtime EXEC operation: {op}", context, "exec")

    missing = [r for r in sorted(required) if r not in roles]
    if missing:
        return _runtime_error("R_EXEC_ROLE", f"Missing required roles: {', '.join(missing)}", context, "exec")

    invariant = context.get("invariant_law")
    time_mode = context.get("time_mode")

    if invariant == "ZSUM" and op in {"CREATE", "DESTROY"}:
        return _runtime_error("R_INV_ZSUM", f"{op} violates ZSUM invariant", context, "exec")
    if invariant == "NZSUM" and op == "TRANSFER":
        return _runtime_error("R_INV_NZSUM", "TRANSFER does not satisfy NZSUM by itself", context, "exec")
    if invariant == "BAL":
        return _runtime_error("R_INV_BAL", "BAL is not an operational invariant law in runtime v0.1", context, "exec")
    if time_mode == "REV" and op in {"CREATE", "DESTROY"}:
        return _runtime_error("R_TIME_REV", f"{op} is not reversible under REV runtime mode", context, "exec")

    reversible = op in {"TRANSFER", "CHANGE", "OBSERVE", "ACT"}
    if time_mode == "REV" and not reversible:
        return _runtime_error("R_TIME_REV", f"{op} is not reversible under REV runtime mode", context, "exec")

    role_labels = {name: _value_label(value) for name, value in roles.items()}
    effect_class = {
        "TRANSFER": "redistribution",
        "CREATE": "net_growth",
        "DESTROY": "net_loss",
        "ACT": "action",
        "OBSERVE": "observation",
        "CHANGE": "state_transition",
    }[op]

    step = _make_step("EXEC", op, role_labels, context, reversible, effect_class)
    return {
        "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
        "accepted": True,
        "entry_kind": "exec",
        "context": {
            "time_mode": context.get("time_mode"),
            "invariant_law": context.get("invariant_law"),
            "schedule": context.get("schedule"),
        },
        "plan": [step],
        "errors": [],
        "notes": [],
        "decomposition_count": 0,
    }


def _core_runtime(node: ASTNode, context: Dict[str, Any]) -> Dict[str, Any]:
    roles = _role_map(node)

    if node["class_name"] == "PRC" and node["root"] == "EXP":
        step = _make_step(
            "CORE",
            "EXPAND",
            {name: _value_label(value) for name, value in roles.items()},
            context,
            reversible=False,
            effect_class="structural_growth",
        )
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": True,
            "entry_kind": "core_runtime",
            "context": {
                "time_mode": context.get("time_mode"),
                "invariant_law": context.get("invariant_law"),
                "schedule": context.get("schedule"),
            },
            "plan": [step],
            "errors": [],
            "notes": ["decomposed_pattern_runtime"],
            "decomposition_count": 0,
        }

    if node["class_name"] == "REL" and node["root"] == "DEP":
        step = _make_step(
            "CORE",
            "DEPENDENCY",
            {name: _value_label(value) for name, value in roles.items()},
            context,
            reversible=False,
            effect_class="dependency_relation",
        )
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": True,
            "entry_kind": "core_runtime",
            "context": {
                "time_mode": context.get("time_mode"),
                "invariant_law": context.get("invariant_law"),
                "schedule": context.get("schedule"),
            },
            "plan": [step],
            "errors": [],
            "notes": ["decomposed_pattern_runtime"],
            "decomposition_count": 0,
        }

    if node["class_name"] == "REL" and node["root"] == "CAU":
        cause = roles.get("cau")
        result = roles.get("res")
        if cause is None or result is None:
            return _runtime_error("R_CAU", "REL:CAU requires cau and res", context, "core_runtime")
        ctx = dict(context)
        ctx["schedule"] = "causal_sequence"
        return _combine_results([_execute_scope(cause, ctx), _execute_scope(result, ctx)], ctx, "causal_chain")

    if node["class_name"] == "STA":
        step = _make_step(
            "CORE",
            "ASSERT_STATE",
            {name: _value_label(value) for name, value in roles.items()},
            context,
            reversible=False,
            effect_class="state_assertion",
        )
        step["state_root"] = node["root"]
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": True,
            "entry_kind": "core_runtime",
            "context": {
                "time_mode": context.get("time_mode"),
                "invariant_law": context.get("invariant_law"),
                "schedule": context.get("schedule"),
            },
            "plan": [step],
            "errors": [],
            "notes": [],
            "decomposition_count": 0,
        }

    return _runtime_error(
        "R_CORE_NODE",
        f"Unsupported core runtime node: {node['class_name']}:{node['root']}",
        context,
        "core_runtime",
    )


def _execute_node(node: ASTNode, context: Dict[str, Any]) -> Dict[str, Any]:
    context = _normalize_context(context)

    if node["class_name"] == "FRM":
        roles = _role_map(node)

        if node["root"] == "TIME":
            scope = roles.get("scp")
            if scope is None:
                return _runtime_error("R_TIME_SCOPE", "FRM:TIME requires scp", context, "frame")
            new_context = dict(context)
            new_context["time_mode"] = _value_token(roles.get("mode"))
            return _execute_scope(scope, new_context)

        if node["root"] == "INV":
            scope = roles.get("scp")
            if scope is None:
                return _runtime_error("R_INV_SCOPE", "FRM:INV requires scp", context, "frame")
            new_context = dict(context)
            new_context["invariant_law"] = _value_token(roles.get("law"))
            return _execute_scope(scope, new_context)

        if node["root"] == "SCN":
            scope = roles.get("scp")
            if scope is None:
                return _runtime_error("R_SCN_SCOPE", "FRM:SCN requires scp", context, "frame")
            new_context = dict(context)
            new_context["notes"] = list(new_context.get("notes", [])) + ["scene_wrapper"]
            return _execute_scope(scope, new_context)

        return _runtime_error("R_FRAME", f"Unsupported frame root in runtime: {node['root']}", context, "frame")

    if node["class_name"] == "EXEC":
        return _exec_operation(node, context)

    if node["class_name"] == "PAT":
        return _runtime_error("R_PATTERN", "Pattern macro remained undecomposed in runtime path", context, "pattern")

    return _core_runtime(node, context)


def execute_ast_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    try:
        decomposed = decompose_ast_document(doc)
    except PatternDecompositionError as exc:
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": False,
            "entry_kind": "decomposition",
            "context": {"time_mode": None, "invariant_law": None, "schedule": None},
            "plan": [],
            "errors": [{"code": "R_DECOMP", "message": str(exc)}],
            "notes": [],
            "decomposition_count": 0,
        }

    result = _execute_node(decomposed["ast"], {})
    result["decomposition_count"] = decomposed.get("metadata", {}).get("pattern_decomposition_count", 0)
    return result


def execute_text(text: str, profile: str = "exec") -> Dict[str, Any]:
    try:
        normalized = normalize(text) if profile == "human" else text
    except Exception as exc:
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": False,
            "entry_kind": "normalization",
            "context": {"time_mode": None, "invariant_law": None, "schedule": None},
            "plan": [],
            "errors": [{"code": "R_NORMALIZE", "message": str(exc)}],
            "notes": [],
            "decomposition_count": 0,
        }

    try:
        doc = text_to_ast_document(
            normalized,
            source_profile="normalized" if profile == "human" else profile,
            source_text=text,
        )
    except Exception as exc:
        return {
            "runtime_version": "SEMASCRIPT_EXEC_RUNTIME_v0.1",
            "accepted": False,
            "entry_kind": "parse",
            "context": {"time_mode": None, "invariant_law": None, "schedule": None},
            "plan": [],
            "errors": [{"code": "R_PARSE", "message": str(exc)}],
            "notes": [],
            "decomposition_count": 0,
        }

    if profile == "human":
        doc["metadata"]["normalized_text"] = normalized
    return execute_ast_document(doc)


def load_and_execute(path: str) -> Dict[str, Any]:
    doc = load_ast_document(path)
    return execute_ast_document(doc)
