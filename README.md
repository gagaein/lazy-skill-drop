# lazy-skill-drop
`git clone https://github.com/gagaein/lazy-skill-drop ~/.claude/skills/lazy-skill-drop`

Turn this week's GitHub trending into your skill's README — then ship it in 30 seconds.

- Weekly scan measures 7 structural fields from real install data: hook length, install position, word count, bullet density, heading depth, example rate, position statement presence
- Self-audit on 7 regression-calibrated dimensions before every publish — blocks itself if it fails its own rules
- Auto-submits PRs to 3 awesome lists (fork → edit → push → gh pr create) with no clicking
- Privacy scan blocks tokens, API keys, and personal paths (macOS/Linux/Windows) before push

Most README generators pick a template and freeze it. lazy-skill-drop re-measures the real leaderboard every Monday — when the top 300K-install skill uses 64 numbered rules, the formula updates. When the next top skill uses 13 bullets and prose, the type-aware targets update too. The numbers you write against are always last week's market, not a guess from January.

## How it works

**Knowledge layer** — Monday 9am UTC, `scan.py` pulls structural DNA from top skill repos: hook length, install line, word count, bullet count, heading depth, position statement presence, example rate. Writes everything to `viral-patterns.md`. The formula drifts automatically with the market.

**Capability layer** — when the formula drifts >0.20 from last week, `propose.py` opens a PR to update lazydrop's own targets. Knowledge updates every Monday on its own; SKILL.md parameters only change when you merge the PR.

**Self-audit** — before every publish, `audit_self.py` grades lazydrop's own README and SKILL.md on the same 7 dimensions it grades yours. If the tool fails its own rules, it blocks publish and tells you exactly what to fix. No silent rot.

## Drift severity

```
STABLE    < 0.20   quiet knowledge update, no PR
DRIFT     < 0.45   PR with proposed SKILL.md changes
SHIFT     < 0.65   high-priority PR, knowledge auto-applied
PARADIGM  > 0.65   suggests full rewrite, needs your call
```

## What ships every time

- `gh repo create` with topics set for discoverability on skills.sh
- README written against this week's formula, two-pass anti-AI-slop polish (Tier 1–3 banned words)
- Three awesome-list PRs auto-forked, entry inserted under the right section, PR opened
- Privacy scan blocks tokens, API keys, personal macOS/Linux/Windows paths before push
- Performance log entry — if last 3 ships underperformed, suggests rolling formula back

## What you do

**Once:** `brew install gh && gh auth login`

**Every skill:** design with Claude, say "ship it", confirm once.

lazydrop handles the README, the audit, the repo creation, and the three awesome-list PRs.

---

_Pure Python stdlib + gh CLI. No npm, no Docker, no API keys._
_Works with Claude Code, Cursor, Codex, Gemini CLI, and any agent supporting the [Agent Skills](https://agentskills.io) format._
