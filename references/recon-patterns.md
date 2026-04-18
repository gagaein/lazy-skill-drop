---
max_lines: 120
version: w2026-17b
role: AI-operational
---

# Recon Patterns

Run before Phase B (Forge). Produces market verdict, moats assessment, and position draft.

## Search strategy (4 axes)

1. **Exact function** keywords → find same-bucket
2. **Domain + verb** (apply/pick/generate/scan/build/drop) → find adjacent
3. **Upper category** broad query → find dead-bucket signal
4. **Cross-ecosystem** — same intent in Cursor rules, MCP servers, Codex agents, Gemini CLI agents, Custom GPTs, OpenCode skills. Skill-space spans ≥12 agents (see Sources).

## Per-candidate signals (extract 6)

1. Last commit date → feeds Status axis
2. Star count — primary activity signal for now (install count deferred, see Future work)
3. README first 500 words
4. Description verb (apply/pick/generate/scan/build/drop) → feeds Bucket axis
5. Explicit non-goals ("if you need X, use Y")
6. Listed ecosystem platforms (Claude Code / Cursor / Codex / MCP / OpenCode / etc.)

## Bucket + Status — orthogonal, tag both

**Bucket** (relatedness — pick one):
- **Direct**: solves ≥90% of same problem for same user
- **Adjacent**: same problem different user, OR different problem same user
- **Tangential**: different user AND different problem, but search-keyword overlap creates discovery collision (e.g. `pr-creator` vs `pr-risk-analyzer`)

**Status** (activity — pick one):
- **Live**: commit within 6 months
- **Dead**: no commit in 6+ months

Tag every candidate `bucket=X, status=Y`. Both axes always present.

## Moats checklist (assess own skill, 5 items, Yes/No/Partial)

1. **Data moat** — exclusive data source (private API key, hand-labeled corpus, UGC closed to competitors)
2. **Network moat** — gets better as more people use it (shared ratings, collaborative matching, compounding signal)
3. **Brand moat** — users will search the skill's name directly, not the generic category
4. **Integration moat** — deeply embedded in one specific tool (dedicated MCP server, VS Code extension, Cursor rule pack)
5. **Velocity moat** — update cadence competitors can't match (weekly evolve loop, auto-regenerating from trending data)

Rule: ≤1 Yes = price-sensitive, hard to defend. ≥2 Yes = durable positioning.

## Verdict table

Count Direct-Live candidates; counts below use Live-only unless stated.

| Verdict | Signal | Strategy |
|---|---|---|
| UNCLAIMED | 0 Direct, ≤2 Adjacent all <100⭐ | Category Creation (if runway) or first-mover positioning |
| EMERGING | 0-1 Direct, 2-5 Adjacent all <1y old | Subcategory or attribute positioning, lock a wedge fast |
| CROWDED_BUT_DIFFERENTIABLE | 0 Direct, 3-6 Adjacent, each ~60% overlap | Clear differentiation: "X and Y do A but assume B; this does B" |
| SATURATED | 1-2 Direct, ≥5 Adjacent, leader ≥500⭐ | Attribute positioning — pick ONE thing to win |
| HEAD_ON_COLLISION | ≥2 Direct ≥1000⭐, all maintained | 10x test OR redefine to subcategory |
| DECLINING | ≥3 Adjacent-Dead, flat stars across Live ones | Identify shift cause, enter only with new angle |

Tangential candidates inform naming (Phase N) but do not count toward verdict thresholds.

## Position draft templates

```
UNCLAIMED            → "First-class skill for [problem]. Nothing like it exists yet."
EMERGING             → "Built for [wedge] in the emerging [category] space."
CROWDED_DIFF         → "{top_adjacent_1} and {top_adjacent_2} let you [A] but assume [B]. This one does [B]."
SATURATED            → "[Attribute]-focused [category]. While others [approach], this one [different]."
HEAD_ON              → Either "10x [axis]" or rename to "[Category] for [niche]."
DECLINING            → "Modernized [old category] for [new reality]" or exit.
```

## Category Creation red lines (do NOT recommend if ANY apply)

1. Runway < 18 months
2. No demonstrable 10x
3. No media bandwidth (blog cadence / conferences / vocabulary work)
4. Bootstrapped / lean
5. Motivation is "avoiding a crowded category"

Default to Attribute Positioning or Subcategory Creation for personal skills.

## What Recon does NOT do

- Does not pick name (use naming-patterns.md)
- Does not write README (Phase B)
- Does not auto-block publish (user may have valid 10x thesis)
- Does not replace Phase A — Recon validates, Phase A extracts

## Commit to memory

Write `{verdict, top-3 adjacent with bucket+status, moats Y/N/Partial × 5, position draft}` to `memory/recon-log.md`. propose.py reads this to detect category-level shifts across weeks.

## Precedence

When Recon says SATURATED but the user insists, do not block. Log override.
When viral-patterns says "short hook" but Recon position_statement needs length, keep position_statement above the hook, don't squeeze it in.


