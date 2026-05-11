#!/usr/bin/env python3
"""Validate every JSON file in the repo parses, and that family tree.json
has the expected shape. Run from CI before pytest.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_TREE_KEYS = {"family_name", "souls", "relationships"}
REQUIRED_SOUL_KEYS = {"name", "relationship", "alias", "born", "generation"}


def _iter_json_files() -> list[Path]:
    skip_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv"}
    out: list[Path] = []
    for p in REPO_ROOT.rglob("*.json"):
        if any(part in skip_dirs for part in p.parts):
            continue
        out.append(p)
    return out


def main() -> int:
    failures: list[str] = []

    for path in _iter_json_files():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            failures.append(f"{path.relative_to(REPO_ROOT)}: parse error: {exc}")
            continue

        if path.name == "tree.json":
            if not isinstance(data, dict):
                failures.append(f"{path.relative_to(REPO_ROOT)}: not an object")
                continue
            missing = REQUIRED_TREE_KEYS - set(data.keys())
            if missing:
                failures.append(
                    f"{path.relative_to(REPO_ROOT)}: missing keys: {sorted(missing)}"
                )
                continue
            for slug, soul in data.get("souls", {}).items():
                missing_soul = REQUIRED_SOUL_KEYS - set(soul.keys())
                if missing_soul:
                    failures.append(
                        f"{path.relative_to(REPO_ROOT)}: soul {slug!r} missing keys: {sorted(missing_soul)}"
                    )

    if failures:
        print("JSON validation failed:", file=sys.stderr)
        for line in failures:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"ok: {len(_iter_json_files())} JSON files valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
