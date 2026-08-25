
from __future__ import annotations

import argparse
import json
from pathlib import Path

from exec_runtime import execute_text


def build_runtime_corpus_report(manifest: dict) -> dict:
    entries = []
    for entry in manifest["entries"]:
        if not entry.get("run_runtime", True):
            continue

        result = execute_text(entry["text"], profile=entry["profile"])
        entries.append({
            "id": entry["id"],
            "profile": entry["profile"],
            "tags": entry.get("tags", []),
            "accepted": result.get("accepted", False),
            "plan_length": len(result.get("plan", [])),
            "schedule": result.get("context", {}).get("schedule"),
            "invariant_law": result.get("context", {}).get("invariant_law"),
            "errors": result.get("errors", []),
            "notes": result.get("notes", []),
        })

    accepted = sum(1 for e in entries if e["accepted"])
    rejected = len(entries) - accepted
    return {
        "schema_version": "SEMASCRIPT_BATCH_RUNTIME_CORPUS_REPORT_v0.1",
        "entries": entries,
        "summary": {
            "total": len(entries),
            "accepted": accepted,
            "rejected": rejected,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run batch runtime corpus")
    parser.add_argument("manifest", help="Path to runtime/state corpus manifest")
    parser.add_argument("--output", required=True, help="Output report JSON")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    report = build_runtime_corpus_report(manifest)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
