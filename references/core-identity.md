---
name: core-identity
description: Frozen mission anchor for lazy-skill-drop. NEVER auto-edited. Read by identity_guard.py and propose.py.
version: locked
role: human-protected
protected: always
evolution: never
---

# Core Identity — lazy-skill-drop

## Mission (frozen)

lazy-skill-drop is a one-confirm publisher for Claude skills. Most skills die
from packaging, not capability. Three things, in this order, are the product:

1. **Recon** — analyze the user's adjacent competitors (live + dead) before writing anything; emit verdict + position draft.
2. **Forge** — generate the user's README.md + SKILL.md against this week's structural formula, measured from real install data of currently-trending skills.
3. **Publish** — one user confirmation, then automatic `gh repo create` + push + PRs to 3 awesome-lists.

The weekly self-evolution loop (scan → delta → propose PR) **serves** these three. It is not the product. If a formula update appears to weaken any of them, the PR must be rejected, not merged.

## Invariants — phrase families that must remain in README.md or SKILL.md

`identity_guard.py` runs on every evolve workflow tick. If any family has zero matches across README.md + SKILL.md (case-insensitive regex), the workflow fails and refuses to push knowledge-layer updates.

### family_recon
- "recon"
- "competitor"
- "competitive"
- "adjacent tool"
- "what.*tools? miss"

### family_forge
- "viral"
- "this week"
- "trending"
- "real install"
- "formula"

### family_publish
- "ship"
- "publish"
- "one confirm"
- "gh repo create"
- "awesome"

### family_dual_artifact
- "README.*SKILL.md"
- "SKILL.md.*README"
- "two-document"

## Anti-drift structural constraints (not regex-checked, human-checked)

- Phase R (Recon) must remain in SKILL.md
- Phase B must produce **both** README.md AND SKILL.md
- Phase D must require explicit user confirmation (not auto-publish on silence)

If a propose.py PR appears to violate any of these, refuse to merge. The PR body's "Identity invariants" section exists to surface this on every review.

## When to edit this file

Only when the core mission of lazy-skill-drop changes. That is a human decision. This file is excluded from every auto-commit scope in `.github/workflows/evolve.yml`. Edits arrive only via human-authored commits.
