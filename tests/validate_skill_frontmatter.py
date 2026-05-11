#!/usr/bin/env python3
"""Validate that SKILL.md's YAML frontmatter parses and has the required fields.

Run as a CI step before pytest so a malformed SKILL.md fails fast.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = REPO_ROOT / "SKILL.md"

REQUIRED_FIELDS = {"name", "description", "version"}


def load_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        raise ValueError("SKILL.md does not start with '---' frontmatter delimiter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md frontmatter is not properly closed with '---'")
    return yaml.safe_load(parts[1]) or {}


def main() -> int:
    if not SKILL_PATH.is_file():
        print(f"error: {SKILL_PATH} not found", file=sys.stderr)
        return 1

    text = SKILL_PATH.read_text(encoding="utf-8")

    try:
        meta = load_frontmatter(text)
    except (ValueError, yaml.YAMLError) as exc:
        print(f"error parsing SKILL.md frontmatter: {exc}", file=sys.stderr)
        return 1

    missing = REQUIRED_FIELDS - set(meta.keys())
    if missing:
        print(
            f"error: SKILL.md frontmatter missing required fields: {sorted(missing)}",
            file=sys.stderr,
        )
        return 1

    name = meta["name"]
    version = meta["version"]
    print(f"ok: SKILL.md  name={name!r}  version={version!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
