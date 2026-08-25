
from __future__ import annotations

import argparse
import json
from pathlib import Path

from human_normalizer import normalize
from semascript_ast import text_to_ast_document, ast_to_node
from semascript_validator import validate_core_node, validate_exec_node


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SEMASCRIPT corpus entries")
    parser.add_argument("manifest", help="Path to corpus manifest JSON")
    parser.add_argument("--output", required=True, help="Output validation report JSON")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    report_entries = []

    for entry in manifest["entries"]:
        try:
            normalized = normalize(entry["text"]) if entry["profile"] == "human" else entry["text"]
            doc = text_to_ast_document(
                normalized,
                source_profile="normalized" if entry["profile"] == "human" else entry["profile"],
                source_text=entry["text"],
            )
            node = ast_to_node(doc["ast"])
            mode = "exec" if entry["profile"] == "exec" else "core"
            result = validate_exec_node(node) if mode == "exec" else validate_core_node(node)
            report_entries.append({
                "id": entry["id"],
                "profile": entry["profile"],
                "mode": mode,
                "normalized_text": normalized,
                "valid": result.valid,
                "errors": [{"code": code, "message": message} for code, message in result.errors],
            })
        except Exception as exc:
            report_entries.append({
                "id": entry["id"],
                "profile": entry["profile"],
                "mode": "unknown",
                "normalized_text": None,
                "valid": False,
                "errors": [{"code": "PIPELINE", "message": str(exc)}],
            })

    Path(args.output).write_text(json.dumps({
        "schema_version": "SEMASCRIPT_CORPUS_REPORT_v0.1",
        "entries": report_entries
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
