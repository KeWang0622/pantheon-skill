"""Smoke tests for the /pantheon-demo loader.

These are the load-bearing tests — `/pantheon-demo` is the user's first
interaction with Pantheon, so the loader must:

- never overwrite real archives,
- be idempotent across re-runs,
- handle slug conflicts by prefixing with ``demo_``,
- respect ``--force``.

The fixtures isolate every run to a tmp_path so we never touch the real
``~/.pantheon/``.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools import demo_loader


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _example_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "examples" / "wang_family"


def _install(target: Path, *, force: bool = False) -> dict:
    return demo_loader.install_demo(_example_dir(), target, force=force)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_fresh_install_creates_all_souls(tmp_path: Path) -> None:
    result = _install(tmp_path)
    assert result["family_name"] == "王家"
    statuses = {s.slug: s.status for s in result["souls"]}
    assert statuses == {
        "father_wangjianguo": "installed",
        "grandma_zhangxiuying": "installed",
        "grandpa_wanglaoxiansheng": "installed",
    }
    for slug in statuses:
        soul_dir = tmp_path / "souls" / slug
        assert (soul_dir / "meta.json").is_file()
        assert (soul_dir / "memory.md").is_file()
        assert (soul_dir / "soul.md").is_file()


def test_rerun_renames_to_demo_prefix(tmp_path: Path) -> None:
    """If a slug already exists, the demo soul installs as `demo_<slug>` so we
    never clobber a user's real archive."""
    _install(tmp_path)  # first install
    result = _install(tmp_path)  # second run
    for soul in result["souls"]:
        assert soul.status == "renamed"
        assert soul.final_slug.startswith("demo_")
        assert (tmp_path / "souls" / soul.final_slug).is_dir()
    # Originals are untouched.
    for slug in ("father_wangjianguo", "grandma_zhangxiuying", "grandpa_wanglaoxiansheng"):
        assert (tmp_path / "souls" / slug / "meta.json").is_file()


def test_third_run_is_idempotent(tmp_path: Path) -> None:
    """Once both <slug> and demo_<slug> exist, further runs skip cleanly."""
    _install(tmp_path)
    _install(tmp_path)
    result = _install(tmp_path)
    for soul in result["souls"]:
        assert soul.status == "skipped"


def test_force_overwrites_existing(tmp_path: Path) -> None:
    _install(tmp_path)
    # Modify a file so we can prove --force actually replaced it.
    target_meta = tmp_path / "souls" / "father_wangjianguo" / "meta.json"
    target_meta.write_text('{"tampered": true}', encoding="utf-8")
    result = _install(tmp_path, force=True)
    for soul in result["souls"]:
        assert soul.status == "overwritten"
    restored = json.loads(target_meta.read_text(encoding="utf-8"))
    assert restored.get("tampered") is None
    assert restored.get("slug") == "father_wangjianguo"


def test_family_data_mirrored(tmp_path: Path) -> None:
    _install(tmp_path)
    family = tmp_path / "family"
    assert (family / "tree.json").is_file()
    assert (family / "generational_dna.md").is_file()
    assert (family / "rituals" / "grandma_hongshaorou.md").is_file()
    assert (family / "rituals" / "spring_festival.md").is_file()
    tree = json.loads((family / "tree.json").read_text(encoding="utf-8"))
    assert tree["family_name"] == "王家"


def test_missing_example_dir_errors_cleanly(tmp_path: Path) -> None:
    fake = tmp_path / "does_not_exist"
    try:
        demo_loader.install_demo(fake, tmp_path / "out")
    except FileNotFoundError as exc:
        assert "does_not_exist" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")


def test_cli_emits_json(tmp_path: Path, capsys) -> None:
    rc = demo_loader.main(["--target", str(tmp_path), "--json"])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["family_name"] == "王家"
    assert len(parsed["souls"]) == 3


def test_cli_human_summary_lists_souls(tmp_path: Path, capsys) -> None:
    rc = demo_loader.main(["--target", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "王家" in out
    assert "father_wangjianguo" in out
    assert "/pantheon-talk" in out
