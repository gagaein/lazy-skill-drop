# lazy-skill-drop
`git clone https://github.com/gagaein/lazy-skill-drop ~/.claude/skills/lazy-skill-drop`

Say "ship it" and your skill goes live with a README that copies what's working this week.

- Recon before forge — scans 4 axes (exact, domain+verb, category, cross-ecosystem across 12+ agent platforms), tags every competitor `bucket=Direct|Adjacent|Tangential, status=Live|Dead`, returns one of 6 verdicts (UNCLAIMED → HEAD_ON_COLLISION)
- Names + writes README + SKILL.md against this week's viral formula from real install data: 9–16 word hook, install at line 2, 350–450 word body, position statement, concrete example, type-aware bullet count
- One-confirm publish: `gh repo create` with topics, push, fork 3 awesome-lists, insert under the right section, open PRs — no clicking, no forms
- Privacy scan blocks tokens, API keys, and personal paths (macOS / Linux / Windows) before push

## Example

```
you: ship it
lazydrop: recon done — verdict CROWDED_BUT_DIFFERENTIABLE
  3 Direct-Live competitors, leader 412★
  position: "X and Y do A but assume B; this does B directly."
  name: domain-noun pattern (35% of top-20 this week) → "repo-spotter"
  README forged: 412 words, 11-word hook, install at L2, 4 bullets, 1 example
  audit: PASS (7/7 dimensions)
  → repo + 3 awesome-list PRs ready. confirm? (y/n)
you: y
✓ github.com/you/repo-spotter
✓ awesome-claude-code  PR #847
✓ awesome-claude-skills PR #211
✓ claude-skill-index   PR #94
```

## What adjacent tools miss

Generic README generators freeze a template from January. Anthropic's `skill-creator` scaffolds the directory and stops at your local disk. lazy-skill-drop does the part both leave to you — position against what's actually live, name in this week's pattern, ship in one confirm.

## How it works

**Recon (Phase R)** — 4 search axes, 6 signals per candidate (last commit, install count, README first 500 words, description verb, non-goals, listed platforms), 5-moat scorecard. Output: verdict + position draft.

**Forge (Phase B)** — README and SKILL.md generated from this week's structural formula. Length, bullet count, hook structure, install-line position all match the top quartile of currently-trending skills. Naming uses the dominant structure for your skill type (35% domain-noun, 25% verb-noun, 20% brand-prefixed in the latest scan).

**Polish** — two-pass anti-slop filter. Tier-1 banned words (`seamless`, `leverage`, `robust`, `delve`, `utilize`, …) caught before publish. Position statement, length, install-line, and 4 other dimensions audited.

**Ship** — `gh repo create` + push + auto-PR to 3 awesome-lists. Privacy scan first.

The structural formula re-measures itself weekly from real install data. You don't manage that.

## What you do

Once: `gh auth login`.
Every skill: design with Claude, say "ship it", confirm once.

Works with Claude Code, Cursor, Codex, Gemini CLI, OpenCode, and any agent supporting [Agent Skills](https://agentskills.io). Pure Python stdlib + `gh` CLI. No npm, no Docker, no API keys.

---
MIT · built by [@gagaein](https://github.com/gagaein)
