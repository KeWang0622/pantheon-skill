# Changelog

All notable changes to Pantheon are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed
- Nothing yet.

---

## [1.0.0] — 2026-05-10

The first stable release. Pantheon now ships with a complete demo experience: a fictional three-generation Chinese family (**王家**) that lets anyone run every command end-to-end in under 30 seconds, without uploading any personal data.

### Added

- **`/pantheon-demo` command** (`tools/demo_loader.py`, `SKILL.md`). One-shot installer for the example family — copies `examples/wang_family/` into `~/.pantheon/`. Idempotent. Never overwrites real archives (renames on slug conflict). Supports `--force` and `--json`.
- **王家 example family** (`examples/wang_family/`). Three fully-built souls:
  - `grandpa_wanglaoxiansheng` — 王老先生 (1932–2015), 钳工, lower-confidence reconstruction by design.
  - `grandma_zhangxiuying` — 张秀英 (1935–2020), textile worker, 32 years of three-shift work.
  - `father_wangjianguo` — 王建国 (1958–2023), middle-school physics teacher, 38 years.
  - Each soul ships with `meta.json`, `memory.md`, and `soul.md`. All clearly flagged `fictional: true`.
- **Hero video** (`docs/assets/pantheon-hero.mp4`, 35s). A cinematic walk through the three-deaths frame with the *"三万还不知足 / 你从小就倔 跟我一样"* dialogue as the centerpiece.
- **Bilingual README switcher.** `README.md` is now English-led with `README_ZH.md` mirrored. Both link to the other at the top.
- **`.github/` scaffolding.** `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/bug_report.yml`, `ISSUE_TEMPLATE/feature_request.yml`, `ISSUE_TEMPLATE/config.yml`, `FUNDING.yml`.
- **`SECURITY.md`**. Privacy threat model, vulnerability disclosure process.
- **CI** (`.github/workflows/ci.yml`). Runs on Ubuntu + macOS across Python 3.9–3.12. Validates SKILL.md frontmatter, validates every JSON file, runs the pytest suite.
- **pytest suite** (`tests/`). 14 tests covering the demo loader (8 tests) and the example souls' structural invariants (6 tests). Includes regression coverage for: fresh install, idempotent re-run, slug-conflict renaming, `--force` overwrite, `meta.json` schema, honesty boundary presence, voice check presence, tree.json consistency.
- **`tests/validate_skill_frontmatter.py`** and **`tests/validate_json.py`**. Standalone validators usable from CI without pytest.

### Changed

- **README is now English-primary** and output-first (dialog → demo CTA → engines, in that order). The architecture tree is collapsed into a `<details>` block at the bottom.
- **Surfaced the honesty boundaries and ethics** higher in the README so the trust posture is visible above the fold.
- **`SKILL.md`** updated to register `/pantheon-demo` in the command reference and document the orchestrator behavior for the new command.

### Fixed

- The README previously referenced `souls/example_father/` as a shipped soul, but the directory was empty. The new `examples/wang_family/` replaces this and is fully populated and tested.

### Removed

- The `souls/example_father/` placeholder referenced in the v0.x README is replaced by the fully-built `examples/wang_family/`.

---

## Earlier history (pre-1.0)

Pre-1.0 development was iterative and not tracked in a changelog. The git log starting from commit `c520487` (`Initial release: 万神殿 Pantheon — Digital Immortality for Your Family`) is the canonical pre-1.0 history. The major milestones:

- **`c520487`** — Initial release. Soul reconstruction methodology, ethical framework, crisis resources.
- **`dcb03ad`** — Architecture rebuild inspired by ex-skill / nuwa-skill / colleague-skill.
- **`5290954`** — Pantheon v2: Family System Intelligence (the family-graph thesis).
- **`a5428ec`** — Crisis hotline numbers verified against real sources.
- **`c6d71ca`** — Full English README mirror.

---

[Unreleased]: https://github.com/KeWang0622/pantheon-skill/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/KeWang0622/pantheon-skill/releases/tag/v1.0.0
