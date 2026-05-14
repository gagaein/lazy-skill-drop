# lazy-skill-drop
`git clone https://github.com/gagaein/lazy-skill-drop ~/.claude/skills/lazy-skill-drop`

Build a Claude skill positioned against real competitors and structured like this week's top installs.

- **Before you write a line of code** — checks GitHub for skills already doing this, shows their install counts, tells you where the gap is. If the space is saturated without a 10x angle, you'll know before you commit time.
- **Designs a differentiated architecture** — drafts your skill's scope and file structure based on (a) what competitors miss and (b) how this week's top-installed skills are built. Not a generic template — a template shaped by what's winning.
- **Writes README + SKILL.md from real install data** — sentence length, install line position, hook structure, length budget all match this week's top quartile.
- **One yes to publish** — `gh repo create` + push + PRs to 3 discovery lists. No forms, no clicking.

## How it works

Tell Claude `"I want to build a skill that [does X]"` (or `我想开发一个 [X] 技能`). Then:

1. **Competitor scan.** Looks at GitHub for skills already doing this. Shows you who's there, how many installs they have, and where the gap is. If the space is saturated and you don't have a 10x angle, you'll hear about it before you write code.

2. **Differentiated design.** Drafts your skill's scope from what competitors miss, and your file structure modeled on this week's top-installed skills. You see the proposal — name, files, what's in scope and what isn't, plus the 2–3 reference skills it's modeled on — and change anything you disagree with.

3. **README + SKILL.md from real data.** A weekly script measures the structural shape of winning skill docs — hook style, install-line placement, length budget, bullet density. Your skill's docs are written to that shape.

4. **One yes to publish.** When you're happy, say so once. lazydrop creates the GitHub repo, pushes the code, and opens PRs to 3 skill-discovery lists. You see one screen, you say `y`, the rest is automatic.

## When to use this

- You have an idea for a Claude skill but haven't started yet
- You've built something and don't know how to package it so people install it
- You suspect someone may have already shipped this, and you want to check before investing more time

## Quick start

```
# one time
gh auth login

# in any Claude conversation
"I want to build a skill that [your idea]"
```

That's it. lazydrop takes over from there.

---
MIT · built by [@gagaein](https://github.com/gagaein) · works with Claude Code, Cursor, Codex, Gemini CLI, OpenCode, and any agent supporting [Agent Skills](https://agentskills.io). Pure Python stdlib + `gh` CLI — no npm, no Docker, no API keys.
