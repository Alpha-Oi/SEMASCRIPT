
from __future__ import annotations

import json
from pathlib import Path

from run_runtime_corpus import build_runtime_corpus_report
from run_state_corpus import build_state_corpus_report


def main() -> None:
    corpus_dir = Path(__file__).parent / "corpus"
    manifest = json.loads((corpus_dir / "runtime_state_corpus_manifest.json").read_text(encoding="utf-8"))

    runtime_report = build_runtime_corpus_report(manifest)
    state_report = build_state_corpus_report(manifest)

    ok = True

    if runtime_report["summary"]["total"] != 8:
        ok = False
        print("FAILED: runtime total mismatch", runtime_report["summary"])

    if state_report["summary"]["total"] != 8:
        ok = False
        print("FAILED: state total mismatch", state_report["summary"])

    runtime_map = {e["id"]: e for e in runtime_report["entries"]}
    state_map = {e["id"]: e for e in state_report["entries"]}

    # positive runtime/state examples
    ok = ok and runtime_map["BRC01"]["accepted"] is True
    ok = ok and state_map["BRC01"]["accepted"] is True
    ok = ok and runtime_map["BRC04"]["schedule"] == "cyclical"
    ok = ok and state_map["BRC05"]["dependency_count"] == 1
    ok = ok and state_map["BRC06"]["expansion_count"] == 1

    # negative examples
    ok = ok and runtime_map["BRC07"]["accepted"] is False
    ok = ok and any(err["code"] == "R_INV_ZSUM" for err in runtime_map["BRC07"]["errors"])
    ok = ok and state_map["BRC08"]["accepted"] is False
    ok = ok and any(err["code"] == "S_BALANCE" for err in state_map["BRC08"]["errors"])

    if ok:
        print("batch_runtime_state_corpus: passed=1 failed=0 total=1")
    else:
        print("batch_runtime_state_corpus: passed=0 failed=1 total=1")


if __name__ == "__main__":
    main()
