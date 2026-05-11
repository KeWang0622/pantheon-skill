# Contributing to Pantheon

Thank you for considering a contribution. Pantheon handles the most personal data anyone has — the memory of people they have lost — so the bar for changes is high. Please read this in full before opening a PR.

---

## Before you start

1. Read [`README.md`](../README.md) to understand what Pantheon is.
2. Read [`ETHICS.md`](../ETHICS.md) — every PR is judged against these guidelines.
3. Try `/pantheon-demo` end-to-end. Don't propose changes to a system you haven't run.

---

## What we accept

| ✅ Welcome | ❌ Not welcome |
|------------|----------------|
| Bug fixes with a failing test attached | Feature flags or A/B-testing infrastructure |
| New data-source parsers (e.g. Discord, Line) | Anything that uploads soul data anywhere |
| Improvements to the tag translation table | Generic "personality clone" features |
| Better honesty-boundary enforcement | Push notifications, daily reminders, "send a message from beyond" |
| Localization (Japanese, Korean, Spanish, ...) | "Pro tier" / subscription / monetization scaffolding |
| Accessibility improvements | Telemetry, analytics, "anonymous usage data" |
| Performance work in the engines | Changes that synthesize content beyond source data |
| Documentation, examples, more demo families | Removing or weakening the AI-reconstruction disclosure |

If your change is in the right-hand column, please open an issue first to discuss before writing code. We will almost certainly say no, but we want to do so with respect.

---

## How to develop

```bash
# Fork + clone
git clone https://github.com/YOUR_USERNAME/pantheon-skill.git
cd pantheon-skill

# Install dev dependencies
pip install -r requirements.txt
pip install pytest

# Run the test suite
pytest

# Try the demo end-to-end (writes to /tmp, not ~/.pantheon)
python tools/demo_loader.py --target /tmp/pantheon_dev --force --json
```

---

## Pull request checklist

Every PR must:

1. **Have a failing test before your change, passing after.** If your change is infrastructure (CI, docs, config), say so in the PR description.
2. **Not break any existing tests.** Run `pytest` locally before pushing.
3. **Not weaken any honesty boundary.** If your change touches `prompts/`, `references/`, or `engine/`, explain in the PR description how you confirmed the boundaries still hold.
4. **Pass the ethics review.** If your change could be construed as commercializing grief, breaching consent, or enabling impersonation, flag it explicitly in the PR description for maintainer discussion.
5. **Update `CHANGELOG.md`** under the `## Unreleased` section.
6. **Update docs.** If you touched a command, update the `命令速查 / Command Reference` table in `SKILL.md` and the relevant section in `README.md`.

---

## Style

- **Python 3.9+.** Type hints encouraged, not required. Avoid third-party deps unless absolutely necessary — Pantheon is dependency-light by design.
- **Markdown.** GitHub-flavored. American English in `README.md`; Chinese in `README_ZH.md`. Both must be updated when user-visible behavior changes.
- **Tests.** `pytest`. Colocated under `tests/`. One test, one assertion when possible.
- **Commits.** Conventional-ish: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`. One concept per commit.

---

## When you have lost someone

This is a personal project for personal reasons. Several contributors here are working on Pantheon *because* they have lost someone close. We don't expect you to share your story, but we also don't pretend grief isn't in the room.

If a contribution becomes hard to make, step back. Pantheon will still be here when you're ready.

---

## Questions

Open a [discussion](https://github.com/KeWang0622/pantheon-skill/discussions) or an issue. We try to respond within a week.
