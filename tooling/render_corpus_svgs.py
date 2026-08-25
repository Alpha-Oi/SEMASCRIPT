
from __future__ import annotations

import argparse
import json
from pathlib import Path

from svg_renderer import render_svg_from_text, save_svg


def main() -> None:
    parser = argparse.ArgumentParser(description="Render SEMASCRIPT corpus manifest to SVG prototypes")
    parser.add_argument("manifest", help="Path to corpus manifest JSON")
    parser.add_argument("--output-dir", required=True, help="Output SVG directory")
    parser.add_argument("--decompose", action="store_true", help="Render decomposed form")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for entry in manifest["entries"]:
        svg = render_svg_from_text(entry["text"], profile=entry["profile"], decompose=args.decompose)
        save_svg(svg, out_dir / f"{entry['id']}.svg")


if __name__ == "__main__":
    main()
