
from __future__ import annotations

import argparse
from pathlib import Path

from human_normalizer import normalize


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize SEMASCRIPT Human shorthand to Core form")
    parser.add_argument("file", help="Path to file with Human shorthand")
    args = parser.parse_args()

    text = Path(args.file).read_text(encoding="utf-8").strip()
    print(normalize(text))


if __name__ == "__main__":
    main()
