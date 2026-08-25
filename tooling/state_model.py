
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional, Tuple
import json
from pathlib import Path

from exec_runtime import execute_text, load_and_execute

State = Dict[str, Any]
RuntimeReport = Dict[str, Any]


class StateModelError(Exception):
    """Raised when execution state cannot be updated."""


def create_empty_state() -> State:
    return {
        "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "resources": {},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {
            "applied_steps": 0,
            "last_schedule": None,
        },
    }


def load_state(path: str | Path) -> State:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_state(state: State, path: str | Path) -> None:
    Path(path).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _label_parts(label: str) -> Tuple[Optional[str], str]:
    if label.startswith("[") and label.endswith("]") and ":" in label:
        body = label[1:-1]
        class_name, root = body.split(":", 1)
        return class_name, root
    return None, label


def _entity_token(label: Optional[str]) -> str:
    if not label:
        raise StateModelError("Missing entity label")
    class_name, root = _label_parts(label)
    if class_name != "ENT":
        raise StateModelError(f"Expected ENT label, got {label}")
    return root


def _state_token(label: Optional[str]) -> str:
    if not label:
        raise StateModelError("Missing state label")
    class_name, root = _label_parts(label)
    if class_name != "STA":
        raise StateModelError(f"Expected STA label, got {label}")
    return root


def _resource_token(label: Optional[str]) -> str:
    if not label:
        raise StateModelError("Missing resource label")
    class_name, root = _label_parts(label)
    if class_name != "ENT":
        raise StateModelError(f"Expected ENT resource label, got {label}")
    return root


def _qty_value(label: Optional[str]) -> int:
    if not label:
        return 1
    class_name, root = _label_parts(label)
    if class_name == "VAL":
        if root.isdigit():
            return int(root)
        if "=" in root:
            maybe = root.split("=", 1)[1]
            if maybe.isdigit():
                return int(maybe)
    if label.isdigit():
        return int(label)
    return 1


def _resource_total(state: State) -> int:
    total = 0
    for _, inventory in state["resources"].items():
        for _, qty in inventory.items():
            total += int(qty)
    return total


def _ensure_entity(state: State, entity: str) -> None:
    state["resources"].setdefault(entity, {})
    state["states"].setdefault(entity, [])


def _append_history(state: State, step: Dict[str, Any], note: Optional[str] = None) -> None:
    entry = {
        "op_name": step["op_name"],
        "op_family": step["op_family"],
        "roles": dict(step["roles"]),
        "constraints": dict(step.get("constraints", {})),
    }
    if note:
        entry["note"] = note
    state["history"].append(entry)
    state["metadata"]["applied_steps"] += 1
    state["metadata"]["last_schedule"] = step.get("constraints", {}).get("schedule")


def apply_runtime_report(runtime_report: RuntimeReport, initial_state: Optional[State] = None) -> Dict[str, Any]:
    state = deepcopy(initial_state) if initial_state is not None else create_empty_state()

    if not runtime_report.get("accepted", False):
        return {
            "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
            "accepted": False,
            "initial_state": initial_state if initial_state is not None else create_empty_state(),
            "final_state": state,
            "runtime_report": runtime_report,
            "errors": runtime_report.get("errors", []),
        }

    schedule = runtime_report.get("context", {}).get("schedule")
    if schedule == "branch_set":
        return {
            "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
            "accepted": False,
            "initial_state": initial_state if initial_state is not None else create_empty_state(),
            "final_state": state,
            "runtime_report": runtime_report,
            "errors": [{"code": "S_BRANCH_DEFERRED", "message": "branch_set requires external branch selection before state application"}],
        }

    invariant = runtime_report.get("context", {}).get("invariant_law")
    total_before = _resource_total(state)

    for step in runtime_report.get("plan", []):
        op = step["op_name"]
        roles = step["roles"]

        if op == "TRANSFER":
            src = _entity_token(roles.get("src"))
            dst = _entity_token(roles.get("dst"))
            obj = _resource_token(roles.get("obj"))
            qty = _qty_value(roles.get("qty"))
            _ensure_entity(state, src)
            _ensure_entity(state, dst)
            src_qty = int(state["resources"][src].get(obj, 0))
            if src_qty < qty:
                return {
                    "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
                    "accepted": False,
                    "initial_state": initial_state if initial_state is not None else create_empty_state(),
                    "final_state": state,
                    "runtime_report": runtime_report,
                    "errors": [{"code": "S_BALANCE", "message": f"Insufficient balance for {src}:{obj}"}],
                }
            state["resources"][src][obj] = src_qty - qty
            state["resources"][dst][obj] = int(state["resources"][dst].get(obj, 0)) + qty
            _append_history(state, step)

        elif op == "CREATE":
            dst = _entity_token(roles.get("dst"))
            obj = _resource_token(roles.get("obj"))
            qty = _qty_value(roles.get("qty"))
            _ensure_entity(state, dst)
            state["resources"][dst][obj] = int(state["resources"][dst].get(obj, 0)) + qty
            _append_history(state, step)

        elif op == "DESTROY":
            ctx = roles.get("ctx")
            obj = _resource_token(roles.get("obj"))
            qty = _qty_value(roles.get("qty"))
            target = _entity_token(ctx) if ctx else "GLOBAL"
            _ensure_entity(state, target)
            cur = int(state["resources"][target].get(obj, 0))
            if cur < qty:
                return {
                    "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
                    "accepted": False,
                    "initial_state": initial_state if initial_state is not None else create_empty_state(),
                    "final_state": state,
                    "runtime_report": runtime_report,
                    "errors": [{"code": "S_BALANCE", "message": f"Insufficient balance for destroy on {target}:{obj}"}],
                }
            state["resources"][target][obj] = cur - qty
            _append_history(state, step)

        elif op == "ACT":
            state["actions"].append({
                "agt": roles.get("agt"),
                "obj": roles.get("obj"),
                "ctx": roles.get("ctx"),
            })
            _append_history(state, step)

        elif op == "OBSERVE":
            state["observations"].append({
                "agt": roles.get("agt"),
                "obj": roles.get("obj"),
            })
            _append_history(state, step)

        elif op == "CHANGE":
            obj = roles.get("obj")
            res = roles.get("res")
            if obj:
                entity = _entity_token(obj)
                _ensure_entity(state, entity)
                if res:
                    token = _state_token(res)
                    if token not in state["states"][entity]:
                        state["states"][entity].append(token)
            _append_history(state, step)

        elif op == "DEPENDENCY":
            state["dependencies"].append({
                "dst": roles.get("dst"),
                "src": roles.get("src"),
            })
            _append_history(state, step)

        elif op == "EXPAND":
            state["expansions"].append({
                "src": roles.get("src"),
                "res": roles.get("res"),
            })
            _append_history(state, step)

        elif op == "ASSERT_STATE":
            ctx = roles.get("ctx")
            if ctx:
                entity = _entity_token(ctx)
                _ensure_entity(state, entity)
                token = step.get("state_root")
                if token and token not in state["states"][entity]:
                    state["states"][entity].append(token)
            _append_history(state, step)

        else:
            return {
                "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
                "accepted": False,
                "initial_state": initial_state if initial_state is not None else create_empty_state(),
                "final_state": state,
                "runtime_report": runtime_report,
                "errors": [{"code": "S_OP", "message": f"Unsupported state operation: {op}"}],
            }

    if invariant == "ZSUM" and _resource_total(state) != total_before:
        return {
            "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
            "accepted": False,
            "initial_state": initial_state if initial_state is not None else create_empty_state(),
            "final_state": state,
            "runtime_report": runtime_report,
            "errors": [{"code": "S_INV_ZSUM", "message": "ZSUM invariant violated by resulting state"}],
        }

    return {
        "state_model_version": "SEMASCRIPT_STATE_MODEL_v0.1",
        "accepted": True,
        "initial_state": initial_state if initial_state is not None else create_empty_state(),
        "final_state": state,
        "runtime_report": runtime_report,
        "errors": [],
    }


def execute_text_with_state(text: str, profile: str = "exec", initial_state: Optional[State] = None) -> Dict[str, Any]:
    runtime_report = execute_text(text, profile=profile)
    return apply_runtime_report(runtime_report, initial_state=initial_state)


def execute_ast_with_state(path: str, initial_state: Optional[State] = None) -> Dict[str, Any]:
    runtime_report = load_and_execute(path)
    return apply_runtime_report(runtime_report, initial_state=initial_state)
