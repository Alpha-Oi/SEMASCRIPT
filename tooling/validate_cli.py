
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from semascript_validator import validate_core_text, validate_exec_text


def main() -> None:
    parser = argparse.ArgumentParser(description="SEMASCRIPT parser/validator MVP")
    parser.add_argument("file", help="Path to file with a single SEMASCRIPT construction")
    parser.add_argument("--mode", choices=["core", "exec"], default="core")
    args = parser.parse_args()

    text = Path(args.file).read_text(encoding="utf-8").strip()
    fn: Callable[[str], object] = validate_core_text if args.mode == "core" else validate_exec_text
    result = fn(text)

    print(f"mode={args.mode}")
    print(f"valid={result.valid}")
    if result.errors:
        print("errors:")
        for code, message in result.errors:
            print(f" - {code}: {message}")


if __name__ == "__main__":
    main()
