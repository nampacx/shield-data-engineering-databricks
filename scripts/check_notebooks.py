"""Lint the chapter notebooks: valid JSON, no outputs, every code cell parses, standalone.

Usage: python scripts/check_notebooks.py [notebook.ipynb ...]   (default: notebooks/**/*.ipynb)
Exits 1 and lists the problems when any notebook fails.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _python_only(source: str) -> str:
    """Blank out IPython magics (%pip, %sql, !cmd) so the rest can be parsed."""
    return "\n".join(
        "" if ln.lstrip().startswith(("%", "!")) else ln for ln in source.split("\n")
    )


def check(path: Path) -> list[str]:
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"not valid JSON: {exc}"]
    problems: list[str] = []
    if nb.get("nbformat") != 4 or not isinstance(nb.get("cells"), list):
        return ["not an nbformat 4 notebook"]
    ids = [c.get("id") for c in nb["cells"]]
    if len(set(ids)) != len(ids):
        problems.append("cell ids are not unique")
    for i, cell in enumerate(nb["cells"]):
        where = f"cell {i}"
        source = "".join(cell.get("source", []))
        if not cell.get("id"):
            problems.append(f"{where}: has no id (nbformat 4.5 needs one)")
        if cell.get("cell_type") != "code":
            continue
        if cell.get("outputs"):
            problems.append(f"{where}: has outputs (strip them before commit)")
        if cell.get("execution_count") is not None:
            problems.append(f"{where}: has an execution_count")
        if any(ln.lstrip().startswith("%run") for ln in source.split("\n")):
            problems.append(f"{where}: uses %run (notebooks must be standalone)")
        try:
            ast.parse(_python_only(source))
        except SyntaxError as exc:
            problems.append(f"{where}: does not parse ({exc.msg}, line {exc.lineno})")
    return problems


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv] or sorted(ROOT.glob("notebooks/**/*.ipynb"))
    failed = 0
    for path in paths:
        problems = check(path)
        failed += bool(problems)
        for problem in problems:
            print(f"{path}: {problem}")
    print(f"{len(paths)} notebook(s) checked, {failed} with problems")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
