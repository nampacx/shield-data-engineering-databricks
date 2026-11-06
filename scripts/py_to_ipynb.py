"""Convert Databricks source-format .py notebooks to .ipynb (renders on GitHub).

Usage: python scripts/py_to_ipynb.py notebooks/databricks/*.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HEADER = "# Databricks notebook source"
SEP = "# COMMAND ----------"


def _cell(raw: str) -> dict:
    lines = raw.strip("\n").split("\n")
    if lines and lines[0].startswith("# MAGIC %md"):
        first = lines[0].removeprefix("# MAGIC %md").strip()
        body = ([first] if first else []) + [
            ln.removeprefix("# MAGIC").removeprefix(" ") for ln in lines[1:]
        ]
        return {"cell_type": "markdown", "metadata": {}, "source": _src(body)}
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _src(lines),
    }


def _src(lines: list[str]) -> list[str]:
    return [ln + "\n" for ln in lines[:-1]] + lines[-1:] if lines else []


def convert(path: Path) -> Path:
    text = path.read_text(encoding="utf-8")
    text = text.removeprefix(HEADER).lstrip("\n")
    cells = [_cell(c) for c in text.split(SEP) if c.strip()]
    nb = {
        "cells": cells,
        "metadata": {
            "application/vnd.databricks.v1+notebook": {"language": "python"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = path.with_suffix(".ipynb")
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(convert(Path(arg)))
