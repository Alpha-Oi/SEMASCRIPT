
from __future__ import annotations

import argparse
import json
from pathlib import Path

from human_normalizer import normalize
from semascript_ast import text_to_ast_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse SEMASCRIPT text into AST JSON")
    parser.add_argument("file", help="Path to input text file")
    parser.add_argument("--profile", choices=["human", "core", "exec"], default="core")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    source_text = Path(args.file).read_text(encoding="utf-8").strip()
    normalized = normalize(source_text) if args.profile == "human" else source_text

    doc = text_to_ast_document(
        normalized,
        source_profile="normalized" if args.profile == "human" else args.profile,
        source_text=source_text,
    )
    if args.profile == "human":
        doc["metadata"]["normalized_text"] = normalized

    payload = json.dumps(doc, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
