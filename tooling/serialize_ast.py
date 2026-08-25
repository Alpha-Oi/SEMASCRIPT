
from __future__ import annotations

import argparse
from pathlib import Path

from semascript_ast import load_ast_document, ast_to_slinear


def main() -> None:
    parser = argparse.ArgumentParser(description="Serialize SEMASCRIPT AST JSON back to S-Linear")
    parser.add_argument("file", help="Path to AST JSON file")
    args = parser.parse_args()

    doc = load_ast_document(args.file)
    print(ast_to_slinear(doc["ast"]))


if __name__ == "__main__":
    main()
