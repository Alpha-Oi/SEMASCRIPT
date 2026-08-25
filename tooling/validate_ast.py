
from __future__ import annotations

import argparse
import json
from pathlib import Path

from semascript_ast import load_ast_document, ast_to_node
from semascript_validator import validate_core_node, validate_exec_node


def build_report(doc: dict, mode: str) -> dict:
    node = ast_to_node(doc["ast"])
    result = validate_core_node(node) if mode == "core" else validate_exec_node(node)
    annotations = [
        {"code": code, "level": "error", "message": message}
        for code, message in result.errors
    ]
    return {
        "schema_version": doc.get("schema_version"),
        "mode": mode,
        "valid": result.valid,
        "errors": annotations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SEMASCRIPT AST JSON")
    parser.add_argument("file", help="Path to AST JSON file")
    parser.add_argument("--mode", choices=["core", "exec", "auto"], default="auto")
    parser.add_argument("--output", help="Optional output report JSON path")
    args = parser.parse_args()

    doc = load_ast_document(args.file)
    top_class = doc["ast"]["class_name"]
    mode = "exec" if args.mode == "auto" and top_class == "EXEC" else ("core" if args.mode == "auto" else args.mode)
    report = build_report(doc, mode)

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
