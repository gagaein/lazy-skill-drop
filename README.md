# lazy-skill-drop

[![License](https://img.shields.io/github/license/gagaein/lazy-skill-drop)](LICENSE) [![Stars](https://img.shields.io/github/stars/gagaein/lazy-skill-drop?style=social)](https://github.com/gagaein/lazy-skill-drop/stargazers) [![Topic: claude-skill](https://img.shields.io/badge/topic-claude--skill-blue)](https://github.com/topics/claude-skill)

> Works with Claude Code, Cursor, Codex, Gemini CLI, OpenCode, and any agent supporting [Agent Skills](https://agentskills.io). Pure Python stdlib + `gh` CLI — no npm, no Docker, no API keys.

`git clone https://github.com/gagaein/lazy-skill-drop ~/.claude/skills/lazy-skill-drop`

A Claude skill that researches GitHub before you build, so you don't ship the 47th version of someone else's skill.

- **Recon before you commit time** — scans GitHub for skills already doing what you're planning. Shows their install counts, what's in scope vs. out of scope, and a verdict (UNCLAIMED / EMERGING / CROWDED / SATURATED / HEAD_ON_COLLISION). If the space is already saturated, you find out now.
- **Differentiated architecture proposal** — drafts your skill's scope from the competitor gap, then suggests file structure modeled on 2–3 named top-installed skills (with their install counts). Layout types: full-pipeline / rules-pack / tool-only / single-file.
- **README + SKILL.md from real install data** — a weekly scan of trending skills measures install-line placement, length budget, hook patterns, bullet density. Your skill's docs are written to that shape.
- **Publish in one yes** — `gh repo create` + push. Awesome-list PR bodies are pre-written and saved for you to submit manually after your repo earns organic stars.

## How it works

Tell Claude `"I want to build a skill that [does X]"` (or `我想开发一个 [X] 技能`). Then:

1. **Competitor scan.** Looks at GitHub for skills already doing this. If you're about to build the 47th slide-maker, you'll know before you write code.

2. **Differentiated design.** Drafts your skill's scope from what competitors leave out, and file structure modeled on 2–3 specific top-installed skills (named, with install counts). You see the proposal — name, files, what's in scope and what isn't — and change anything you disagree with.

3. **README + SKILL.md from real data.** A weekly script measures the structural shape of currently-winning skill docs — hook style, install-line placement, length budget. Your docs are written to that shape.

4. **Publish in one yes.** When you're happy, say so once. lazydrop creates the GitHub repo and pushes the code. Awesome-list PR bodies are saved to `memory/pr-bodies.md` for you to submit yourself after the repo earns ≥10 organic stars.

## Why no auto-submit to awesome-lists?

Because we read the CONTRIBUTING files. `travisvn/awesome-claude-skills` and similar curated lists explicitly close AI-generated and sub-10-star PRs without comment. Submitting on your behalf before the repo earns organic traction would burn your reputation with the exact maintainers you need. PR bodies are pre-written and ready — submit them yourself after stars accumulate. (If you have a reason to opt in earlier, `publish.py --auto-submit-prs` is still available.)

## When to use this

- You have an idea for a Claude skill but haven't started yet
- You suspect someone has already shipped this and want to check before investing more time
- You've built something and want to package it the way currently-trending skills are packaged

## Quick start

```
# one time
gh auth login

# in any Claude conversation
"I want to build a skill that [your idea]"
```

That's it. lazydrop takes over from there.

---
Open-source under the [MIT License](LICENSE) — license name, not an institutional affiliation · built by [@gagaein](https://github.com/gagaein).
