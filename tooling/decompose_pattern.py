
from __future__ import annotations

import argparse
import json
from pathlib import Path

from human_normalizer import normalize
from semascript_ast import text_to_ast_document, load_ast_document
from pattern_decomposer import decompose_ast_document, ast_document_to_slinear


def main() -> None:
    parser = argparse.ArgumentParser(description="Decompose SEMASCRIPT pattern macros into Core-compatible forms")
    parser.add_argument("file", help="Input file")
    parser.add_argument("--input-format", choices=["text", "ast"], default="text")
    parser.add_argument("--profile", choices=["human", "core", "exec"], default="core")
    parser.add_argument("--output-format", choices=["ast", "slinear"], default="slinear")
    parser.add_argument("--output", help="Optional output file")
    args = parser.parse_args()

    if args.input_format == "ast":
        doc = load_ast_document(args.file)
    else:
        source_text = Path(args.file).read_text(encoding="utf-8").strip()
        normalized = normalize(source_text) if args.profile == "human" else source_text
        doc = text_to_ast_document(
            normalized,
            source_profile="normalized" if args.profile == "human" else args.profile,
            source_text=source_text,
        )
        if args.profile == "human":
            doc["metadata"]["normalized_text"] = normalized

    decomposed = decompose_ast_document(doc)

    if args.output_format == "ast":
        payload = json.dumps(decomposed, ensure_ascii=False, indent=2)
    else:
        payload = ast_document_to_slinear(decomposed)

    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
