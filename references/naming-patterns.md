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
**Week:** w2026-17 | **Sample:** top-20 skills by install count

### Structure distribution (top-20)

| Structure | Count | Share | Examples |
|---|---|---|---|
| domain-noun | 7 | 35% | frontend-design, web-design-guidelines, vercel-react-best-practices |
| verb-noun | 5 | 25% | find-skills, skill-creator, code-review |
| brand-prefixed | 4 | 20% | microsoft-foundry, remotion-best-practices, vercel-composition-patterns |
| portmanteau / single-word | 3 | 15% | soultrace, brainstorming, agent-browser |
| ironic | 1 | 5% | superpowers |

### What correlates with high install velocity this week

- **Brand-prefixed names** (microsoft-, vercel-, remotion-) dominate top-5 — but this is org authority, not naming quality. Not replicable for solo skills.
- **Exact function names** among solo skills: find-skills (1.1M), skill-creator (152K) — win when the function IS the differentiator.
- **Single-word/portmanteau** with strong identity: soultrace (132K) works because it names the experience, not the mechanism.
- **Short beats long** among solo skills: 1-2 word names outperform 3+ word names at equivalent authority level.

### Direction: what tends to produce hits (not rules)

Pick one of these directions — they're listed by how often they correlate with velocity:

1. **Exact function, verb-first** — works when your differentiator IS the function. `find-skills`, `skill-creator`. If you do ONE thing extremely well, name that thing.
2. **Experience/metaphor, single word** — works when the differentiator is how it *feels*, not what it does. `soultrace`, `superpowers`, `caveman`. The name creates an identity.
3. **Domain-noun, clear audience** — works when SEO matters more than brand. `frontend-design`, `web-design-guidelines`. Discovery-optimized, low memorability.
4. **Verb used as noun** — tight portmanteau or single verb that can be used in a sentence. `skilldrop`, `dispatch`. Works when the action IS the product.

Avoid: names that describe an internal mechanism the user never sees (scan-forge, readme-factory). If a user would never say that phrase when they need the skill, the name is too internal.

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
