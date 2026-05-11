"""Pantheon demo loader.

Copies the bundled example family (``examples/wang_family/``) into
``~/.pantheon/`` so the user can experience Pantheon end-to-end without
uploading their own family's data.

Design rules:

- **Never overwrite real archives.** If a slug already exists under
  ``~/.pantheon/souls/``, the demo soul is installed under a ``demo_``
  prefix instead.
- **Idempotent.** Re-running is safe: the script reports what already
  existed and only writes what's new.
- **Self-contained.** No third-party dependencies.

The script is invoked by the ``/pantheon-demo`` command defined in
``SKILL.md``. It can also be run directly:

    python tools/demo_loader.py [--target ~/.pantheon] [--force]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXAMPLE = REPO_ROOT / "examples" / "wang_family"
DEFAULT_TARGET = Path.home() / ".pantheon"

DEMO_PREFIX = "demo_"


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class SoulInstall:
    slug: str
    final_slug: str
    status: str  # "installed" | "renamed" | "skipped" | "overwritten"

    @property
    def label(self) -> str:
        if self.status == "renamed":
            return f"  · {self.slug:<32} → {self.final_slug}  (existing soul preserved)"
        if self.status == "skipped":
            return f"  · {self.slug:<32} (already exists — skipped)"
        if self.status == "overwritten":
            return f"  · {self.slug:<32} (overwritten by --force)"
        return f"  · {self.slug:<32} installed"


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------


def _list_example_souls(example_dir: Path) -> list[Path]:
    souls_dir = example_dir / "souls"
    if not souls_dir.is_dir():
        return []
    return sorted(p for p in souls_dir.iterdir() if p.is_dir())


def _install_soul(
    soul_src: Path,
    souls_target: Path,
    *,
    force: bool,
) -> SoulInstall:
    slug = soul_src.name
    target = souls_target / slug

    if target.exists():
        if force:
            shutil.rmtree(target)
            shutil.copytree(soul_src, target)
            return SoulInstall(slug=slug, final_slug=slug, status="overwritten")

        renamed = f"{DEMO_PREFIX}{slug}"
        renamed_target = souls_target / renamed
        if renamed_target.exists():
            # Already installed under demo_ prefix on a previous run.
            return SoulInstall(slug=slug, final_slug=renamed, status="skipped")

        shutil.copytree(soul_src, renamed_target)
        return SoulInstall(slug=slug, final_slug=renamed, status="renamed")

    shutil.copytree(soul_src, target)
    return SoulInstall(slug=slug, final_slug=slug, status="installed")


def _install_family_dir(example_dir: Path, target_root: Path, *, force: bool) -> list[str]:
    """Mirror examples/<family>/family/* into <target>/family/*, preserving any user files."""
    src = example_dir / "family"
    dst = target_root / "family"
    if not src.is_dir():
        return []

    dst.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    for item in sorted(src.rglob("*")):
        if item.is_dir():
            continue
        relative = item.relative_to(src)
        out = dst / relative
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists() and not force:
            installed.append(f"  · family/{relative} (already exists — skipped)")
            continue
        shutil.copy2(item, out)
        installed.append(f"  · family/{relative}")
    return installed


def install_demo(
    example_dir: Path = DEFAULT_EXAMPLE,
    target: Path = DEFAULT_TARGET,
    *,
    force: bool = False,
) -> dict:
    """Install the example family into ``target``. Returns a result dict."""
    if not example_dir.is_dir():
        raise FileNotFoundError(f"example family not found at {example_dir}")

    souls_dir = target / "souls"
    souls_dir.mkdir(parents=True, exist_ok=True)

    soul_results = [
        _install_soul(p, souls_dir, force=force)
        for p in _list_example_souls(example_dir)
    ]
    family_results = _install_family_dir(example_dir, target, force=force)

    family_name = "Unknown"
    tree_path = example_dir / "family" / "tree.json"
    if tree_path.is_file():
        try:
            family_name = json.loads(tree_path.read_text(encoding="utf-8")).get(
                "family_name", "Unknown"
            )
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "target": str(target),
        "example_dir": str(example_dir),
        "family_name": family_name,
        "souls": soul_results,
        "family_files": family_results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_summary(result: dict) -> None:
    family = result["family_name"]
    target = result["target"]
    print()
    print(f"  🕯️  万神殿 · Pantheon — demo installed")
    print(f"      Family: {family}")
    print(f"      Target: {target}")
    print()
    print("  Souls:")
    for soul in result["souls"]:
        print(soul.label)
    if result["family_files"]:
        print()
        print("  Family data:")
        for line in result["family_files"]:
            print(line)
    print()
    print("  Try:")

    # Use the actual final slugs so the printed commands always work.
    talk_slug = next(
        (s.final_slug for s in result["souls"] if "father" in s.slug),
        result["souls"][0].final_slug if result["souls"] else "father_wangjianguo",
    )
    print(f"    /pantheon-talk {talk_slug}")
    print("    /pantheon-tree")
    print("    /pantheon-dna")
    print("    /pantheon-ritual")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install the Pantheon demo family.")
    parser.add_argument(
        "--example",
        type=Path,
        default=DEFAULT_EXAMPLE,
        help="Source example directory (default: examples/wang_family/).",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help="Target Pantheon root (default: ~/.pantheon/).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing souls with matching slugs.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of human summary.",
    )
    args = parser.parse_args(argv)

    try:
        result = install_demo(args.example, args.target, force=args.force)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "target": result["target"],
                    "family_name": result["family_name"],
                    "souls": [
                        {
                            "slug": s.slug,
                            "final_slug": s.final_slug,
                            "status": s.status,
                        }
                        for s in result["souls"]
                    ],
                    "family_files": result["family_files"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        _print_summary(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
