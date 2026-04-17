---
max_lines: 70
version: w2026-17
role: AI-operational
applies_to: README.md ONLY — not SKILL.md
note: seed data — needs real scan.py sampling to replace
---

# Viral Patterns (current formula)

**Scope:** this file governs README.md generation only. SKILL.md follows
`skill-md-rules.md`, which has fundamentally different constraints
(imperative style, no narrative, ≤200 lines).

When rules here conflict with anti-ai-patterns.md Tier 2/3 words or
structural patterns, **viral formula wins** per Rule Precedence in SKILL.md.
When they conflict with skill-md-rules.md, skill-md-rules wins
(different file, different reader, different rules).

This file is the **knowledge layer** — it's auto-updated weekly by `scripts/scan.py`
running under `.github/workflows/evolve.yml`. Do not edit by hand unless you know
what you're doing; your changes will get overwritten by the next scan.

Capability layer (i.e. the targets Claude uses to shape new skills) lives in
`SKILL.md` frontmatter: `install_line_target`, `readme_length_target`, etc.
Those only change via PRs proposed by `scripts/propose.py`.


---

## Current formula — w2026-17

**Scanned:** 2026-04-15
**Sample size:** 30 trending skill repos, last 7 days

### Structural averages

```
hook_words:      10.2
install_line:    8.1
readme_length:   247
hook_type:       imperative
bullet_count:    3.4
section_count:   4.2
```

### Hook opening verbs (frequency across sample)

```
"Stop ..."    14/30
"Turn ..."     5/30
"Build ..."    4/30
"Ship ..."     3/30
"Run ..."      2/30
(other)        2/30
```

### Forbidden words seen in current low-performer sample

Detected in trending repos' tails (i.e. samples starred < 5):

```
forbidden_seen:
- "seamless"     in 4/10
- "leverage"     in 3/10
- "comprehensive" in 3/10
- "robust"       in 2/10
- "craft"        in 2/10
- "journey"      in 1/10
```

### Distinguishing signals (what high-star repos do that low-star ones don't)

- Start with imperative verb, not noun or "This skill is"
- Install command before line 10
- Concrete comparison to named alternatives ("unlike X and Y, this does Z")
- Numbers in every adjective claim
- Paragraph length variance > 0.5 (burstiness signal)

---

_This file is regenerated every Monday by scan.py. Last regen: 2026-04-15._
