
from __future__ import annotations

import argparse
import json
from pathlib import Path

from human_normalizer import normalize, HumanNormalizationError
from semascript_ast import text_to_ast_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize SEMASCRIPT corpus entries into AST documents")
    parser.add_argument("manifest", help="Path to corpus manifest JSON")
    parser.add_argument("--output", required=True, help="Output normalized corpus JSON")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    entries = manifest["entries"]
    out = []

    for entry in entries:
        item = {
            "id": entry["id"],
            "profile": entry["profile"],
            "source_text": entry["text"],
        }
        try:
            normalized = normalize(entry["text"]) if entry["profile"] == "human" else entry["text"]
            doc = text_to_ast_document(
                normalized,
                source_profile="normalized" if entry["profile"] == "human" else entry["profile"],
                source_text=entry["text"],
            )
            item["normalized_text"] = normalized
            item["ast_document"] = doc
            item["normalized"] = True
            item["error"] = None
        except Exception as exc:
            item["normalized_text"] = None
            item["ast_document"] = None
            item["normalized"] = False
            item["error"] = str(exc)
        out.append(item)

    Path(args.output).write_text(json.dumps({
        "schema_version": "SEMASCRIPT_CORPUS_NORMALIZED_v0.1",
        "entries": out
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
