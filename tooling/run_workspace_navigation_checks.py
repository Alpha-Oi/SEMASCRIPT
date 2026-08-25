
from __future__ import annotations

from session_model import create_session_from_text
from project_model import create_workspace, add_session_to_workspace
from workspace_navigation import build_workspace_dependency_map


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

    s1 = create_session_from_text(
        text="gen(template -> instance)",
        profile="human",
        decompose=True,
        initial_state=empty_state(),
        session_name="Gen Instance",
    )
    s2 = create_session_from_text(
        text="[EXEC:TRANSFER <src=[ENT:INSTANCE]; dst=[ENT:STORE]; obj=[ENT:RESOURCE]>]",
        profile="exec",
        decompose=True,
        initial_state={
            "state_version": "SEMASCRIPT_STATE_MODEL_v0.1",
            "resources": {"INSTANCE": {"RESOURCE": 2}, "STORE": {"RESOURCE": 0}},
            "states": {},
            "dependencies": [],
            "observations": [],
            "actions": [],
            "expansions": [],
            "history": [],
            "metadata": {"applied_steps": 0, "last_schedule": None},
        },
        session_name="Transfer From Instance",
    )

    project = create_workspace(project_name="Navigation Project")
    project = add_session_to_workspace(project, s1, session_id="gen_instance", tags=["producer"])
    project = add_session_to_workspace(project, s2, session_id="transfer_instance", tags=["consumer"])

    dep_map = build_workspace_dependency_map(project)
    ok1 = dep_map["summary"]["session_count"] == 2 and len(dep_map["nodes"]) == 2
    if ok1:
        passed += 1
    else:
        print("FAILED: node summary")

    flow_links = [link for link in dep_map["links"] if link["relation"] == "flow"]
    ok2 = any(link["from_session_id"] == "gen_instance" and link["to_session_id"] == "transfer_instance" and "INSTANCE" in link["tokens"] for link in flow_links)
    if ok2:
        passed += 1
    else:
        print("FAILED: flow link detection", dep_map)

    print(f"workspace_navigation_dependency_map: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
