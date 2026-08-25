
from __future__ import annotations

import argparse
import json
from pathlib import Path

from state_model import execute_text_with_state


def build_state_corpus_report(manifest: dict) -> dict:
    entries = []
    for entry in manifest["entries"]:
        if not entry.get("run_state", True):
            continue

        result = execute_text_with_state(
            entry["text"],
            profile=entry["profile"],
            initial_state=entry.get("initial_state"),
        )
        final_state = result.get("final_state", {})
        entries.append({
            "id": entry["id"],
            "profile": entry["profile"],
            "tags": entry.get("tags", []),
            "accepted": result.get("accepted", False),
            "history_len": len(final_state.get("history", [])),
            "dependency_count": len(final_state.get("dependencies", [])),
            "expansion_count": len(final_state.get("expansions", [])),
            "action_count": len(final_state.get("actions", [])),
            "observation_count": len(final_state.get("observations", [])),
            "errors": result.get("errors", []),
        })

    accepted = sum(1 for e in entries if e["accepted"])
    rejected = len(entries) - accepted
    return {
        "schema_version": "SEMASCRIPT_BATCH_STATE_CORPUS_REPORT_v0.1",
        "entries": entries,
        "summary": {
            "total": len(entries),
            "accepted": accepted,
            "rejected": rejected,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run batch state corpus")
    parser.add_argument("manifest", help="Path to runtime/state corpus manifest")
    parser.add_argument("--output", required=True, help="Output report JSON")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    report = build_state_corpus_report(manifest)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
