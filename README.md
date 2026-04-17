# lazy-skill-drop
`git clone https://github.com/you/lazy-skill-drop ~/.claude/skills/lazy-skill-drop`

Turn this week's GitHub trending into your skill's README.

Say "ship it" — lazydrop writes, audits, and auto-submits to 3 awesome lists. No forms.

- Weekly scan measures 7 structural fields from real install data: hook length, install position, word count, bullet density, example rate
- Self-audit on 8 regression-calibrated dimensions before every publish — blocks itself if it fails its own rules
- Auto-submits PRs to 3 awesome lists (fork → edit → push → gh pr create) with no clicking
- Privacy scan blocks tokens, API keys, and personal paths (macOS/Linux/Windows) before push

## How it works

**Knowledge layer** — Monday 9am UTC, `scan.py` measures structural DNA from top skill repos. Writes to `viral-patterns.md`. Formula drifts with the market.

**Capability layer** — when formula drifts >0.20 from last week, `propose.py` opens a PR to update lazydrop's own targets. Knowledge auto-updates; behavior only changes with your approval.

**Self-audit** — every run, `audit_self.py` grades lazydrop's own docs on the same dimensions it grades yours. If the tool fails its own rules, it tells you instead of rotting silently.

## Drift severity

```
STABLE    < 0.20   quiet knowledge update, no PR
DRIFT     < 0.45   PR with proposed SKILL.md changes
SHIFT     < 0.65   high-priority PR, knowledge auto-applied
PARADIGM  > 0.65   suggests full rewrite, needs your call
```

## What you do

**Once:** `brew install gh && gh auth login`
**Every skill:** design with Claude, say "ship it", confirm once.

---

_Pure Python stdlib + gh CLI. No npm, no Docker, no API keys._
