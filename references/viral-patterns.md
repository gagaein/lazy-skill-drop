---
max_lines: 70
version: w2026-17
role: AI-operational
applies_to: README.md ONLY — not SKILL.md
note: real data — sampled from skills.sh top 20 + obra/superpowers + anthropics/skills
---

# Viral Patterns (current formula)

**Scope:** this file governs README.md generation only. SKILL.md follows
`skill-md-rules.md`, which has fundamentally different constraints.

This file is the **knowledge layer** — auto-updated weekly by `scripts/scan.py`.
Do not edit by hand; changes will be overwritten by the next scan.

Capability layer (install_line_target, readme_length_target, etc.) lives in
`SKILL.md` frontmatter and only changes via PRs from `scripts/propose.py`.

---

## Current formula — w2026-17

**Scanned:** 2026-04-17
**Sample:** 11 skills, 3,303K total installs (skills.sh top 20 + obra/superpowers + anthropics)
**Method:** manual README extraction from skills.sh pages + GitHub; 7-field quantification

### Structural averages (install-weighted)

```
hook_words:      12.1   (range 4–15)
install_line:     2.0   (ALL skills put install on line 2, right after H1)
readme_length:  209     words (excl. code blocks, range 104–261)
paragraph_count:  5.2   prose paragraphs
bullet_count:    11.5   bullet/list items
heading_depth:    2.2   max H-level (H2 always, H3 common, H4 rare)
```

### Hook opening structure (frequency across sample)

```
command verb first   7/11   "Create ...", "Audit ...", "Take ..."
noun phrase first    3/11   "Domain-specific ...", "Comprehensive ...", "An agentic ..."
question             0/11
```

**Critical finding:** install_line seed was 8.1 — real data is 2.0.
Every top skill puts install command immediately after the H1 title.
The "hook → problem → install" narrative structure is NOT what top skills use.

### Actual top-skill structure (H1 → line 2 install → 4 bullets → H2 body)

```
# skill-name
$ npx skills add owner/repo --skill skill-name

One-sentence capability statement.

- Specific claim with numbers (e.g. "64 rules across 8 categories")
- Second specific claim with scope
- Third specific claim with example output
- Fourth specific claim

## When to Apply / How It Works
...
```

### Concrete example rate

```
has_code_example:    7/11 = 64%   (curl, JS blocks, before/after snippets)
has_position_stmt:   1/11 =  9%   ← was assumed important; actually rare
```

**Critical finding:** position_statement ("unlike X, this does Y") appears in
only 1 of 11 top skills. Replace with: **specific numbers in bullets**.
Top-performing hooks use counts: "50+ styles", "64 rules", "30+ rule files".

### Forbidden words seen in current low-performer sample

```
forbidden_seen:
    "seamless"      in 4/10
    "leverage"      in 3/10
    "comprehensive" in 3/10  ← NOTE: ui-ux-pro-max uses it successfully
    "robust"        in 2/10
```

**Exception rule:** "comprehensive" survives when immediately followed by a
count ("Comprehensive design guide with 50+ styles, 161 color palettes").
The number redeems the vague adjective. Without a number → still forbidden.

### Distinguishing signals (what high-install skills do that low-install ones don't)

- Install command on line 2 — not buried after paragraphs
- 4-bullet summary with concrete numbers (not vague promises)
- Verb-first hook sentence OR noun phrase with specific domain + scale
- Code example OR API call example (64% rate)
- H2 section "When to Apply" or "When to Use" as first body heading
- "Must Use" / "Skip" decision matrix (appears in ui-ux-pro-max, skill-creator)

### What does NOT correlate with installs

- Position statement vs competitors (only caveman, 45K installs, does this)
- Short README length (skill-creator 246w, find-skills 242w both 150K+)
- Prose over bullets — top skills use 10–15 bullets, NOT prose paragraphs

---

### Sources

| Skill | Installs | Type |
|---|---|---|
| find-skills (vercel-labs) | 1,100K | monorepo |
| vercel-react-best-practices | 322K | monorepo |
| frontend-design (anthropics) | 302K | monorepo |
| obra/superpowers | ~600K | standalone |
| web-design-guidelines | 257K | monorepo |
| remotion-best-practices | 244K | monorepo |
| skill-creator (anthropics) | 152K | monorepo |
| soultrace-ai | 132K | standalone |
| ui-ux-pro-max | 119K | standalone |
| caveman | 45K | standalone |
| obsidian-skills | 30K | standalone |

_This file is regenerated every Monday by scan.py. Last regen: 2026-04-17._
