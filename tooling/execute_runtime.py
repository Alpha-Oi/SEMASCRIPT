
from __future__ import annotations

import argparse
import json
from pathlib import Path

from exec_runtime import execute_text, load_and_execute


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute SEMASCRIPT runtime semantics v0.1")
    parser.add_argument("file", help="Input file")
    parser.add_argument("--input-format", choices=["text", "ast"], default="text")
    parser.add_argument("--profile", choices=["human", "core", "exec"], default="exec")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    if args.input_format == "ast":
        result = load_and_execute(args.file)
    else:
        text = Path(args.file).read_text(encoding="utf-8").strip()
        result = execute_text(text, profile=args.profile)

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
