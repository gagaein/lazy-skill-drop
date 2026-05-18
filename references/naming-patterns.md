---
max_lines: 90
version: w2026-17
role: AI-operational
protected: true
evolution: naming-only section is AUTO-UPDATED by scan.py; core-principles section is PROTECTED
---

# Naming Patterns

## When to run this phase

**After Phase C (Position) is confirmed, before Phase B (Forge).**

The positioning sentence tells you three things a name should reflect:
1. What pain you address (from `problem` field)
2. Which competitors you beat and how (from the positioning sentence itself)
3. What the user will say when they need you (from the activation context)

A name generated before positioning is guesswork. A name generated after positioning
can encode the differentiation directly.

---

## Naming reasoning example (this skill's own naming decision)

This section shows **how to reason through a naming decision for a full-pipeline skill**.
It documents lazy-skill-drop's own case. Use it as a reasoning template, not as constraints
that apply to the skill you're currently naming.

**lazy-skill-drop's differentiation:**
- Scans the real leaderboard weekly — formula rebuilt from install data, not frozen in January
- Full pipeline: Recon → Position → Name → README + SKILL.md → Audit → Publish → Evolve
- Self-audits its own output on the same rules it applies to others
- Zero-form UX — extracts from conversation, never asks what user already said

**Why this narrows the name choices:**
- Naming one step (readme-forge, scan-forge) undersells the pipeline scope
- Needs to signal "idea → published" completeness, not a single tool action
- Should work as a verb in a sentence: "skilldrop this", "dispatch my skill"

**Apply the same reasoning to the skill you're naming:**
1. What is its core differentiation (from Phase C positioning sentence)?
2. Does the name signal the full scope or just one step?
3. Does it work as a verb or noun in a natural sentence?

---

## Viral naming patterns (AUTO-UPDATED by scan.py weekly)

<!-- SCAN_SECTION_START — do not edit below this line manually -->
**Week:** w2026-21 | **Sample:** top-8 skills by install count

### Structure distribution (top-8)

| Structure            | Count | Share | Examples |
|---|---|---|---|
| domain-noun          |     5 |   62% | frontend-slides, obsidian-second-brain, claude-blog |
| verb-noun            |     1 |   12% | design-extract |
| brand-prefixed       |     0 |    0% | — |
| portmanteau          |     2 |   25% | hue, nopua |

### High-velocity names this week (fastest growing)

frontend-slides, design-extract, drawio-skill

### Direction: what tends to produce hits

1. **Exact function, verb-first** — works when your differentiator IS the function (`find-skills`, `skill-creator`). Name the thing you do if you do ONE thing extremely well.
2. **Experience/metaphor, single word** — works when the differentiator is how it *feels* (`soultrace`, `superpowers`). Creates identity, not description.
3. **Domain-noun, clear audience** — SEO-optimized, high discovery, lower memorability (`frontend-design`, `web-design-guidelines`).
4. **Tight portmanteau / verb-as-noun** — works when the action IS the product (`skilldrop`, `dispatch`). Must pass: "let me {name} this skill."

Avoid names that describe an internal step the user never sees (scan-forge, readme-factory).

<!-- SCAN_SECTION_END -->

---

## Competitor check (from recon-log.md)

Before locking a name, read `memory/recon-log.md` top-3 adjacent skills.

Check two things:
1. **Name collision** — does any top adjacent have a similar name? If yes, the name creates confusion even if the product is different. Pick a new direction.
2. **Name differentiation** — does your name signal something different from theirs? If they're called `brand-design-md` and `design-chooser`, a name like `design-md-picker` is too close. Go a level up in abstraction or pick a different metaphor.

---

## Gut-check (3 questions)

These are questions, not pass/fail gates.

1. **Can you say it as a verb in a sentence?** "Let me {name} this skill idea" — does it work naturally?
2. **Does it name the outcome or a step?** If it names a step, you're underselling. Go broader.
3. **Would someone search for this name to find this skill?** If not, will they find it anyway via the problem description?

---

## Protected note

This file has two zones:
- **Core principles** (everything outside the `SCAN_SECTION`) — PROTECTED. The evolution loop does not modify these. They encode durable reasoning, not market data.
- **Viral patterns section** (between SCAN_SECTION markers) — AUTO-UPDATED by scan.py. The formula numbers and structure distribution change weekly.

If propose.py ever suggests removing a core principle section, that proposal should be REJECTED. The scan section is the only part that evolves.
