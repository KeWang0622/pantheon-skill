# Security & Privacy Policy

Pantheon handles some of the most sensitive data anyone has: the records, messages, and memories of people they have lost. We take security and privacy extremely seriously.

## Threat model

The realistic threats to a Pantheon user are:

1. **Local file exfiltration.** Someone gaining access to the user's machine can read `~/.pantheon/souls/*/memory.md` and `soul.md` and learn deeply personal information.
2. **Inadvertent upload.** A user accidentally sharing a soul archive (e.g. by adding `~/.pantheon/` to a synced cloud folder, screen-sharing, or pasting a soul file into a chat).
3. **Cross-soul leakage.** A bug in `family_graph` causing one soul to surface another soul's private content inappropriately.
4. **Reconstruction misuse.** Someone using a Pantheon-built soul to impersonate the deceased in a way that harms surviving family members.

We do not currently treat passive network attackers as in-scope because Pantheon does not transmit data over the network in its standard configuration. If that ever changes, this section will be updated and the change called out in `CHANGELOG.md`.

## What Pantheon does to mitigate

- **All data stays local.** No telemetry. No analytics. No "anonymous usage data." Pantheon imports the standard library, `pillow` (optional, for photo EXIF), and `pytest` (dev only). No outbound network calls in normal operation.
- **`~/.pantheon/` is the entire storage footprint.** Nothing is written outside it except temporary scratch in `/tmp` when explicitly invoked.
- **Soul archives are human-readable Markdown + JSON.** No proprietary binary formats. Users can audit, edit, or delete any archive with a text editor.
- **Versioning + rollback.** Every update creates a snapshot via `tools/version_manager.py`. Mistakes are reversible.
- **The `/pantheon-demo` flow never overwrites real archives** — it falls back to a `demo_` prefix on slug conflict.
- **`is_example: true` and `fictional: true` flags** in demo souls' `meta.json` force the runtime to display *"This is a fictional example"* at the top of every dialog.

## What Pantheon explicitly does NOT do

- Pantheon does not upload soul archives anywhere. There is no cloud service, no shared registry, no "social" features.
- Pantheon does not use your soul data to train any model.
- Pantheon does not send analytics or telemetry of any kind.
- Pantheon does not embed advertising or any third-party tracker.

## Reporting a vulnerability

If you discover a security issue — anything from a path-traversal bug in a parser to a leak between souls in the family graph — please report it privately rather than opening a public issue.

**Preferred channel:** GitHub private vulnerability reporting → [Report a vulnerability](https://github.com/KeWang0622/pantheon-skill/security/advisories/new).

**Email:** the address listed in `package.json` (when present) or DM the maintainer on GitHub.

Please include:

- A clear description of the vulnerability.
- Steps to reproduce against the `/pantheon-demo` Wang family example wherever possible (so we never need to look at your real data).
- Any proof-of-concept code (sanitized).
- Your suggested fix, if any.

We will respond within **7 days** with an acknowledgment and within **30 days** with a fix or a written rationale if a fix is not feasible. We will credit you in the security advisory unless you ask us not to.

## What Pantheon will not pay for

Pantheon does not currently run a bug bounty program. We are an open-source project run by individual maintainers. If a vulnerability you report leads to a coordinated disclosure, we will credit you, thank you publicly, and remember you fondly.

## If you are a journalist or researcher

You are welcome to study Pantheon. Please use the `/pantheon-demo` Wang family example for reproduction — those souls are fictional composites and we maintain them precisely so researchers, journalists, and security testers never have to work against real grief data.
