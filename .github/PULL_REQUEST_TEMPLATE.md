<!--
Thanks for opening a PR. Please make sure you've read CONTRIBUTING.md before continuing.
-->

## What this PR does



## Why

<!-- The real-world need or scenario this addresses. -->



## Ethics check

<!-- Required for any non-trivial change. Pantheon's reputation depends on these. -->

- [ ] No change to the AI-reconstruction disclosure shown at the top of each `/pantheon-talk` session.
- [ ] No change that allows the reconstruction to speculate beyond source data.
- [ ] No telemetry, analytics, or upload paths added.
- [ ] No monetization scaffolding (subscription, pro tier, paywall).
- [ ] If this PR touches `prompts/`, `references/`, or `engine/`, I've confirmed the honesty boundaries still hold and explained how below.

<!-- If any box is unchecked, explain in detail. The maintainer will discuss before reviewing code. -->

## Testing

- [ ] `pytest` passes locally.
- [ ] If this introduces a new behavior, I've added a test that fails on `main` and passes here.
- [ ] If this changes a `/pantheon-*` command, I've run `/pantheon-demo` end-to-end and the command still works against the Wang family example.

## Docs

- [ ] `README.md` updated (if user-visible behavior changed).
- [ ] `README_ZH.md` updated (if user-visible behavior changed).
- [ ] `SKILL.md` updated (if a command's behavior or argument-hint changed).
- [ ] `CHANGELOG.md` entry added under `## Unreleased`.

## Related issues

<!-- e.g. Closes #42 -->
