# lazy-skill-drop

Turn this week's GitHub trending into your skill's README.

Every Monday it scans what's actually starring, extracts the structural formula from the top samples, and shapes your README by that — not a template frozen in January. When you say "ship it", lazydrop writes, audits itself by the same rules, and auto-submits to three awesome lists.

```bash
git clone https://github.com/you/lazy-skill-drop ~/.claude/skills/lazy-skill-drop
```

## How it actually works

**Knowledge layer** — Monday 9am UTC, `scan.py` measures structural DNA from the top `topic:claude-skill` repos: hook length, install position, word count, forbidden-word density, paragraph rhythm. Writes to `viral-patterns.md`.

**Capability layer** — when the formula drifts more than 0.20 from last week, `propose.py` opens a PR to update lazydrop's own targets. Knowledge auto-updates; behavior only changes with your approval.

**Self-audit** — every run, `audit_self.py` grades lazydrop's own docs on the same 8 dimensions it grades yours. If the tool fails its own rules, it tells you plainly instead of silently rotting.

## What ships every time

- `gh repo create` + topics set for discoverability
- README on this week's `w2026-17` formula, two-pass anti-AI-slop polish (Tier 1-4 banned words)
- Three awesome-list PRs auto-forked, entry inserted, PR opened — no clicking
- Privacy scan blocks tokens, API keys, personal paths (macOS / Linux / Windows) before push
- Performance log — if your last 3 ships flopped, lazydrop suggests rolling formula back instead of drifting forward

## Drift severity

```
STABLE    < 0.20   → quiet knowledge update, no PR
DRIFT     < 0.45   → PR with proposed SKILL.md changes
SHIFT     < 0.65   → high-priority PR, knowledge auto-applied
PARADIGM  > 0.65   → suggests full rewrite, needs your call
```

## What you do

**Once:** `brew install gh && gh auth login`. Ten seconds.
**Every skill:** design with Claude, say "ship it", confirm once. 30 seconds.

---

_Pure Python stdlib + gh CLI. No npm, no Docker, no API keys. Works with Claude Code, Cursor, Codex._
