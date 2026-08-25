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
        "resources": {},
        "states": {},
        "dependencies": [],
        "observations": [],
        "actions": [],
        "expansions": [],
        "history": [],
        "metadata": {"applied_steps": 0, "last_schedule": None},
    }


def export_text_session(base_url: str, text: str, session_name: str) -> dict:
    _, payload = post_json(base_url, "/api/export-session-text", {
        "text": text,
        "profile": "human",
        "decompose": True,
        "initial_state": empty_state(),
        "session_name": session_name,
    })
    return payload


def project_entry(
    session_id: str,
    session: dict,
    branch_name: str,
    parent_session_ids: list[str] | None = None,
    tags: list[str] | None = None,
    commit_kind: str | None = None,
) -> dict:
    parents = list(parent_session_ids or [])
    if commit_kind == "merge_commit" or len(parents) > 1:
        lineage_kind = "merge_commit"
    elif parents:
        lineage_kind = "commit"
    else:
        lineage_kind = "root"

    entry_metadata = {
        "branching": {
            "branch_name": branch_name,
            "parent_session_ids": parents,
            "lineage_kind": lineage_kind,
        },
    }
    if commit_kind:
        entry_metadata["commit_kind"] = commit_kind

    return {
        "session_id": session_id,
        "session": session,
        "tags": tags or [],
        "entry_metadata": entry_metadata,
        "branch_name": branch_name,
    }


def export_project_index(base_url: str, sessions: list[dict], project_name: str, active_session_id: str) -> dict:
    _, payload = post_json(base_url, "/api/export-project-index", {
        "sessions": sessions,
        "project_name": project_name,
        "active_session_id": active_session_id,
    })
    return payload


def build_branch_ops_project(base_url: str) -> dict:
    base = export_text_session(base_url, "gen(template -> instance)", "Base")
    main_2 = export_text_session(base_url, "gen(template -> instance_main)", "Main 2")
    feature_1 = export_text_session(base_url, "spr(seed -> form_a)", "Feature 1")
    feature_2 = export_text_session(base_url, "spr(seed -> form_b)", "Feature 2")
    return export_project_index(
        base_url,
        [
            project_entry("base_s", base, "main"),
            project_entry("main_2", main_2, "main", ["base_s"]),
            project_entry("feature_1", feature_1, "feature_x", ["base_s"]),
            project_entry("feature_2", feature_2, "feature_x", ["feature_1"]),
        ],
        project_name="HTTP Project Ops",
        active_session_id="feature_2",
    )


def find_session(project_index: dict, session_id: str) -> dict:
    return next(item for item in project_index.get("sessions", []) if item["session_id"] == session_id)


def main() -> None:
    total = 9
    passed = 0

    server = ThreadingHTTPServer(("127.0.0.1", 0), InspectorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        exported_branch_project = build_branch_ops_project(base_url)
        feature_entry = find_session(exported_branch_project, "feature_1")
        ok1 = (
            feature_entry["entry_metadata"]["branching"]["branch_name"] == "feature_x"
            and feature_entry["entry_metadata"]["branching"]["parent_session_ids"] == ["base_s"]
            and exported_branch_project["branches"]["feature_x"]["head_session_id"] == "feature_2"
            and exported_branch_project["active_branch_name"] == "feature_x"
        )
        if ok1:
            passed += 1
        else:
            print("FAILED: branch-aware export project index", exported_branch_project)

        branch_base = export_text_session(base_url, "gen(template -> instance)", "Branch Base")
        branch_project = export_project_index(
            base_url,
            [project_entry("base_s", branch_base, "main")],
            project_name="HTTP Branch Create",
            active_session_id="base_s",
        )
        _, branch_created = post_json(base_url, "/api/create-project-branch", {
            "project_index": branch_project,
            "source_session_id": "base_s",
            "branch_name": "feature_new",
        })
        ok2 = (
            "feature_new" in branch_created["project_index"]["branches"]
            and any(
                event["event_type"] == "branch_created"
                and event.get("payload", {}).get("branch_name") == "feature_new"
                for event in branch_created["project_index"]["history"]["events"]
            )
        )
        if ok2:
            passed += 1
        else:
            print("FAILED: create project branch HTTP route", branch_created)

        _, compare_result = post_json(base_url, "/api/compare-project-sessions", {
            "project_index": exported_branch_project,
            "left_session_id": "base_s",
            "right_session_id": "main_2",
        })
        ok3 = (
            compare_result["compare_version"] == "SEMASCRIPT_CROSS_SESSION_DIFF_v0.1"
            and compare_result["left_session_id"] == "base_s"
            and compare_result["right_session_id"] == "main_2"
        )
        if ok3:
            passed += 1
        else:
            print("FAILED: compare project sessions HTTP route", compare_result)

        auto_base = export_text_session(base_url, "gen(template -> instance)", "Auto Base")
        auto_left = export_text_session(base_url, "gen(template -> instance_a)", "Auto Left")
        auto_right = export_text_session(base_url, "gen(template -> instance)", "Auto Right")
        auto_project = export_project_index(
            base_url,
            [
                project_entry("base_s", auto_base, "main"),
                project_entry("left_s", auto_left, "feature_auto", ["base_s"]),
                project_entry("right_s", auto_right, "main", ["base_s"]),
            ],
            project_name="HTTP Auto Merge",
            active_session_id="right_s",
        )
        _, auto_merge_result = post_json(base_url, "/api/merge-project-sessions-three-way", {
            "project_index": auto_project,
            "base_session_id": "base_s",
            "left_session_id": "left_s",
            "right_session_id": "right_s",
        })
        _, auto_merge_commit = post_json(base_url, "/api/commit-project-merge-result", {
            "project_index": auto_project,
            "merge_or_resolution_result": auto_merge_result,
            "session_id": "merged_branch_commit",
            "session_name": "Merged Branch Commit",
            "activate": True,
            "tags": ["http-project-ops"],
            "branch_name": "merge_branch",
        })
        auto_commit_project = auto_merge_commit["project_index"]
        auto_commit_entry = find_session(auto_commit_project, "merged_branch_commit")
        ok4 = (
            auto_merge_result["summary"]["auto_merged"] is True
            and auto_commit_entry["entry_metadata"]["branching"]["branch_name"] == "merge_branch"
            and auto_commit_project["branches"]["merge_branch"]["head_session_id"] == "merged_branch_commit"
            and auto_commit_project["active_session_id"] == "merged_branch_commit"
        )
        if ok4:
            passed += 1
        else:
            print("FAILED: auto merge commit branch targeting", auto_merge_result, auto_merge_commit)

        conflict_base = export_text_session(base_url, "gen(template -> instance)", "Conflict Base")
        conflict_left = export_text_session(base_url, "gen(template -> instance_a)", "Conflict Left")
        conflict_right = export_text_session(base_url, "gen(template -> instance_b)", "Conflict Right")
        conflict_project = export_project_index(
            base_url,
            [
                project_entry("base_s", conflict_base, "main"),
                project_entry("left_s", conflict_left, "feature_conflict", ["base_s"]),
                project_entry("right_s", conflict_right, "main", ["base_s"]),
            ],
            project_name="HTTP Conflict Merge",
            active_session_id="right_s",
        )
        _, conflict_merge = post_json(base_url, "/api/merge-project-sessions-three-way", {
            "project_index": conflict_project,
            "base_session_id": "base_s",
            "left_session_id": "left_s",
            "right_session_id": "right_s",
        })
        _, conflict_resolution = post_json(base_url, "/api/resolve-project-merge-conflicts", {
            "project_index": conflict_project,
            "base_session_id": "base_s",
            "left_session_id": "left_s",
            "right_session_id": "right_s",
            "decisions": {"source_text": {"choice": "left"}},
        })
        _, resolved_commit = post_json(base_url, "/api/commit-project-merge-result", {
            "project_index": conflict_project,
            "merge_or_resolution_result": conflict_resolution,
            "session_id": "resolved_merge_commit",
            "session_name": "Resolved Merge Commit",
            "activate": False,
            "tags": ["resolved-http-merge"],
            "branch_name": "main",
        })
        resolved_project = resolved_commit["project_index"]
        resolved_entry = find_session(resolved_project, "resolved_merge_commit")
        ok5 = (
            conflict_merge["summary"]["conflict_count"] >= 1
            and resolved_entry["entry_metadata"]["merge_commit"]["conflict_count"] >= 1
            and resolved_entry["session"]["project"]["source_text"] == "gen(template -> instance_a)"
            and any(event["event_type"] == "merge_committed" for event in resolved_project["history"]["events"])
        )
        if ok5:
            passed += 1
        else:
            print("FAILED: conflict merge resolve/commit HTTP route", conflict_merge, conflict_resolution, resolved_commit)

        rebase_project = build_branch_ops_project(base_url)
        _, rebase_result = post_json(base_url, "/api/rebase-project-branch", {
            "project_index": rebase_project,
            "source_branch_name": "feature_x",
            "target_branch_name": "main",
            "activate_head": True,
        })
        replayed_ids = [item["replayed_session_id"] for item in rebase_result["branch_rebase_result"]["replayed_sessions"]]
        first_replayed_entry = find_session(rebase_result["project_index"], replayed_ids[0])
        ok6 = (
            rebase_result["branch_rebase_result"]["summary"]["replayed_count"] == 1
            and first_replayed_entry["entry_metadata"]["branching"]["parent_session_ids"] == ["main_2"]
            and first_replayed_entry["entry_metadata"]["branching"]["branch_name"] == "feature_x"
            and rebase_result["project_index"]["active_branch_name"] == "feature_x"
        )
        if ok6:
            passed += 1
        else:
            print("FAILED: branch rebase HTTP route", rebase_result)

        cherry_pick_project = build_branch_ops_project(base_url)
        _, cherry_pick_result = post_json(base_url, "/api/cherry-pick-project-sessions", {
            "project_index": cherry_pick_project,
            "source_session_ids": ["feature_1", "feature_2"],
            "target_branch_name": "main",
            "activate_head": True,
        })
        picked_ids = [item["replayed_session_id"] for item in cherry_pick_result["branch_cherry_pick_result"]["replayed_sessions"]]
        first_picked_entry = find_session(cherry_pick_result["project_index"], picked_ids[0])
        ok7 = (
            cherry_pick_result["branch_cherry_pick_result"]["summary"]["picked_count"] == 2
            and first_picked_entry["entry_metadata"]["branching"]["parent_session_ids"] == ["main_2"]
            and first_picked_entry["entry_metadata"]["branching"]["branch_name"] == "main"
            and cherry_pick_result["project_index"]["active_branch_name"] == "main"
        )
        if ok7:
            passed += 1
        else:
            print("FAILED: cherry-pick HTTP route", cherry_pick_result)

        squash_project = build_branch_ops_project(base_url)
        _, squash_result = post_json(base_url, "/api/squash-project-sessions", {
            "project_index": squash_project,
            "source_session_ids": ["feature_1", "feature_2"],
            "target_branch_name": "main",
            "session_id": "squash_s",
            "session_name": "Squashed Feature",
            "activate_head": True,
        })
        squash_entry = find_session(squash_result["project_index"], "squash_s")
        ok8 = (
            squash_result["branch_squash_result"]["summary"]["folded_count"] == 2
            and squash_entry["entry_metadata"]["commit_kind"] == "squash_fold"
            and squash_entry["entry_metadata"]["branching"]["branch_name"] == "main"
            and squash_result["project_index"]["active_session_id"] == "squash_s"
        )
        if ok8:
            passed += 1
        else:
            print("FAILED: squash HTTP route", squash_result)

        reset_project = build_branch_ops_project(base_url)
        _, reset_result = post_json(base_url, "/api/reset-project-branch-head", {
            "project_index": reset_project,
            "branch_name": "feature_x",
            "target_session_id": "feature_1",
            "activate_head": True,
        })
        ok9 = (
            reset_result["branch_reset_result"]["target_session_id"] == "feature_1"
            and reset_result["project_index"]["branches"]["feature_x"]["head_session_id"] == "feature_1"
            and reset_result["project_index"]["active_session_id"] == "feature_1"
            and reset_result["project_index"]["active_branch_name"] == "feature_x"
        )
        if ok9:
            passed += 1
        else:
            print("FAILED: reset branch head HTTP route", reset_result)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    print(f"inspector_http_project_ops_e2e: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
