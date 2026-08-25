
from __future__ import annotations

import argparse
import json
from pathlib import Path

from state_model import execute_text_with_state, execute_ast_with_state, load_state


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute SEMASCRIPT with execution state container")
    parser.add_argument("file", help="Input file")
    parser.add_argument("--input-format", choices=["text", "ast"], default="text")
    parser.add_argument("--profile", choices=["human", "core", "exec"], default="exec")
    parser.add_argument("--state", help="Optional initial state JSON")
    parser.add_argument("--output", help="Optional output JSON")
    args = parser.parse_args()

    initial_state = load_state(args.state) if args.state else None

    if args.input_format == "ast":
        result = execute_ast_with_state(args.file, initial_state=initial_state)
    else:
        text = Path(args.file).read_text(encoding="utf-8").strip()
        result = execute_text_with_state(text, profile=args.profile, initial_state=initial_state)

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
