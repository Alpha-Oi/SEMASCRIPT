
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace
from session_diff import compare_sessions


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

    a = create_session_from_text(
        text="gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Gen",
    )
    b = create_session_from_text(
        text="spr(seed -> form)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Spr",
    )

    project = create_workspace(project_name="Compare Project")
    project = add_session_to_workspace(project, a, session_id="gen_s")
    project = add_session_to_workspace(project, b, session_id="spr_s")

    diff = compare_sessions(project, "gen_s", "spr_s")
    ok1 = diff["compare_version"] == "SEMASCRIPT_CROSS_SESSION_DIFF_v0.1" and diff["left_session_id"] == "gen_s" and diff["right_session_id"] == "spr_s"
    if ok1:
        passed += 1
    else:
        print("FAILED: diff identity", diff)

    ok2 = (
        diff["structure"]["entities"]["left_only"] or diff["structure"]["entities"]["right_only"]
    ) and diff["execution"]["expansion_count"]["left"] != diff["execution"]["expansion_count"]["right"]
    if ok2:
        passed += 1
    else:
        print("FAILED: diff content", diff)

    print(f"cross_session_compare_diff_mode: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
