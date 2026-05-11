"""Tests that the bundled example souls have the structure the runtime expects.

If any of these fail, ``/pantheon-talk`` will misbehave for new users running
``/pantheon-demo``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_FAMILY = REPO_ROOT / "examples" / "wang_family"
SOULS_DIR = EXAMPLE_FAMILY / "souls"

REQUIRED_META_FIELDS = {
    "name",
    "slug",
    "relationship",
    "alias",
    "born",
    "version",
    "is_example",
    "fictional",
}


@pytest.fixture(scope="module")
def soul_dirs() -> list[Path]:
    return sorted(p for p in SOULS_DIR.iterdir() if p.is_dir())


def test_example_family_has_three_souls(soul_dirs: list[Path]) -> None:
    slugs = {p.name for p in soul_dirs}
    assert slugs == {
        "father_wangjianguo",
        "grandma_zhangxiuying",
        "grandpa_wanglaoxiansheng",
    }


def test_every_soul_has_required_files(soul_dirs: list[Path]) -> None:
    for soul in soul_dirs:
        for fname in ("meta.json", "memory.md", "soul.md"):
            assert (soul / fname).is_file(), f"{soul.name} missing {fname}"


def test_meta_json_has_required_fields(soul_dirs: list[Path]) -> None:
    for soul in soul_dirs:
        meta = json.loads((soul / "meta.json").read_text(encoding="utf-8"))
        missing = REQUIRED_META_FIELDS - set(meta.keys())
        assert not missing, f"{soul.name}/meta.json missing fields: {sorted(missing)}"
        assert meta["slug"] == soul.name, (
            f"{soul.name}/meta.json slug={meta['slug']!r} does not match directory name"
        )
        assert meta["is_example"] is True
        assert meta["fictional"] is True


def test_soul_md_has_honesty_boundary_section(soul_dirs: list[Path]) -> None:
    """Every example soul must include an honesty boundary — this is the part of
    the soul model that prevents the reconstruction from speculating beyond
    source data. If a soul ships without one, the runtime will happily make
    things up."""
    for soul in soul_dirs:
        body = (soul / "soul.md").read_text(encoding="utf-8")
        assert "Honesty Boundary" in body or "诚实边界" in body, (
            f"{soul.name}/soul.md missing honesty boundary section"
        )


def test_soul_md_has_voice_check(soul_dirs: list[Path]) -> None:
    """The voice-check section is the runtime's regression test for whether the
    reconstruction has drifted from the soul's actual speech patterns."""
    for soul in soul_dirs:
        body = (soul / "soul.md").read_text(encoding="utf-8")
        assert "Voice check" in body or "声音检验" in body, (
            f"{soul.name}/soul.md missing voice check"
        )


def test_family_tree_lists_example_souls() -> None:
    tree = json.loads(
        (EXAMPLE_FAMILY / "family" / "tree.json").read_text(encoding="utf-8")
    )
    tree_slugs = set(tree["souls"].keys())
    # The example family ships three fully-built souls. The tree.json declares
    # the wider family graph including souls that aren't fully reconstructed
    # (e.g. 二叔, 妈妈) — so the example souls must be a subset of the tree.
    soul_slugs = {p.name for p in SOULS_DIR.iterdir() if p.is_dir()}
    missing = soul_slugs - tree_slugs
    assert not missing, (
        f"these souls are shipped but not in tree.json: {sorted(missing)}"
    )
