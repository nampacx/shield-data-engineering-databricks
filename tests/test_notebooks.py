import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_notebooks", ROOT / "scripts" / "check_notebooks.py")
check_notebooks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_notebooks)


def _nb(tmp_path, cells):
    path = tmp_path / "nb.ipynb"
    path.write_text(json.dumps({"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": cells}))
    return path


def _code(source, outputs=None, count=None):
    return {"cell_type": "code", "metadata": {}, "source": [source],
            "outputs": outputs or [], "execution_count": count}


def test_repo_notebooks_pass():
    for path in sorted((ROOT / "notebooks").glob("**/*.ipynb")):
        assert check_notebooks.check(path) == [], path


def test_clean_notebook_passes(tmp_path):
    assert check_notebooks.check(_nb(tmp_path, [_code("%pip install x\nx = 1")])) == []


def test_flags_outputs_counts_run_and_syntax(tmp_path):
    cells = [
        _code("x = 1", outputs=[{"output_type": "stream"}], count=3),
        _code("%run ./other"),
        _code("def broken(:"),
    ]
    problems = check_notebooks.check(_nb(tmp_path, cells))
    assert len(problems) == 4
