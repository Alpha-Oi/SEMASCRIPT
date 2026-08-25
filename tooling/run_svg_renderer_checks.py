
from __future__ import annotations

import json
from pathlib import Path

from svg_renderer import render_svg_from_text


def main() -> None:
    fixture_dir = Path(__file__).parent / "fixtures"
    cases = json.loads((fixture_dir / "svg_renderer_cases.json").read_text(encoding="utf-8"))

    total = len(cases)
    passed = 0

    for case in cases:
        svg = render_svg_from_text(case["input"], profile=case["profile"], decompose=case.get("decompose", False))
        ok = "<svg" in svg and all(token in svg for token in case.get("must_contain", []))
        if ok:
            passed += 1
        else:
            print(f"FAILED: {case['id']}")
            print(svg[:500])

    print(f"svg_renderer: passed={passed} failed={total - passed} total={total}")


if __name__ == "__main__":
    main()
