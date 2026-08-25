
from __future__ import annotations

import argparse
from pathlib import Path

from svg_renderer import render_svg_from_text, render_svg_from_ast_file, save_svg


def main() -> None:
    parser = argparse.ArgumentParser(description="Render SEMASCRIPT to SVG prototype")
    parser.add_argument("file", help="Input file")
    parser.add_argument("--input-format", choices=["text", "ast"], default="text")
    parser.add_argument("--profile", choices=["human", "core", "exec"], default="core")
    parser.add_argument("--decompose", action="store_true", help="Decompose patterns before rendering")
    parser.add_argument("--output", required=True, help="Output SVG path")
    args = parser.parse_args()

    if args.input_format == "ast":
        svg = render_svg_from_ast_file(args.file)
    else:
        text = Path(args.file).read_text(encoding="utf-8").strip()
        svg = render_svg_from_text(text, profile=args.profile, decompose=args.decompose)

    save_svg(svg, args.output)


if __name__ == "__main__":
    main()
